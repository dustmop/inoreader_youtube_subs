import sys
assert sys.version_info.major == 3, 'Need Python3'
import os
import requests
import urllib
import webbrowser
import time
from http.server import BaseHTTPRequestHandler, HTTPServer


def read_file(filename):
  try:
    fp = open(filename, 'r')
  except IOError:
    return None
  content = fp.read().strip()
  fp.close()
  return content


def write_file(filename, content):
  fout = open(filename, 'w')
  fout.write(content)
  fout.close()


CLIENT_ID = read_file('app/client_id.dat')
CLIENT_SECRET = read_file('app/client_secret.dat')
PORT = 8000
REDIRECT_URI = 'http://localhost:%s' % PORT
# TODO: Randomize
CSRF_TOKEN = 'abcdefg'


_g_service = None


class SingleHandler(BaseHTTPRequestHandler):
  def do_GET(self):
    query = urllib.parse.urlparse(self.path).query
    qs = urllib.parse.parse_qs(query)
    if 'state' in qs and 'code' in qs and qs['state'][0] == CSRF_TOKEN:
      write_file('app/inoreader.code', qs['code'][0])
      self.write_response()
      global _g_service
      _g_service.stop_webserver()
    else:
      self.write_forbidden()

  def write_response(self):
    self.send_response(200)
    self.send_header('Content-type', 'text/html')
    self.end_headers()
    self.wfile.write(bytes('Authorized', 'utf8'))

  def write_forbidden(self):
    self.send_response(403)
    self.send_header('Content-type', 'text/html')
    self.end_headers()
    self.wfile.write(bytes('Forbidden', 'utf8'))


class SingleHTTPServer(HTTPServer):
  def serve_loop(self):
    self.running = True
    while self.running:
      self.handle_request()

  def stop(self):
    self.running = False


class InoreaderService(object):
  def auth(self):
    self.access_token = read_file('app/inoreader.access')
    self.refresh_token = read_file('app/inoreader.refresh')
    self.expire_token = read_file('app/inoreader.expire')
    if self.access_token and self.refresh_token:
      expire_time = int(self.expire_token)
      if time.time() >= expire_time:
        self.refresh_tokens(self.refresh_token)
      return
    auth_code = self.get_auth_code()
    self.retrieve_tokens(auth_code)

  def get_subscriptions(self):
    url = 'https://www.inoreader.com/reader/api/0/subscription/list'
    headers = {'Authorization': 'Bearer %s' % self.access_token}
    res = requests.get(url, headers=headers)
    if res.status_code >= 400:
      raise RuntimeError(res.text)
    return res.json()

  def retrieve_tokens(self, auth_code):
    template = 'code={auth_code}&redirect_uri={redirect_uri}&client_id={client_id}&client_secret={client_secret}&scope=&grant_type=authorization_code'
    data = {'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'redirect_uri': REDIRECT_URI,
            'auth_code': auth_code}
    url = 'https://www.inoreader.com/oauth2/token'
    payload = template.format(**data)
    headers = {
      'Content-type': 'application/x-www-form-urlencoded'
    }
    res = requests.post(url, payload, headers=headers)
    if res.status_code >= 400:
      raise RuntimeError(res.text)
    tokens = res.json()
    self.access_token = tokens['access_token']
    self.refresh_token = tokens['refresh_token']
    write_file('app/inoreader.access', self.access_token)
    write_file('app/inoreader.refresh', self.refresh_token)
    write_file('app/inoreader.expire', str(int(time.time() + 3600)))

  def refresh_tokens(self, refresh_token):
    template = 'client_id={client_id}&client_secret={client_secret}&grant_type=refresh_token&refresh_token={refresh_token}'
    data = {'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'refresh_token': refresh_token}
    url = 'https://www.inoreader.com/oauth2/token'
    payload = template.format(**data)
    headers = {
      'Content-type': 'application/x-www-form-urlencoded'
    }
    res = requests.post(url, payload, headers=headers)
    if res.status_code >= 400:
      if 'Invalid refresh token' in res.text:
        print(res.text)
        print('Deleting old refresh token, please try again')
        os.remove('app/inoreader.refresh')
        sys.exit(1)
      raise RuntimeError(res.text)
    tokens = res.json()
    self.access_token = tokens['access_token']
    self.refresh_token = tokens['refresh_token']
    self.expiration = str(int(tokens['expires_in']) + int(time.time()))
    write_file('app/inoreader.access', self.access_token)
    write_file('app/inoreader.refresh', self.refresh_token)
    write_file('app/inoreader.expire', self.expiration)

  def get_auth_code(self):
    template = 'https://www.inoreader.com/oauth2/auth?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope={optional_scopes}&state={csrf_protection_string}'
    data = {'client_id': CLIENT_ID,
            'redirect_uri': REDIRECT_URI,
            'optional_scopes': 'read',
            'csrf_protection_string': CSRF_TOKEN}
    auth_url = template.format(**data)
    print('Opening URL in your browser: {url}'.format(url=auth_url))
    webbrowser.open(auth_url)
    self.waitfor_webserver()
    # Retrieve new auth token.
    return read_file('app/inoreader.code')

  def waitfor_webserver(self):
    self.httpd = SingleHTTPServer(('localhost', PORT), SingleHandler)
    self.httpd.serve_loop()

  def stop_webserver(self):
    self.httpd.stop()


def process():
  service = InoreaderService()
  global _g_service
  _g_service = service
  service.auth()
  # Get subscription, filter and sort.
  tagged = []
  untagged = []
  subs = service.get_subscriptions()
  for item in subs['subscriptions']:
    categories = [cat['label'] for cat in item['categories']]
    categories.remove('YouTube Subscriptions')
    if not categories:
      untagged.append(item['title'])
    else:
      tagged.append((item['title'], categories))
  tagged.sort(key=lambda x:x[0])
  untagged.sort(key=lambda x:x[0])
  # Display results
  print('----------------------------------------')
  print('-- Tagged subscriptions ----------------')
  for title, categories in tagged:
    print(title + ' - ' + str(categories))
  print('----------------------------------------')
  print('-- Untagged ----------------------------')
  for title in untagged:
    print(title)


if __name__ == '__main__':
  process()
