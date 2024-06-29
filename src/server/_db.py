import functools
from inspect import signature, Parameter

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from ._config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_DATABASE_URI_PRIMARY, SQLALCHEMY_ENGINE_OPTIONS


# _db.py exists so that we dont have a circular dependency:
#   previously `_common` imported from `_security` which imported from `admin.models`, which imported (back again) from `_common` for database connection objects



# a decorator to automatically provide a sqlalchemy session by default, if an existing session is not explicitly
# specified to override it.  it is preferred to use a single session for a sequence of operations logically grouped
# together, but this allows individual operations to be run by themselves without having to provide an
# already-established session.  requires an argument to the wrapped function named 'session'.
#   for instance:
#
#     @default_session(WriteSession)
#     def foo(session):
#       pass
#
#     #   calling:
#     foo()
#     #   is identical to:
#     with WriteSession() as s:
#       foo(s)
def default_session(sess):
    def decorator__default_session(func):
        # make sure `func` is compatible w/ this decorator
        func_params = signature(func).parameters
        if 'session' not in func_params or func_params['session'].kind == Parameter.POSITIONAL_ONLY:
            raise Exception(f"@default_session(): function {func.__name__}() must accept an argument 'session' that can be specified by keyword.")
        # save position of 'session' arg, to later check if its been passed in by position/order
        sess_index = list(func_params).index('session')

        @functools.wraps(func)
        def wrapper__default_session(*args, **kwargs):
            if 'session' in kwargs or len(args) >= sess_index+1:
                # 'session' has been specified by the caller, so we have nothing to do here.  pass along all args unchanged.
                return func(*args, **kwargs)
            # otherwise, we will wrap this call with a context manager for the default session provider, and pass that session instance to the wrapped function.
            with sess() as session:
                return func(*args, **kwargs, session=session)

        return wrapper__default_session

    return decorator__default_session


engine: Engine = create_engine(SQLALCHEMY_DATABASE_URI, **SQLALCHEMY_ENGINE_OPTIONS, execution_options={'engine_id': 'default'})
Session = sessionmaker(bind=engine)

if SQLALCHEMY_DATABASE_URI_PRIMARY and SQLALCHEMY_DATABASE_URI_PRIMARY != SQLALCHEMY_DATABASE_URI:
    # if available, use the main/primary DB for write operations.  DB replication processes should be in place to
    # propagate any written changes to the regular (load balanced) replicas.
    write_engine: Engine = create_engine(SQLALCHEMY_DATABASE_URI_PRIMARY, **SQLALCHEMY_ENGINE_OPTIONS, execution_options={'engine_id': 'write_engine'})
    WriteSession = sessionmaker(bind=write_engine)
    # TODO: insert log statement acknowledging this second session handle is in use?
else:
    write_engine: Engine = engine
    WriteSession = Session
# NOTE: `WriteSession` could be called `AdminSession`, as its only (currently) used by the admin page, and the admin
#       page is the only thing that should be writing to the db.  its tempting to let the admin page read from the
#       regular `Session` and write with `WriteSession`, but concurrency problems may arise from sync/replication lag.
