from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from db.msg4analysis import insert_unprocessed_message


async def is_it_dublicate(msgs, estate_obj) -> bool:
    if not msgs:
        return False
    threshold = 0.8
    for msg in msgs:
        # Создание TF-IDF векторизатора
        vectorizer = TfidfVectorizer()

        # Преобразование текстов в TF-IDF векторы
        tfidf_matrix = vectorizer.fit_transform([msg, estate_obj['msg']])

        # Вычисление косинусного сходства
        similarity_matrix = cosine_similarity(tfidf_matrix)

        # Извлечение значения схожести между текстами
        similarity_score = similarity_matrix[0, 1]

        # Возвращение результата на основе порогового значения
        if similarity_score >= threshold:
            await insert_unprocessed_message('DUBLICATE', msg=msg, msg_2=estate_obj["msg"], url=estate_obj["url"])
            print(f'______________DUBLICATE______________')
            return True
    return False
