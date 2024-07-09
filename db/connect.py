import logging
from datetime import datetime, timedelta

from sqlalchemy import select, func, and_, delete
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from function.dublicate_check import is_it_dublicate
from .create import Estate

logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

DATABASE_URL = "postgresql+asyncpg://admin:password@localhost/estate"

# Создание асинхронного двигателя и фабрики сессий
engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


async def insert_estates_tg(estates_list):

    async with async_session() as session:
        async with session.begin():
            lst_msg_id = await get_last_msg_id(estates_list[0]['group_id'])
            count = 0
            for estate in estates_list:
                if estate['msg_id'] <= lst_msg_id:
                    continue
                if await find_same_prise_msgs(estate):
                    continue
                count += 1

                new_estate = Estate(
                    resource=estate['resource'],
                    datetime=estate['datetime'],
                    city=estate['city'],
                    district=estate.get('district', ''),
                    rooms=estate.get('rooms', -1),
                    price=estate['price'],
                    url=estate.get('url', ''),
                    group_id=estate.get('group_id', -1),
                    msg_id=estate.get('msg_id', -1),
                    language=estate.get('language', ''),
                    msg=estate['msg'],
                    msg_ru=estate.get('msg_ru', ''),
                    msg_en=estate.get('msg_en', ''),
                    msg_el=estate.get('msg_el', '')
                )
                session.add(new_estate)
            print(f'add {count} estate(s)')
        await session.commit()


async def get_last_msg_id(group_id: str) -> int:
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(func.max(Estate.msg_id)).where(Estate.group_id == group_id)
            )
            last_msg_id = result.scalar_one_or_none()
            return last_msg_id if last_msg_id is not None else 0


async def find_same_prise_msgs(estate_obj):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(Estate.msg).where(
                    and_(
                        Estate.price == estate_obj['price'],
                        Estate.city == estate_obj['city'],
                        Estate.group_id != estate_obj['group_id']
                    )
                )
            )
            msgs = [row[0] for row in result.all()]
            return await is_it_dublicate(msgs, estate_obj)


async def delete_old_msgs(days):
    async with async_session() as session:
        async with session.begin():
            threshold_date = datetime.now() - timedelta(days=days)
            stmt = delete(Estate).where(Estate.datetime < threshold_date)
            await session.execute(stmt)
            await session.commit()
