import argparse
from helpers import create_directory


def setup_parsing():
    my_parser = argparse.ArgumentParser()
    my_parser.add_argument('url', action='store')
    my_parser.add_argument('-silent', action='store_true')
    args = my_parser.parse_args()
    start_url = args.url

    if start_url.startswith(('http://', 'https://')):
        start_url = start_url if not start_url.endswith('/') else start_url.strip('/')
        site_name = \
            start_url.replace('http://', '') if start_url.startswith('http://') else start_url.replace('https://', '')
    else:
        site_name = start_url if not start_url.endswith('/') else start_url.strip('/')
        start_url = 'http://' + site_name

    create_directory(site_name)  # creating directory
    return site_name, start_url


if __name__ == '__main__':
    print(setup_parsing())
