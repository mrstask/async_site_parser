import pytest
from handlers import HtmlHandler
import asyncio
import os
import aiohttp
from pprint import pprint

HTML_INBOUND = {'http://xn--90abjzldcl.xn--p1ai/wp-content/plugins/wp-pagenavi/pagenavi-css.css?ver=2.70',
                'http://xn--90abjzldcl.xn--p1ai/wp-content/themes/bwstheme/img/powerball-logo.png',
                'http://xn--90abjzldcl.xn--p1ai/wp-admin/admin-ajax.php',
                'http://xn--90abjzldcl.xn--p1ai/comments/feed',
                'http://xn--90abjzldcl.xn--p1ai/wp-includes/css/dist/block-library/style.min.css?ver=5.0.3',
                'http://xn--90abjzldcl.xn--p1ai/',
                'http://xn--90abjzldcl.xn--p1ai',
                'http://xn--90abjzldcl.xn--p1ai/oficialnyj-sajt',
                'http://xn--90abjzldcl.xn--p1ai/wp-json/',
                'http://xn--90abjzldcl.xn--p1ai/konfidencialnost',
                'http://xn--90abjzldcl.xn--p1ai/wp-json/oembed/1.0/embed?url=http%3A%2F%2Fxn--90abjzldcl.xn--p1ai%2F',
                'http://xn--90abjzldcl.xn--p1ai/wp-content/themes/bwstheme/css/my.css',
                'http://xn--90abjzldcl.xn--p1ai/igrat-v-powerball',
                'http://xn--90abjzldcl.xn--p1ai/wp-content/themes/bwstheme/css/powerball.css',
                'http://xn--90abjzldcl.xn--p1ai/xmlrpc.php?rsd',
                'http://xn--90abjzldcl.xn--p1ai/wp-content/plugins/waiting/',
                'http://xn--90abjzldcl.xn--p1ai/cookie',
                'http://xn--90abjzldcl.xn--p1ai/feed',
                'http://xn--90abjzldcl.xn--p1ai/rezultaty-powerball',
                'http://xn--90abjzldcl.xn--p1ai/wp-content/themes/bwstheme/css/style.css',
                'http://xn--90abjzldcl.xn--p1ai/wp-content/plugins/waiting/js/jquery.countdown.js',
                'http://xn--90abjzldcl.xn--p1ai/wp-content/uploads/2019/01/02.jpg',
                'http://xn--90abjzldcl.xn--p1ai/wp-content/themes/bwstheme/slick/slick-theme.css',
                'http://xn--90abjzldcl.xn--p1ai/karta-sajta',
                'http://xn--90abjzldcl.xn--p1ai/wp-content/plugins/waiting/js/pbc.js?v=0.4.7',
                'http://xn--90abjzldcl.xn--p1ai/wp-content/themes/bwstheme/css/result.css',
                'http://xn--90abjzldcl.xn--p1ai/wp-content/plugins/contact-form-7/includes/css/styles.css?ver=5.1.1',
                'http://xn--90abjzldcl.xn--p1ai/baza-znanij',
                'http://xn--90abjzldcl.xn--p1ai/wp-json/contact-form-7/v1',
                'http://xn--90abjzldcl.xn--p1ai/otzyvy',
                'http://xn--90abjzldcl.xn--p1ai/wp-content/themes/bwstheme/img/banner2.jpg',
                'http://xn--90abjzldcl.xn--p1ai/wp-includes/js/wp-emoji-release.min.js?ver=5.0.3',
                'http://xn--90abjzldcl.xn--p1ai/sindikat-powerball',
                'http://xn--90abjzldcl.xn--p1ai/wp-json/oembed/1.0/embed?url=http%3A%2F%2Fxn--90abjzldcl.xn--p1ai%2F&format=xml',
                'http://xn--90abjzldcl.xn--p1ai/wp-content/plugins/waiting/css/style.css?v=0.4.7',
                'http://xn--90abjzldcl.xn--p1ai/wp-includes/wlwmanifest.xml',
                'http://xn--90abjzldcl.xn--p1ai/wp-content/themes/bwstheme/slick/slick.css',
                'http://xn--90abjzldcl.xn--p1ai/xmlrpc.php'}
