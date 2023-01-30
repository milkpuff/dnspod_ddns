
import re
import requests
import logging
import os
import json
import time

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_path = os.path.split(__file__)[0]
file_handler = logging.FileHandler(os.path.join(file_path, 'log.log'))
stream_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)


LOGIN_TOKEN = ''
SUB_DOMAIN = ''
DOMAIN = ''
RECORD_ID = ''


def sync_ipv6(ip):
    data = {
        'login_token': LOGIN_TOKEN,
        'format': 'json',
        'value': ip,
        'sub_domain': SUB_DOMAIN,
        'domain': DOMAIN,
        'record_line': '默认',
        'record_id': RECORD_ID,
    }

    url = 'https://dnsapi.cn/Record.Ddns'
    session = requests.session()
    r = session.post(url=url, data=data, )
    # print(r.json())
    return r.json()


def get_ipv6():
    with open('/proc/net/if_inet6') as f:
        addr, _ = f.readline().split(maxsplit=1)
    addr = re.findall(r'.{4}', addr)
    addr = ':'.join(addr)
    return addr


def load_ip_cache():
    path = os.path.split(os.path.abspath(__file__))[0]
    file = os.path.join(path, 'ip_cache.json')
    try:
        with open(file, 'r') as f:
            data = json.load(f)
    except Exception as e:
        logger.info(f'load json failed, error: {e}')
        data = {}
    ip = data.get('ip', None)
    t = data.get('t', 0)
    return ip, t


def save_ip_cache(ip):
    path = os.path.split(os.path.abspath(__file__))[0]
    file = os.path.join(path, 'ip_cache.json')
    data = {
        'ip': ip,
        't': time.time(),
    }
    with open(file, 'w') as f:
        json.dump(data, f)


def main():
    ip = get_ipv6()
    ip_cache, t = load_ip_cache()
    if ip_cache == ip_cache:
        now = time.time()
        if now - t < 3600*12:
            logger.info(f'ip: {ip}, ip_cache: {ip_cache}, is same, give up update dns. ')
            return
        else:
            logger.info('time past more than 12h, update dns. ')
    else:
        logger.info(f'ip have changed, ip: {ip}, ip_cache: {ip_cache}, update dns. ')

    # print('ipv6: ', ip)
    logger.info(f'ipv6: {ip}')
    res = sync_ipv6(ip)
    logger.info(f'{res}')
    save_ip_cache(ip)


if __name__ == '__main__':
    main()
