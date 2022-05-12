import telebot
import configure
import sqlite3
from telebot import types
from SimpleQIWI import *

bot = telebot.TeleBot(configure.config['token']) #Подключение токена
con = sqlite3.connect('baza.db', check_same_thread=False) #Создание соединения с БД
cur = con.cursor()# Создание курсора (делает запросы и получает их результаты)
lock = threading.Lock() #Блокировщик
api = QApi(token=configure.config['tokenqiwi'], phone=configure.config['phoneqiwi']) #Подключение киви
markdown = """   
    *bold text*
    _italic text_
    [text](URL) 
    """  #Полужирный, курсивный и подчеркнутый шрифт

cur.execute("""CREATE TABLE IF NOT EXISTS users (id BIGINT, nick TEXT, cash INT, access INT, bought INT)""")  #Методы для выполнения
cur.execute("""CREATE TABLE IF NOT EXISTS shop (id INT, name TEXT, price INT, tovar TEXT, whobuy TEXT)""")    #команд SQL
con.commit()  #Метод, который обеспечивает внесение изменений в БД

@bot.message_handler(commands=['start']) #Объявлени команды, по которой вызывается бот
def start(message):
	try:
		cur.execute(f"SELECT id FROM users WHERE id = {message.from_user.id}")
		if cur.fetchone() is None:
			cur.execute(f"INSERT INTO users VALUES ({message.from_user.id}, '{message.from_user.first_name}', 0, 0, 0)")
			bot.send_message(message.chat.id, f"👾 Добро пожаловать в магазин покупки и продажи аккаунтов, {message.from_user.first_name}!👾\n Пропишите /help, чтобы узнать все команды\n")
			con.commit()
		else:
			bot.send_message(message.chat.id, f"🦦 Вы уже зарегистрированы! Пропишите /help, чтобы узнать все команды.")
	except:
		bot.send_message(message.chat.id, f'🚫 Ошибка при выполнении команды. Повторите запрос или пропишите /help! 🚫')

@bot.message_handler(commands=['getrazrab'])
def getrazrab(message):
	if message.from_user.id == 1942166894:
		cur.execute(f"UPDATE users SET access = 777 WHERE id = 1942166894")
		bot.send_message(message.chat.id, f"Вы выдали себе Разработчика")
		con.commit()
	else:
		bot.send_message(message.chat.id, f"Отказано в доступе!")

@bot.message_handler(commands=['profile'])
def profile(message):
	try:
		cur.execute(f"SELECT * FROM users WHERE id = {message.from_user.id}")
		getaccess = cur.fetchone()[3]
		if getaccess == 0:
			access = 'Пользователь'
		elif getaccess == 1:
			access = 'Администратор'
		elif getaccess == 666:
			access = 'Разработчик'
		for info in cur.execute(f"SELECT * FROM users WHERE id = {message.from_user.id}"):
			bot.send_message(message.chat.id, f"*👤 Ваш профиль:*\n\n*ID:* {info[0]}\n*Баланс:* {info[2]}₽\n*Уровень доступа:* {access}\n*Куплено товаров:* {info[4]}", parse_mode='Markdown')
	except:
		bot.send_message(message.chat.id, f'🚫 Ошибка при выполнении команды. Повторите запрос или пропишите /help! 🚫')

@bot.message_handler(commands=['help'])
def help(message):
	with lock:
		mes = message.chat.id
		cur.execute(f"SELECT * FROM users WHERE id = {message.from_user.id}")
		getaccess = cur.fetchone()[3]
	if getaccess >= 1:
		bot.send_message(mes, '*Помощь по командам:*\n\n*Команды для пользователя*\n/profile - Посмотреть свой профиль\n/help - Посмотреть список команд\n/helper - помощник по продаже/покупке\n/buy - Купить аккаунт\n/donate - Пополнить счёт\n/mybuy - Посмотреть список купленных аккаунтов\n/guard - Связаться с помощником\n\n*Команды для администрации*\n/viewprofile - Посмотреть чужой профиль\n'
							  '/allusers - Список всех пользователей\n/accesslvl - Выдать уровень доступа\n/givemoney - Выдать деньги\n/getid - Узнать ID пользователя\n/addbuy - Добавить аккаунт\n/changebuy - Изменить данные об аккаунте\n/deletebuy - Удалить товар+\n/ot - Ответить пользователю',parse_mode='Markdown')
	else:
		bot.send_message(message.chat.id, '*Помощь по командам:*\n\n*Команды для пользователя*\n/profile - Посмотреть свой профиль\n/help - Посмотреть список команд\n/helper - помощник по продаже/покупке\n/buy - Купить аккаунт\n/donate - Пополнить счёт\n/mybuy - Посмотреть список купленных аккаунтов\n/answer - Связаться с помощником',parse_mode='Markdown')

@bot.message_handler(commands=['helper'])
def helper(message):
	try:
		bot.send_message(message.chat.id,'*Помощник по продаже-покупке*\n\nВ продаже-покупке участвуют 3 человека:\n1 - продавец\n2 - покупатель\n3 - лицо, защищающее права покупателя и продавца\n\n*Если вы хотите продать аккаунт, пропишите /guard*\n*В письме укажите:*\nНазвание игры\nХарактеристика аккаунта\nСумма аккаунта\n\n*Если вы хотите приобрести аккаунт, пропишите /buy*'
								'\nВыберете аккаунт из предложенного списка и обратитесь за поддержкой по /guard\n\n*Актуальные вопросы*\n*1.Как пополняется счет?*\nСчет пополняется с помощью платежной системы Qiwi\nДля пополнения счета пропишите /donate\nПри отправке средств обязательно укажите комментарий с вашим ID\nАдминистратор проверит заявку после зачисления средств\nВ течение 2 часов на ваш виртуальный счет поступят средства'
								'\n*2.Как происходит сделка при покупке аккаунта?*\nВся операция происходит с независимым помощником (/guard)\nПомощник отвечает за гарантии честной сделки и защищает пользователей до ее окончания\nЕсли вы купили аккаунт, то обратитесь по адресу /guard\nПропишите информацию о покупке аккаунта\nПосле получения сообщения помощник свяжется с продавцом и покупателем'
								'\nОн отправит данные аккаунта покупателю и сумму покупки продавцу',parse_mode='Markdown')
	except:
		bot.send_message(message.chat.id, f'🚫 Ошибка при выполнении команды. Повторите запрос или пропишите /help! 🚫')

