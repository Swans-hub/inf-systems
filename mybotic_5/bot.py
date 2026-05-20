import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import requests
import xml.etree.ElementTree as ET
import time

TOKEN = "8511765494:AAHP7QhrDwVJC9Gwrh-fO7Foq2_XmkXZFNY"
bot = telebot.TeleBot(TOKEN)

# ===== КЭШ =====
currencies_cache = None
last_update = 0

def get_all_currencies():
    url = "http://www.cbr.ru/scripts/XML_daily.asp"
    currencies = {}

    try:
        response = requests.get(url, timeout=10)
        response.encoding = 'windows-1251'
        root = ET.fromstring(response.text)

        for valute in root.findall('Valute'):
            code = valute.find('CharCode').text
            name = valute.find('Name').text
            value = valute.find('Value').text
            nominal = int(valute.find('Nominal').text)

            rate = float(value.replace(',', '.')) / nominal

            currencies[code] = {
                'name': name,   # ← русское название
                'rate': rate,
                'nominal': nominal
            }

        print(f"✅ Загружено {len(currencies)} валют")
        return currencies

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None


def get_cached_currencies():
    global currencies_cache, last_update

    if currencies_cache is None or time.time() - last_update > 600:
        currencies_cache = get_all_currencies()
        last_update = time.time()
        print("🔄 Курсы обновлены")

    return currencies_cache


# ===== ФОРМАТ КУРСА =====
def format_currency_rate(code, currency):
    rate = currency['rate']
    name = currency['name']
    nominal = currency['nominal']

    if nominal == 1:
        direct = f"1 {code} = {rate:.4f} ₽"
    else:
        direct = f"{nominal} {code} = {rate * nominal:.4f} ₽ | 1 {code} = {rate:.4f} ₽"

    reverse_rate = 1 / rate if rate else 0
    reverse = f"1 ₽ = {reverse_rate:.6f} {code}"

    return f"💱 {code} ({name})\n{direct}\n{reverse}"


def format_all_rates(currencies):
    if not currencies:
        return "❌ Не удалось получить курсы валют"

    message = "🏦 Курсы валют ЦБ РФ\n\n"

    for code in sorted(currencies.keys()):
        curr = currencies[code]
        message += f"• {code} ({curr['name']}): {curr['rate']:.4f} ₽\n"

    return message


# ===== КЛАВИАТУРА =====
def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("📊 Все курсы", "🔍 Валюта")
    keyboard.add("🇷🇺 1 рубль", "💰 Конвертер")
    return keyboard


# ===== КОМАНДЫ =====
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "🌍 Привет! Я бот курсов валют\n\n"
        "Теперь показываю валюты с названиями 😎\n\n"
        "Используй кнопки ниже 👇",
        reply_markup=get_main_keyboard()
    )


@bot.message_handler(commands=['rate'])
def rate_command(message):
    parts = message.text.split()

    if len(parts) != 2:
        bot.reply_to(message, "Пример: /rate USD")
        return

    code = parts[1].upper()
    currencies = get_cached_currencies()

    if currencies and code in currencies:
        text = format_currency_rate(code, currencies[code])
        bot.reply_to(message, text)
    else:
        bot.reply_to(message, "❌ Валюта не найдена")


@bot.message_handler(commands=['convert'])
def convert_currency(message):
    try:
        parts = message.text.split()

        if len(parts) != 3:
            bot.reply_to(message, "Пример: /convert 100 USD")
            return

        amount = float(parts[1])
        code = parts[2].upper()

        currencies = get_cached_currencies()

        if code not in currencies:
            bot.reply_to(message, "❌ Валюта не найдена")
            return

        rate = currencies[code]['rate']
        rub = amount * rate

        name = currencies[code]['name']

        bot.reply_to(message, f"💰 {amount} {code} ({name}) = {rub:.2f} ₽")

    except:
        bot.reply_to(message, "❌ Ошибка. Пример: /convert 100 USD")


# ===== КНОПКИ =====
@bot.message_handler(func=lambda m: m.text == "📊 Все курсы")
def all_rates(message):
    currencies = get_cached_currencies()
    text = format_all_rates(currencies)
    bot.send_message(message.chat.id, text)


@bot.message_handler(func=lambda m: m.text == "🔍 Валюта")
def choose_currency(message):
    bot.send_message(message.chat.id, "Напиши код валюты, например: USD")


@bot.message_handler(func=lambda m: m.text == "🇷🇺 1 рубль")
def ruble_rates(message):
    currencies = get_cached_currencies()

    text = "🇷🇺 1 рубль в валютах:\n\n"

    for code in ["USD", "EUR", "CNY", "GBP"]:
        if code in currencies:
            rate = currencies[code]['rate']
            reverse = 1 / rate if rate else 0
            name = currencies[code]['name']

            text += f"• {code} ({name}): {reverse:.6f}\n"

    bot.send_message(message.chat.id, text)


@bot.message_handler(func=lambda m: m.text == "💰 Конвертер")
def converter_hint(message):
    bot.send_message(message.chat.id, "Введи: /convert 100 USD")


# ===== БЫСТРЫЙ ВВОД ВАЛЮТЫ =====
@bot.message_handler(func=lambda m: len(m.text) == 3)
def quick_currency(message):
    code = message.text.upper()
    currencies = get_cached_currencies()

    if currencies and code in currencies:
        text = format_currency_rate(code, currencies[code])
        bot.send_message(message.chat.id, text)


# ===== ЗАПУСК =====
if __name__ == "__main__":
    print("🚀 Бот запущен")
    bot.infinity_polling()