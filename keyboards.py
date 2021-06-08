from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Одна кнопка
btn_Hello = KeyboardButton("Привет 👋")
btn_Weather = KeyboardButton("Узнать погоду 🌤")
btn_Help = KeyboardButton("Узнать комманды ⤵️")
btn_RandNum = KeyboardButton("Случайное число 🎲")
btn_RandAnim = KeyboardButton("Случайное животное 👻")
btn_Cat = KeyboardButton("Кошка")
btn_Dog = KeyboardButton("Собака")
btn_Horse = KeyboardButton("Лошадь")
btn_Parrot = KeyboardButton("Попугай")
btn_Giraffe = KeyboardButton("Жираф")
btn_Moscow = KeyboardButton("Москва")
btn_SaintP = KeyboardButton("Санкт-Петербург")
btn_AnyTown = KeyboardButton("Другой город")
mainMark = ReplyKeyboardMarkup(resize_keyboard=True).row(btn_Hello, btn_Weather, btn_Help)
mainMark.row(btn_RandNum, btn_RandAnim).row(btn_Cat, btn_Dog, btn_Horse, btn_Parrot, btn_Giraffe)
townSelect = ReplyKeyboardMarkup(resize_keyboard=True).row(btn_Moscow, btn_SaintP).add(btn_AnyTown)
