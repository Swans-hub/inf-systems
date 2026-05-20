#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ======================================================================
# Модуль: main.py
# Назначение: Главный модуль системы управления сотрудниками с разграничением прав
# Автор: Иванов И.И.
# Дата создания: 2025-03-15
# Изменения:
#   2025-03-20  Иванов И.И.  Добавлена проверка пароля в Bcrypt
#   2025-04-10  Петров П.П.   Исправлена ошибка вывода телефона для гостя (было None)
# ======================================================================

# ----------------------------------------------------------------------
# Импорт необходимых библиотек
# ----------------------------------------------------------------------
import sqlite3          # Работа с БД SQLite (встроенная, легковесная)
import bcrypt           # Хэширование паролей (без хранения в открытом виде)
import os               # Проверка существования файла БД
from getpass import getpass  # Скрытый ввод пароля (не отображается на экране)

# ======================================================================
# Глобальные переменные модуля
# ======================================================================
DB_NAME = "company.db"   # Имя файла базы данных (константа, не изменяется)
CURRENT_USER = None      # Текущий авторизованный пользователь (словарь или None)
CURRENT_ROLE = None      # Роль текущего пользователя (строка: "director", "deputy", "secretary", "guest")

# ======================================================================
# Подпрограмма: init_db
# Назначение: Создание таблиц БД, если они не существуют.
# Входные параметры: отсутствуют.
# Выходные параметры: отсутствуют.
# Побочные эффекты: создаёт файл БД и таблицы в нём.
# Условия вызова: должна вызываться один раз при запуске программы.
# ======================================================================
def init_db():
    """
    Инициализация базы данных.
    Создаёт таблицу employees (сотрудники) и users (пользователи с паролями).
    Если БД уже существует, ничего не пересоздаёт.
    """
    # ------------------------------------------------------------------
    # Проверка: если БД уже есть, не пересоздаём таблицы
    # ------------------------------------------------------------------
    if os.path.exists(DB_NAME):
        return

    # ------------------------------------------------------------------
    # Подключение к БД (будет создан новый файл)
    # ------------------------------------------------------------------
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # ------------------------------------------------------------------
    # Таблица сотрудников (хранит личную информацию)
    # Поля:
    #   id - первичный ключ
    #   last_name, first_name, middle_name - ФИО
    #   position - должность
    #   address - адрес (доступен не всем ролям)
    #   phone_work - рабочий телефон (доступен всем)
    #   phone_private - личный телефон (доступен только директору и секретарю)
    # ------------------------------------------------------------------
    cursor.execute('''
        CREATE TABLE employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            last_name TEXT NOT NULL,
            first_name TEXT NOT NULL,
            middle_name TEXT,
            position TEXT,
            address TEXT,
            phone_work TEXT,
            phone_private TEXT
        )
    ''')

    # ------------------------------------------------------------------
    # Таблица пользователей (авторизация)
    # Поля:
    #   username - логин
    #   password_hash - хэш пароля (bcrypt)
    #   role - роль (director, deputy, secretary, guest)
    # ------------------------------------------------------------------
    cursor.execute('''
        CREATE TABLE users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')

    # ------------------------------------------------------------------
    # Добавление тестовых пользователей (пароли потом хэшируются)
    # Пароль для директора: "dir123", для заместителя: "dep456", для секретаря: "sec789"
    # Гость: без пароля
    # ------------------------------------------------------------------
    users_data = [
        ("director", bcrypt.hashpw("dir123".encode(), bcrypt.gensalt()).decode(), "director"),
        ("deputy", bcrypt.hashpw("dep456".encode(), bcrypt.gensalt()).decode(), "deputy"),
        ("secretary", bcrypt.hashpw("sec789".encode(), bcrypt.gensalt()).decode(), "secretary"),
        ("guest", "", "guest")   # Гость — пустой пароль
    ]
    cursor.executemany("INSERT INTO users VALUES (?, ?, ?)", users_data)

    conn.commit()
    conn.close()


# ======================================================================
# Подпрограмма: login
# Назначение: авторизация пользователя по логину и паролю.
# Входные параметры: отсутствуют (ввод с клавиатуры).
# Выходные параметры: bool - True если авторизация успешна, иначе False.
# Условия: глобальные переменные CURRENT_USER и CURRENT_ROLE изменяются.
# Примечание: гостю пароль не требуется.
# ======================================================================
def login():
    """
    Запрашивает логин и пароль, проверяет их по БД.
    Устанавливает глобальные переменные CURRENT_USER и CURRENT_ROLE.
    Возвращает True при успешном входе, иначе False.
    """
    global CURRENT_USER, CURRENT_ROLE

    username = input("Логин: ").strip()
    password = getpass("Пароль: ")

    # ------------------------------------------------------------------
    # Подключение к БД
    # ------------------------------------------------------------------
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # ------------------------------------------------------------------
    # Поиск пользователя по логину
    # ------------------------------------------------------------------
    cursor.execute("SELECT username, password_hash, role FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    # ------------------------------------------------------------------
    # Если пользователь не найден — доступ запрещён
    # ------------------------------------------------------------------
    if user is None:
        print("Ошибка: неверный логин или пароль.")
        return False

    db_username, db_password_hash, db_role = user

    # ------------------------------------------------------------------
    # Проверка пароля (отдельный случай для гостя)
    # ------------------------------------------------------------------
    if db_role == "guest":
        # Гость: пароль не требуется, вход без проверки
        if password == "":
            CURRENT_USER = {"username": db_username, "role": db_role}
            CURRENT_ROLE = db_role
            print("Добро пожаловать, Гость! Доступны только ФИО и должность сотрудников.")
            return True
        else:
            print("Ошибка: для гостя пароль не требуется.")
            return False
    else:
        # Обычные пользователи: проверяем хэш пароля
        if bcrypt.checkpw(password.encode(), db_password_hash.encode()):
            CURRENT_USER = {"username": db_username, "role": db_role}
            CURRENT_ROLE = db_role
            print(f"Добро пожаловать, {db_username}! Ваша роль: {db_role}")
            return True
        else:
            print("Ошибка: неверный логин или пароль.")
            return False


# ======================================================================
# Подпрограмма: view_employees
# Назначение: вывод списка сотрудников с учётом прав роли.
# Входные параметры: отсутствуют.
# Выходные параметры: отсутствуют (вывод на экран).
# Условия: должна вызываться только после успешного login().
# Примечание: Гость видит только ФИО, должность и рабочий телефон.
#             Секретарь и выше — видят адрес и личный телефон.
# ======================================================================
def view_employees():
    """Выводит список сотрудников в зависимости от роли пользователя."""
    global CURRENT_ROLE

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # ------------------------------------------------------------------
    # Разный набор полей в зависимости от роли
    # ------------------------------------------------------------------
    if CURRENT_ROLE == "guest":
        # Гость: только фамилия, имя, отчество, должность, рабочий телефон
        cursor.execute("SELECT last_name, first_name, middle_name, position, phone_work FROM employees")
        rows = cursor.fetchall()
        print("\n--- Список сотрудников (гостевой доступ) ---")
        print("Фамилия Имя Отчество | Должность | Рабочий телефон")
        print("-" * 60)
        for row in rows:
            # ФИО склеиваем из трёх частей
            full_name = f"{row[0]} {row[1]} {row[2] if row[2] else ''}".strip()
            print(f"{full_name:30} | {row[3]:15} | {row[4]}")
    else:
        # Секретарь, заместитель, директор: видят всё
        cursor.execute("SELECT last_name, first_name, middle_name, position, address, phone_work, phone_private FROM employees")
        rows = cursor.fetchall()
        print("\n--- Список сотрудников (полный доступ) ---")
        print("ФИО | Должность | Адрес | Рабочий телефон | Личный телефон")
        print("-" * 80)
        for row in rows:
            full_name = f"{row[0]} {row[1]} {row[2] if row[2] else ''}".strip()
            print(f"{full_name:25} | {row[3]:12} | {row[4]:15} | {row[5]:12} | {row[6]}")

    conn.close()


# ======================================================================
# Подпрограмма: add_employee (только для директора)
# Назначение: добавление нового сотрудника в БД.
# Входные параметры: отсутствуют (ввод с клавиатуры).
# Выходные параметры: отсутствуют.
# Условия: CURRENT_ROLE должна быть "director".
# ======================================================================
def add_employee():
    """Добавляет нового сотрудника. Доступно только директору."""
    if CURRENT_ROLE != "director":
        print("Ошибка: у вас нет прав на добавление сотрудников.")
        return

    print("\n--- Добавление нового сотрудника ---")
    last_name = input("Фамилия: ").strip()
    first_name = input("Имя: ").strip()
    middle_name = input("Отчество: ").strip()
    position = input("Должность: ").strip()
    address = input("Адрес: ").strip()
    phone_work = input("Рабочий телефон: ").strip()
    phone_private = input("Личный телефон: ").strip()

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO employees (last_name, first_name, middle_name, position, address, phone_work, phone_private)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (last_name, first_name, middle_name, position, address, phone_work, phone_private))
    conn.commit()
    conn.close()

    print("Сотрудник успешно добавлен.")


# ======================================================================
# Подпрограмма: delete_employee (только для директора)
# Назначение: удаление сотрудника по ID.
# Входные параметры: отсутствуют (ID вводится пользователем).
# Выходные параметры: отсутствуют.
# ======================================================================
def delete_employee():
    """Удаляет сотрудника по ID. Доступно только директору."""
    if CURRENT_ROLE != "director":
        print("Ошибка: у вас нет прав на удаление сотрудников.")
        return

    try:
        emp_id = int(input("Введите ID сотрудника для удаления: "))
    except ValueError:
        print("Ошибка: ID должен быть числом.")
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM employees WHERE id = ?", (emp_id,))
    conn.commit()
    if cursor.rowcount == 0:
        print("Сотрудник с таким ID не найден.")
    else:
        print("Сотрудник удалён.")
    conn.close()


# ======================================================================
# Подпрограмма: update_employee (для директора и заместителя)
# Назначение: изменение данных сотрудника.
# Входные параметры: отсутствуют.
# Выходные параметры: отсутствуют.
# Примечание: заместитель не может изменять ID и удалять, но может менять другие поля.
# ======================================================================
def update_employee():
    """Изменяет данные сотрудника. Доступно директору (все поля) и заместителю (кроме ID и удаления)."""
    if CURRENT_ROLE not in ["director", "deputy"]:
        print("Ошибка: у вас нет прав на изменение данных сотрудников.")
        return

    try:
        emp_id = int(input("Введите ID сотрудника для изменения: "))
    except ValueError:
        print("Ошибка: ID должен быть числом.")
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Проверяем, существует ли сотрудник
    cursor.execute("SELECT * FROM employees WHERE id = ?", (emp_id,))
    if not cursor.fetchone():
        print("Сотрудник не найден.")
        conn.close()
        return

    print("Введите новые данные (оставьте поле пустым, чтобы не менять):")
    last_name = input("Фамилия: ").strip()
    first_name = input("Имя: ").strip()
    middle_name = input("Отчество: ").strip()
    position = input("Должность: ").strip()
    address = input("Адрес: ").strip()
    phone_work = input("Рабочий телефон: ").strip()
    phone_private = input("Личный телефон: ").strip()

    # Формируем SQL-запрос динамически (только для непустых полей)
    updates = []
    values = []
    if last_name:
        updates.append("last_name = ?")
        values.append(last_name)
    if first_name:
        updates.append("first_name = ?")
        values.append(first_name)
    if middle_name:
        updates.append("middle_name = ?")
        values.append(middle_name)
    if position:
        updates.append("position = ?")
        values.append(position)
    if address:
        updates.append("address = ?")
        values.append(address)
    if phone_work:
        updates.append("phone_work = ?")
        values.append(phone_work)
    if phone_private:
        updates.append("phone_private = ?")
        values.append(phone_private)

    if updates:
        values.append(emp_id)
        query = f"UPDATE employees SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, values)
        conn.commit()
        print("Данные обновлены.")
    else:
        print("Ни одно поле не было изменено.")
    conn.close()


# ======================================================================
# Подпрограмма: main
# Назначение: главное меню программы, маршрутизация по ролям.
# Входные параметры: отсутствуют.
# Выходные параметры: отсутствуют.
# ======================================================================
def main():
    """Основной цикл приложения."""
    init_db()

    print("=== Система управления сотрудниками ===")
    if not login():
        return

    while True:
        print("\n--- Меню ---")
        if CURRENT_ROLE == "director":
            print("1. Просмотр сотрудников")
            print("2. Добавить сотрудника")
            print("3. Редактировать сотрудника")
            print("4. Удалить сотрудника")
            print("5. Выход")
            choice = input("Ваш выбор: ")
            if choice == "1":
                view_employees()
            elif choice == "2":
                add_employee()
            elif choice == "3":
                update_employee()
            elif choice == "4":
                delete_employee()
            elif choice == "5":
                break
            else:
                print("Неверный ввод.")

        elif CURRENT_ROLE == "deputy":
            print("1. Просмотр сотрудников")
            print("2. Редактировать сотрудника")
            print("3. Выход")
            choice = input("Ваш выбор: ")
            if choice == "1":
                view_employees()
            elif choice == "2":
                update_employee()
            elif choice == "3":
                break
            else:
                print("Неверный ввод.")

        elif CURRENT_ROLE == "secretary" or CURRENT_ROLE == "guest":
            print("1. Просмотр сотрудников")
            print("2. Выход")
            choice = input("Ваш выбор: ")
            if choice == "1":
                view_employees()
            elif choice == "2":
                break
            else:
                print("Неверный ввод.")

    print("Программа завершена.")


# ======================================================================
# Точка входа в программу
# ======================================================================
if __name__ == "__main__":
    main()