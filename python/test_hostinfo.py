import unittest
from unittest.mock import patch, MagicMock
import io
import socket
import sys
import signal
from io import StringIO, BytesIO
from hostinfo_server import (
 get_host_info,
 SimpleHTTPRequestHandler,
 run_web_server,
 terminate,
 main
)
class TestHostInfoServer(unittest.TestCase):

 @patch('socket.gethostname')
 @patch('socket.gethostbyname')
 def test_get_host_info(self, mock_gethostbyname, mock_gethostname):
 """Test that get_host_info returns the expected hostname and IP"""
 # Setup test data
 mock_gethostname.return_value = 'testhost'
 mock_gethostbyname.return_value = '192.168.1.1'
 expected = 'testhost 192.168.1.1\n'

 # Execute function
 result = get_host_info()

 # Verify result
 self.assertEqual(result, expected)

 @patch('hostinfo_server.get_host_info')
 def test_do_GET(self, mock_get_host_info):
 """Test that SimpleHTTPRequestHandler.do_GET properly serves host
info"""
 # Setup test data - using a simple string
 test_host_info = 'testhost 192.168.1.1\n'
 mock_get_host_info.return_value = test_host_info

 # Create output buffer to capture written data
 buffer = BytesIO()

 # Create a testing subclass that captures responses
 class TestHandler(SimpleHTTPRequestHandler):
 def __init__(self):
 self.wfile = buffer
 self.responses = []
 self.headers_sent = False

 def send_response(self, code, message=None):
 self.responses.append((code, message))

 def end_headers(self):
 self.headers_sent = True

 # Create and execute handler
 handler = TestHandler()
 handler.do_GET()

 # Verify the correct response
 self.assertEqual(handler.responses[0], (200, 'OK'))
 self.assertTrue(handler.headers_sent)
 self.assertEqual(buffer.getvalue(), test_host_info.encode('utf-8'))


 def test_terminate(self):
 """Test that terminate function exits gracefully"""
 # Redirect stdout to capture output
 captured_output = StringIO()
 sys.stdout = captured_output

 # Setup exit capture
 exit_called = False

 def fake_exit(code):
 nonlocal exit_called
 exit_called = True
 self.assertEqual(code, 0)

 # Patch sys.exit temporarily
 original_exit = sys.exit
 sys.exit = fake_exit

 try:
 # Execute function
 terminate(None, None)
 finally:
 # Restore stdout and sys.exit
 sys.stdout = sys.__stdout__
 sys.exit = original_exit

 # Verify correct behavior
 self.assertTrue(exit_called)
 output = captured_output.getvalue()
 self.assertIn('Termination requested', output)

 @patch('signal.signal')
 @patch('hostinfo_server.run_web_server')
 def test_main(self, mock_run_web_server, mock_signal):
 """Test that main sets up signal handler and starts server"""
 # Save original sys.argv and replace with test values
 original_argv = sys.argv
 sys.argv = ['hostinfo_server.py', '8080']

 try:
 # Execute function
 main()
 finally:
 # Restore original sys.argv
 sys.argv = original_argv

 # Verify signal handler registration
 mock_signal.assert_called_once_with(signal.SIGTERM, terminate)
   # Verify server launch with correct port
 mock_run_web_server.assert_called_once_with(8080)
if __name__ == '__main__':
 unittest.main()