@bot.message_handler(commands=['buy'])
def buy(message):
	try:
		text = '*Список аккаунтов*\n\n'
		for info in cur.execute(f"SELECT * FROM users WHERE id = {message.from_user.id}"):
			for infoshop in cur.execute(f"SELECT * FROM shop"):
				text += f"{infoshop[0]}. {infoshop[1]}\nЦена: {infoshop[2]} \nХарактеристики аккаунта:\n{infoshop[3]}\n"
			rmk = types.InlineKeyboardMarkup()
			item_yes = types.InlineKeyboardButton(text='✅', callback_data='firstbuytovaryes')
			item_no = types.InlineKeyboardButton(text='❌', callback_data='firstbuytovarno')
			rmk.add(item_yes, item_no)
			msg = bot.send_message(message.chat.id, f'{text}*Вы хотите перейти к покупке товара?*',parse_mode='Markdown',reply_markup=rmk)
	except:
		bot.send_message(message.chat.id, f'🚫 Ошибка при выполнении команды. Повторите запрос или пропишите /help! 🚫')

def buy_next(message):
	try:
		if message.text == message.text:
			global tovarid
			tovarid = int(message.text)
			for info in cur.execute(f"SELECT * FROM users WHERE id = {message.from_user.id}"):
				for infoshop in cur.execute(f"SELECT * FROM shop WHERE id = {tovarid}"):
					if info[2] < infoshop[2]:
						bot.send_message(message.chat.id, '*У вас недостаточно средств для приобретения товара!*\n\nЧтобы пополнить счёт, пропишите /donate')
					else:
						rmk = types.InlineKeyboardMarkup()
						item_yes = types.InlineKeyboardButton(text='✅',callback_data='buytovaryes')
						item_no = types.InlineKeyboardButton(text='❌',callback_data='buytovarno')
						rmk.add(item_yes, item_no)
						msg = bot.send_message(message.chat.id, f"Вы подтверждаете покупку товара?",reply_markup=rmk)
	except:
		bot.send_message(message.chat.id, f'🚫 Ошибка при выполнении команды. Повторите запрос или пропишите /help! 🚫')

@bot.callback_query_handler(lambda call: call.data == 'firstbuytovaryes' or call.data == 'firstbuytovarno')
def firstbuy_callback(call):
	try:
		if call.data == 'firstbuytovaryes':
			msg = bot.send_message(call.message.chat.id, f"*Введите ID товара, который хотите купить:*",parse_mode='Markdown')
			bot.register_next_step_handler(msg, buy_next)
		elif call.data == 'firstbuytovarno':
			bot.delete_message(call.message.chat.id, call.message.message_id-0)
			bot.send_message(call.message.chat.id, f"Вы отменили покупку аккаунта")
		bot.answer_callback_query(callback_query_id=call.id)
	except:
		bot.send_message(call.message.chat.id, f'🚫 Ошибка при выполнении команды. Повторите запрос или пропишите /help! 🚫')

@bot.callback_query_handler(lambda call: call.data == 'buytovaryes' or call.data == 'buytovarno')
def buy_callback(call):
	try:
		if call.data == 'buytovaryes':
			for info in cur.execute(f"SELECT * FROM users WHERE id = {call.from_user.id}"):
				for infoshop in cur.execute(f"SELECT * FROM shop WHERE id = {tovarid}"):
					if str(info[0]) not in infoshop[4]:
						cashtovar = int(info[2] - infoshop[2])
						boughttovar = int(info[4] + 1)
						whobuytovarinttostr = str(info[0])
						whobuytovar = str(infoshop[4] + whobuytovarinttostr + ',')
						cur.execute(f"SELECT * FROM users WHERE id = {call.from_user.id}")
						bot.delete_message(call.message.chat.id, call.message.message_id-0)
						bot.send_message(call.message.chat.id, f"✅ Вы успешно купили аккаунт\n\nНазвание игры: {infoshop[1]}\nЦена: {infoshop[2]}\nХарактеристики:\n {infoshop[3]}")
						cur.execute(f"UPDATE users SET cash = {cashtovar} WHERE id = {call.from_user.id}")
						cur.execute(f"UPDATE users SET bought = {boughttovar} WHERE id = {call.from_user.id}")
						cur.execute(f"SELECT * FROM shop WHERE id = {tovarid}")
						cur.execute(f"UPDATE shop SET whobuy = '{whobuytovar}' WHERE id = {tovarid}")
						con.commit()
					else:
						bot.delete_message(call.message.chat.id, call.message.message_id-0)
						bot.send_message(call.message.chat.id, f"*Данный товар уже куплен!*",parse_mode='Markdown')
		elif call.data == 'buytovarno':
			bot.delete_message(call.message.chat.id, call.message.message_id-0)
			bot.send_message(call.message.chat.id, f"*Вы отменили покупку товара!*")
		bot.answer_callback_query(callback_query_id=call.id)
	except:
		bot.send_message(call.message.chat.id, f'🚫 Ошибка при выполнении команды. Повторите запрос или пропишите /help! 🚫')

@bot.message_handler(commands=['donate'])
def donate(message):
	try:
		msg = bot.send_message(message.chat.id, f"*Введите сумму для пополнения:*",parse_mode='Markdown')
		bot.register_next_step_handler(msg, donate_value)
	except:
		bot.send_message(message.chat.id, f'🚫 Ошибка при выполнении команды. Повторите запрос или пропишите /help! 🚫')

@bot.message_handler(commands=['mybuy'])
def mybuy(message):
	try:
		text = '*Список купленных товаров:*\n\n'
		for info in cur.execute(f"SELECT * FROM users WHERE id = {message.from_user.id}"):
			for infoshop in cur.execute(f"SELECT * FROM shop"):
				if str(info[0]) in infoshop[4]:
					text += f"*{infoshop[0]}. {infoshop[1]}*\nТовар: {infoshop[3]}\n\n"
		bot.send_message(message.chat.id,f"{text}",parse_mode='Markdown',disable_web_page_preview=True)
	except:
		bot.send_message(message.chat.id, f'🚫 Ошибка при выполнении команды. Повторите запрос или пропишите /help! 🚫')

