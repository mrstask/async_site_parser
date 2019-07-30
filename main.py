import aiohttp
import asyncio
from pprint import pprint
from handlers import HtmlHandler
import time

from settings import auth_login, auth_password, start_url, TO_SAVE_TYPES, USELESS_TYPES

qu = asyncio.Queue()
parsed_urls = set()
queued_urls = set()
bad_urls = set()

auth = aiohttp.BasicAuth(login=auth_login, password=auth_password)
type_methods = {'text/html': 'html_inbound_links_parser',  # without parameters
                'text/css': 'get_links_from_css',
                'text/javascript': 'get_links_from_scripts',
                'text/xml': 'get_links_from_xml',  # without parameters
                'application/json': 'get_links_from_json' # without parameters
                }


async def add_links_and_save_file(obj, response):
    for url in obj.inbound:
        if url not in parsed_urls and url not in queued_urls:
            queued_urls.add(url)
            await qu.put(url)
    await HtmlHandler.write_binary(response)


async def get_inbound_links_and_save_file(response, response_text, response_url, content_type):
    type_object = HtmlHandler(response_text, response_url)

    if content_type in ['text/css', 'text/javascript']:
        getattr(type_object, type_methods[content_type])(type_object.response_text)
    else:
        getattr(type_object, type_methods[content_type])()
    print('links')
    pprint(type_object.inbound.difference(queued_urls))
    await add_links_and_save_file(type_object, response)


async def content_router(response):
    if response.content_type == 'text/html':
        await get_inbound_links_and_save_file(response, await response.text(), response.url, response.content_type)

    if response.content_type == 'text/css':
        await get_inbound_links_and_save_file(response, await response.text(), response.url, response.content_type)

    if response.content_type == 'text/javascript':
        await get_inbound_links_and_save_file(response, await response.text(), response.url, response.content_type)

    if response.content_type == 'text/xml':
        await get_inbound_links_and_save_file(response, await response.text(), response.url, response.content_type)

    if response.content_type == 'application/json':
        await get_inbound_links_and_save_file(response, await response.text(), response.url, response.content_type)

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
            try:
                async with session.get(url, allow_redirects=False) as response:
                    if response.status == 200:
                        print(response.url, response.content_type)
                        parsed_urls.add(url)
                        queued_urls.add(url)
                        await content_router(response)
                    if response.status in (404, 500):
                        print('bad_url ', response.url, ' ', response.status)
                        bad_urls.add(url)
            except Exception as e:
                print('session get exception for url', url, type(e), e)


if __name__ == '__main__':
    start_time = time.time()
    asyncio.run(main())
    print('parsed urls', len(parsed_urls))
    pprint(parsed_urls)
    print('*'*100)
    print('bad urls')
    pprint(bad_urls)
    print("--- %s seconds ---" % (time.time() - start_time))
