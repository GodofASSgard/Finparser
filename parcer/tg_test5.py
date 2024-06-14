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
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        print(f"Имя компании: {company_name}")
        cursor.execute("SELECT company_id FROM Companies WHERE company_name = ?", (company_name,))
        result = cursor.fetchone()
        print(f"Результат запроса: {result}")
        cursor.close()
        conn.close()
        return result[0] if result else None
    except pyodbc.Error as e:
        print("Ошибка в подключении или выполнении запроса: ", e)
        return None

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

def save_or_update_user_choices(user_id: int, source_ids: list, company_ids: list):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        source_ids_str = ','.join(str(id) for id in source_ids)
        company_ids_str = ','.join(str(id) for id in company_ids)

        print(f"Идентификаторы источников: {source_ids_str}")
        print(f"Идентификаторы компаний: {company_ids_str}")

        if user_id_exists(user_id):
            query = "UPDATE Users SET source_id = ?, company_id = ? WHERE telegramm_id = ?"
            print(f"Executing query: {query}")
            cursor.execute(query, (source_ids_str, company_ids_str, user_id))
        else:
            query = "INSERT INTO Users (telegramm_id, source_id, company_id) VALUES (?, ?, ?)"
            print(f"Executing query: {query}")
            cursor.execute(query, (user_id, source_ids_str, company_ids_str))

        conn.commit()
        cursor.close()
        conn.close()

        print("Данные успешно записаны в базу данных.")

    except pyodbc.Error as e:
        print("Ошибка в подключении или выполнении запроса: ", e)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def main(message):
    user_id = message.from_user.id
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
    save_or_update_user_choices(user_id, sources, companies)  # Сохраняем или обновляем записи в базе данных
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
        source_id = get_source_id_by_name('РБК')
        user_data[user_id]['sources'].append(source_id)
        on_click1(message)
    elif message.text == 'Коммерсант':
        source_id = get_source_id_by_name('Коммерсант')
        user_data[user_id]['sources'].append(source_id)
        on_click1(message)
    elif message.text in ['МосБиржа', 'СПБ Биржа', 'Лукойл', 'Газпром', 'Яндекс', 'Вконтакте']:
        company_name = message.text
        company_id = get_company_id_by_name(company_name)
        user_data[user_id]['companies'].append(company_id)
        on_clickConfirm(message)
    elif message.text == 'Подтвердить':
        on_clickCompany(message)
    elif message.text == 'Выбрать еще источник':
        on_click(message)
    elif message.text == 'Выбрать еще':
        on_clickCompany(message)
    elif message.text == 'Это все':
        on_clickEnd(message)

# Запуск бота
bot.polling(none_stop=True)