@bot.message_handler(commands=['guard'])
def guard(message):
	try:
		msg = bot.send_message(message.chat.id, f"*Введите текст, который хотите отправить помощнику*",parse_mode='Markdown')
		bot.register_next_step_handler(msg, teh_next)
	except:
		bot.send_message(message.chat.id, f'🚫 Ошибка при выполнении команды. Повторите запрос или пропишите /help! 🚫')

def teh_next(message):
	try:
		if message.text == message.text:
			global tehtextbyuser
			global tehnamebyuser
			global tehidbyuser
			tehidbyuser = int(message.from_user.id)
			tehnamebyuser = str(message.from_user.first_name)
			tehtextbyuser = str(message.text)
			rmk = types.InlineKeyboardMarkup()
			item_yes = types.InlineKeyboardButton(text='✉️',callback_data='tehsend')
			item_no = types.InlineKeyboardButton(text='❌',callback_data='tehno')
			rmk.add(item_yes, item_no)
			msg = bot.send_message(message.chat.id, f"Данные об отправке:\n\nТекст для отправки: {tehtextbyuser}\n\nВы действительно хотите отправить это помощнику?",parse_mode='Markdown',reply_markup=rmk)
	except:
		bot.send_message(message.chat.id, f'🚫 Ошибка при выполнении команды. Повторите запрос или пропишите /help! 🚫')

@bot.callback_query_handler(func=lambda call: call.data == 'tehsend' or call.data == 'tehno')
def teh_callback(call):
	try:
		if call.data == 'tehsend':
			for info in cur.execute(f"SELECT * FROM users WHERE id = {call.from_user.id}"):
				bot.delete_message(call.message.chat.id, call.message.message_id-0)
				bot.send_message(call.message.chat.id, f"Ваше сообщение отправлено помощнику, ожидайте ответа.")
				bot.send_message(1942166894, f"Пользователь {tehnamebyuser} отправил сообщение помощнику\n\nID пользователя: {tehidbyuser}\nТекст: {tehtextbyuser}\n\nЧтобы ответить пользователю напишите /answer")
		elif call.data == 'tehno':
			bot.delete_message(call.message.chat.id, call.message.message_id-0)
			bot.send_message(call.message.chat.id, f"Вы отменили отправку сообщения помощнику")
		bot.answer_callback_query(callback_query_id=call.id)
	except:
		bot.send_message(call.message.chat.id, f'🚫 Ошибка при выполнении команды. Повторите запрос или пропишите /help! 🚫')

@bot.message_handler(commands=['viewprofile'])
def viewprofile(message):
	try:
		cur.execute(f"SELECT * FROM users WHERE id = {message.from_user.id}")
		getaccess = cur.fetchone()[3]
		accessquery = 1
		if getaccess < accessquery:
			bot.send_message(message.chat.id, 'У вас нет доступа!')
		else:
			for info in cur.execute(f"SELECT * FROM users WHERE id = {message.from_user.id}"):
				msg = bot.send_message(message.chat.id, f'Введите ID пользователя')
				bot.register_next_step_handler(msg, getprofile_next)
	except:
		bot.send_message(message.chat.id, f'🚫 Ошибка при выполнении команды. Повторите запрос или пропишите /help! 🚫')

def getprofile_next(message):
	try:
		if message.text == message.text:
			getprofileid = message.text
			for info in cur.execute(f"SELECT * FROM users WHERE id = {getprofileid}"):
				if info[3] == 0:
					accessname = 'Пользователь'
				elif info[3] == 1:
					accessname = 'Администратор'
				elif info[3] == 777:
					accessname = 'Разработчик'
				bot.send_message(message.chat.id, f"*Профиль {info[1]}:*\n\n*ID пользователя:* {info[0]}\n*Баланс:* {info[2]} ₽\n*Уровень доступа:* {accessname}\n*Куплено товаров:* {info[4]}",parse_mode='Markdown')
	except:
		bot.send_message(message.chat.id, f'🚫 Ошибка при выполнении команды. Повторите запрос или пропишите /help! 🚫')

@bot.message_handler(commands=['allusers'])
def allusers(message):
	try:
		cur.execute(f"SELECT * FROM users WHERE id = {message.from_user.id}")
		getaccess = cur.fetchone()[3]
		accessquery = 1
		if getaccess < accessquery:
			bot.send_message(message.chat.id, 'У вас нет доступа!')
		else:
			text = '*Список всех пользователей:*\n\n'
			idusernumber = 0
			for info in cur.execute(f"SELECT * FROM users"):
				if info[3] == 0:
					accessname = 'Пользователь'
				elif info[3] == 1:
					accessname = 'Администратор'
				elif info[3] == 777:
					accessname = 'Разработчик'
				idusernumber += 1
				text += f"*{idusernumber}. {info[0]} ({info[1]})*\n*Баланс:* {info[2]} ₽\n*Уровень доступа:* {accessname}\n*Профиль:*" + f" [{info[1]}](tg://user?id="+str(info[0])+")\n\n"
			bot.send_message(message.chat.id, f"{text}",parse_mode='Markdown')
	except:
		bot.send_message(message.chat.id, f'🚫 Ошибка при выполнении команды. Повторите запрос или пропишите /help! 🚫')

@bot.message_handler(commands=['accesslvl'])
def setaccess(message):
	try:
		cur.execute(f"SELECT * FROM users WHERE id = {message.from_user.id}")
		getaccess = cur.fetchone()[3]
		accessquery = 777
		if getaccess < accessquery:
			bot.send_message(message.chat.id, f"У вас нет доступа!")
		else:
			for info in cur.execute(f"SELECT * FROM users WHERE id = {message.from_user.id}"):
				msg = bot.send_message(message.chat.id, 'Введите ID пользователя', parse_mode="Markdown")
				bot.register_next_step_handler(msg, access_user_id_answer)
	except:
		bot.send_message(message.chat.id, f'🚫 Ошибка при выполнении команды. Повторите запрос или пропишите /help! 🚫')
