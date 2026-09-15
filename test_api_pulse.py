import io
import unittest
from unittest.mock import patch

from api_pulse import check_endpoint


class FakeResponse:
    def __init__(self, status):
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class ApiPulseTests(unittest.TestCase):
    @patch("api_pulse.urllib.request.urlopen")
    def test_healthy_endpoint(self, urlopen):
        urlopen.return_value = FakeResponse(200)
        result = check_endpoint("Test", "https://example.com", slow_ms=5000)
        self.assertEqual(result["state"], "HEALTHY")
        self.assertEqual(result["status"], 200)

    @patch("api_pulse.urllib.request.urlopen")
    def test_http_error_is_down(self, urlopen):
        import urllib.error
        urlopen.side_effect = urllib.error.HTTPError(
            "https://example.com", 503, "Service Unavailable", {}, io.BytesIO()
        )
        result = check_endpoint("Test", "https://example.com")
        self.assertEqual(result["state"], "DOWN")
        self.assertEqual(result["status"], 503)


if __name__ == "__main__":
    unittest.main()
