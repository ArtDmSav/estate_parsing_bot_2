import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from .create import UnprocessedMessage

logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

DATABASE_URL = "postgresql+asyncpg://admin:password@localhost/estate"

# Создание асинхронного двигателя и фабрики сессий
engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


# Functions for collect date for analysis
# ____________________________________________________________


async def insert_unprocessed_message(case, msg='', msg_2='', url=''):
    # async with async_session() as session:
    #     async with session.begin():
    #         # Проверка на существование записи с заданными условиями
    #         result = await session.execute(
    #             select(UnprocessedMessage).where(UnprocessedMessage.url != url))
    #
    #         existing_message = result.first()
    #         print(f'existing_message = {existing_message}')
    #
    #         # Добавление новой записи, если такая запись не существует
    #         # if existing_message is None:
    #         new_message = UnprocessedMessage(
    #             case=case,
    #             msg=msg,
    #             msg_2=msg_2,
    #             url=url
    #         )
    #         session.add(new_message)
    #         await session.commit()
    async with async_session() as session:
        async with session.begin():
            new_message = UnprocessedMessage(
                case=case,
                msg=msg,
                msg_2=msg_2,
                url=url
            )
            session.add(new_message)

            try:
                await session.commit()
            except IntegrityError:
                await session.rollback()
                print(f"Запись с такими данными уже существует: url={url}")
