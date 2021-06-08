import logging #нужно, чтобы записывать логи
import random #нужно, чтобы получать рандомное число
import requests #библиотека для создания запросов на сайт
import datetime #нужно, чтобы преобразовать формат записи даты и времени
import config #импортируем наши токены на бота и аккаунта на сайте погоды
import keyboards as kb #импортируем наши кнопки

from aiogram import Bot, Dispatcher, executor, types
from database import dbase #импортируем класс, с объявленными нами методами

# log
logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.TOKEN) #передаём боту
dp = Dispatcher(bot)

db = dbase('db.db') #подключаемся к бд через init


@dp.message_handler(commands=['start']) #первая команда при работе с ботом
async def welcome(message: types.Message):
    if not db.subscriber_exists(message.from_user.id): #проверяем id юзера на нахождение в нашей таблице subscriptions
        db.add_subscriber(message.from_user.id) #если пользователя нет, то добавляем его
    with open('data/welcome_st.tgs', 'rb') as welcoming: #записываем наш приветственный стикер в файл
        await message.answer_sticker(welcoming) #отсылаем его пользователю
    await message.answer("Hi\n I'm Your Personal Bot!", reply_markup=kb.mainMark) #представляемся и показываем кнопки для работы с ботом


@dp.message_handler(commands=['subscribe']) #если задействована команда подписаться
async def subscribe(message: types.Message):
    if not db.subscriber_exists(message.from_user.id):
        db.add_subscriber(message.from_user.id)
    else:
        db.update_subscription(message.from_user.id, True) #если пользователь есть в базе, то вкллючаем ему статус подписки
    await message.answer("Подписка оформлена!") #выводим сообщение


@dp.message_handler(commands=['unsubscribe']) #если задействована команда отписаться
async def unsubscribe(message: types.Message):
    if not db.subscriber_exists(message.from_user.id):
        db.add_subscriber(message.from_user.id, False)
        await message.answer("Вы не были подписаны.") #выводим сообщение
    else:
        db.update_subscription(message.from_user.id, False)
        await message.answer("Вы успешно отписаны.")


@dp.message_handler(commands=['weather']) #если задействована команда узнать погоду
async def get_weather(message: types.Message):
    city = message.text.split()[-1] #так как команда у нас состоит из двух слов, нам надо вытащить город
    weather_smile = { #Находим подходящий смайлик, смотрим его номер в Юникоде и создаём словарь
        "Clear": "Ясно \U00002600", #ключ мы вытащили со страницы, а значение будем использовать при выводе информации
        "Clouds": "Облачно \U00002601",
        "Rain": "Дождь \U00002614",
        "Drizzle": "Дождь \U00002614",
        "Thunderstorm": "Гроза \U000026A1",
        "Snow": "Снег \U0001F328",
        "Mist": "Туман \U0001F32B",
        "Fog": "Туман \U0001F32B"
    }

    try:
        r = requests.get( #делаем запрос на сайт, подставляем интересующий нас город и токен с акаунта
            f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={config.WEATHER_TOKEN}&units=metric"
        )
        data = r.json() #записываем данные в файл

        town = data["name"] #вытаскиваем по ключу название города
        cur_weather = data["main"]["temp"] #записываем температуру

        weather_description = data["weather"][0]["main"] #записываем описание погоды
        if weather_description in weather_smile: #проверяем, есть ли данное описние погоды у нас в словаре
            wd = weather_smile[weather_description] #записываем перевод и изображение
        else:
            wd = "Look at window \U000026A0" #я брал не все типы погоды с сайта, поэтому некоторые надо будет обрабатывать так
                                             #например, отсутствует торнадо и песчаная буря
        humidity = data["main"]["humidity"] #записываем влажность воздуха
        pressure = data["main"]["pressure"] #записываем давление
        wind = data["wind"]["speed"] #записываем скорость ветра
        sunrise_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunrise"]) #записываем время восхода солнца
        sunset_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunset"]) #записываем время захода солнца

        await message.answer(f"***{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}***\n" #сформировали вывод
                             f"Погода в городе: {town}\nТемпература: {cur_weather}C°\n{wd}\n"
                             f"Влажность: {humidity}%\nВетер: {wind} м/с\nДавление: {pressure} мм.рт.ст\n"
                             f"Восход солнца: {sunrise_timestamp}\nЗакат солнца: {sunset_timestamp}"
                             )
    except Exception:
        await message.reply("Я не знаю такого города...\n Попробуйте ввести заново.") #обработка ошибок, скорее всего появятся, если не так ввести название города


