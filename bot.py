import telebot
import time
import datetime
import MySQLdb
import config
from telebot import logger
from MySQLdb import OperationalError
from telebot import types

 #токен бота

bot = telebot.TeleBot(config.token, threaded=False)  # подключение к боту (конфиг)
conn = MySQLdb.connect('149.202.217.219', 'telega_admin', 'sayder123', 'telegram_bot')
print('Бот запущен - Daily Money')
#cursor = config.conn.cursor()  # подключение к бд (конфиг)
upd = bot.get_updates()
lastupd = upd[0]
global user_id
user_id = lastupd.message.chat.id
entering_number = False

def extract_unique_code(text):
    return text.split()[1] if len(text.split()) > 1 else None

def fetch_data(query):
        cursor = conn.cursor()
        cursor.execute(query)
        return cursor.fetchone()
def reward():
    print("Выдача награды пользователям")
    markup = telebot.types.InlineKeyboardMarkup()
    button = telebot.types.InlineKeyboardButton(text='Забрать награду', callback_data='reward')
    markup.add(button)
    bot.send_message(user_id, "Забирайте награду скорее", reply_markup=markup)

reward_time = datetime.datetime.now()

if (reward_time.hour == 12 and reward_time.minute == 0):
    reward()

def mainmenu():
    user_markup = telebot.types.ReplyKeyboardMarkup(True)
    user_markup.row('Баланс')
    user_markup.row('Партнёрская программа')
    bot.send_message(user_id, "Вы в главном меню, начисления происходят автоматически, вам придёт уведомление!",
                     reply_markup=user_markup)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    unique_code = extract_unique_code(message.text)
    user_id = message.chat.id
    if (unique_code == None):
        unique_code = 0
    print("Реф код: {}".format(unique_code))
    #  global our_id # Идентификатор пользователя
    # our_id = message.chat.id # Устанавливаем идентификатор
    print("Пользователь запустил бота - {}".format(user_id))
    user_count = fetch_data("SELECT COUNT(*) FROM `bot` WHERE chatid = {}".format(user_id))
    print("Количество аккаунтов с его ID: {}\n".format(user_count[0]))

    if (user_count[0] < 1):

        reg_info = fetch_data("INSERT IGNORE INTO `bot` (`chatid`,`balance`,`paywaiting`,`referrer`) VALUES ({0},0,0,{1})".format(user_id,unique_code))
        conn.commit()
        print(reg_info)
        bot.send_message(message.chat.id, "Добро пожаловать в DailyMoneyBot \nНаш бот раздаёт бонусы каждый день за просто так.\nУ нас также есть партнёрская программа, с помощью которой вы можете зарабатывать по 0.05 руб за каждого приглашенного по вашей ссылке пользователя")
        if (unique_code == 0):
            print("Пользователь {} самостоятельно запустил бота".format(user_id))
        else:
            print('Пользователь {} пригласил {}'.format(user_id, unique_code))
            fetch_data("UPDATE `bot` SET `balance` = `balance` + 0.05 WHERE `chatid` = {}".format(unique_code))
            bot.send_message(user_id,"Вас пригласил пользователь с ID {}\nЕму начислено вознаграждение за приглашение\nЕсли хотите тоже получать по 0.05 за каждого приглашенного, то воспользуйтесь своей ссылкой, перейдя в раздел Партнёрская программа".format(unique_code))
            config.conn.commit()
    else:
        bot.send_message(user_id, "С возвращением! Мы скучали по вам!")
    mainmenu()


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    if call.data == 'reward':
        bot.answer_callback_query(callback_query_id=call.id, text='Награда получена')
        fetch_data("UPDATE `bot` SET `balance`=`balance`+0.03 WHERE `chatid` = {}".format(user_id))
        conn.commit()
        bot.send_message(call.message.chat.id, "Следующая награда через 24 часа")
        bot.delete_message(call.message.chat.id,call.message.message_id)



