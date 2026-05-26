import telebot
import math
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8788259309:AAH2Y4LeUEgLB3v_MSq0XRqHo5gcZL8s-5A"
# import os
# os.environ['HTTP_PROXY'] = 'socks5://127.0.0.1:10808'
# os.environ['HTTPS_PROXY'] = 'socks5://127.0.0.1:10808'

bot = telebot.TeleBot(TOKEN)

def f_sqrt(x): return math.sqrt(x)
def f_inv(x): return 1 / x
def f_exp(x): return math.exp(x)

FUNCTIONS = {
    '1': ('√x', f_sqrt, 'x ≥ 0'),   # добавили условие ОДЗ
    '2': ('1/x', f_inv, 'x ≠ 0'),
    '3': ('e^x', f_exp, 'x любое'),
}

user_funcs = {}

def get_func_keyboard():
    kb = InlineKeyboardMarkup(row_width=3)
    kb.add(
        InlineKeyboardButton("1️⃣ √x", callback_data="func_1"),
        InlineKeyboardButton("2️⃣ 1/x", callback_data="func_2"),
        InlineKeyboardButton("3️⃣ e^x", callback_data="func_3")
    )
    kb.add(InlineKeyboardButton("❌ Отмена", callback_data="cancel"))
    return kb

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user_funcs[chat_id] = []
    bot.send_message(
        chat_id,
        "🧮 *Калькулятор композиции функций*\n\n"
        "Вычисляю: `F₁(F₂(F₃(x)))`\n\n"
        "⚠️ *ОДЗ:*\n"
        "• √x — x ≥ 0\n"
        "• 1/x — x ≠ 0\n\n"
        "Выбери *первую* функцию (F₁):",
        parse_mode='Markdown',
        reply_markup=get_func_keyboard()
    )

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    data = call.data

    if data == "cancel":
        bot.edit_message_text("❌ Отменено. Напиши /start заново.", chat_id, call.message.message_id)
        bot.answer_callback_query(call.id)
        if chat_id in user_funcs:
            del user_funcs[chat_id]
        return

    if data.startswith("func_"):
        func_num = data.split("_")[1]
        if chat_id not in user_funcs:
            bot.answer_callback_query(call.id, "Сначала напиши /start", show_alert=True)
            return

        selected = user_funcs[chat_id]
        selected.append(func_num)

        if len(selected) == 1:
            bot.edit_message_text(
                f"✅ Выбрана первая функция: {FUNCTIONS[func_num][0]}\n"
                f"   ОДЗ: {FUNCTIONS[func_num][2]}\n\n"
                f"Теперь выбери *вторую* функцию (F₂):",
                chat_id=chat_id,
                message_id=call.message.message_id,
                parse_mode='Markdown',
                reply_markup=get_func_keyboard()
            )
        elif len(selected) == 2:
            bot.edit_message_text(
                f"✅ Выбрана вторая функция: {FUNCTIONS[func_num][0]}\n"
                f"   ОДЗ: {FUNCTIONS[func_num][2]}\n\n"
                f"Теперь выбери *третью* функцию (F₃):",
                chat_id=chat_id,
                message_id=call.message.message_id,
                parse_mode='Markdown',
                reply_markup=get_func_keyboard()
            )
        elif len(selected) == 3:
            f1, f2, f3 = selected
            formula = f"{FUNCTIONS[f1][0]}({FUNCTIONS[f2][0]}({FUNCTIONS[f3][0]}(x)))"
            bot.edit_message_text(
                f"✅ Композиция: `{formula}`\n\n"
                f"Теперь введи число *x* (с учётом ОДЗ):",
                chat_id=chat_id,
                message_id=call.message.message_id,
                parse_mode='Markdown'
            )
            bot.register_next_step_handler_by_chat_id(chat_id, process_x)
        bot.answer_callback_query(call.id)

def process_x(message):
    chat_id = message.chat.id
    if chat_id not in user_funcs:
        bot.send_message(chat_id, "Напиши /start")
        return

    try:
        x = float(message.text.strip())
        f1_code, f2_code, f3_code = user_funcs[chat_id]
        f1 = FUNCTIONS[f1_code][1]
        f2 = FUNCTIONS[f2_code][1]
        f3 = FUNCTIONS[f3_code][1]

        # ----- Проверка ОДЗ для x (первый шаг) -----
        if f3_code == '1' and x < 0:
            bot.send_message(chat_id, "❌ Ошибка ОДЗ: для √x нужен x ≥ 0")
            del user_funcs[chat_id]
            return
        if f3_code == '2' and x == 0:
            bot.send_message(chat_id, "❌ Ошибка ОДЗ: для 1/x нужен x ≠ 0")
            del user_funcs[chat_id]
            return

        step1 = f3(x)

        # ----- Проверка ОДЗ для step1 (второй шаг) -----
        if f2_code == '1' and step1 < 0:
            bot.send_message(chat_id, f"❌ Ошибка ОДЗ: результат F₃(x) = {step1} < 0, а для √x нужен неотрицательный аргумент")
            del user_funcs[chat_id]
            return
        if f2_code == '2' and step1 == 0:
            bot.send_message(chat_id, f"❌ Ошибка ОДЗ: результат F₃(x) = {step1} = 0, а для 1/x нужен ненулевой аргумент")
            del user_funcs[chat_id]
            return

        step2 = f2(step1)

        # ----- Проверка ОДЗ для step2 (третий шаг) -----
        if f1_code == '1' and step2 < 0:
            bot.send_message(chat_id, f"❌ Ошибка ОДЗ: результат F₂(F₃(x)) = {step2} < 0, а для √x нужен неотрицательный аргумент")
            del user_funcs[chat_id]
            return
        if f1_code == '2' and step2 == 0:
            bot.send_message(chat_id, f"❌ Ошибка ОДЗ: результат F₂(F₃(x)) = {step2} = 0, а для 1/x нужен ненулевой аргумент")
            del user_funcs[chat_id]
            return

        step3 = f1(step2)

        bot.send_message(
            chat_id,
            f"📊 *Результат*\n\n"
            f"x = {x}\n"
            f"F₃(x) = {step1}\n"
            f"F₂(F₃(x)) = {step2}\n"
            f"F₁(F₂(F₃(x))) = {step3}\n\n"
            f"✨ **Ответ:** {step3} ✨\n\n"
            f"Напиши /start для новой композиции.",
            parse_mode='Markdown'
        )

    except ValueError:
        bot.send_message(chat_id, "❌ Введи ЧИСЛО!")
    except Exception as e:
        bot.send_message(chat_id, f"❌ Ошибка: {e}")
    finally:
        if chat_id in user_funcs:
            del user_funcs[chat_id]

@bot.message_handler(func=lambda m: True)
def unknown(message):
    bot.send_message(message.chat.id, "Напиши /start", reply_markup=telebot.types.ReplyKeyboardRemove())

if __name__ == "__main__":
    print("✅ Бот запущен (ОДЗ включена)")
    bot.infinity_polling()