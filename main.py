import aiohttp
import asyncio
import time

from argparsing import setup_parsing
from logger import setup_logger, my_logger
from handlers import StreamHelpers

# from settings import auth_login, auth_password
# auth = aiohttp.BasicAuth(login=auth_login, password=auth_password) # if need to add auth uncomment this


async def main(start_domain):
    await stream.qu.put(start_domain)
    tasks = []
    for _ in range(10):
        task = asyncio.Task(worker(stream.qu))
        tasks.append(task)
    await asyncio.gather(*tasks)


async def worker(queue):
    async with aiohttp.ClientSession() as session:  # if want auth aiohttp.ClientSession(auth=auth)
        while queue.qsize() > 0:
            url = await queue.get()
            try:
                async with session.get(url, allow_redirects=True) as response:
                    if response.status == 200:
                        my_logger.debug(str(response.url) + ' ' + str(response.content_type))
                        stream.parsed_urls.add(url)
                        stream.queued_urls.add(url)
                        await StreamHelpers.content_router(response, stream)
                    if response.status in (404, 500):
                        # print('bad_url ', response.url, ' ', response.status)
                        my_logger.error(str(response.url) + ' ' + str(response.status))
                        stream.bad_urls.add(url)
            except Exception as e:
                my_logger.error('session get exception for url' + str(url) + str(type(e)) + str(e))


if __name__ == '__main__':
    start = time.time()
    site_name, start_url = setup_parsing()
    setup_logger(site_name)
    stream = StreamHelpers()
    asyncio.run(main(start_url))
    my_logger.debug('parsed urls ' + str(len(stream.parsed_urls)) + str(stream.parsed_urls))
    my_logger.debug('bad urls ' + str(stream.bad_urls))
    finish = time.time()
    print(finish - start)

