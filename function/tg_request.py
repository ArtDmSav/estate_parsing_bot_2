import asyncio

from telethon import TelegramClient, errors

from config.data import USERNAME, API_ID, API_HASH


async def estates_telegram_list(chat_id: str, start_msg_id: int) -> list:
    global client
    try:
        # Создание клиента
        client = TelegramClient(USERNAME, API_ID, API_HASH, system_version="4.16.30-vxCUSTOM")
        await client.start()

        # Инициализация переменной для хранения всех сообщений
        all_messages = []

        # Итерация по сообщениям с учетом лимитов
        async for message in client.iter_messages(f't.me/{chat_id}', limit=100):
            all_messages.append(message)
        print(f'Получено {len(all_messages)} сообщений')
        #
        # # Обработка сообщений (например, вывод на экран)
        # for message in all_messages:
        #     print(message.sender_id, message.text)

        return all_messages
    except errors.FloodWaitError as e:
        print(f"Flood wait error. Waiting for {e.seconds} seconds.")
        await asyncio.sleep(e.seconds + 5)
    except errors.TimeoutError:
        print(f"Timeout error.")
    except Exception as e:
        print(f"Unexpected error: {e}")

    finally:
        # Отключение клиента
        await client.disconnect()
