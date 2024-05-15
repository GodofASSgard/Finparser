import pyodbc
import requests
from bs4 import BeautifulSoup

def insert_news_to_access_db(title, annotation, url, content):
    try:
        # Строка подключения к вашей базе данных MS Access
        conn_str = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Users\nebey\OneDrive\Документы\Parser.accdb;'

        # Установка соединения
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        # Пример SQL-запроса для вставки данных
        sql_query = "INSERT INTO News (title, annotation, url, content) VALUES (?, ?, ?, ?)"

        # Выполнение запроса с передачей параметров
        cursor.execute(sql_query, (title, annotation, url, content))

        # Подтверждение изменений в базе данн ых
        conn.commit()

        print("Данные успешно добавлены в таблицу News.")

    except pyodbc.Error as e:
        print(f"Ошибка при вставке данных: {e}")

    finally:
        # Закрытие соединения
        if conn:
            conn.close()




def parse_rbk_news():
    url = "https://quote.rbc.ru/tag/investments"  # URL-адрес для парсинга
    response = requests.get(url)  # Запрос к веб-странице
    soup = BeautifulSoup(response.content, 'html.parser')  # Создание объекта BeautifulSoup для анализа HTML-кода

    news_items = soup.find_all('a', class_='news-feed__item js-visited js-news-feed-item js-yandex-counter')  # Поиск всех элементов новостей

    for news_item in news_items:  # Цикл для обхода всех найденных новостей
        title = news_item.find('span', class_='news-feed__item__title').text.strip()  # Получение заголовка новости
        link = news_item['href']  # Получение ссылки на новость

        if link:  # Проверка наличия ссылки
            response = requests.get(link)  # Запрос к странице новости
            soup = BeautifulSoup(response.content, 'html.parser')  # Создание объекта BeautifulSoup для анализа HTML-кода

            # Получение аннотации
            annotation_element = soup.find('div', class_='article__text__overview')
            annotation = None
            if annotation_element is not None:
                annotation = annotation_element.find('span').text  # Получение текста аннотации

            # Получение всех текстов под тегом <p>
            news_texts = []
            paragraphs = soup.find_all('p')
            for paragraph in paragraphs:
                news_texts.append(paragraph.text.strip())

            # Объединение текстов новости в одну строку
            content = '\n'.join(news_texts)

            # Вставка данных в базу данных
            insert_news_to_access_db(title, annotation, link, content)


def parse_kommersant_news():
    url = 'https://www.kommersant.ru/finance'
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        news_blocks = soup.find_all('span', class_='vam')
        for block in news_blocks:
            news_title = block.text.strip()
            news_link = 'https://www.kommersant.ru' + block.parent['href']
            news_response = requests.get(news_link)
            if news_response.status_code == 200:
                news_soup = BeautifulSoup(news_response.text, 'html.parser')
                news_header = news_soup.find('h1', class_='doc_header__name js-search-mark').text.strip()
                news_annotation_tag = news_soup.find('h2', class_='doc_header__subheader')
                news_annotation = news_annotation_tag.text.strip() if news_annotation_tag else None

                # Найдем все элементы <p> с классом 'doc__text'
                news_text_tags = news_soup.find_all('p', class_='doc__text')
                news_texts = [tag.text.strip() for tag in news_text_tags]

                # Объединим тексты в одну строку
                content = '\n'.join(news_texts)

                # Вставим данные в базу данных
                insert_news_to_access_db(news_title, news_annotation, news_link, content)

                print("Данные успешно добавлены в базу данных.")
            else:
                print("Не удалось получить доступ к странице новости:", news_link)
    else:
        print("Не удалось получить доступ к странице с финансовыми новостями.")

def parse_finam_news():#не работает

    # Ссылка на страницу
    url = 'https://www.finam.ru/publications/selection/united/'

    # Заголовок User-Agent
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'
    }

    # Выполняем GET-запрос к странице с заголовком User-Agent
    response = requests.get(url, headers=headers)

    # Проверяем успешность запроса
    if response.status_code == 200:
        # Создаем объект BeautifulSoup для парсинга HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Находим все ссылки на новости
        news_links = soup.find_all('a', class_=' display-b cl-black line-24 cl-transport-black')
        print("Количество найденных ссылок на новости:", len(news_links))

        print("Найдены ссылки на новости:")
        for link in news_links:
            print(link)  # Отладочный вывод
            # Получаем заголовок новости
            title = link.text.strip()

            # Получаем ссылку на новость
            news_url = 'https://www.finam.ru' + link['href']

            # Получаем аннотацию новости, если есть
            annotation = link.find('span', class_='cl-grey font-12 line-16 bold')
            annotation_text = annotation.text.strip() if annotation else 'None'

            # Выполняем GET-запрос к странице новости
            news_response = requests.get(news_url, headers=headers)

            # Проверяем успешность запроса к странице новости
            if news_response.status_code == 200:
                # Создаем объект BeautifulSoup для парсинга HTML новости
                news_soup = BeautifulSoup(news_response.text, 'html.parser')

                # Находим заголовок новости
                news_title = news_soup.find('h1', class_='mb2x').text.strip()

                # Находим текст новости
                news_text = news_soup.find('span').text.strip()

                # Выводим заголовок, ссылку, аннотацию и текст новости
                print('Заголовок:', news_title)
                print('Ссылка:', news_url)
                print('Аннотация:', annotation_text)
                print('Текст новости:', news_text)
                print('-' * 50)
            else:
                print('Ошибка при получении новости:', news_response.status_code)
                print('Контент:', news_response.content)
    else:
        print('Ошибка при получении страницы:', response.status_code)
        print('Контент:', response.content)

def main():
  #parse_kommersant_news()

  #parse_finam_news()
  parse_rbk_news()
  insert_news_to_access_db()




if __name__ == "__main__":
  main()


