# standard library
import unittest

from delphi.epidata.server._printer import CSVPrinter, sanitize_download_filename

# py3tester coverage target
__test_target__ = "delphi.epidata.server._printer"


class TestDownloadFilenameSanitization(unittest.TestCase):
    """Regression tests for https://github.com/cmu-delphi/delphi-epidata/issues/1805.

    The /covidcast/csv download filename is built from user-controlled
    `signal` components, so it must be sanitized and quoted before being
    placed in the Content-Disposition header.
    """

    def _content_disposition(self, filename):
        printer = CSVPrinter(filename)
        return printer.make_response(iter([])).headers["Content-Disposition"]

    def test_header_filename_is_quoted(self):
        self.assertEqual(
            self._content_disposition("epidata"),
            'attachment; filename="epidata.csv"',
        )

    def test_legitimate_covidcast_filename_preserved(self):
        self.assertEqual(
            self._content_disposition(
                "covidcast-jhu-csse-confirmed_incidence_num-20200101-to-20200901"
            ),
            'attachment; filename="covidcast-jhu-csse-confirmed_incidence_num-20200101-to-20200901.csv"',
        )

    def test_header_injection_chars_sanitized(self):
        # from the issue repro: signal=x:a%22;%20evil%3D%221
        header = self._content_disposition('covidcast-x-a"; evil="1')
        self.assertEqual(header, 'attachment; filename="covidcast-x-a_evil_1.csv"')
        self.assertNotIn(";", header.split("attachment; ", 1)[1])
        self.assertNotIn('"', header.split('filename="', 1)[1].rsplit('"', 1)[0])

    def test_crlf_stripped_from_filename(self):
        header = self._content_disposition("covidcast-x-a\rb\revil\r")
        self.assertNotIn("\r", header)
        self.assertNotIn("\n", header)
        self.assertEqual(header, 'attachment; filename="covidcast-x-a_b_evil.csv"')

    def test_empty_after_sanitization_falls_back_to_default(self):
        self.assertEqual(
            self._content_disposition(";;;"), 'attachment; filename="epidata.csv"'
        )

    def test_no_header_when_filename_falsy(self):
        printer = CSVPrinter(None)
        self.assertNotIn("Content-Disposition", printer.make_response(iter([])).headers)

    def test_sanitize_download_filename_unit(self):
        self.assertEqual(sanitize_download_filename("a b.c-d_e"), "a_b.c-d_e")
        self.assertEqual(sanitize_download_filename("..hidden.."), "hidden")
        self.assertEqual(sanitize_download_filename("a/b\\c:d"), "a_b_c_d")
        self.assertEqual(sanitize_download_filename("x%0d%0a"), "x_0d_0a")


if __name__ == "__main__":
    unittest.main()
