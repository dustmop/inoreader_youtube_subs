import sys
assert sys.version_info.major == 3, 'Need Python3'
import requests


def read_file(filename):
  fp = open(filename, 'r')
  content = fp.read()
  fp.close()
  return content.strip()


def process():
  input_file = sys.argv[1]
  url = 'https://www.inoreader.com/reader/subscriptions/import'
  cookie = read_file('user/inoreader.cookie')
  subscriptions = read_file(input_file)
  user_agent = read_file('user/user-agent.dat')
  headers = {
    'Host': 'www.inoreader.com',
    'User-Agent': user_agent,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'http://www.inoreader.com/',
    'Content-Length': '18640',
    'Cookie': cookie.strip(),
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
  }
  files = {
    'import_default_folder': '0',
    'upload_new_folder_name': '',
    'import_file': (input_file, subscriptions, 'text/xml'),
  }
  r = requests.post(url, files=files, headers=headers)
  print r.text


if __name__ == '__main__':
  process()
