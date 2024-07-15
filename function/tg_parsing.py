import asyncio
import re
from datetime import datetime
from functools import partial

from deep_translator import GoogleTranslator
from deep_translator.exceptions import RequestError
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

from db.msg4analysis import insert_unprocessed_message


async def main_parsing(estates_list: list, group_id: str) -> list:
    parsing_estates = []
    dt = datetime.now()
    for estate in estates_list:
        estate_dict = {}
        # Сatching error when receiving images without text
        try:
            msg = estate.message.lower()
        except AttributeError:
            continue
        # Collect dict for db
        if await rent_parsing(msg):
            estate_dict['price'] = await price_parsing(msg)
            if estate_dict['price'] == -1:
                await insert_unprocessed_message(case='NO PRICE', msg=msg, url=f't.me/{group_id}/{estate.id}')
                print(f'-------------PRICE DOESNT FIND --------------------!!!!!!!!!\nt.me/{group_id}/{estate.id}')
                continue
            language, msg_ru, msg_en, msg_el = await translate_language(msg)
            if not language:
                await insert_unprocessed_message(case='NO LANGUAGE', msg=msg, url=f't.me/{group_id}/{estate.id}')
                print(f'-------------- LANGUAGE DOESNT FIND --------------------!!!!!!!!!\nt.me/{group_id}/{estate.id}')
                continue

            estate_dict['resource'] = 1  # 1 - Telegram, 2 - website
            estate_dict['datetime'] = dt
            estate_dict['city'] = await city_parsing(msg)
            estate_dict['group_id'] = group_id
            estate_dict['msg_id'] = estate.id
            estate_dict['url'] = f't.me/{group_id}/{estate.id}'
            estate_dict['msg'] = msg
            estate_dict['language'] = language
            estate_dict['msg_ru'] = msg_ru
            estate_dict['msg_en'] = msg_en
            estate_dict['msg_el'] = msg_el

            if estate_dict['city'] == "cyprus":
                print(f'----------- DOESNT FIND CITY ---------------------- \nt.me/{group_id}/{estate.id}')
                await insert_unprocessed_message(case='NO FOUND CITY', msg=msg, url=f't.me/{group_id}/{estate.id}')

            parsing_estates.append(estate_dict)
    return parsing_estates


async def rent_parsing(msg: str) -> bool:
    re_rent = r"(#?(for)? ?(for)?rent)|(#? ?[а🅰️]ренда)|(сдам)|(сдается)"
    return True if re.search(re_rent, msg, re.IGNORECASE) else False


async def city_parsing(msg: str) -> str:
    # Write city name on 3 language (En, Gr[en transcription], Ru)
    limassol = \
        (r"(л[ие]м[ао]сс?ол[ае]?)|(l[ie]m[ae]ss?o[ls])|(n[ei]ap[oa]lis)|(lim)|(лим)|"
         r"(\b[Nn][Ee]?[Aa]?[Pp][Aa]?[Oo]?[Ll][Ii][Ss][Ee]?[Ss]?\b)|(\b[Нн][Ее][Аа]?[Пп][Аа]?[Оо]?[Лл][Ии][Сс][Сс]?[Ее]?[Йй]?\b)|"
         r"(\bagi?a? ?fy?l?i?a?\b)|(\bаги?я? ?ф[ийы]л?я?\b)|"
         r"(г[еи]ра?м[аое]?с[ое]й?и?[оя]\b)|(germass?og[ei][aiye]?[ia]?\b)|"
         r"(\bаг[ий]?ос ?т[иы]х[оа]н[ао]с\b)|(\bagios ?t[hy][ck]?[oi][nh]?[aons]{2,}\b)|"
         r"(\bкат[ат]?[оа] ?пол[еи]м[еи]д[иы]?[яиа]\b)|(\bkat[ot]?[oa] ?pol[ei]m[ei]d[iy]?[aeia]\b)|"
         r"(\bм[еи]с{1,2}[аи] ?г?[еи][тт][оа][нн][ия][ья]?\b)|(\bmes{1,2}a ?ge?[iie]t{1,2}on[yi][ai]?\b)|"
         r"(\bз[ао]к{1,2}[ао]к{1,2}и[ий]?\b)|(zak{1,2}[ao]k{1,2}[iye]?\b)|"
         r"(папас)|(papas)|(metro)|(мол[оа]сс?е?)")
    larnaka = r"(л[ао]рнак[ае])|(l[ae]r[nv]aka)"
    pafos = r"(паф[ао]сс?е?)|(paf[ao]ss?)"
    nikosiya = r"(н[ие]к[оа]сс?и[яи])|(n[ie]k[oa]ss?ia)|(lefkosa)"

    if re.search(limassol, msg, re.IGNORECASE):
        return "limassol"
    if re.search(larnaka, msg, re.IGNORECASE):
        return "larnaka"
    if re.search(pafos, msg, re.IGNORECASE):
        return "paphos"
    if re.search(nikosiya, msg, re.IGNORECASE):
        return "nicosia"

    return "cyprus"


