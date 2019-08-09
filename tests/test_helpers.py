import pytest
from argparsing import get_start_url_and_name


@pytest.mark.parametrize('site_domain, expected_url', [
    ('http://stuff.com', 'http://stuff.com'),
    ('http://stuff.com/', 'http://stuff.com'),
    ('https://stuff.com', 'https://stuff.com'),
    ('https://stuff.com/', 'https://stuff.com'),
    ('stuff.com/', 'http://stuff.com'),
    ('stuff.com', 'http://stuff.com')
])
def test_arguments_parsing(site_domain, expected_url):
    site_name, url = get_start_url_and_name(site_domain)
    assert [site_name, url] == ['stuff.com', expected_url]
