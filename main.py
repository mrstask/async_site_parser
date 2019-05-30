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


async def content_router(response):
    if response.content_type == 'text/html':
        response_text = await response.text()
        html_class = HtmlHandler(response_text)
        for url in html_class.html_inbound_links_parser():
            if url not in parsed_urls and url not in queued_urls:
                queued_urls.add(url)
                await qu.put(url)
        await HtmlHandler.write_binary(response, response.content_type)
        print('parsed_urls', len(parsed_urls))
        print('queue size', qu.qsize())

    if response.content_type in TO_SAVE_TYPES:
        await HtmlHandler.write_binary(response, content_type)

    if response.content_type == 'text/css':
        css_class = HtmlHandler(await response.text())
        for url in css_class.get_links_from_css(css_class.response_text):
            if url not in parsed_urls and url not in queued_urls:
                queued_urls.add(url)
                await qu.put(url)
        await HtmlHandler.write_binary(response, content_type)

    if response.content_type == 'text/javascript':
        js_class = HtmlHandler(await response.text())
        for url in js_class.get_links_from_scripts(js_class.response_text):
            if url not in parsed_urls and url not in queued_urls:
                queued_urls.add(url)
                await qu.put(url)
        await js_class.write_binary(response, content_type)
    if response.content_type == 'text/xml':
        print('xml')
        # todo process xml
        pass
    if response.content_type == 'application/json':
        # todo process json
        print('json')
        pass
    if response.content_type in USELESS_TYPES:
        print('useless_types')


async def worker(queue):
    async with aiohttp.ClientSession(auth=auth) as session:
        while queue.qsize() > 0:
            url = await queue.get()  # из очереди
            print(url)
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        parsed_urls.add(url)
                        await content_router(response, response.content_type)
                    if response.status in (404, 500):
                        print('bad_url ', response.url, ' ', response.status)
                        bad_urls.add(url)
            except Exception as e:
                print(type(e), e)


async def main():
    await qu.put(start_url)
    tasks = []
    for _ in range(20):
        task = asyncio.Task(worker(qu))
        tasks.append(task)

    await asyncio.gather(*tasks)


if __name__ =='__main__':
    asyncio.run(main())
    print(len(parsed_urls))
    pprint(parsed_urls)
    print('*'*100)
    pprint(bad_urls)
