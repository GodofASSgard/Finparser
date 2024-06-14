import pyodbc
import telebot
from telebot import types

# Создаем экземпляр бота с токеном
bot = telebot.TeleBot('7140130318:AAEpWKLeZBOe4LVHUOV23qIykl2ffWwDTy8')

# Настройка соединения с базой данных MS Access
db_path = r'C:\Users\nebey\OneDrive\Документы\Parser.accdb'
connection_string = (
        r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
        r'DBQ=' + db_path + ';'
)

# Словарь для хранения данных пользователя во время сессии
user_data = {}



# Словарь для хранения данных пользователя во время сессии
user_data = {}

def get_source_id_by_name(source_name):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        print(f"Executing query: SELECT source_id FROM NewsSources WHERE source_name = '{source_name}'")
        cursor.execute("SELECT source_id FROM NewsSources WHERE source_name = ?", (source_name,))
        result = cursor.fetchone()
        print(f"Query result: {result}")
        cursor.close()
        conn.close()
        return result[0] if result else None
    except pyodbc.Error as e:
        print("Ошибка в подключении: ", e)
        return None


def get_company_id_by_name(company_name):
    conn = None
    cursor = None
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        # Выводим имя компании для отладки
        print(f"Имя компании: {company_name}")

        # Формируем и выполняем SQL-запрос
        cursor.execute("SELECT company_id FROM Companies WHERE company_name = ?", (company_name,))

        # Получаем результат запроса
        result = cursor.fetchone()

        # Выводим результат для отладки
        print(f"Результат запроса: {result}")

        # Если есть результат, выводим ID компании
        if result:
            company_id = result[0]
            print(f"ID компании: {company_id}")
            return company_id
        else:
            print("Компания не найдена в базе данных.")
            return None

    except pyodbc.Error as e:
        print("Ошибка в подключении или выполнении запроса: ", e)
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()









def user_id_exists(user_id: int) -> bool:
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        print(f"Executing query: SELECT COUNT(*) FROM Users WHERE telegramm_id = {user_id}")
        cursor.execute("SELECT COUNT(*) FROM Users WHERE telegramm_id = ?", (user_id,))
        result = cursor.fetchone()
        print(f"Query result: {result}")
        cursor.close()
        conn.close()
        return result[0] > 0
    except pyodbc.Error as e:
        print("Ошибка в подключении: ", e)
        return False

def save_user_id(user_id: int):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        print(f"Executing query: INSERT INTO Users (telegramm_id) VALUES ({user_id})")
        cursor.execute("INSERT INTO Users (telegramm_id) VALUES (?)", (user_id,))
        conn.commit()
        cursor.close()
        conn.close()
    except pyodbc.Error as e:
        print("Ошибка в подключении: ", e)

def save_user_choices(user_id: int, source_ids: list, company_ids: list):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        # Преобразуем списки идентификаторов источников и компаний в строки с разделителем ','
        source_ids_str = ','.join(str(id) for id in source_ids)
        company_ids_str = ','.join(str(id) for id in company_ids)

        # Выводим строки идентификаторов для отладки
        print(f"Идентификаторы источников: {source_ids_str}")
        print(f"Идентификаторы компаний: {company_ids_str}")

        # Вставляем запись в таблицу Users с идентификаторами источников и компаний
        query = "INSERT INTO Users (telegramm_id, source_id, company_id) VALUES (?, ?, ?)"
        print(f"Executing query: {query}")
        print(f"With values: user_id={user_id}, source_ids={source_ids_str}, company_ids={company_ids_str}")
        cursor.execute(query, (user_id, source_ids_str, company_ids_str))

        # Подтверждаем изменения в базе данных
        conn.commit()

        # Закрываем курсор и соединение
        cursor.close()
        conn.close()

        # Выводим сообщение об успешной записи данных
        print("Данные успешно записаны в базу данных.")

    except pyodbc.Error as e:
        print("Ошибка в подключении или выполнении запроса: ", e)







# Обработчик команды /start
@bot.message_handler(commands=['start'])
def main(message):
    user_id = message.from_user.id
    if not user_id_exists(user_id):  # Проверяем, существует ли пользователь в базе данных
        save_user_id(user_id)  # Если нет, сохраняем его
    user_data[user_id] = {'sources': [], 'companies': []}  # Создаем запись для пользователя в словаре user_data
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('Продолжить')
    markup.row(btn1)
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name} {message.from_user.last_name}!\n'
                                      f'Я бот, который помогает мониторить новости и анализировать их. Для того, чтобы воспользоваться ботом, нажмите "Продолжить"',
                     reply_markup=markup)

