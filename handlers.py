import os

import re
import tinycss2
import time
import aiofiles
from urllib.parse import urljoin, unquote, quote
import html
from lxml import html as lhtml
from settings import start_url as domain
import json
import itertools

project_directory = '/Users/slaza/PycharmProjects/asynchronous_site_parser/'
class HtmlHandler:
    def __init__(self, response):
        self.inbound = set()
        self.outbound = set()
        self.response_text = response
        self.parsed_response = lhtml.fromstring(self.response_text.encode('utf8'))

    def html_inbound_links_parser(self) -> set:
        scripts = self.get_scripts_from_html()
        self.get_links_from_scripts(scripts)

        styles = self.get_styles_from_html()
        self.get_links_from_css(styles)

        self.get_links_from_img()

        self.get_links_from_a_and_link()

        self.normalize_inbound_links()

        return self.inbound

    def get_scripts_from_html(self) -> str:
        scripts = self.parsed_response.xpath('//script/text()')
        return ''.join([script.replace('\\', '') for script in scripts])

    def get_styles_from_html(self) -> str:
        styles = self.parsed_response.xpath('//style/text()')
        return ''.join([style for style in styles])

    def get_links_from_scripts(self, script_text: str):
        try:
            pattern = re.compile(r'[\'|\"](((http(s)*:)|(//))([\w\d\.\-\&\?\/\=])+)[\'|\"]')
            parsed_links = [str(groups[0]) for groups in re.findall(pattern, script_text)]
            self.separate_links_by_type(parsed_links)
            self.normalize_inbound_links()
            return None
        except Exception as e:
            print('get_scripts', type(e))

    def get_links_from_css(self, styles: str):
        parsed_links = []
        for item in tinycss2.parse_stylesheet(styles):
            if item.type in ['qualified-rule', 'at-rule']:
                for css_item in item.prelude + item.content:
                    if css_item.type == 'url':
                        parsed_links.append(css_item.value)
        self.separate_links_by_type(parsed_links)
        self.normalize_inbound_links()
        return None

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

    @staticmethod
    def parse_urls_by_mask(text: str) -> list:
        pattern = re.compile(r'[\'|\"](((http(s)*:)|(//))([\w\d\.\-\&\?\/\=])+)[\'|\"]')
        return [groups[0] for groups in re.findall(pattern, text)]

    def separate_links_by_type(self, links: (list, set)):
        for link in links:
            self.check_link_type(link)
        return None

    def check_link_type(self, link: str):
        if link.startswith(('http', '//')) and not link.startswith(domain):
            self.outbound.add(link)
        else:
            self.inbound.add(link)
        return None

    def normalize_inbound_links(self):
        temp_set = []
        for link in self.inbound:
            if link.startswith(domain):
                temp_set.append(link)
            elif link.startswith('/'):
                temp_set.append(domain[:-1] + link)
            else:
                temp_set.append(domain + link)

        self.inbound = set([item for item in temp_set if '#' not in item])
        return None

    @staticmethod
    async def write_binary(response, file_type=''):
        # sub_directory = []
        # name = []
        # path = response.url.raw_path
        # types = {'text/html': ('index.html', '.html'),
        #          'application/json': ('index.json', '.json'),
        #          'text/xml': ('index.xml', '.xml')}
        # if response.url.query_string:
        #     directory_appendix = response.url.query_string.split('&')
        #     for item in directory_appendix:
        #         sub, sub_name = item.split('=')
        #         sub_directory.append(sub)
        #         name.append(quote(sub_name, safe=''))
        #     path = path + '/' + '/'.join(sub_directory) + '/' + '='.join(name)
        # else:
        #     if '.' not in path and not path.endswith('/'):
        #         path = path + '/'
        #     path = response.url.raw_host + path
        #     # removing filename
        #     directory = '/'.join(path.split('/')[:-1])
        #     if file_type and '.' not in response.url.name:
        #         path = path + types[file_type]
        #         print('changed path from ', response.url.raw_host + path, ' to ', path)
        directory = "FAKE VARIABLE"
        path = directory
        path = response_url.raw_host + path
        if not os.path.exists(project_directory + directory):
            os.makedirs(directory)
        try:
            async with aiofiles.open(path, mode='wb') as f:
                await f.write(await response.read())
                await f.close()
        except OSError:
            print('OSError')
        return path

    @staticmethod
    def convert_url_to_static(response_url, file_type: str) -> [str, str]:
        sub_directory = []
        name = []
        path = response_url.raw_path
        types = {'text/html': ('index.html', '.html'),
                 'application/json': ('index.json', '.json'),
                 'text/xml': ('index.xml', '.xml')}
        # checking if url has parameters,
        if response_url.query_string:
            file_name = response_url.raw_name.replace('.', '_') + '?' + response_url.query_string + types[file_type][1]
        else:
            # if url has no slash ending and has no extension
            if not path.endswith('/') and '.' not in path:
                path = path + '/'
            # handling file_name
            if file_type and '.' not in response_url.name:
                file_name = types[file_type][0]
                print('changed path from ', response_url.raw_host + path, ' to ', path + file_name)
            else:
                file_name = path.split('/')[-1]
            # handling directory
        directory = '/'.join(path.split('/')[:-1])
        return directory, file_name



    def get_links_from_xml(self):
        parsed_links = set()
        patterns = [r'=[\'\"]?((http|//)[^\'\" >]+)', r'>((http)[^ <]+)']
        match = itertools.chain.from_iterable([re.findall(pattern, self.response_text) for pattern in patterns])
        [parsed_links.add(x[0]) for x in match]
        self.separate_links_by_type(parsed_links)
        self.normalize_inbound_links()
        return None

    def get_links_from_json(self):
        for key, item in json.loads(self.response_text).items():
            self.child_parser(item)
        return None

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


async def worker(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            await HtmlHandler.write_binary(response, 'index.html')


if __name__ == '__main__':
    import asyncio
    import aiohttp
    asyncio.run(worker('http://lotoflotto.com/'))