@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.text == 'Баланс':
        user_markup = telebot.types.ReplyKeyboardMarkup(True)
        user_markup.row('Вывести','Изменить кошелёк')
        user_markup.row('Назад')
        bot.send_message(message.chat.id, "Здесь вы можете заказать выплату. Выплаты происходят от 25 рублей на Qiwi!",
                         reply_markup=user_markup)
        your_balance = fetch_data("SELECT `balance` FROM `bot` WHERE `chatid` = {}".format(user_id))
        bot.send_message(message.chat.id, "Ваш баланс: {} руб.".format(your_balance[0]))
        print("Пользователь {} проверил свой баланс: {} руб.".format(user_id,your_balance[0]))
    elif message.text == 'Партнёрская программа':
        bot.send_message(message.chat.id,
                         "Приглашайте друзей в наш проект и получайте по 0.05 руб за каждого пользователя\nВаша партнёрская ссылка:\nt.me/Daily_Money_bot?start={}".format(
                             user_id))
    elif message.text == 'Назад':
        mainmenu()
    elif message.text == 'Изменить кошелёк':
        markup = telebot.types.ReplyKeyboardMarkup(True)
        markup.row('Назад')
        msg = bot.send_message(user_id, "Введите свой Qiwi-кошелёк. Вводить без + в начале!",reply_markup=markup)
        bot.register_next_step_handler(msg, process_purse)

    elif message.text == '/dqwdeqwdawfdscxzczxczxczxcwrsdqwdafgr':
        print("Производится рассылка рекламы пользователям")
        count_users = fetch_data('SELECT COUNT(`id`) FROM `bot`')
        print("Количество получателей: {}".format(count_users[0]))
        i = 1
        while (i <= count_users[0]):
            receiver = fetch_data('SELECT `chatid` FROM `bot` WHERE `id` = {}'.format(i))
            print("Следующий получатель сообщения: {}".format(receiver[0]))
            rand_id = fetch_data('SELECT `id` FROM `advertisement` ORDER BY RAND()')
            adv_text = fetch_data('SELECT `advertise_text` FROM `advertisement` WHERE `id` = {}'.format(rand_id[0]))
            bot.send_message(receiver[0], "Реклама:\n{}".format(adv_text[0]))
            time.sleep(2)
            i = i + 1

    elif message.text == '/dasdwertmujikhjkiufsd3f32':
        print(conn)
        print("Производится раздача бонуса пользователям")
        count_users = fetch_data('SELECT COUNT(`id`) FROM `bot`')
        print("Количество получателей: {}".format(count_users[0]))
        i = 1
        while (i <= count_users[0]):
            receiver = fetch_data('SELECT `chatid` FROM `bot` WHERE `id` = {}'.format(i))
            print("Следующий получатель бонуса: {}".format(receiver[0]))
            bot.send_message(receiver[0], reward())
            i = i + 1
            time.sleep(2)

    elif message.text == 'Вывести':
        withdraw_purse = fetch_data("SELECT `purse` FROM `bot` WHERE `chatid` = {}".format(user_id))
        wp = withdraw_purse[0]
        if wp < 1:
            bot.send_message(user_id,
                             "У вас не установлен кошелёк!\nПерейдите в Баланс > Изменить кошелёк чтобы установить его.")
        else:
            withdraw_money()


def process_purse(message):
    try:
        purse = message.text
        if(purse != "Назад"):
            fetch_data('UPDATE `bot` SET `purse` = {} WHERE `chatid` = {}'.format(purse,user_id))
            conn.commit()
            print("Пользователь {} установил себе кошелёк: {}".format(user_id,purse))
            bot.send_message(user_id,"Кошёлек установлен.\nТекущий Qiwi-кошелёк: {}".format(purse))
            mainmenu()
        else:
            mainmenu()
    except Exception as e:
        bot.send_message(user_id,"Укажите корректный Qiwi-кошелёк")
        print(e)

def withdraw_money():
    withdraw = fetch_data("SELECT `balance` FROM `bot` WHERE `chatid` = {}".format(user_id))
    if withdraw[0] >= 25:
        fetch_data(
            "UPDATE `bot` SET `balance`= 0, `paywaiting` = {0} WHERE `chatid` = {1}".format(withdraw[0], user_id))
        conn.commit()
        print(
            "Новая заявка на вывод средств от пользователя: {}, сумма = {}".format(user_id, withdraw[0]))
        bot.send_message(user_id, "Заявка на выплату успешно создана, ожидайте выплату")
        mainmenu()
    else:
        bot.send_message(user_id, "Вы еще не набрали минимальную сумму для вывода")
        mainmenu()

while True:
    try:
        bot.polling(none_stop=True)
    except Exception as err:
        print(err)
        time.sleep(5)

    try:
        conn = MySQLdb.connect('149.202.217.219', 'telega_admin', 'sayder123', 'telegram_bot')
    except MySQLdb.DatabaseError as err:
        print(err)
        time.sleep(5)
        conn = MySQLdb.connect('149.202.217.219', 'telega_admin', 'sayder123', 'telegram_bot')






