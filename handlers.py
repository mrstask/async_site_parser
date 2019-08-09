import os
import re
import aiofiles
import json
import itertools
import html
import asyncio
import csv
from urllib.parse import quote, urljoin
from lxml import html as lhtml
from settings import project_directory, TYPE_METHODS, TO_SAVE_TYPES, USELESS_TYPES
from logger import my_logger
# from pprint import pprint

# todo huynya s putyami
# save_path = project_directory + site_name + '/'

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
            my_logger.exception('%(funcName)s -  %(message)s' + str(e))

    def get_links_from_css(self, styles: str):
        try:
            parsed_links = re.findall(r'url\(([^)]+)\)', styles)
            temp_parsed_links = []
            for url in parsed_links:
                if '"' not in url:
                    temp_parsed_links.append(url)
            parsed_links = [url.strip('\'') for url in temp_parsed_links]
            parsed_links = [url for url in parsed_links if '<' not in url]
            # pprint(parsed_links)
            self.separate_links_by_type(parsed_links)
            self.normalize_inbound_links()
            return None
        except Exception as e:
            my_logger.exception('%(funcName)s -  %(message)s' + str(e))

    def get_links_from_a_and_link(self):
        try:
            a_urls = [str(link) for link in self.parsed_response.xpath('//a/@href') if link]
            link_urls = [str(link) for link in self.parsed_response.xpath('//link/@href') if link]
            self.separate_links_by_type(a_urls + link_urls)
            self.normalize_inbound_links()
            return None
        except Exception as e:
            my_logger.exception('%(funcName)s -  %(message)s' + str(e))

    def get_links_from_img(self):
        try:
            images = [str(image) for image in self.parsed_response.xpath('//img/@src')]
            self.separate_links_by_type(images)
            self.normalize_inbound_links()
            return None
        except Exception as e:
            my_logger.exception('%(funcName)s -  %(message)s' + str(e))

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
            my_logger.error('%(funcName)s -  %(message)s' + 'weird json content' + type(json_loaded) +
                          str(self.response_url))
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
        new_url, file_path = HtmlHandler.convert_url_to_static(response.url, response.content_type)
        # my_logger.debug(response.url, new_url, file_path)
        save_directory = response.url.raw_host + '/'.join(file_path.split('/')[:-1])
        if not os.path.exists(project_directory + save_directory):
            os.makedirs(project_directory + save_directory)
        try:
            async with aiofiles.open(project_directory + response.url.raw_host + file_path, mode='wb') as f:
                await f.write(await response.read())
                await f.close()
        except OSError:
            my_logger.exception(str(OSError))
        return project_directory + response.url.raw_host + file_path

    @staticmethod
    def convert_url_to_static(response_url, file_type: str) -> [str, str]:
        if response_url.query_string and file_type not in ['text/css', 'font/woff', 'image/svg+xml', 'image/png',
                                                           'image/jpeg', 'image/gif']:
            new_url, file_name = HtmlHandler.convert_url_with_question(response_url, file_type)
            file_path = '/'.join(response_url.raw_path.split('/')[:-1]) + file_name
        else:
            new_url = response_url
            file_path = HtmlHandler.convert_url_with_no_slash_no_ext(response_url, file_type)
        return new_url, file_path

    @staticmethod
    def convert_url_with_no_slash_no_ext(response_url, file_type):
        path = response_url.raw_path
        path = path + '/' if not path.endswith('/') and '.' not in path else path
        if file_type and '.' not in response_url.name:
            file_name = path + SAVE_TYPES[file_type][0]
        else:
            file_name = path
        return file_name

    @staticmethod
    def convert_url_with_question(response_url, file_type):
        path = response_url.raw_path
        file_name = '/' + quote(response_url.raw_name.replace('.', '_') + '?' +
                                response_url.query_string + SAVE_TYPES[file_type][1], safe='')
        my_logger.info('changed path from ' + str(response_url) + ' to ' + response_url.scheme
                       + '://' + response_url.raw_host + path + file_name)
        new_url = response_url.scheme + '://' + response_url.raw_host + path[:-1] + file_name
        HtmlHandler.write_htaccess_file(str(response_url), new_url, response_url.raw_host)
        return new_url, file_name

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
    def write_htaccess_file(old_url, new_url, site_name):
        path = project_directory + site_name + '/csv_for_htaccess.csv'
        open_type = 'a' if os.path.exists(path) else 'w'
        with open(path, open_type) as file:
            writer = csv.writer(file)
            writer.writerow([old_url, new_url])


class StreamHelpers:
    def __init__(self):
        self.qu = asyncio.Queue()
        self.parsed_urls = set()
        self.queued_urls = set()
        self.bad_urls = set()

    async def add_links_and_save_file(self, file_object, response):
        for url in file_object.inbound:
            if url not in self.parsed_urls and url not in self.queued_urls:
                self.queued_urls.add(url)
                await self.qu.put(url)
        await HtmlHandler.write_binary(response)

    async def get_inbound_links_and_save_file(self, response, response_text, response_url, content_type):
        type_object = HtmlHandler(response_text, response_url)

        if content_type in ['text/css', 'text/javascript']:
            getattr(type_object, TYPE_METHODS[content_type])(type_object.response_text)
        else:
            getattr(type_object, TYPE_METHODS[content_type])()
        my_logger.info(str(response_url) + ': ' + str(type_object.inbound.difference(self.queued_urls)))
        await self.add_links_and_save_file(type_object, response)

    @staticmethod
    async def content_router(response, stream):
        if response.content_type == 'text/html':
            await stream.get_inbound_links_and_save_file(response, await response.text(), response.url,
                                                         response.content_type)

        if response.content_type == 'text/css':
            await stream.get_inbound_links_and_save_file(response, await response.text(), response.url,
                                                         response.content_type)

        if response.content_type == 'text/javascript':
            await stream.get_inbound_links_and_save_file(response, await response.text(), response.url,
                                                         response.content_type)

        if response.content_type == 'text/xml':
            await stream.get_inbound_links_and_save_file(response, await response.text(), response.url,
                                                         response.content_type)

        if response.content_type == 'application/json':
            await stream.get_inbound_links_and_save_file(response, await response.text(), response.url,
                                                         response.content_type)

        if response.content_type in TO_SAVE_TYPES:
            await HtmlHandler.write_binary(response)

        if response.content_type in USELESS_TYPES:
            my_logger.warning(str(response.url) + '- USELESS_TYPES')


