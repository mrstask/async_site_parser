import os
import re
import tinycss2
import aiofiles
import json
import itertools
import html
from urllib.parse import quote, urljoin
from lxml import html as lhtml
from settings import start_url as domain, project_directory
from pprint import pprint


class HtmlHandler:
    def __init__(self, response, response_url):
        self.file_for_htaccess = []
        self.inbound = set()
        self.outbound = set()
        self.response_text = response
        self.response_url = response_url
        self.parsed_response = lhtml.fromstring(self.response_text.encode('utf8'))

    def html_inbound_links_parser(self) -> set:
        scripts = self.get_scripts_from_html()
        self.get_links_from_scripts(scripts)

        styles = self.get_styles_from_html()
        self.get_links_from_css(styles)

        self.get_links_from_img()

        self.get_links_from_a_and_link()
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
            pprint(parsed_links)
            self.separate_links_by_type(parsed_links)
            self.normalize_inbound_links()
            return None
        except Exception as e:
            print('get_scripts', type(e))

    def get_links_from_css(self, styles: str):
        parsed_links = []
        for item in tinycss2.parse_stylesheet(styles):
            if item.type in ['qualified-rule', 'at-rule']:
                css_items = [] if not item.prelude else item.prelude + [] if not item.content else item.content
                for css_item in css_items:
                    if css_item.type == 'url' and '<' not in css_item.value:
                        parsed_links.append(css_item.value)
        pprint(parsed_links)
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
        temp_set = set()
        for link in self.inbound:
            if '#' in link:
                if '?#' in link:
                    link = ''.join(link.split('?#')[:-1])
                else:
                    link = ''.join(link.split('#')[:-1])
            if link.startswith(domain):
                temp_set.add(link)
            elif link.startswith('.'):
                temp_set.add(urljoin(domain + self.response_url.raw_path,  link))
            elif not link.startswith('/'):
                temp_set.add(domain + '/' + link)
            else:
                temp_set.add(domain + link)
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

    def convert_url_to_static(self, file_type: str) -> [str, str]:
        path = self.response_url.raw_path
        types = {'text/html': ('index.html', '.html'),
                 'application/json': ('index.json', '.json'),
                 'text/xml': ('index.xml', '.xml'),
                 'application/rss+xml': ('index.xml', '.xml'),
                 'text/css': ('index.css', '.css'),
                 }
        # checking if url has parameters,
        if self.response_url.query_string and file_type != 'text/css':
            file_name = self.response_url.raw_name.replace('.', '_') + '?' + self.response_url.query_string + \
                        types[file_type][1]
            file_name = quote(file_name, safe='')
            print('changed path from ', self.response_url, ' to ', self.response_url.scheme +
                  '://' + self.response_url.raw_host + path + file_name)
            self.file_for_htaccess.append(self.response_url.scheme + '://' + self.response_url.raw_host + path +
                                          file_name)
        else:
            # if url has no slash ending and has no extension
            if not path.endswith('/') and '.' not in path:
                path = path + '/'
            # handling file_name
            if file_type and '.' not in self.response_url.name:
                file_name = types[file_type][0]
                print('changed path from ', self.response_url, ' to ', self.response_url.scheme +
                      '://' + self.response_url.raw_host + path + file_name)
                self.file_for_htaccess.append(self.response_url.scheme + '://' + self.response_url.raw_host + path +
                                              file_name)
            else:
                file_name = path.split('/')[-1]
            # handling directory
        directory = '/'.join(path.split('/')[:-1])
        return directory, file_name

    def get_links_from_xml(self):
        parsed_links = set()
        patterns = [r'=[\'\"]?((http|//)[^\'\" >]+)', r'>((http)[^ <]+)']
        match = itertools.chain.from_iterable([re.findall(pattern, html.unescape(self.response_text)) for pattern in patterns])
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


