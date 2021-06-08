import logging
import random
import requests
import datetime
import config
import keyboards as kb

from aiogram import Bot, Dispatcher, executor, types
from database import dbase

# log
logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)

db = dbase('db.db')


@dp.message_handler(commands=['start'])
async def welcome(message: types.Message):
    with open('data/welcome_st.tgs', 'rb') as welcoming:
        await message.answer_sticker(welcoming)
    await message.answer("Hi\n I'm Your Personal Bot!", reply_markup=kb.mainMark)


@dp.message_handler(commands=['subscribe'])
async def subscribe(message: types.Message):
    if not db.subscriber_exists(message.from_user.id):
        db.add_subscriber(message.from_user.id)
    else:
        db.update_subscription(message.from_user.id, True)
    await message.answer("Подписка оформлена!")


@dp.message_handler(commands=['unsubscribe'])
async def unsubscribe(message: types.Message):
    if not db.subscriber_exists(message.from_user.id):
        db.add_subscriber(message.from_user.id, False)
        await message.answer("Вы не были подписаны.")
    else:
        db.update_subscription(message.from_user.id, False)
        await message.answer("Вы успешно отписаны.")


@dp.message_handler(commands=['weather'])
async def get_weather(message: types.Message):
    city = message.text.split()[-1]
    weather_smile = {
        "Clear": "Ясно \U00002600",
        "Clouds": "Облачно \U00002601",
        "Rain": "Дождь \U00002614",
        "Drizzle": "Дождь \U00002614",
        "Thunderstorm": "Гроза \U000026A1",
        "Snow": "Снег \U0001F328",
        "Mist": "Туман \U0001F32B",
        "Fog": "Туман \U0001F32B"
    }

    try:
        r = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={config.WEATHER_TOKEN}&units=metric"
        )
        data = r.json()

        town = data["name"]
        cur_weather = data["main"]["temp"]

        weather_description = data["weather"][0]["main"]
        if weather_description in weather_smile:
            wd = weather_smile[weather_description]
        else:
            wd = "Look at window \U000026A0"

        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"]
        wind = data["wind"]["speed"]
        sunrise_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunrise"])
        sunset_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunset"])

        await message.answer(f"***{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}***\n"
                             f"Погода в городе: {town}\nТемпература: {cur_weather}C°\n{wd}\n"
                             f"Влажность: {humidity}%\nВетер: {wind} м/с\nДавление: {pressure} мм.рт.ст\n"
                             f"Восход солнца: {sunrise_timestamp}\nЗакат солнца: {sunset_timestamp}"
                             )
    except Exception:
        await message.reply("Я не знаю такого города...\n Попробуйте ввести заново.")


@dp.message_handler(commands=['help'])
@dp.message_handler(lambda message: message.text and 'Узнать комманды ⤵️' in message.text)
async def help(message: types.Message):
    with open('data/allCommands.txt', 'r', encoding="utf-8") as f:
        text = f.read()
    await message.answer('All commands:\n' + text, reply_markup=kb.mainMark)


@dp.message_handler(commands=['test'])
async def echo(message: types.Message):
    await message.answer("Я работаю, всё хорошо!")


@dp.message_handler(regexp='(^cat[s]?$|puss|^кошк[а,и]?$)')
async def cats(message: types.Message):
    with open('data/cat1.jpg', 'rb') as photo:
        await message.answer_photo(photo, caption='Cats are here 😺')


@dp.message_handler(regexp='(^dog[s]?$|hound|^собак[а,и]?$)')
async def dogs(message: types.Message):
    with open('data/dog1.jpg', 'rb') as photo:
        await message.answer_photo(photo, caption='Dogs are here 🐕')


@dp.message_handler(regexp='(^horse[s]?$|equine|^лошад[ь,и]?$)')
async def horses(message: types.Message):
    with open('data/horse1.jpg', 'rb') as photo:
        await message.answer_photo(photo, caption='Horses are here 🐎')


@dp.message_handler(regexp='(^parrot[s]?$|^попуга[й,и]?$)')
async def parrots(message: types.Message):
    with open('data/parrot1.jpg', 'rb') as photo:
        await message.answer_photo(photo, caption='Parrots are here 🦜')


@dp.message_handler(regexp='(^giraffe[s]?$|^жираф[ы]?$)')
async def giraffes(message: types.Message):
    with open('data/giraffe1.jpg', 'rb') as photo:
        await message.answer_photo(photo, caption='Giraffes are here 🦒')


@dp.message_handler(content_types=['text'])
async def work(message: types.Message):
    if message.text == "Привет 👋":
        await message.answer("👋 Привет 👋", reply_markup=kb.mainMark)
    elif message.text == "Узнать погоду 🌤":
        await message.answer("Введите команду /weather <city> \n***\n"
                             "Город указать на английском языке", reply_markup=kb.mainMark)
    elif message.text == "Случайное число 🎲":
        await message.answer(str(random.randint(0, 100)), reply_markup=kb.mainMark)
    elif message.text == "Случайное животное 👻":
        animals = {
            1: "data/cat1.jpg",
            2: "data/dog1.jpg",
            3: "data/horse1.jpg",
            4: "data/parrot1.jpg",
            5: "data/giraffe1.jpg"
        }
        with open(f'{animals[random.randint(1, 5)]}', 'rb') as photo:
            await message.answer_photo(photo, caption='Random animal is ready', reply_markup=kb.mainMark)
    else:
        await message.reply("Не понимаю, что вы хотите сделать.\n Попробуйте выбрать интересующую кнопку.")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False)
