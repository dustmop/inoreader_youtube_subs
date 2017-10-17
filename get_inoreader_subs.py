import sys
assert sys.version_info.major == 3, 'Need Python3'
import requests
import urllib
from http.server import BaseHTTPRequestHandler, HTTPServer


def read_file(filename):
  fp = open(filename, 'r')
  content = fp.read().strip()
  fp.close()
  return content


CLIENT_ID = read_file('app/client_id.dat')
# TODO: Randomize
CSRF_TOKEN = 'abcdefg'
PORT = 8000


def display_auth_url():
  template = 'https://www.inoreader.com/oauth2/auth?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope={optional_scopes}&state={csrf_protection_string}'
  data = {'client_id': CLIENT_ID,
          'redirect_uri': 'http://localhost:' % PORT,
          'optional_scopes': 'read',
          'csrf_protection_string': CSRF_TOKEN}
  url = template.format(**data)
  print('Go to this URL in your browser:')
  print(url)
  print('')


_h = None


class testHTTPServer_RequestHandler(BaseHTTPRequestHandler):
  def do_GET(self):
    query = urllib.parse.urlparse(self.path).query
    qs = urllib.parse.parse_qs(query)
    if qs['state'][0] == CSRF_TOKEN:
      self.send_response(200)
      self.send_header('Content-type','text/html')
      self.end_headers()
      message = "Authorized!"
      self.wfile.write(bytes(message, "utf8"))
      fp = open('app/inoreader.oauth', 'w')
      fp.write(qs['code'][0])
      fp.close()
      global _h
      _h.running = False
      return
    else:
      self.send_response(403)
      self.send_header('Content-type','text/html')
      self.end_headers()
      message = "Forbidden"
      self.wfile.write(bytes(message, "utf8"))


class DerivedHTTPServer(HTTPServer):
  def serve_forever(self):
    self.running = True
    while self.running:
      self.handle_request()


def process():
  display_auth_url()
  server_address = ('localhost', PORT)
  global _h
  _h = DerivedHTTPServer(server_address, testHTTPServer_RequestHandler)
  _h.serve_forever()
  print('Done')


if __name__ == '__main__':
  process()
