"""Structured logger utility for creating JSON logs."""

# the Delphi group uses two ~identical versions of this file.
# try to keep them in sync with edits, for sanity.
#   https://github.com/cmu-delphi/covidcast-indicators/blob/main/_delphi_utils_python/delphi_utils/logger.py  # pylint: disable=line-too-long
#   https://github.com/cmu-delphi/delphi-epidata/blob/dev/src/common/logger.py

import contextlib
import logging
import multiprocessing
import os
import sys
import threading
from traceback import format_exception

import structlog


def handle_exceptions(logger):
    """Handle exceptions using the provided logger."""

    def exception_handler(scope, etype, value, traceback):
        logger.exception("Top-level exception occurred",
                         scope=scope, exc_info=(etype, value, traceback))

    def sys_exception_handler(etype, value, traceback):
        exception_handler("sys", etype, value, traceback)

    def threading_exception_handler(args):
        if args.exc_type == SystemExit and args.exc_value.code == 0:
            # `sys.exit(0)` is considered "successful termination":
            #   https://docs.python.org/3/library/sys.html#sys.exit
            logger.debug("normal thread exit", thread=args.thread,
                        stack="".join(
                            format_exception(
                                args.exc_type, args.exc_value, args.exc_traceback)))
        else:
            exception_handler(f"thread: {args.thread}",
                              args.exc_type, args.exc_value, args.exc_traceback)

    sys.excepthook = sys_exception_handler
    threading.excepthook = threading_exception_handler


def get_structured_logger(name=__name__,
                          filename=None,
                          log_exceptions=True):
    """Create a new structlog logger.

    Use the logger returned from this in indicator code using the standard
    wrapper calls, e.g.:

    logger = get_structured_logger(__name__)
    logger.warning("Error", type="Signal too low").

    The output will be rendered as JSON which can easily be consumed by logs
    processors.

    See the structlog documentation for details.

    Parameters
    ---------
    name: Name to use for logger (included in log lines), __name__ from caller
    is a good choice.
    filename: An (optional) file to write log output.
    """
    # Set the underlying logging configuration
    if "LOG_DEBUG" in os.environ:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    logging.basicConfig(
        format="%(message)s",
        level=log_level,
        handlers=[logging.StreamHandler()])

    def add_pid(_logger, _method_name, event_dict):
        """Add current PID to the event dict."""
        event_dict["pid"] = os.getpid()
        return event_dict

    # Configure structlog. This uses many of the standard suggestions from
    # the structlog documentation.
    structlog.configure(
        processors=[
            # Filter out log levels we are not tracking.
            structlog.stdlib.filter_by_level,
            # Include logger name in output.
            structlog.stdlib.add_logger_name,
            # Include log level in output.
            structlog.stdlib.add_log_level,
            # Include PID in output.
            add_pid,
            # Allow formatting into arguments e.g., logger.info("Hello, %s",
            # name)
            structlog.stdlib.PositionalArgumentsFormatter(),
            # Add timestamps.
            structlog.processors.TimeStamper(fmt="iso"),
            # Match support for exception logging in the standard logger.
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            # Decode unicode characters
            structlog.processors.UnicodeDecoder(),
            # Render as JSON
            structlog.processors.JSONRenderer(),
        ],
        # Use a dict class for keeping track of data.
        context_class=dict,
        # Use a standard logger for the actual log call.
        logger_factory=structlog.stdlib.LoggerFactory(),
        # Use a standard wrapper class for utilities like log.warning()
        wrapper_class=structlog.stdlib.BoundLogger,
        # Cache the logger
        cache_logger_on_first_use=True,
    )

    # Create the underlying python logger and wrap it with structlog
    system_logger = logging.getLogger(name)
    if filename and not system_logger.handlers:
        system_logger.addHandler(logging.FileHandler(filename))
    system_logger.setLevel(log_level)
    logger = structlog.wrap_logger(system_logger)

    if log_exceptions:
        handle_exceptions(logger)

    return logger


