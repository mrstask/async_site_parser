import os
import re
import aiofiles
import json
import itertools
import html
import csv
from urllib.parse import quote, urljoin
from lxml import html as lhtml
from settings import start_url as project_directory
# from pprint import pprint

SAVE_TYPES = {'text/html': ('index.html', '.html'),
              'application/json': ('index.json', '.json'),
              'text/xml': ('index.xml', '.xml'),
              'application/rss+xml': ('index.xml', '.xml'),
              }


class HtmlHandler:
    def __init__(self, response_text, response_url):
        self.domain = response_url.scheme + '://' + response_url.raw_host
        self.inbound = set()
        self.outbound = set()
        self.response_text = response_text
        self.response_url = response_url
        self.parsed_response = lhtml.fromstring(self.response_text.encode('utf8'))
    """ LINK PARSERS """
    def html_inbound_links_parser(self) -> set:
        scripts = self.get_scripts_from_html()
        self.get_links_from_scripts(scripts)

        styles = self.get_styles_from_html()
        self.get_links_from_css(styles)

        self.get_links_from_img()

        self.get_links_from_a_and_link()
        return self.inbound

    def get_links_from_scripts(self, script_text: str):
        try:
            pattern = re.compile(r'[\'|\"](((http(s)*:)|(//))([\w\d\.\-\&\?\/\=])+)[\'|\"]')
            parsed_links = [str(groups[0]) for groups in re.findall(pattern, script_text)]
            # pprint(parsed_links)
            self.separate_links_by_type(parsed_links)
            self.normalize_inbound_links()
            return None
        except Exception as e:
            print('get_scripts', type(e))

    def get_links_from_css(self, styles: str):
        try:
            parsed_links = re.findall(r'url\(([^)]+)\)', styles)
            parsed_links = [url.strip('\'') for url in parsed_links]
            parsed_links = [url for url in parsed_links if '<' not in url]
            # pprint(parsed_links)
            self.separate_links_by_type(parsed_links)
            self.normalize_inbound_links()
            return None
        except Exception as e:
            print('get_scripts', type(e))

    def get_links_from_a_and_link(self):
        try:
            a_urls = [str(link) for link in self.parsed_response.xpath('//a/@href') if link]
            link_urls = [str(link) for link in self.parsed_response.xpath('//link/@href') if link]
            self.separate_links_by_type(a_urls + link_urls)
            self.normalize_inbound_links()
            return None
        except Exception as e:
            print('get_scripts', type(e))

    def get_links_from_img(self):
        try:
            images = [str(image) for image in self.parsed_response.xpath('//img/@src')]
            self.separate_links_by_type(images)
            self.normalize_inbound_links()
            return None
        except Exception as e:
            print('get_image_urls', type(e))

    def get_links_from_xml(self):
        parsed_links = set()
        patterns = [r'=[\'\"]?((http|//)[^\'\" >]+)', r'>((http)[^ <]+)']
        match = itertools.chain.from_iterable([re.findall(pattern, html.unescape(self.response_text))
                                               for pattern in patterns])
        [parsed_links.add(x[0]) for x in match]
        self.separate_links_by_type(parsed_links)
        self.normalize_inbound_links()
        return None

    def get_links_from_json(self):
        json_loaded = json.loads(self.response_text)
        if isinstance(json_loaded, dict):
            for key, item in json_loaded.items():
                self.child_parser(item)
        elif isinstance(json_loaded, list):
            for list_item in json_loaded:
                for key, item in list_item.items():
                    self.child_parser(item)
        else:
            print('weird json content', type(json_loaded), self.response_url)
        return None

    """ HELPER METHODS """
    @staticmethod
    def parse_urls_by_mask(text: str) -> list:
        pattern = re.compile(r'[\'|\"](((http(s)*:)|(//))([\w\d\.\-\&\?\/\=])+)[\'|\"]')
        return [groups[0] for groups in re.findall(pattern, text)]

    def separate_links_by_type(self, links: (list, set)):
        for link in links:
            self.check_link_type(link)
        return None

    def check_link_type(self, link):
        if link.startswith(('http', '//')) and not link.startswith(self.domain):
            self.outbound.add(link)
        else:
            self.inbound.add(link)
        return None

    def normalize_inbound_links(self):
        temp_set = set()
        for link in self.inbound:
            if '#' in link:
                if '?#' in link:
                    link = ''.join(link.split('?#')[:-1])
                else:
                    link = ''.join(link.split('#')[:-1])

            if link.startswith(self.domain):
                temp_set.add(link)
            elif link.startswith('.'):
                temp_set.add(urljoin(self.domain + self.response_url.raw_path,  link))
            elif not link.startswith('/'):
                temp_set.add(self.domain + '/' + link)
            else:
                temp_set.add(self.domain + link)
        self.inbound = temp_set
        return None

    @staticmethod
    async def write_binary(response):
        directory, file_name = HtmlHandler.convert_url_to_static(response.url, response.content_type)
        path = response.url.raw_host + directory + '/'
        if not os.path.exists(project_directory + path):
            os.makedirs(project_directory + path)
        try:
            async with aiofiles.open(project_directory + path + file_name, mode='wb') as f:
                await f.write(await response.read())
                await f.close()
        except OSError:
            print('OSError')
        return project_directory + path + file_name

    @staticmethod
    def convert_url_to_static(response_url, file_type: str) -> [str, str]:
        if response_url.query_string and file_type not in ['text/css', 'font/woff', 'image/svg+xml', 'image/png']:
            file_name = HtmlHandler.convert_url_with_question(response_url, file_type)
        else:
            file_name = HtmlHandler.convert_url_with_no_slash_no_ext(response_url, file_type)
        directory = '/'.join(response_url.raw_path.split('/')[:-1])
        return directory, file_name

    @staticmethod
    def convert_url_with_no_slash_no_ext(response_url, file_type):
        path = response_url.raw_path
        path = path + '/' if not path.endswith('/') and '.' not in path else path
        if file_type and '.' not in response_url.name:
            file_name = SAVE_TYPES[file_type][0]
        else:
            file_name = path.split('/')[-1]
        return file_name

    @staticmethod
    def convert_url_with_question(response_url, file_type):
        path = response_url.raw_path
        file_name = quote(response_url.raw_name.replace('.', '_') + '?' +
                          response_url.query_string + SAVE_TYPES[file_type][1], safe='')
        print('changed path from ', response_url, ' to ', response_url.scheme + '://'
              + response_url.raw_host + path + file_name)
        HtmlHandler.write_htaccess_file((str(response_url), response_url.scheme + '://'
                                         + response_url.raw_host + path + file_name))
        return file_name

    def get_scripts_from_html(self) -> str:
        scripts = self.parsed_response.xpath('//script/text()')
        return ''.join([script.replace('\\', '') for script in scripts])

    def get_styles_from_html(self) -> str:
        styles = self.parsed_response.xpath('//style/text()')
        return ''.join([style for style in styles])

    def child_parser(self, child):
        if isinstance(child, (bool, int, type(None))):
            pass
        elif isinstance(child, str):
            if child.startswith(('http', '/')):
                self.check_link_type(child)
        elif isinstance(child, list):
            [self.child_parser(_) for _ in child]
        else:
            for _, value in child.items():
                self.child_parser(value)
        return None

    @staticmethod
    def write_htaccess_file(file_for_htaccess):
        path = project_directory + 'csv_for_htaccess.csv'
        open_type = 'a' if os.path.exists(path) else 'w'
        with open(path, open_type) as file:
            writer = csv.writer(file)
            writer.writerow(file_for_htaccess)

