import telebot
from telebot import types
bot=telebot.TeleBot('7140130318:AAEpWKLeZBOe4LVHUOV23qIykl2ffWwDTy8')
@bot.message_handler(commands=['start'])
def main(message):
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('Продолжить')
    markup.row(btn1)
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name} {message.from_user.last_name}!\n'
                                      f'Я бот, который помогает мониторить новости и анализировать их. Для того, чтобы воспользоваться ботом, нажмите "Продолжить"', reply_markup=markup)

def on_click(message):
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('РБК')
    btn2 = types.KeyboardButton('Коммерсант')
    markup.row(btn1,btn2)
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
    if message.text == 'Продолжить':
        on_click(message)
    elif message.text == 'РБК' or message.text == 'Коммерсант':
        on_click1(message)
    elif message.text == 'Подтвердить':
        on_clickCompany(message)
    elif message.text == 'МосБиржа'or message.text == 'СПБ Биржа'or message.text == 'Лукойл' or message.text == 'Газпром'or message.text == 'Яндекс' or message.text == 'Вконтакте':
        on_clickConfirm(message)
    elif message.text == 'Это все':
        on_clickEnd(message)

bot.polling(none_stop=True)