@dp.message_handler(commands=['help']) #если задействована команда вызова помощи
@dp.message_handler(lambda message: message.text and 'Узнать команды ⤵️' in message.text) #если команда вызвана через кнопку
async def help(message: types.Message):
    with open('data/allCommands.txt', 'r', encoding="utf-8") as f: #считываем информацию из файла, utf-8 чтобы читался русский язык
        text = f.read()
    await message.answer('All commands:\n' + text, reply_markup=kb.mainMark)


@dp.message_handler(commands=['test']) #если задействована команда теста
async def echo(message: types.Message):
    await message.answer("Я работаю, всё хорошо!")


@dp.message_handler(regexp='(^cat[s]?$|puss|^кошк[а,и]?$)') #если задействована команда вывода изображения кошки
async def cats(message: types.Message):
    with open('data/cat1.jpg', 'rb') as photo:
        await message.answer_photo(photo, caption='Cats are here 😺') #возвращаем картинку с подписью


@dp.message_handler(regexp='(^dog[s]?$|hound|^собак[а,и]?$)') #если задействована команда вывода изображения собаки
async def dogs(message: types.Message):
    with open('data/dog1.jpg', 'rb') as photo:
        await message.answer_photo(photo, caption='Dogs are here 🐕') #возвращаем картинку с подписью


@dp.message_handler(regexp='(^horse[s]?$|equine|^лошад[ь,и]?$)') #если задействована команда вывода изображения лошади
async def horses(message: types.Message):
    with open('data/horse1.jpg', 'rb') as photo:
        await message.answer_photo(photo, caption='Horses are here 🐎') #возвращаем картинку с подписью


@dp.message_handler(regexp='(^parrot[s]?$|^попуга[й,и]?$)') #если задействована команда вывода изображения попугая
async def parrots(message: types.Message):
    with open('data/parrot1.jpg', 'rb') as photo:
        await message.answer_photo(photo, caption='Parrots are here 🦜') #возвращаем картинку с подписью


@dp.message_handler(regexp='(^giraffe[s]?$|^жираф[ы]?$)') #если задействована команда вывода изображения жирафа
async def giraffes(message: types.Message):
    with open('data/giraffe1.jpg', 'rb') as photo:
        await message.answer_photo(photo, caption='Giraffes are here 🦒') #возвращаем картинку с подписью


@dp.message_handler(content_types=['text'])  #если был введён текст, который не отработал раньше
async def work(message: types.Message):
    if message.text == "Привет 👋":
        await message.answer("👋 Привет 👋", reply_markup=kb.mainMark)
    elif message.text == "Узнать погоду 🌤":
        await message.answer("Введите команду /weather <city> \n***\n"
                             "Город указать на английском языке", reply_markup=kb.mainMark)
    elif message.text == "Случайное число 🎲":
        await message.answer(str(random.randint(0, 100)), reply_markup=kb.mainMark) #выводим случайное число с 0 до 100
    elif message.text == "Случайное животное 👻":
        animals = { #сделаем словарь, в качестве ключа сделали число, чтобы было легко потом вызвать функцию random
            1: "data/cat1.jpg",
            2: "data/dog1.jpg",
            3: "data/horse1.jpg",
            4: "data/parrot1.jpg",
            5: "data/giraffe1.jpg"
        }
        with open(f'{animals[random.randint(1, 5)]}', 'rb') as photo: #открываем 1 из 5 файлов на бинарное считывание
            await message.answer_photo(photo, caption='Random animal is ready', reply_markup=kb.mainMark)
    else:
        await message.reply("Не понимаю, что вы хотите сделать.\n Попробуйте выбрать интересующую кнопку.")
        #если полученный текст никуда не подошёл


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False)
