import telebot


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

print('0')
@bot.message_handler(content=['Редакт. профиль'])
def procces_first_step(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
    markup.row('Киев','Одесса')
    markup.row('Днепр','Москва')
        
    msg = bot.send_message(message.chat.id, 'Выберите город в которм вы живете:', reply_markup=markup)
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
    bot.send_message(message.chat.id, 'Сохранение изменений:',reply_markup = user_markup)
    bot.send_message(message.chat.id, 'Аватарка:')
    idphoto  = message.photo[0].file_id
    user_id = message.from_user.id
    bot.send_photo(message.chat.id, idphoto)

    t = Template('*$title* *$name* \n Город: *$userCity* \n Имя: *$name* \n Пол: *$male* \n Год: *$age*')

    return t.substitute({
        'title' : title,
        'name' : name,
        'userCity' : user.city,
        'male' : user.male,
        'age' : user.age
    })