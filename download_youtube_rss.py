import sys
assert sys.version_info.major == 3, 'Need Python3'
import requests


def read_file(filename):
  fp = open(filename, 'r')
  content = fp.read()
  fp.close()
  return content.strip()


def process():
  output_file = sys.argv[1]
  url = 'https://www.youtube.com/subscription_manager?action_takeout=1'
  cookie = read_file('user/youtube.cookie')
  user_agent = read_file('user/user-agent.dat')
  headers = {
    'Host': 'www.youtube.com',
    'User-Agent': user_agent,
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://www.youtube.com/subscription_manager',
    'Cookie': cookie.strip(),
  }
  r = requests.get(url, headers=headers)
  if r.status_code >= 400:
    print('FAILED to download')
    sys.exit(1)
  fout = open(output_file, 'w')
  fout.write(r.text)
  fout.close()


if __name__ == '__main__':
  process()