class LoggerThread():
    """
    A construct to use a logger from multiprocessing workers/jobs.

    the bare structlog loggers are thread-safe but not multiprocessing-safe.
    a `LoggerThread` will spawn a thread that listens to a mp.Queue
    and logs messages from it with the provided logger,
    so other processes can send logging messages to it
    via the logger-like `SubLogger` interface.
    the SubLogger even logs the pid of the caller.

    this is good to use with a set of jobs that are part of a mp.Pool,
    but isnt recommended for general use
    because of overhead from threading and multiprocessing,
    and because it might introduce lag to log messages.

    somewhat inspired by:
    docs.python.org/3/howto/logging-cookbook.html#logging-to-a-single-file-from-multiple-processes
    """

    class SubLogger():
        """MP-safe logger-like interface to convey log messages to a listening LoggerThread."""

        def __init__(self, queue):
            """Create SubLogger with a bound queue."""
            self.queue = queue

        def _log(self, level, *args, **kwargs):
            kwargs_plus = {'sub_pid': multiprocessing.current_process().pid}
            kwargs_plus.update(kwargs)
            self.queue.put([level, args, kwargs_plus])

        def debug(self, *args, **kwargs):
            """Log a DEBUG level message."""
            self._log(logging.DEBUG, *args, **kwargs)

        def info(self, *args, **kwargs):
            """Log an INFO level message."""
            self._log(logging.INFO, *args, **kwargs)

        def warning(self, *args, **kwargs):
            """Log a WARNING level message."""
            self._log(logging.WARNING, *args, **kwargs)

        def error(self, *args, **kwargs):
            """Log an ERROR level message."""
            self._log(logging.ERROR, *args, **kwargs)

        def critical(self, *args, **kwargs):
            """Log a CRITICAL level message."""
            self._log(logging.CRITICAL, *args, **kwargs)




    def get_sublogger(self):
        """Retrieve SubLogger for this LoggerThread."""
        return self.sublogger

    def __init__(self, logger, q=None):
        """Create and start LoggerThread with supplied logger, creating a queue if not provided."""
        self.logger = logger
        if q:
            self.msg_queue = q
        else:
            self.msg_queue = multiprocessing.Queue()

        def logger_thread_worker():
            logger.info('thread started')
            while True:
                msg = self.msg_queue.get()
                if msg == 'STOP':
                    logger.debug('received stop signal')
                    break
                level, args, kwargs = msg
                if level in [logging.DEBUG, logging.INFO, logging.WARNING,
                             logging.ERROR, logging.CRITICAL]:
                    logger.log(level, *args, **kwargs)
                else:
                    logger.error('received unknown logging level!  exiting...',
                                 level=level, args_kwargs=(args, kwargs))
                    break
            logger.debug('stopping thread')

        self.thread = threading.Thread(target=logger_thread_worker,
                                       name="LoggerThread__"+logger.name)
        logger.debug('starting thread')
        self.thread.start()

        self.sublogger = LoggerThread.SubLogger(self.msg_queue)
        self.running = True

    def stop(self):
        """Terminate this LoggerThread."""
        if not self.running:
            self.logger.warning('thread already stopped')
            return
        self.logger.debug('sending stop signal')
        self.msg_queue.put('STOP')
        self.thread.join()
        self.running = False
        self.logger.info('thread stopped')


@contextlib.contextmanager
def pool_and_threadedlogger(logger, *poolargs):
    """
    Provide (to a context) a multiprocessing Pool and a proxy to the supplied logger.

    Emulates the multiprocessing.Pool() context manager,
    but also provides (via a LoggerThread) a SubLogger proxy to logger
    that can be safely used by pool workers.
    Also "cleans up" the pool by waiting for workers to complete
    as it exits the context.
    """
    with multiprocessing.Manager() as manager:
        logger_thread = LoggerThread(logger, manager.Queue())
        try:
            with multiprocessing.Pool(*poolargs) as pool:
                yield pool, logger_thread.get_sublogger()
                pool.close()
                pool.join()
        finally:
            logger_thread.stop()