# Показ кнопок выбора источников
def on_click(message):
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('РБК')
    btn2 = types.KeyboardButton('Коммерсант')
    markup.row(btn1, btn2)
    bot.send_message(message.chat.id, 'Выберите источник, из которого будете отслеживать информацию',
                     reply_markup=markup)

# Показ кнопок подтверждения выбора источника или выбора еще одного источника
def on_click1(message):
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('Выбрать еще источник')
    btn2 = types.KeyboardButton('Подтвердить')
    markup.row(btn1, btn2)
    bot.send_message(message.chat.id, 'Выбрать еще источник или подтвердить', reply_markup=markup)

# Показ кнопок выбора компании
def on_clickCompany(message):
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('МосБиржа')
    btn2 = types.KeyboardButton('СПБ Биржа')
    markup.row(btn1, btn2)
    btn3 = types.KeyboardButton('Лукойл')
    btn4 = types.KeyboardButton('Газпром')
    markup.row(btn3, btn4)
    btn5 = types.KeyboardButton('Яндекс')
    btn6 = types.KeyboardButton('Вконтакте')
    markup.row(btn5, btn6)
    bot.send_message(message.chat.id, 'Выберите компанию, которую собираетесь отслеживать', reply_markup=markup)

# Показ кнопок подтверждения выбора компании или выбора еще одной компании
def on_clickConfirm(message):
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('Это все')
    btn2 = types.KeyboardButton('Выбрать еще')
    markup.row(btn1, btn2)
    bot.send_message(message.chat.id, 'Это все компании, которые вы собираетесь отслеживать, или выбрать еще?',
                     reply_markup=markup)

# Завершение процесса выбора и сохранение данных
def on_clickEnd(message):
    user_id = message.from_user.id
    sources = user_data[user_id]['sources']  # Получаем список ID источников, выбранных пользователем
    companies = user_data[user_id]['companies']  # Получаем список ID компаний, выбранных пользователем
    save_user_choices(user_id, sources, companies)  # Сохраняем записи в базе данных
    del user_data[user_id]  # Удаляем временные данные пользователя
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('Вперед')
    markup.row(btn1)
    bot.send_message(message.chat.id, 'Все нужные данные введены. Удачного пользования!', reply_markup=markup)


# Обработчик сообщений
@bot.message_handler(func=lambda message: True)
def message_handler(message):
    user_id = message.from_user.id
    if message.text == 'Продолжить':
        on_click(message)
    elif message.text == 'РБК':
        source_id = get_source_id_by_name('РБК')  # Получить ID РБК из таблицы NewsSources
        user_data[user_id]['sources'].append(source_id)  # Добавить ID источника в список источников пользователя
        on_click1(message)  # Показать кнопки для подтверждения или выбора еще одного источника
    elif message.text == 'Коммерсант':
        source_id = get_source_id_by_name('Коммерсант')  # Получить ID Коммерсант из таблицы NewsSources
        user_data[user_id]['sources'].append(source_id)  # Добавить ID источника в список источников пользователя
        on_click1(message)  # Показать кнопки для подтверждения или выбора еще одного источника
    elif message.text in ['МосБиржа', 'СПБ Биржа', 'Лукойл', 'Газпром', 'Яндекс', 'Вконтакте']:
        company_name = message.text  # Получить имя компании
        company_id = get_company_id_by_name(company_name)  # Получить ID компании из таблицы Companies
        user_data[user_id]['companies'].append(company_id)  # Добавить ID компании в список компаний пользователя
        on_clickConfirm(message)  # Показать кнопки для подтверждения или выбора еще одной компании
    elif message.text == 'Подтвердить':
        on_clickCompany(message)  # Показать кнопки выбора компании
    elif message.text == 'Выбрать еще источник':
        on_click(message)  # Показать кнопки выбора источника
    elif message.text == 'Выбрать еще':
        on_clickCompany(message)  # Показать кнопки выбора компании
    elif message.text == 'Это все':
        on_clickEnd(message)  # Завершить процесс выбора и сохранить данные


# Запуск бота
bot.polling(none_stop=True)