HTML_OUTBOUND = {'https://s.w.org/images/core/emoji/11/svg/',
                 'http://gmpg.org/xfn/11',
                 'https://s.w.org/images/core/emoji/11/72x72/',
                 'https://app.partnerlottery.com/aff.php?id=574_1_3_6',
                 '//s.w.org',
                 'https://fonts.googleapis.com/css?family=Open+Sans',
                 'https://stackpath.bootstrapcdn.com/bootstrap/4.2.1/css/bootstrap.min.css',
                 'https://use.fontawesome.com/releases/v5.6.3/css/all.css'}

js_outbound = {'http://', 'http://www.youtube.com/embed/',
               'https://ssl.',
               'https://www.gstatic.com/cv/js/sender/v1/cast_sender.js',
               'http://p.jwpcdn.com/'}

css_inbound = {'http://xn--90abjzldcl.xn--p1ai/misc/tree-bottom.png', 'http://xn--90abjzldcl.xn--p1ai/misc/menu-leaf.png', 'http://xn--90abjzldcl.xn--p1ai/misc/menu-collapsed.png', 'http://xn--90abjzldcl.xn--p1ai/misc/message-24-error.png', 'http://xn--90abjzldcl.xn--p1ai/misc/grippie.png', 'http://xn--90abjzldcl.xn--p1ai/misc/message-24-ok.png', 'http://xn--90abjzldcl.xn--p1ai/misc/throbber-inactive.png', 'http://xn--90abjzldcl.xn--p1ai/misc/throbber-active.gif', 'http://xn--90abjzldcl.xn--p1ai/misc/tree.png', 'http://xn--90abjzldcl.xn--p1ai/misc/message-24-warning.png', 'http://xn--90abjzldcl.xn--p1ai/misc/draggable.png', 'http://xn--90abjzldcl.xn--p1ai/misc/help.png', 'http://xn--90abjzldcl.xn--p1ai/misc/progress.gif', 'http://xn--90abjzldcl.xn--p1ai/misc/menu-expanded.png'}
XML_INBOUND = [{'http://xn--90abjzldcl.xn--p1ai/loterejnye-pobedy-kakova-prichina-slepoj-very-uchastnikov-v-chudo',
                'http://xn--90abjzldcl.xn--p1ai/blog/feed',
                'http://xn--90abjzldcl.xn--p1ai/wp-content/uploads/2019/05/03.21.20-_-3PM-_-Jonathans-Place.jpg',
                'http://xn--90abjzldcl.xn--p1ai/voditel-gruzovika-iz-bruklina-uvolilsya-s-raboty-posle-vyigrysha-dzhekpota-v-298-mln-powerball',
                'http://xn--90abjzldcl.xn--p1ai/wp-content/uploads/2019/04/03.21.20-_-3PM-_-Jonathans-Place-3.jpg',
                'http://xn--90abjzldcl.xn--p1ai/v-den-materi-pobeditel-wisconsin-powerball-udivil-podarochnoj-kartoj-v-200-zhenshhinu-vybrannuyu-sluchajno/feed',
                'http://xn--90abjzldcl.xn--p1ai/?p=230',
                'http://xn--90abjzldcl.xn--p1ai/?p=262',
                'http://xn--90abjzldcl.xn--p1ai/zhenshhina-vyigryvaet-krupnejshij-v-istorii-avstralii-dzhekpot-powerball',
                'http://xn--90abjzldcl.xn--p1ai/?p=286',
                'http://xn--90abjzldcl.xn--p1ai/pobeditelnica-iz-floridy-vyigravshaya-samyj-krupnyj-dzhekpot-v-ssha-podala-v-sud-isk-na-svoego-syna-rastrativshego-ee-vyigrysh',
                'http://xn--90abjzldcl.xn--p1ai/wp-content/uploads/2019/04/03.21.20-_-3PM-_-Jonathans-Place-2.jpg',
                'http://xn--90abjzldcl.xn--p1ai/zhenshhina-vyigryvaet-krupnejshij-v-istorii-avstralii-dzhekpot-powerball/feed',
                'http://xn--90abjzldcl.xn--p1ai/feed',
                'http://xn--90abjzldcl.xn--p1ai/v-den-materi-pobeditel-wisconsin-powerball-udivil-podarochnoj-kartoj-v-200-zhenshhinu-vybrannuyu-sluchajno',
                'http://xn--90abjzldcl.xn--p1ai/?p=236', 'http://xn--90abjzldcl.xn--p1ai/?p=171',
                'http://xn--90abjzldcl.xn--p1ai/wp-content/uploads/2019/02/03.21.20-_-3PM-_-Jonathans-Place-8.jpg',
                'http://xn--90abjzldcl.xn--p1ai/?p=257',
                'http://xn--90abjzldcl.xn--p1ai',
                'http://xn--90abjzldcl.xn--p1ai/pobeditelnica-iz-floridy-vyigravshaya-samyj-krupnyj-dzhekpot-v-ssha-podala-v-sud-isk-na-svoego-syna-rastrativshego-ee-vyigrysh/feed',
                'http://xn--90abjzldcl.xn--p1ai/chlen-palaty-predstavitelej-stavshij-pobeditelem-v-powerball-vystupaet-protiv-anonimnosti-dlya-prizerov-loterei', 'http://xn--90abjzldcl.xn--p1ai/wp-content/uploads/2019/01/03.21.20-_-3PM-_-Jonathans-Place-4.jpg', 'http://xn--90abjzldcl.xn--p1ai/blog',
                'http://xn--90abjzldcl.xn--p1ai/wp-content/uploads/2019/02/03.21.20-_-3PM-_-Jonathans-Place-7.jpg',
                'http://xn--90abjzldcl.xn--p1ai/wp-content/uploads/2019/01/03.21.20-_-3PM-_-Jonathans-Place-5.jpg',
                'http://xn--90abjzldcl.xn--p1ai/chlen-palaty-predstavitelej-stavshij-pobeditelem-v-powerball-vystupaet-protiv-anonimnosti-dlya-prizerov-loterei/feed',
                'http://xn--90abjzldcl.xn--p1ai/voditel-gruzovika-iz-bruklina-uvolilsya-s-raboty-posle-vyigrysha-dzhekpota-v-298-mln-powerball/feed',
                'http://xn--90abjzldcl.xn--p1ai/loterejnye-pobedy-kakova-prichina-slepoj-very-uchastnikov-v-chudo/feed'},
               set()]

