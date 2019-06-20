import pytest
from handlers import HtmlHandler
import asyncio
import os
import aiohttp
#from pprint import pprint


@pytest.fixture
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


async def worker(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text(), response.url


async def another_worker(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return response.url, response.content_type


def test_html_file_parsing():
    url = 'http://xn--90abjzldcl.xn--p1ai/'
    response = asyncio.run(worker(url))
    html_class = HtmlHandler(*response)
    test_inbound = html_class.html_inbound_links_parser()
    test_outbound = html_class.outbound

    assert len(test_outbound) == 8
    assert len(test_inbound) == 38


def test_js_file_parsing():
    url = 'http://lotoflotto.com/sites/default/files/js/js_23S4ZJ2YFIznAjgWDjd7jegTMfWRBdq-fZxZgeORSTY.js'
    response = asyncio.run(worker(url))
    js_class = HtmlHandler(*response)
    js_class.get_links_from_scripts(js_class.response_text)

    assert len(js_class.outbound) == 5
    assert len(js_class.inbound) == 0


def test_css_file_parsing():
    url = 'http://lotoflotto.com/sites/default/files/css/css_xE-rWrJf-fncB6ztZfd2huxqgxu4WO-qwma6Xer30m4.css'
    response = asyncio.run(worker(url))
    css_class = HtmlHandler(*response)
    css_class.get_links_from_css(css_class.response_text)

    assert len(css_class.outbound) == 0
    assert len(css_class.inbound) == 14


@pytest.mark.parametrize('url, inbound, outbound', [
    ('http://xn--90abjzldcl.xn--p1ai/wp-content/themes/bwstheme/css/my.css', 12, 2),
    ('http://xn--90abjzldcl.xn--p1ai/wp-content/themes/bwstheme/css/result.css', 2, 0)
])
def test_css2_file_parsing(url, inbound, outbound):
    response = asyncio.run(worker(url))
    css_class = HtmlHandler(*response)
    css_class.get_links_from_css(css_class.response_text)

    assert len(css_class.inbound) == inbound
    assert len(css_class.outbound) == outbound


def test_css3_file_parsing_dots():
    response = asyncio.run(worker('http://xn--90abjzldcl.xn--p1ai/wp-content/themes/bwstheme/slick/slick-theme.css'))
    css_class = HtmlHandler(*response)
    css_class.get_links_from_css(css_class.response_text)

    assert len(css_class.inbound) == 5


def test_css3_file_parsing_shitty_stuff():
    response = asyncio.run(worker('http://xn--90abjzldcl.xn--p1ai/wp-content/themes/bwstheme/css/powerball.css'))
    css_class = HtmlHandler(*response)
    css_class.get_links_from_css(css_class.response_text)

    assert len(css_class.inbound) == 10


def test_xml_file_parsing_cyrillic_url():
    response = asyncio.run(worker('http://xn--90abjzldcl.xn--p1ai/wp-json/oembed/1.0/embed?url=http%3A%2F%2Fxn--90abjzldcl.xn--p1ai%2F&format=xml'))
    xml_handler = HtmlHandler(*response)
    xml_handler.get_links_from_xml()

    assert len(xml_handler.inbound) == 5


def test_json_file_parsing_empty_json():
    response = asyncio.run(worker('http://xn--90abjzldcl.xn--p1ai/wp-json/wp/v2/users'))
    json_class = HtmlHandler(*response)
    json_class.get_links_from_json()
    assert len(json_class.inbound) == 3
    assert len(json_class.outbound) == 3

@pytest.mark.foo
@pytest.mark.parametrize('url', [
    'http://lottery-lucky.ru/fonts/fontawesome-webfont.woff?v=4.5.0',
    'http://lottery-lucky.ru/fonts/fontawesome-webfont.svg?v=4.5.0',
    'http://lottery-lucky.ru/cdn-cgi/images/browser-bar.png?1376755637',
    'http://xn--90abjzldcl.xn--p1ai/',
    'http://xn--90abjzldcl.xn--p1ai/wp-content/themes/bwstheme/css/powerball.css',
    'http://xn--90abjzldcl.xn--p1ai/wp-content/plugins/all-in-one-seo-pack/public/js/vendor/autotrack.js',
    'http://xn--90abjzldcl.xn--p1ai/wp-content/themes/bwstheme/img/powerball-logo.png',
    'http://xn--90abjzldcl.xn--p1ai/wp-includes/wlwmanifest.xml',
    'http://xn--90abjzldcl.xn--p1ai/feed',
    'http://xn--90abjzldcl.xn--p1ai/wp-json/',
    'http://xn--90abjzldcl.xn--p1ai/wp-json/oembed/1.0/embed?url=http%3A%2F%2Fxn--90abjzldcl.xn--p1ai%2F'
])
def test_file_write(url):
    async def request_for_file_saving(url_to_request):
        async with aiohttp.ClientSession() as session:
            async with session.get(url_to_request) as response:
                return await HtmlHandler.write_binary(response)

    path = asyncio.run(request_for_file_saving(url))
    print(path)
    assert os.path.isfile(path)


@pytest.mark.parametrize('url, inbound_count, outbound_count', [
    ('http://xn--90abjzldcl.xn--p1ai/feed', 29, 8),
    ('http://xn--90abjzldcl.xn--p1ai/wp-includes/wlwmanifest.xml', 0, 1)
])
def test_xml_parser(url, inbound_count, outbound_count):
    response = asyncio.run(worker(url))
    xml_class = HtmlHandler(*response)
    xml_class.get_links_from_xml()

    assert len(xml_class.inbound) == inbound_count
    assert len(xml_class.outbound) == outbound_count


@pytest.mark.parametrize('url, inbound_count, outbound_count', [
    ('http://xn--90abjzldcl.xn--p1ai/wp-json/', 23, 1),
    ('http://xn--90abjzldcl.xn--p1ai/wp-json/oembed/1.0/embed?url=http%3A%2F%2Fxn--90abjzldcl.xn--p1ai%2F', 3, 0)
])
def test_json_parser(url, inbound_count, outbound_count):
    response = asyncio.run(worker(url))
    json_class = HtmlHandler(*response)
    json_class.get_links_from_json()

    assert len(json_class.inbound) == inbound_count
    assert len(json_class.outbound) == outbound_count


@pytest.mark.skip
@pytest.mark.parametrize('url, file_type, path', [
    ('http://127.0.0.1:5000/', 'text/html', ['', 'index.html']),
    ('http://127.0.0.1:5000/index.html', 'text/html', ['', 'index.html']),
    ('http://127.0.0.1:5000/directory/', 'text/html', ['/directory', 'index.html']),
    ('http://127.0.0.1:5000/directory', 'text/html', ['/directory', 'index.html']),
    ('http://127.0.0.1:5000/directory/some_page.html', 'text/html', ['/directory', 'some_page.html']),
    ('http://127.0.0.1:5000/directory/some_page.php', 'text/html', ['/directory', 'some_page.php']),
    ('http://127.0.0.1:5000/directory/some_page.php?id=10', 'text/html', ['/directory', 'some_page_php%3Fid%3D10.html']),
    ('http://127.0.0.1:5000/directory/some_page?id=10', 'text/html', ['/directory', 'some_page%3Fid%3D10.html']),
    ('http://127.0.0.1:5000/directory/some_page?id=10&user=borya&count=50', 'text/html',
     ['/directory', 'some_page%3Fid%3D10%26user%3Dborya%26count%3D50.html']),
    ('http://127.0.0.1:5000/directory/some_page.php?id=10&user=borya&count=50', 'text/html',
     ['/directory', 'some_page_php%3Fid%3D10%26user%3Dborya%26count%3D50.html']),
])
def test_check_correct_path(url, file_type, path):
    response_url, response_type = asyncio.run(another_worker(url))
    directory, file_name = HtmlHandler.convert_url_to_static(response_url, response_type)

    assert [directory, file_name] == path


def test_check_correct_path_for_css_file_with_parameters():
    url = 'http://xn--90abjzldcl.xn--p1ai/wp-content/plugins/waiting/css/style.css?v=0.4.7'
    response_url, response_type = asyncio.run(another_worker(url))
    directory, file_name = HtmlHandler.convert_url_to_static(response_url, response_type)

    assert [directory, file_name] == ['/wp-content/plugins/waiting/css', 'style.css']


def test_csv_file_writing():
    file = ('old_url', 'new_url')
    HtmlHandler.write_htaccess_file(file)








