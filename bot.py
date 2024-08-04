import asyncio
from datetime import datetime

from config.data import TELEGRAM_GROUPS, CHECK_FOR_DEL_MSG_TIME, DEL_MSG_AFTER_DAY, LOOP_SLEEP
from db.connect import insert_estates_tg, get_last_msg_id, delete_old_msgs
from function.tg_parsing import main_parsing
from function.tg_request import estates_telegram_list


async def main():
    count = 143

    while True:
        # Укажите идентификатор чата или его username
        for group_id in TELEGRAM_GROUPS:
            start_msg_id = await get_last_msg_id(group_id) + 1
            # Получаем список новых объявлений с ТГ
            estates_list = await estates_telegram_list(group_id, start_msg_id)
            if estates_list:
                parsed_list = await main_parsing(estates_list, group_id)
                if parsed_list:
                    await insert_estates_tg(parsed_list)

        print(f'parsing done - {datetime.now()}\n')
        count += 1
        if count == CHECK_FOR_DEL_MSG_TIME:
            await delete_old_msgs(DEL_MSG_AFTER_DAY)
            print('delete_old_msgs\n')
            count = 0
        await asyncio.sleep(LOOP_SLEEP)

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Бот был остановлен вручную")