XML_OUTBOUND = [{'http://purl.org/rss/1.0/modules/content/',
                 'http://clients.bestwebstudio.ru/megamillions/?p=121',
                 'http://purl.org/rss/1.0/modules/syndication/',
                 'http://purl.org/dc/elements/1.1/',
                 'http://www.w3.org/2005/Atom',
                 'http://wellformedweb.org/CommentAPI/',
                 'https://wordpress.org/?v=5.0.3',
                 'http://purl.org/rss/1.0/modules/slash/'}, {'http://schemas.microsoft.com/wlw/manifest/weblog'}]

JSON_INBOUND = [{'http://xn--90abjzldcl.xn--p1ai/wp-json/wp/v2/types',
                 'http://xn--90abjzldcl.xn--p1ai/wp-json/wp/v2/media',
                 'http://xn--90abjzldcl.xn--p1ai/wp-json/wp/v2',
                 'http://xn--90abjzldcl.xn--p1ai/wp-json/wp/v2/blocks',
                 'http://xn--90abjzldcl.xn--p1ai',
                 'http://xn--90abjzldcl.xn--p1ai/wp-json/wp/v2/search',
                 'http://xn--90abjzldcl.xn--p1ai/wp-json/wp/v2/tags',
                 'http://xn--90abjzldcl.xn--p1ai/wp-json/wp/v2/statuses',
                 'http://xn--90abjzldcl.xn--p1ai/wp-json/contact-form-7/v1',
                 'http://xn--90abjzldcl.xn--p1ai/wp-json/wp/v2/taxonomies',
                 'http://xn--90abjzldcl.xn--p1ai/wp-json/oembed/1.0',
                 'http://xn--90abjzldcl.xn--p1ai/wp-json/wp/v2/users/me',
                 'http://xn--90abjzldcl.xn--p1ai/wp-json/wp/v2/themes',
                 'http://xn--90abjzldcl.xn--p1ai/wp-json/wp/v2/comments',
                 'http://xn--90abjzldcl.xn--p1ai/wp-json/oembed/1.0/embed',
                 'http://xn--90abjzldcl.xn--p1ai/wp-json/contact-form-7/v1/contact-forms',
                 'http://xn--90abjzldcl.xn--p1ai/wp-json/oembed/1.0/proxy',
                 'http://xn--90abjzldcl.xn--p1ai/wp-json/wp/v2/pages',
                 'http://xn--90abjzldcl.xn--p1ai/wp-json/wp/v2/posts',
                 'http://xn--90abjzldcl.xn--p1ai/wp-json/',
                 'http://xn--90abjzldcl.xn--p1ai/wp-json/wp/v2/categories',
                 'http://xn--90abjzldcl.xn--p1ai/wp-json/wp/v2/users',
                 'http://xn--90abjzldcl.xn--p1ai/wp-json/wp/v2/settings'},
                {'http://xn--90abjzldcl.xn--p1ai/author/webest',
                 'http://xn--90abjzldcl.xn--p1ai/wp-content/uploads/2019/02/Дизайн-без-названия-3.jpg',
                 'http://xn--90abjzldcl.xn--p1ai'}]