def access_user_id_answer(message):
	try:
		if message.text == message.text:
			global usridaccess
			usridaccess = message.text
			rmk = types.ReplyKeyboardMarkup(resize_keyboard=True)
			rmk.add(types.KeyboardButton('Пользователь'), types.KeyboardButton('Администратор'), types.KeyboardButton('Разработчик'))
			msg = bot.send_message(message.chat.id, 'Какой уровень доступа Вы хотите выдать?:', reply_markup=rmk, parse_mode="Markdown")
			bot.register_next_step_handler(msg, access_user_access_answer)
	except:
		bot.send_message(message.chat.id, f'🚫 Ошибка при выполнении команды. Повторите запрос или пропишите /help! 🚫')

def access_user_access_answer(message):
	try:
		global accessgaved
		global accessgavedname
		rmk = types.InlineKeyboardMarkup()
		access_yes = types.InlineKeyboardButton(text='✅',callback_data='setaccessyes')
		access_no = types.InlineKeyboardButton(text='❌',callback_data='setaccessno')
		rmk.add(access_yes, access_no)
		for info in cur.execute(f"SELECT * FROM users WHERE id = {usridaccess}"):
			if message.text == "Пользователь":
				accessgavedname = "Пользователь"
				accessgaved = 0
			elif message.text == "Администратор":
				accessgavedname = "Администратор"
				accessgaved = 1
			elif message.text == "Разработчик":
				accessgavedname = "Разработчик"
				accessgaved = 777

			bot.send_message(message.chat.id, f'Данные для выдачи:\nID пользователя: {usridaccess} ({info[1]})\nУровень доступа: {message.text}\n\nВерно?', reply_markup=rmk)
	except:
		bot.send_message(message.chat.id, f'🚫 Ошибка при выполнении команды. Повторите запрос или пропишите /help! 🚫')

@bot.callback_query_handler(lambda call: call.data == 'setaccessyes' or call.data == 'setaccessno')
def access_user_gave_access(call):
	try:
		removekeyboard = types.ReplyKeyboardRemove()
		if call.data == 'setaccessyes':
			for info in cur.execute(f"SELECT * FROM users WHERE id = {usridaccess}"):
				cur.execute(f"UPDATE users SET access = {accessgaved} WHERE id = {usridaccess}")
				con.commit()
				bot.delete_message(call.message.chat.id, call.message.message_id-0)
				bot.send_message(call.message.chat.id, f'Пользователю {info[1]} выдан уровень доступа {accessgavedname}', reply_markup=removekeyboard)
		elif call.data == 'setaccessno':
			for info in cur.execute(f"SELECT * FROM users WHERE id = {usridaccess}"):
				bot.delete_message(call.message.chat.id, call.message.message_id-0)
				bot.send_message(call.message.chat.id, f'Вы отменили выдачу уровня доступа {accessgavedname} пользователю {info[1]}', reply_markup=removekeyboard)
		bot.answer_callback_query(callback_query_id=call.id)
	except:
		bot.send_message(message.chat.id, f'🚫 Ошибка при выполнении команды. Повторите запрос или пропишите /help! 🚫')

@bot.message_handler(commands=['givemoney'])
def givemoney(message):
	try:
		cur.execute(f"SELECT * FROM users WHERE id = {message.from_user.id}")
		getaccess = cur.fetchone()[3]
		accessquery = 777
		if getaccess < accessquery:
			bot.send_message(message.chat.id, f"У вас нет доступа!")
		else:
			for info in cur.execute(f"SELECT * FROM users WHERE id = {message.from_user.id}"):
				msg = bot.send_message(message.chat.id, 'Введите ID пользователя:', parse_mode="Markdown")
				bot.register_next_step_handler(msg, rubles_user_id_answer)
	except:
		bot.send_message(message.chat.id, f'🚫 Ошибка при выполнении команды. Повторите запрос или пропишите /help! 🚫')

def rubles_user_id_answer(message):
	try:
		if message.text == message.text:
			global usridrubles
			usridrubles = message.text
			rmk = types.ReplyKeyboardMarkup(resize_keyboard=True)
			rmk.add(types.KeyboardButton('10'), types.KeyboardButton('100'), types.KeyboardButton('1000'), types.KeyboardButton('Другая сумма'))
			msg = bot.send_message(message.chat.id, 'Выберите сумму для выдачи:', reply_markup=rmk, parse_mode="Markdown")
			bot.register_next_step_handler(msg, rubles_user_rubles_answer)
	except:
		bot.send_message(message.chat.id, f'🚫 Ошибка при выполнении команды. Повторите запрос или пропишите /help! 🚫')

def rubles_user_rubles_answer(message):
	try:
		global rublesgavedvalue
		removekeyboard = types.ReplyKeyboardRemove()
		rmk = types.InlineKeyboardMarkup()
		access_yes = types.InlineKeyboardButton(text='✅',callback_data='giverublesyes')
		access_no = types.InlineKeyboardButton(text='❌',callback_data='giverublesno')
		rmk.add(access_yes, access_no)
		for info in cur.execute(f"SELECT * FROM users WHERE id = {usridrubles}"):
			if message.text == '10':
				rublesgavedvalue = 10
				bot.send_message(message.chat.id, f'Данные для выдачи:\nID пользователя: {usridrubles} ({info[1]})\nСумма: {rublesgavedvalue}\n\nВерно?',reply_markup=rmk)
			elif message.text == '100':
				rublesgavedvalue = 100
				bot.send_message(message.chat.id, f'Данные для выдачи:\nID пользователя: {usridrubles} ({info[1]})\nСумма: {rublesgavedvalue}\n\nВерно?',reply_markup=rmk)
			elif message.text == '1000':
				rublesgavedvalue = 1000
				bot.send_message(message.chat.id, f'Данные для выдачи:\nID пользователя: {usridrubles} ({info[1]})\nСумма: {rublesgavedvalue}\n\nВерно?',reply_markup=rmk)
			elif message.text == 'Другая сумма':
				msg = bot.send_message(message.chat.id, f"*Введите сумму для выдачи:*",parse_mode='Markdown',reply_markup=removekeyboard)
				bot.register_next_step_handler(msg, rubles_user_rubles_answer_other)
	except:
		bot.send_message(message.chat.id, f'🚫 Ошибка при выполнении команды. Повторите запрос или пропишите /help! 🚫')

