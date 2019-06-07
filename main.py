import aiohttp
import asyncio
from pprint import pprint
from handlers import HtmlHandler

from settings import auth_login, auth_password, start_url, TO_SAVE_TYPES, USELESS_TYPES

qu = asyncio.Queue()
parsed_urls = set()
queued_urls = set()
bad_urls = set()

auth = aiohttp.BasicAuth(login=auth_login, password=auth_password)


async def add_links_and_save_file(obj, response):
    for url in obj.inbound:
        if url not in parsed_urls and url not in queued_urls:
            queued_urls.add(url)
            await qu.put(url)
    await HtmlHandler.write_binary(response)


async def content_router(response):
    if response.content_type == 'text/html':
        html_obj = HtmlHandler(await response.text(), response.url)
        html_obj.html_inbound_links_parser()
        await add_links_and_save_file(html_obj, response)
        print('parsed_urls', len(parsed_urls))
        print('queue size', qu.qsize())

    if response.content_type == 'text/css':
        css_class = HtmlHandler(await response.text(), response.url)
        css_class.get_links_from_css(css_class.response_text)
        await add_links_and_save_file(css_class, response)

    if response.content_type == 'text/javascript':
        js_class = HtmlHandler(await response.text(), response.url)
        js_class.get_links_from_scripts(js_class.response_text)
        await add_links_and_save_file(js_class, response)

    if response.content_type == 'text/xml':
        xml_class = HtmlHandler(await response.text(), response.url)
        xml_class.get_links_from_xml()
        await add_links_and_save_file(xml_class, response)

    if response.content_type == 'application/json':
        json_class = HtmlHandler(await response.text(), response.url)
        json_class.get_links_from_json()
        await add_links_and_save_file(json_class, response)

    if response.content_type in TO_SAVE_TYPES:
        await HtmlHandler.write_binary(response)

    if response.content_type in USELESS_TYPES:
        print('useless_types')


async def main():
    await qu.put(start_url)
    tasks = []
    for _ in range(1):
        task = asyncio.Task(worker(qu))
        tasks.append(task)

    await asyncio.gather(*tasks)


async def worker(queue):
    async with aiohttp.ClientSession(auth=auth) as session:
        while queue.qsize() > 0:
            url = await queue.get()  # из очереди
            print(url)
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        parsed_urls.add(url)
                        await content_router(response)
                    if response.status in (404, 500):
                        print('bad_url ', response.url, ' ', response.status)
                        bad_urls.add(url)
            except Exception as e:
                print(type(e), e)


if __name__ =='__main__':
    asyncio.run(main())
    print(len(parsed_urls))
    pprint(parsed_urls)
    print('*'*100)
    pprint(bad_urls)