JSON_OUTBOUND = [{'http://v2.wp-api.org/'}, set()]

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

    assert test_outbound == HTML_OUTBOUND
    assert test_inbound == HTML_INBOUND


def test_js_file_parsing():
    url = 'http://lotoflotto.com/sites/default/files/js/js_23S4ZJ2YFIznAjgWDjd7jegTMfWRBdq-fZxZgeORSTY.js'
    response = asyncio.run(worker(url))
    js_class = HtmlHandler(*response)
    js_class.get_links_from_scripts(js_class.response_text)

    assert js_class.outbound == js_outbound
    assert js_class.inbound == set()


def test_css_file_parsing():
    url = 'http://lotoflotto.com/sites/default/files/css/css_xE-rWrJf-fncB6ztZfd2huxqgxu4WO-qwma6Xer30m4.css'
    response = asyncio.run(worker(url))
    css_class = HtmlHandler(*response)
    css_class.get_links_from_css(css_class.response_text)

    assert css_class.outbound == set()
    assert css_class.inbound == css_inbound


@pytest.mark.parametrize('url, inbound, outbound', [
    ('http://xn--90abjzldcl.xn--p1ai/wp-content/themes/bwstheme/css/my.css', 12, 2)
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

@pytest.mark.foo
def test_css3_file_parsing_shitty_stuff():
    response = asyncio.run(worker('http://xn--90abjzldcl.xn--p1ai/wp-content/themes/bwstheme/css/powerball.css'))
    css_class = HtmlHandler(*response)
    css_class.get_links_from_css(css_class.response_text)

    assert len(css_class.inbound) == 4



@pytest.mark.parametrize('url', [
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
    assert os.path.isfile(path)


@pytest.mark.parametrize('url, number', [
    ('http://xn--90abjzldcl.xn--p1ai/feed', 0),
    ('http://xn--90abjzldcl.xn--p1ai/wp-includes/wlwmanifest.xml', 1)
])
def test_xml_parser(url, number):
    response = asyncio.run(worker(url))
    xml_class = HtmlHandler(*response)
    xml_class.get_links_from_xml()

    assert xml_class.inbound == XML_INBOUND[number]
    assert xml_class.outbound == XML_OUTBOUND[number]


@pytest.mark.parametrize('url, number', [
    ('http://xn--90abjzldcl.xn--p1ai/wp-json/', 0),
    ('http://xn--90abjzldcl.xn--p1ai/wp-json/oembed/1.0/embed?url=http%3A%2F%2Fxn--90abjzldcl.xn--p1ai%2F', 1)
])
def test_json_parser(url, number):
    response = asyncio.run(worker(url))
    json_class = HtmlHandler(*response)
    json_class.get_links_from_json()

    assert json_class.inbound == JSON_INBOUND[number]
    assert json_class.outbound == JSON_OUTBOUND[number]


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









