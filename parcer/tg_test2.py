import pyodbc
import telebot
from telebot import types

bot = telebot.TeleBot('7140130318:AAEpWKLeZBOe4LVHUOV23qIykl2ffWwDTy8')

# Настройка соединения с базой данных MS Access
db_path = r'C:\Users\nebey\OneDrive\Документы\Parser.accdb'
connection_string = (
    r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
    r'DBQ=' + db_path + ';'
)

user_data = {}

def user_id_exists(user_id: int) -> bool:
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Users WHERE telegramm_id = ?", (user_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result[0] > 0
    except pyodbc.Error as e:
        print("Error in connection: ", e)
        return False

def save_user_id(user_id: int):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Users (telegramm_id) VALUES (?)", (user_id,))
        conn.commit()
        cursor.close()
        conn.close()
    except pyodbc.Error as e:
        print("Error in connection: ", e)

def update_user_choices(user_id: int, sources: list, companies: list):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("UPDATE Users SET source_id = ?, company_id = ? WHERE telegramm_id = ?", (','.join(sources), ','.join(companies), user_id))
        conn.commit()
        cursor.close()
        conn.close()
    except pyodbc.Error as e:
        print("Error in connection: ", e)

@bot.message_handler(commands=['start'])
def main(message):
    user_id = message.from_user.id
    if not user_id_exists(user_id):
        save_user_id(user_id)
    user_data[user_id] = {'sources': [], 'companies': []}
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('Продолжить')
    markup.row(btn1)
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name} {message.from_user.last_name}!\n'
                                      f'Я бот, который помогает мониторить новости и анализировать их. Для того, чтобы воспользоваться ботом, нажмите "Продолжить"', reply_markup=markup)

def on_click(message):
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('РБК')
    btn2 = types.KeyboardButton('Коммерсант')
    markup.row(btn1, btn2)
    bot.send_message(message.chat.id, 'Выберите источник, из которого будете отслеживать информацию', reply_markup=markup)

def on_click1(message):
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('Выбрать еще источник')
    btn2 = types.KeyboardButton('Подтвердить')
    markup.row(btn1, btn2)
    bot.send_message(message.chat.id, 'Выбрать еще источник или подтвердить', reply_markup=markup)

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

def on_clickConfirm(message):
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('Это все')
    btn2 = types.KeyboardButton('Выбрать еще')
    markup.row(btn1, btn2)
    bot.send_message(message.chat.id, 'Это все компании, которые вы собираетесь отслеживать, или выбрать еще?', reply_markup=markup)

def on_clickEnd(message):
    user_id = message.from_user.id
    sources = user_data[user_id]['sources']
    companies = user_data[user_id]['companies']
    update_user_choices(user_id, sources, companies)
    del user_data[user_id]
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('Вперед')
    markup.row(btn1)
    bot.send_message(message.chat.id, 'Все нужные данные введены. Удачного пользования!', reply_markup=markup)

def newschat(message):
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('Вперед')
    markup.row(btn1)
    bot.send_message(message.chat.id, 'Все нужные данные введены. Удачного пользования!', reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def message_handler(message):
    user_id = message.from_user.id
    if message.text == 'Продолжить':
        on_click(message)
    elif message.text == 'РБК' or message.text == 'Коммерсант':
        user_data[user_id]['sources'].append(message.text)
        on_click1(message)
    elif message.text == 'Подтвердить':
        on_clickCompany(message)
    elif message.text in ['МосБиржа', 'СПБ Биржа', 'Лукойл', 'Газпром', 'Яндекс', 'Вконтакте']:
        user_data[user_id]['companies'].append(message.text)
        on_clickConfirm(message)
    elif message.text == 'Выбрать еще источник':
        on_click(message)
    elif message.text == 'Выбрать еще':
        on_clickCompany(message)
    elif message.text == 'Это все':
        on_clickEnd(message)

bot.polling(none_stop=True)