def rubles_user_rubles_answer_other(message):
	try:
		global rublesgavedvalue
		rmk = types.InlineKeyboardMarkup()
		access_yes = types.InlineKeyboardButton(text='✅',callback_data='giverublesyes')
		access_no = types.InlineKeyboardButton(text='❌',callback_data='giverublesno')
		rmk.add(access_yes, access_no)
		for info in cur.execute(f"SELECT * FROM users WHERE id = {usridrubles}"):
			if message.text == message.text:
				rublesgavedvalue = int(message.text)
				bot.send_message(message.chat.id, f'Данные для выдачи:\nID пользователя: {usridrubles} ({info[1]})\nСумма: {rublesgavedvalue}\n\nВерно?',reply_markup=rmk)
	except:
		bot.send_message(message.chat.id, f'🚫 Ошибка при выполнении команды. Повторите запрос или пропишите /help! 🚫')

@bot.callback_query_handler(func=lambda call: call.data == 'giverublesyes' or call.data == 'giverublesno')
def rubles_gave_rubles_user(call):
	try:
		removekeyboard = types.ReplyKeyboardRemove()
		for info in cur.execute(f"SELECT * FROM users WHERE id = {usridrubles}"):
			rubless = int(info[2] + rublesgavedvalue)
			if call.data == 'giverublesyes':
				for info in cur.execute(f"SELECT * FROM users WHERE id = {usridrubles}"):
					cur.execute(f"UPDATE users SET cash = {rubless} WHERE id = {usridrubles}")
					con.commit()
					bot.delete_message(call.message.chat.id, call.message.message_id-0)
					bot.send_message(call.message.chat.id, f'Пользователю {info[1]} выдано {rublesgavedvalue} рублей', reply_markup=removekeyboard)
			elif call.data == 'giverublesno':
				for info in cur.execute(f"SELECT * FROM users WHERE id = {usridrubles}"):
					bot.delete_message(call.message.chat.id, call.message.message_id-0)
					bot.send_message(call.message.chat.id, f'Вы отменили выдачу средств пользователю {info[1]}', reply_markup=removekeyboard)
			bot.answer_callback_query(callback_query_id=call.id)
	except:
		bot.send_message(call.message.chat.id, f'🚫 Ошибка при выполнении команды. Повторите запрос или пропишите /help! 🚫')
@bot.message_handler(commands=['getid'])
def getid(message):
	try:
		cur.execute(f"SELECT * FROM users WHERE id = {message.from_user.id}")
		getaccess = cur.fetchone()[3]
		accessquery = 1
		if getaccess < accessquery:
			bot.send_message(message.chat.id, f"У вас нет доступа!")
		else:
			msg = bot.send_message(message.chat.id, 'Введите никнейм пользователя:')
			bot.register_next_step_handler(msg, next_getiduser_name)
	except:
		bot.send_message(message.chat.id, f'🚫 Ошибка при выполнении команды. Повторите запрос или пропишите /help! 🚫')

def next_getiduser_name(message):
	try:
		if message.text == message.text:
			getusername = message.text
			cur.execute(f"SELECT * FROM users WHERE nick = '{getusername}'")
			result = cur.fetchone()[0]
			bot.send_message(message.chat.id, f'ID пользователя: {result}')
	except:
		bot.send_message(message.chat.id, f'🚫 Ошибка при выполнении команды. Повторите запрос или пропишите /help! 🚫')

@bot.message_handler(commands=['addbuy'])
def addbuy(message):
	try:
		with lock:
			cur.execute(f"SELECT * FROM users WHERE id = {message.from_user.id}")
			getaccess = cur.fetchone()[3]
		if getaccess < 1:
			bot.send_message(message.chat.id, '*У вас нет доступа!*')
		else:
			msg = bot.send_message(message.chat.id, '*Введите ID товара:*',parse_mode='Markdown')
			bot.register_next_step_handler(msg, addbuy_id)
	except:
		bot.send_message(message.chat.id, f'🚫 Ошибка при выполнении команды. Повторите запрос или пропишите /help! 🚫')

def addbuy_id(message):
	try:
		if message.text == message.text:
			global addbuyid
			addbuyid = message.text
			msg = bot.send_message(message.chat.id, '*Введите цену аккаунта:*',parse_mode='Markdown')
			bot.register_next_step_handler(msg, addbuy_price)
	except:
		bot.send_message(message.chat.id, f'🚫 Ошибка при выполнении команды. Повторите запрос или пропишите /help! 🚫')

def addbuy_price(message):
	try:
		if message.text == message.text:
			global addbuyprice
			addbuyprice = message.text
			msg = bot.send_message(message.chat.id, '*Введите название игры:*',parse_mode='Markdown')
			bot.register_next_step_handler(msg, addbuy_name)
	except:
		bot.send_message(message.chat.id, f'🚫 Ошибка при выполнении команды. Повторите запрос или пропишите /help! 🚫')

def addbuy_name(message):
	try:
		if message.text == message.text:
			global addbuyname
			addbuyname = message.text
			msg = bot.send_message(message.chat.id, '*Введите характеристики:*',parse_mode='Markdown')
			bot.register_next_step_handler(msg, addbuy_result)
	except:
		bot.send_message(message.chat.id, f'🚫 Ошибка при выполнении команды. Повторите запрос или пропишите /help! 🚫')

def addbuy_result(message):
	try:
		if message.text == message.text:
			global addbuytovar
			addbuytovar = message.text
			cur.execute(f"SELECT name FROM shop WHERE name = '{addbuyname}'")
			if cur.fetchone() is None:
				cur.execute(f"INSERT INTO shop VALUES ({addbuyid}, '{addbuyname}', {addbuyprice}, '{addbuytovar}', '')")
				con.commit()
				cur.execute(f"SELECT * FROM shop WHERE name = '{addbuyname}'")
				bot.send_message(message.chat.id, f'✅ Вы успешно добавили товар\nID товара: {cur.fetchone()[0]}\nНазвание игры: {addbuyname}\nЦена: {addbuyprice}\nХарактеристики аккаунта: {addbuytovar}')
			else:
				bot.send_message(message.chat.id, f"⛔ Данный товар уже добавлен!")
	except:
		bot.send_message(message.chat.id, f'🚫 Ошибка при выполнении команды. Повторите запрос или пропишите /help! 🚫')


