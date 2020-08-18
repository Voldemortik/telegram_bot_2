import telebot
import pyodbc

import config

from telebot import types
from string import Template

bot = telebot.TeleBot(config.TOKEN)

user_dict = {}
feedback_dict = {}

class User:
    def __init__(self,city):
        self.city = city

        keys = ['name', 'male' , 'age' , 'photo']

        for key in keys:
            self.key = None

@bot.message_handler(commands=['start'])
def welcome(message):
    #/start
    sti = open('static/AnimatedSticker.tgs', 'rb')
    bot.send_sticker(message.chat.id, sti)

    user_markup = telebot.types.ReplyKeyboardMarkup(True)
    user_markup.row('/start')
    user_markup.row('Профиль','Редакт.профиль')
    user_markup.row('О боте','Отзыв')

    bot.send_message(message.from_user.id,"Привет, {0.first_name}!\nЯ - <b>{1.first_name}</b>,здесь ты можешь найти себе друзей или любовь".format(message.from_user, bot.get_me()), reply_markup = user_markup,parse_mode = 'html')

    #profile application
    inline_markup = telebot.types.InlineKeyboardMarkup()
    button1 = telebot.types.InlineKeyboardButton('Создать профиль',callback_data='good')
    inline_markup.add(button1)
    bot.send_message(message.chat.id,"Но для начала тебе нужно создать свой профиль",reply_markup = inline_markup)

@bot.callback_query_handler(func=lambda call: True)
def procces_first_step(call):
    conn = pyodbc.connect("Driver={SQL Server};Server=DESKTOP-B5RC67H\SQLEXPRESS;Database=mydb;Trusted_Connection=yes;")

    cursor = conn.cursor()
    if call.data == 'well':
        print('1')
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row('Киев','Одесса')
        markup.row('Днепр','Москва')
        
        msg = bot.send_message(call.message.chat.id, 'Выберите город в которм вы живете:', reply_markup=markup)
        bot.register_next_step_handler(msg, anketa_city)
    elif cursor.execute("SELECT user_id FROM Table_5 WHERE EXISTS(SELECT user_id FROM Table_5 WHERE user_id='{user_id}')"):    
        user_markup = types.ReplyKeyboardMarkup(True)
        user_markup.row('/start')
        user_markup.row('Профиль','Редакт.профиль')
        user_markup.row('О боте','Отзыв')
        bot.send_message(call.message.chat.id, 'Вы уже создали профиль!',reply_markup = user_markup)
        
    else:
        if call.data == 'good':
            markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.row('Киев','Одесса')
            markup.row('Днепр','Москва')
        
            msg = bot.send_message(call.message.chat.id, 'Выберите город в которм вы живете:', reply_markup=markup)
            bot.register_next_step_handler(msg, anketa_city)

def anketa_city(message):
    try:
        chat_id = message.chat.id
        user_dict[chat_id] = User(message.text)

        markup = types.ReplyKeyboardRemove(selective=False)
        msg = bot.send_message(chat_id, "Напишите своё имя:", reply_markup=markup)
        bot.register_next_step_handler(msg, proccess_fullname_step)
    
    except Exception as e:
        bot.reply_to(message, 'ooops')

def proccess_fullname_step(message):
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.name = message.text

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
        markup.row('Male','Female')
        msg = bot.send_message(chat_id,'Выберите пол:', reply_markup=markup)
        bot.register_next_step_handler(msg, proccess_male_step)

    except Exception as e:
        bot.reply_to(message, 'ooops')

def proccess_male_step(message):
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.male = message.text

        markup = types.ReplyKeyboardRemove(selective=False)
        msg = bot.send_message(chat_id, 'Введите ваш возраст:' , reply_markup=markup)
        bot.register_next_step_handler(msg, proccess_age_step)     

    except Exception as e:
        bot.reply_to(message, 'ooops')

def proccess_age_step(message):
    try:
        int(message.text)
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.age = message.text

        msg = bot.send_message(chat_id, 'Отправте мне фото для вашей аватарки')
        bot.register_next_step_handler(msg, proccess_photo_step)

    except Exception as e:
        bot.reply_to(message, 'ooops')

@bot.message_handler(content_types=["photo"])
def proccess_photo_step(message):
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        idphoto = message.photo[0].file_id
        
        bot.send_message(chat_id, getRegData(user, 'Ваш профиль', user.name,message), parse_mode="Markdown")#Заявка
    
    except Exception as e:
        print(e)

def getRegData(user, title, name, message):

    user_markup = types.ReplyKeyboardMarkup(True)
    user_markup.row('/start')
    user_markup.row('Профиль','Редакт. профиль')
    user_markup.row('О боте','Отзыв')
    bot.send_message(message.chat.id, 'Аватарка:',reply_markup = user_markup)
    idphoto  = message.photo[0].file_id
    user_id = message.from_user.id
    bot.send_photo(message.chat.id, idphoto)

    t = Template('*$title* *$name* \n Город: *$userCity* \n Имя: *$name* \n Пол: *$male* \n Год: *$age*')

    conn = pyodbc.connect("Driver={SQL Server};Server=DESKTOP-B5RC67H\SQLEXPRESS;Database=mydb;Trusted_Connection=yes;")

    cursor = conn.cursor()
    if cursor.execute("SELECT user_id FROM Table_5 WHERE EXISTS(SELECT user_id FROM Table_5 WHERE user_id='{user_id}')"):
            # cursor.execute("INSERT INTO Table_5 (user_id, Name, City, Male, Age, Photo_id) VALUES (?,?,?,?,?,?)", (user_id, name, user.city, user.male, user.age, idphoto))
            cursor.execute("""UPDATE Table_5 SET Name = ?,
                                                 City = ?,
                                                 Male = ?,
                                                 Age = ?,
                                                 Photo_id = ?
                                             WHERE user_id = ?""" , (name, user.city, user.male, user.age, idphoto, user_id))
            conn.commit()
            
    else:

        cursor.execute("SELECT Name FROM Table_5 WHERE Name = '{name}'")
        cursor.execute("INSERT INTO Table_5 VALUES ( ?, ?, ?, ?, ?, ?)", (user_id, name, user.city, user.male, user.age, idphoto))
        conn.commit()

    return t.substitute({
        'title' : title,
        'name' : name,
        'userCity' : user.city,
        'male' : user.male,
        'age' : user.age
    })


