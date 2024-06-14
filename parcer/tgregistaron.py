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

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    if user_id_exists(user_id):
        bot.reply_to(message, "Ваш ID уже сохранен в базе данных!")
    else:
        save_user_id(user_id)
        bot.reply_to(message, "Ваш ID сохранен в базе данных!")

bot.polling()