def donate_value(message):
	try:
		if message.text == message.text:
			global donatevalue
			global commentdonate
			global getusername
			global getuserdonateid
			getusername = message.from_user.first_name
			getuserdonateid = message.from_user.id
			cur.execute(f"SELECT * FROM users WHERE id = {message.from_user.id}")
			commentdonate = cur.fetchone()[0]
			donatevalue = int(message.text)
			rmk = types.InlineKeyboardMarkup()
			item_yes = types.InlineKeyboardButton(text='✅',callback_data='donateyes')
			item_no = types.InlineKeyboardButton(text='❌',callback_data='donateno')
			rmk.add(item_yes, item_no)
			global qiwibalancebe
			qiwibalancebe = api.balance
			msg = bot.send_message(message.chat.id, f"Заявка на пополнение средств успешно создана\n\nВы действительно хотите пополнить средства?",parse_mode='Markdown',reply_markup=rmk)
	except:
		bot.send_message(message.chat.id, f'🚫 Ошибка при выполнении команды. Повторите запрос или пропишите /help! 🚫')

def donateyesoplacheno(message):
	try:
		removekeyboard = types.ReplyKeyboardRemove()
		if message.text == '✅ Оплачено':
			bot.send_message(message.chat.id, f"Ваш запрос отправлен администраторам, ожидайте одобрения и выдачи средств.",reply_markup=removekeyboard)
			bot.send_message(1942166894, f"Пользователь {getusername} оплатил заявку на пополнение средств\n\nID пользователя: {getuserdonateid}\nСумма: {donatevalue}₽\nКомментарий: {commentdonate}\n\nБаланс вашего QIWI раньше: {qiwibalancebe}\nБаланс вашего QIWI сейчас: {api.balance}\n\nПерепроверьте верность оплаты затем подтвердите выдачу средств.\nДля выдачи средств напишите: /giverub")
	except:
		bot.send_message(message.chat.id, f'🚫 Ошибка при выполнении команды. Повторите запрос или пропишите /help! 🚫')

@bot.callback_query_handler(lambda call: call.data == 'donateyes' or call.data == 'donateno')
def donate_result(call):
	try:
		removekeyboard = types.ReplyKeyboardRemove()
		rmk = types.ReplyKeyboardMarkup(resize_keyboard=True)
		rmk.add(types.KeyboardButton('✅ Оплачено'))
		if call.data == 'donateyes':
			bot.delete_message(call.message.chat.id, call.message.message_id-0)
			msg = bot.send_message(call.message.chat.id, f"Кошелек для оплаты: +79217038628\nСумма: {donatevalue}₽\nКомментарий: {commentdonate}\n",parse_mode='Markdown',reply_markup=rmk)
			bot.register_next_step_handler(msg, donateyesoplacheno)
		elif call.data == 'donateno':
			bot.send_message(call.message.chat.id, f"Вы отменили заявку на пополнение средств",reply_markup=removekeyboard)
		bot.answer_callback_query(callback_query_id=call.id)
	except:
		bot.send_message(call.message.chat.id, f'🚫 Ошибка при выполнении команды. Повторите запрос или пропишите /help! 🚫')

@bot.message_handler(commands=['changebuy'])
def changebuy(message):
	try:
		accessquery = 1
		with lock:
			cur.execute(f"SELECT * FROM users WHERE id = {message.from_user.id}")
			getaccess = cur.fetchone()[3]
		if getaccess < 1:
			bot.send_message(message.chat.id, 'У вас нет доступа!')
		else:
			rmk = types.InlineKeyboardMarkup()
			item_name = types.InlineKeyboardButton(text='Название игры',callback_data='editbuyname')
			item_price = types.InlineKeyboardButton(text='Цена',callback_data='editbuyprice')
			item_tovar = types.InlineKeyboardButton(text='Характеристики',callback_data='editbuytovar')
			rmk.add(item_name, item_price, item_tovar)
			msg = bot.send_message(message.chat.id, f"Выберите то, что вы хотите изменить:",reply_markup=rmk,parse_mode='Markdown')
	except:
		bot.send_message(message.chat.id, f'🚫 Ошибка при выполнении команды. Повторите запрос или пропишите /help! 🚫')

def editbuy_name(message):
	try:
		if message.text == message.text:
			global editbuynameidtovar
			editbuynameidtovar = int(message.text)
			msg = bot.send_message(message.chat.id, f"*Введите новое название игры:*",parse_mode='Markdown')
			bot.register_next_step_handler(msg, editbuy_name_new_name)
	except:
		bot.send_message(message.chat.id, f'🚫 Ошибка при выполнении команды. Повторите запрос или пропишите /help! 🚫')

def editbuy_name_new_name(message):
	try:
		if message.text == message.text:
			global editbuynametovar
			editbuynametovar = message.text
			for infoshop in cur.execute(f"SELECT * FROM shop WHERE id = {editbuynameidtovar}"):
				rmk = types.InlineKeyboardMarkup()
				item_yes = types.InlineKeyboardButton(text='✅', callback_data='editbuynewnametovaryes')
				item_no = types.InlineKeyboardButton(text='❌', callback_data='editbuynewnametovarno')
				rmk.add(item_yes, item_no)
				msg = bot.send_message(message.chat.id, f"*Новая информация о товаре:*\n\nID товара: {editbuynameidtovar}\nСтарое имя игры: {infoshop[1]}\nНовое имя игры: {editbuynametovar}\n\nВы подтверждаете изменения?",parse_mode='Markdown',reply_markup=rmk)
	except:
		bot.send_message(message.chat.id, f'🚫 Ошибка при выполнении команды. Повторите запрос или пропишите /help! 🚫')

def editbuy_price(message):
	try:
		if message.text == message.text:
			global editbuypriceidtovar
			editbuypriceidtovar = int(message.text)
			msg = bot.send_message(message.chat.id, f"*Введите новую цену товара:*",parse_mode='Markdown')
			bot.register_next_step_handler(msg, editbuy_price_new_price)
	except:
		bot.send_message(message.chat.id, f'🚫 Ошибка при выполнении команды. Повторите запрос или пропишите /help! 🚫')