#ДЛЯ ТОГО ЧТОБЫ ПРОВЕРИТЬ ДУБЛИКАТ ЮЗАЙ EXISTS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# @bot.message_handler(commands=["Редакт.профиль"])
# def updates(message):
    # chat_id = message.chat.id
    # user_dict[chat_id] = User(message.text)
    # user = user_dict[chat_id]
    # inline_markup = telebot.types.InlineKeyboardMarkup()
    # button1 = telebot.types.InlineKeyboardButton('Изменить профиль',callback_data='good')
    # inline_markup.add(button1)
    # bot.send_message(message.chat.id,"Вы точно хотите изменить профиль?",reply_markup = inline_markup)
    # if call.data == 'good':
    # markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    # markup.row('Киев','Одесса')
    # markup.row('Днепр','Москва')
        
#     msg = bot.send_message(message.chat.id, 'Выберите город в которм вы живете:', reply_markup=markup)
#     bot.register_next_step_handler(msg, anketa_city)
#     user_id = message.from_user.id

#     conn = pyodbc.connect("Driver={SQL Server};Server=DESKTOP-B5RC67H;Database=mydb;Trusted_Connection=yes;")
#     cursor = conn.cursor()

#     cursor.execute('SELECT User_id FROM Table_2 ORDER BY User_id')
#     order_id = cursor.fetchall()
#     print(order_id)
#     print(user_id)
#     update_profile = 'UPDATE Table_2 SET Name = {name} WHERE {order_id} = {user_id}'
#     conn.commit()
#     print('1')

#         conn = pyodbc.connect("Driver={SQL Server};Server=DESKTOP-59BIPOH;Database=mydb;Trusted_Connection=yes;")

#         cursor = conn.cursor()
#         if cursor.fetchone() is None:
            # cursor.execute("INSERT INTO Profiles ( Name, City, Male, Age) VALUES (?,?,?,?)", ('{user.name}', '{user.city}', '{user.male}', '{user.age}'))
            # conn.commit()
            # print('Зарегистрировано!')
#     except Exception as e:
#         print(e)

#     for values in cursor.execute("SELECT * FROM reg"):
#             print(values)

@bot.message_handler(content_types=["text"])
def buttons_1(message):
    if message.text == 'Отзыв':
       msg = bot.send_message(message.chat.id,'Напишите отзыв:')
       bot.register_next_step_handler(msg, feedback_step_2)
    elif message.text == 'О боте':
        bot.send_message(message.chat.id,'Скоро')#Этот бот был создан для того,чтобы пользователь смог найти себе друга,вторую половинку или просто новые знакомства
    elif message.text == 'Профиль':
        user_id = message.from_user.id
        bot.send_message(message.chat.id,Show_profile(user_id,'Ваш профиль',message), parse_mode="Markdown")
    elif message.text == 'Редакт.профиль':
        chat_id = message.chat.id
        user_dict[chat_id] = User(message.text)
        user = user_dict[chat_id]
        inline_markup = telebot.types.InlineKeyboardMarkup()
        button1 = telebot.types.InlineKeyboardButton('Изменить профиль',callback_data='well')
        inline_markup.add(button1)
        bot.send_message(message.chat.id,"Вы точно хотите изменить профиль?",reply_markup = inline_markup)
        
def Show_profile(user_id,title,message):   
    user_markup = types.ReplyKeyboardMarkup(True)
    user_markup.row('/start')
    user_markup.row('Профиль','Редакт.профиль')
    user_markup.row('О боте','Отзыв')

    conn = pyodbc.connect("Driver={SQL Server};Server=DESKTOP-B5RC67H\SQLEXPRESS;Database=mydb;Trusted_Connection=yes;")

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Table_5 WHERE user_id=?", (user_id))
    profile = cursor.fetchall()
    for a in profile:
        a = a
    bot.send_message(message.chat.id, 'Аватарка:',reply_markup = user_markup)
    idphoto  = a.Photo_id
    bot.send_photo(message.chat.id, idphoto)
    t = Template('*$title* *$name* \n Город: *$userCity* \n Имя: *$name* \n Пол: *$male* \n Год: *$age*')
    
    return t.substitute({
        'title' : title,
        'name' : a.Name,
        'userCity' : a.City,
        'male' : a.Male,
        'age' : a.Age
    })


def feedback_step_2(message):
    try:  
        chat_id = message.chat.id
        feedback_dict[chat_id] = User(message.text)
        feedbacks = feedback_dict[chat_id]
        sti = open('static/AnimatedSticker1.tgs','rb')
        bot.send_sticker(chat_id, sti)
        bot.send_message(chat_id, 'Спасибо за отзыв!')
    
    except Exception as e:
        bot.reply_to(message, 'ooops')

if __name__ == '__main__':
    bot.polling(none_stop=True)