async def price_parsing(msg: str) -> int:
    r_str = r"((💵)?(price)?(евро)?(cтоимость)?(цена)?(в)?(за)?(аренд[аы])?(euro)?(eur)? ?(мес)?(месяц)?[€\-💶💴:/]? ?" \
            r"\d{1,3}[\.',\s]?\d{3}" \
            r" ?(💵)?(price)?(евро)?(euro)?(eur)?[€\-💶💴:/]?(cтоимость)?(цена)? ?(в)?(за)?(аренд[аы])? ?(мес)?(месяц)?)" \
            r"|((💵)?(price)?(евро)?(cтоимость)?(цена)?(в)?(за)?(аренд[аы])?(euro)?(eur)? ?(мес)?(месяц)?[€\-💶💴:/]? ?" \
            r"\d{3}" \
            r" ?(💵)?(price)?(евро)?(euro)?(eur)?[€\-💶💴:/]?(cтоимость)?(цена)? ?(в)?(за)?(аренд[аы])? ?(мес)?(месяц)?)"

    # List with our keywords in tuple in list
    first_search = re.findall(r_str, msg)

    print(first_search)
    if first_search:
        # Rewrite num in list without empty string
        first_numbers = [el_s for _ in first_search for el_s in _ if el_s != '']
        print(f'first_numbers {first_numbers}')
    # Catch typecast error
    # If catch error we return result = -1, after we can identify this result (-1) like an error
    try:
        return clean_price(first_numbers)
    except ValueError:
        return -1


def clean_price(first_number):
    re_clean_price = r"(\d{1,3}[\.',\s]?\d{3})|(\d{3})"
    flag = True
    second_number = []
    trig_w = ["евро", "euro", "eur", "€", "💶", "💵", "💴", "price", "цена", "cтоимость"]
    result = []
    for string in first_number:
        for key_w in trig_w:
            if flag and key_w in string:
                flag = False
                num = re.findall(re_clean_price, string)
                second_number = [el_s for _ in num for el_s in _ if el_s != '']
                if not second_number:
                    flag = True
                    continue
                flag_2 = True
                for elem in second_number:
                    for ch in [",", ".", " "]:
                        if ch in elem:
                            result.append(elem.replace(ch, ""))
                            flag_2 = False
                            break
                    if flag_2:
                        result.append(elem)
                return result[0]

    # If we can't find match with list 'trig_w', we start finding price in first search list
    if flag:
        for string in first_number:
            if re.findall(re_clean_price, string):
                if string != "":
                    second_number.append(string.replace(" ", ""))
        flag = False
        for elem in second_number:
            flag_2 = True
            for ch in [".", ","]:
                if ch in elem:
                    flag_2 = False
                    result.append(elem.replace(ch, ""))
            if flag_2:
                result.append(elem)
        result.sort(reverse=True)
        if not result:
            return -1
        try:
            return result[0]
        except IndexError:
            return -1


async def translate_language(msg: str) -> tuple[str, str, str, str]:
    DetectorFactory.seed = 0

    async def detect_language(msg: str) -> str:
        try:
            # Определяем язык
            lang_code = detect(msg)
            return lang_code
        except LangDetectException as e:
            print(e)
            return ''

    async def translate_ru(src: str, msg: str = msg, dest: str = 'ru') -> str:
        loop = asyncio.get_event_loop()
        translate_partial = partial(GoogleTranslator(src, dest).translate, msg)
        msg_ru = await loop.run_in_executor(None, translate_partial)
        return f'{msg_ru}\n\n____________________________\nПереведено с помощью Гугл Переводчика'

    async def translate_en(src: str, msg: str = msg, dest: str = 'en') -> str:
        loop = asyncio.get_event_loop()
        translate_partial = partial(GoogleTranslator(src, dest).translate, msg)
        msg_en = await loop.run_in_executor(None, translate_partial)
        return f'{msg_en}\n\n____________________________\nTranslated using Google Translator'

    async def translate_el(src: str, msg: str = msg, dest: str = 'el') -> str:
        loop = asyncio.get_event_loop()
        translate_partial = partial(GoogleTranslator(src, dest).translate, msg)
        msg_el = await loop.run_in_executor(None, translate_partial)
        return f'{msg_el}\n\n____________________________\nΜεταφράστηκε χρησιμοποιώντας το Google Translator'

    msg_language = await detect_language(msg)

    try:
        match msg_language:
            case 'ru':
                msg_en = await translate_en('ru')
                msg_el = await translate_el('ru')
                return msg_language, msg, msg_en, msg_el
            case 'en':
                msg_ru = await translate_ru('en')
                msg_el = await translate_el('en')
                return msg_language, msg_ru, msg, msg_el
            case 'el':
                msg_en = await translate_en('el')
                msg_ru = await translate_ru('el')
                return msg_language, msg_ru, msg_en, msg
            case _:
                return '', '', '', ''
    except RequestError:
        pass