def editbuy_price_new_price(message):
	try:
		if message.text == message.text:
			global editbuypricetovar
			editbuypricetovar = int(message.text)
			for infoshop in cur.execute(f"SELECT * FROM shop WHERE id = {editbuypriceidtovar}"):
				rmk = types.InlineKeyboardMarkup()
				item_yes = types.InlineKeyboardButton(text='✅', callback_data='editbuynewpricetovaryes')
				item_no = types.InlineKeyboardButton(text='❌', callback_data='editbuynewpricetovarno')
				rmk.add(item_yes, item_no)
				msg = bot.send_message(message.chat.id, f"*Новая информация о товаре:*\n\nID товара: {editbuypriceidtovar}\nСтарая цена: {infoshop[2]}\nНовая цена: {editbuypricetovar}\n\nВы подтверждаете изменения?",parse_mode='Markdown',reply_markup=rmk)
	except:
		bot.send_message(message.chat.id, f'🚫 Ошибка при выполнении команды. Повторите запрос или пропишите /help! 🚫')

def editbuy_tovar(message):
	try:
		if message.text == message.text:
			global editbuytovaridtovar
			editbuytovaridtovar = int(message.text)
			msg = bot.send_message(message.chat.id, f"*Введите новые характеристики аккаунта:*",parse_mode='Markdown')
			bot.register_next_step_handler(msg, editbuy_tovar_new_tovar)
	except:
		bot.send_message(message.chat.id, f'🚫 Ошибка при выполнении команды. Повторите запрос или пропишите /help! 🚫')

def editbuy_tovar_new_tovar(message):
	try:
		if message.text == message.text:
			global editbuytovartovar
			editbuytovartovar = message.text
			for infoshop in cur.execute(f"SELECT * FROM shop WHERE id = {editbuytovaridtovar}"):
				rmk = types.InlineKeyboardMarkup()
				item_yes = types.InlineKeyboardButton(text='✅', callback_data='editbuynewtovartovaryes')
				item_no = types.InlineKeyboardButton(text='❌', callback_data='editbuynewtovartovarno')
				rmk.add(item_yes, item_no)
				msg = bot.send_message(message.chat.id, f"*Новая информация о товаре:*\n\nID товара: {editbuytovaridtovar}\nСтарые характеристики: {infoshop[3]}\nНовые характеристики: {editbuytovartovar}\n\nВы подтверждаете изменения?",parse_mode='Markdown',reply_markup=rmk)
	except:
		bot.send_message(message.chat.id, f'🚫 Ошибка при выполнении команды. Повторите запрос или пропишите /help! 🚫')

@bot.callback_query_handler(lambda call: call.data == 'editbuynewtovartovaryes' or call.data == 'editbuynewtovartovarno')
def editbuy_tovar_new_callback(call):
	try:
		if call.data == 'editbuynewtovartovaryes':
			cur.execute(f"SELECT * FROM shop WHERE id = {editbuytovaridtovar}")
			cur.execute(f"UPDATE shop SET tovar = '{editbuytovartovar}' WHERE id = {editbuytovaridtovar}")
			con.commit()
			bot.delete_message(call.message.chat.id, call.message.message_id-0)
			bot.send_message(call.message.chat.id, f"Вы успешно изменили характеристики аккаунта на {editbuytovartovar}")
		elif call.data == 'editbuynewtovartovarno':
			bot.delete_message(call.message.chat.id, call.message.message_id-0)
			bot.send_message(call.message.chat.id, f"Вы отменили изменение характеристики аккаунта")
		bot.answer_callback_query(callback_query_id=call.id)
	except:
		bot.send_message(call.message.chat.id, f'🚫 Ошибка при выполнении команды. Повторите запрос или пропишите /help! 🚫')

@bot.callback_query_handler(lambda call: call.data == 'editbuynewpricetovaryes' or call.data == 'editbuynewpricetovarno')
def editbuy_price_new_callback(call):
	try:
		if call.data == 'editbuynewpricetovaryes':
			cur.execute(f"SELECT * FROM shop WHERE id = {editbuypriceidtovar}")
			cur.execute(f"UPDATE shop SET price = {editbuypricetovar} WHERE id = {editbuypriceidtovar}")
			con.commit()
			bot.delete_message(call.message.chat.id, call.message.message_id-0)
			bot.send_message(call.message.chat.id, f"Вы успешно изменили цену аккаунта на {editbuypricetovar}")
		elif call.data == 'editbuynewpricetovarno':
			bot.delete_message(call.message.chat.id, call.message.message_id-0)
			bot.send_message(call.message.chat.id, f"Вы отменили изменение цены товара")
		bot.answer_callback_query(callback_query_id=call.id)
	except:
		bot.send_message(call.message.chat.id, f'🚫 Ошибка при выполнении команды. Повторите запрос или пропишите /help! 🚫')
@bot.callback_query_handler(lambda call: call.data == 'editbuynewnametovaryes' or call.data == 'editbuynewnametovarno')
def editbuy_name_new_callback(call):
	try:
		if call.data == 'editbuynewnametovaryes':
			cur.execute(f"SELECT * FROM shop WHERE id = {editbuynameidtovar}")
			cur.execute(f"UPDATE shop SET name = '{editbuynametovar}' WHERE id = {editbuynameidtovar}")
			con.commit()
			bot.delete_message(call.message.chat.id, call.message.message_id-0)
			bot.send_message(call.message.chat.id, f"Вы успешно изменили название игры на {editbuynametovar}")
		elif call.data == 'editbuynewnametovarno':
			bot.delete_message(call.message.chat.id, call.message.message_id-0)
			bot.send_message(call.message.chat.id, f"Вы отменили изменение названия игры")
		bot.answer_callback_query(callback_query_id=call.id)
	except:
		bot.send_message(call.message.chat.id, f'🚫 Ошибка при выполнении команды. Повторите запрос или пропишите /help! 🚫')


