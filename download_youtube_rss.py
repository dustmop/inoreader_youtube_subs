import requests
import sys


def read_file(filename):
  fp = open(filename, 'r')
  content = fp.read()
  fp.close()
  return content.strip()


def process():
  output_file = sys.argv[1]
  url = 'https://www.youtube.com/subscription_manager?action_takeout=1'
  cookie = read_file('youtube.cookie')
  user_agent = read_file('user-agent.dat')
  headers = {
    'Host': 'www.youtube.com',
    'User-Agent': user_agent,
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://www.youtube.com/subscription_manager',
    'Cookie': cookie.strip(),
  }
  r = requests.get(url, headers=headers)
  fout = open(output_file, 'w')
  fout.write(r.text)
  fout.close()


if __name__ == '__main__':
  if sys.version_info.major != 3:
    raise RuntimeError('Need Python3')
  process()
