import asyncio

from sqlalchemy_aio import ASYNCIO_STRATEGY

from sqlalchemy import (
    Column, Integer, MetaData, Table, Text, create_engine, select)
from sqlalchemy.schema import CreateTable, DropTable


async def main():
    async def setup_database():
        engine = create_engine(
            # In-memory sqlite database cannot be accessed from different
            # threads, use file.
            'sqlite:///test.db', strategy=ASYNCIO_STRATEGY
        )

        metadata = MetaData()
        users = Table(
            'users', metadata,
            Column('id', Integer, primary_key=True),
            Column('name', Text),
        )

        # Create the table
        await engine.execute(CreateTable(users))
        return await engine.connect(), users

    conn, users = await setup_database()
    # Insert some users
    await conn.execute(users.insert().values(name='Jeremy Goodwin'))
    await conn.execute(users.insert().values(name='Natalie Hurley'))
    await conn.execute(users.insert().values(name='Dan Rydell'))
    await conn.execute(users.insert().values(name='Casey McCall'))
    await conn.execute(users.insert().values(name='Dana Whitaker'))

    result = await conn.execute(users.select(users.c.name.startswith('D')))
    d_users = await result.fetchall()

    await conn.close()

    # Print out the users
    for user in d_users:
        print('Username: %s' % user[users.c.name])


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