@bot.callback_query_handler(lambda call: call.data == 'editbuyname' or call.data == 'editbuyprice' or call.data == 'editbuytovar')
def editbuy_first_callback(call):
	try:
		if call.data == 'editbuyname':
			msg = bot.send_message(call.message.chat.id, f"*Введите ID товара, которому хотите изменить название:*",parse_mode='Markdown')
			bot.register_next_step_handler(msg, editbuy_name)
		elif call.data == 'editbuyprice':
			msg = bot.send_message(call.message.chat.id, f"*Введите ID товара, которому хотите изменить цену:*",parse_mode='Markdown')
			bot.register_next_step_handler(msg, editbuy_price)
		elif call.data == 'editbuytovar':
			msg = bot.send_message(call.message.chat.id, f"*Введите ID товара, которому хотите изменить характеристики:*",parse_mode='Markdown')
			bot.register_next_step_handler(msg, editbuy_tovar)
		bot.answer_callback_query(callback_query_id=call.id)
	except:
		bot.send_message(call.message.chat.id, f'🚫 Ошибка при выполнении команды. Повторите запрос или пропишите /help! 🚫')

@bot.message_handler(commands=['deletebuy'])
def deletebuy(message):
	try:
		accessquery = 1
		with lock:
			cur.execute(f"SELECT * FROM users WHERE id = {message.from_user.id}")
			getaccess = cur.fetchone()[3]
		if getaccess < 1:
			bot.send_message(message.chat.id, 'У вас нет доступа!')
		else:
			msg = bot.send_message(message.chat.id, f"*Введите ID товара, который хотите удалить:*",parse_mode='Markdown')
			bot.register_next_step_handler(msg, removebuy_next)
	except:
		bot.send_message(message.chat.id, f'🚫 Ошибка при выполнении команды. Повторите запрос или пропишите /help! 🚫')

def removebuy_next(message):
	try:
		if message.text == message.text:
			global removeidtovar
			removeidtovar = int(message.text)
			for info in cur.execute(f"SELECT * FROM users WHERE id = {message.from_user.id}"):
				for infoshop in cur.execute(f"SELECT * FROM shop WHERE id = {removeidtovar}"):
					rmk = types.InlineKeyboardMarkup()
					item_yes = types.InlineKeyboardButton(text='✅',callback_data='removebuytovaryes')
					item_no = types.InlineKeyboardButton(text='❌',callback_data='removebuytovarno')
					rmk.add(item_yes, item_no)
					msg = bot.send_message(message.chat.id, f"Данные об удалении:\n\nID товара: {infoshop[0]}\nНазвание игры: {infoshop[1]}\nЦена аккаунта: {infoshop[2]}\nХарактеристики:\n {infoshop[3]}\n\nВы действительно хотите удалить товар?",reply_markup=rmk)
	except:
		bot.send_message(message.chat.id, f'🚫 Ошибка при выполнении команды. Повторите запрос или пропишите /help! 🚫')

@bot.callback_query_handler(lambda call: call.data == 'removebuytovaryes' or call.data == 'removebuytovarno')
def removebuy_callback(call):
	try:
		if call.data == 'removebuytovaryes':
			cur.execute(f"SELECT * FROM shop")
			cur.execute(f"DELETE FROM shop WHERE id = {removeidtovar}")
			bot.delete_message(call.message.chat.id, call.message.message_id-0)
			bot.send_message(call.message.chat.id, f"✅ Вы успешно удалили товар")
			con.commit()
		elif call.data == 'removebuytovarno':
			bot.delete_message(call.message.chat.id, call.message.message_id-0)
			bot.send_message(call.message.chat.id, f"🚫 Вы отменили удаление товара")
		bot.answer_callback_query(callback_query_id=call.id)
	except:
		bot.send_message(call.message.chat.id, f'🚫 Ошибка при выполнении команды. Повторите запрос или пропишите /help! 🚫')

@bot.message_handler(commands=['answer'])
def answer(message):
	try:
		msg = bot.send_message(message.chat.id, f"Введите ID пользователя, которому хотите отправить сообщение:")
		bot.register_next_step_handler(msg, sendmsgtouser_next)
	except:
		bot.send_message(message.chat.id, f'🚫 Ошибка при выполнении команды. Повторите запрос или пропишите /help! 🚫')

def sendmsgtouser_next(message):
	try:
		if message.text == message.text:
			global getsendmsgtouserid
			getsendmsgtouserid = int(message.text)
			msg = bot.send_message(message.chat.id, f"Введите текст, который хотите отправить пользователю:")
			bot.register_next_step_handler(msg, sendmsgtouser_next_text)
	except:
		bot.send_message(message.chat.id, f'🚫 Ошибка при выполнении команды. Повторите запрос или пропишите /help! 🚫')

def sendmsgtouser_next_text(message):
	try:
		if message.text == message.text:
			global getsendmsgtousertext
			getsendmsgtousertext = str(message.text)
			rmk = types.InlineKeyboardMarkup()
			item_yes = types.InlineKeyboardButton(text='✅',callback_data='sendmsgtouseryes')
			item_no = types.InlineKeyboardButton(text='❌',callback_data='sendmsgtouserno')
			rmk.add(item_yes, item_no)
			msg = bot.send_message(message.chat.id, f"Данные об отправке сообщения:\n\nID пользователя: {getsendmsgtouserid}\nТекст для отправки: {getsendmsgtousertext}\n\nОтправить сообщение?",reply_markup=rmk)
	except:
		bot.send_message(message.chat.id, f'🚫 Ошибка при выполнении команды. Повторите запрос или пропишите /help! 🚫')

@bot.callback_query_handler(func=lambda call: call.data == 'sendmsgtouseryes' or call.data == 'sendmsgtouserno')
def sendmsgtouser_callback(call):
	try:
		if call.data == 'sendmsgtouseryes':
			bot.delete_message(call.message.chat.id, call.message.message_id-0)
			bot.send_message(call.message.chat.id, f"Сообщение отправлено!")
			bot.send_message(getsendmsgtouserid, f"*Администратор прислал вам сообщение:*\n\n{getsendmsgtousertext}",parse_mode='Markdown')
		elif call.data == 'sendmsgtouserno':
			bot.delete_message(call.message.chat.id, call.message.message_id-0)
			bot.send_message(call.message.chat.id, f"🚫 | Вы отменили отправку сообщения пользователю")
		bot.answer_callback_query(callback_query_id=call.id)
	except:
		bot.send_message(call.message.chat.id, f'🚫 Ошибка при выполнении команды. Повторите запрос или пропишите /help! 🚫')



bot.polling(none_stop=True,interval=0)