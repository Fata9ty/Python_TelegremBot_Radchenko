import datetime
from os.path import isfile, getsize
from os import remove, listdir
import os
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from secrets import API_TOKEN
import asyncio

updater = Updater(token=API_TOKEN)

now = datetime.datetime.now()


def build_note(note_name, note_text):
    try:
        with open(note_name, "w") as new_note:
            new_note.write(note_text)
        print(f'Заметка {note_name} успешно создана {str(now.strftime("%d-%m-%Y %H:%M"))}')
    except:
        print("Произошла ошибка в функции build_note.")


def edit_note(note_for_edit, new_text):
    try:
        note_for_edit = input("Введите название заметки для изменения:")
        if isfile(note_for_edit):
            with open(note_for_edit, "r") as note:
                print('Содержимое заметки:%s%s' % ('\n', note.read()))
        else:
            print(f'Файла с названием {note_for_edit} не имеется в списке заметок')
            return
        new_text = input("Введите новый текст заметки:")
        with open(note_for_edit, "w") as edit_note:
            edit_note.write(new_text + "\n" + "\n" + str(now.strftime("%d-%m-%Y %H:%M")))
        with open('note_log.txt', 'a') as log:
            log.writelines(f'Заметка {note_for_edit} успешно изменена {str(now.strftime("%d-%m-%Y %H:%M"))}' + '\n')
    except:
        print("Произошла ошибка в функции edit_note.")

def edit_note_handler(update, context):
    try:
        new_text = update.message.text
        note_for_edit = update.message.chat_id
        edit_note(new_text, note_for_edit)
        context.bot.send_message(chat_id=update.message.chat_id, text=f"Заметка {note_for_edit} изменена.")
    except:
        context.bot.send_message(chat_id=update.message.chat_id, text="Произошла ошибка.")

updater.dispatcher.add_handler(CommandHandler('edit', edit_note_handler))

def create_note(note_name, note_text):
    try:
        note_name = input("Введите название заметки:")
        note_text = input("Напишите заметку:")
        build_note(note_name, note_text)
    except:
        print("Произошла ошибка в функции create_note.")

def create_note_handler(update, context):
    try:
        note_name = update.message.chat_id
        note_text = update.message.text
        create_note(note_name, note_text)
        context.bot.send_message(chat_id=update.message.chat_id, text=f"Заметка {note_name} создана.")
    except:
        context.bot.send_message(chat_id=update.message.chat_id, text="Произошла ошибка.")

updater.dispatcher.add_handler(CommandHandler('create', create_note_handler))

def read_note(note_for_read):
    try:
        note_for_read = input("Введите название заметки для просмотра:")
        if isfile(note_for_read):
            with open(note_for_read, "r") as note:
                print('Содержимое заметки:%s%s' % ('\n', note.read()))
        else:
            print(f'Файла с названием {note_for_read} не имеется в списке заметок')
    except:
        print("Произошла ошибка в функции read_note.")

def read_note_handler(update, context):
    try:
        note_for_read = update.message.chat_id
        read_note(note_for_read)
    except:
        context.bot.send_message(chat_id=update.message.chat_id, text="Произошла ошибка.")

updater.dispatcher.add_handler(CommandHandler('read', read_note_handler))

def read_log():
    try:
        with open("note_log.txt", "r") as log:
            print(f'Журнал действий: \n{log.read()}')
    except:
        print("Произошла ошибка в функции read_log.")

def read_log_handler(update, context):
    try:
        read_log()
    except:
        context.bot.send_message(chat_id=update.message.chat_id, text="Произошла ошибка.")

updater.dispatcher.add_handler(CommandHandler('read_log', read_log_handler))

def delete_note_handler(update, context):
    try:
        note_for_delete = update.message.chat_id
        delete_note(note_for_delete)
        context.bot.send_message(chat_id=update.message.chat_id, text=f"Заметка {note_for_delete} удалена.")
    except:
        context.bot.send_message(chat_id=update.message.chat_id, text="Произошла ошибка.")

updater.dispatcher.add_handler(CommandHandler('delete', delete_note_handler))

def delete_note(note_for_delete):
    try:
        note_for_delete = input("Введите название заметки для удаления:")
        if isfile(note_for_delete):
            remove(note_for_delete)
            print(f'Заметка {note_for_delete} успешно удалена')
            with open('note_log.txt', 'a') as log:
                log.writelines(f'Заметка {note_for_delete} успешно удалена {str(now.strftime("%d-%m-%Y %H:%M"))}' + '\n')
        else:
            print(f'Файла с названием {note_for_delete} не имеется в списке заметок')
    except:
        print("Произошла ошибка в функции delete_note.")


def display_sorted_notes_handler(update, context):
    try:
        display_sorted_notes()
    except:
        context.bot.send_message(chat_id=update.message.chat_id, text="Произошла ошибка.")

updater.dispatcher.add_handler(CommandHandler('display', display_sorted_notes_handler))

def display_sorted_notes():
    try:
        notes_unsorted = [note for note in listdir() if note.endswith(".txt")]
        notes_sorted = sorted(notes_unsorted,
                              key=lambda x: os.stat(x).st_size)
        for note in notes_sorted:
            with open(note, "r") as note_for_read:
                print(f'Название заметки: {note} \n Содержимое заметки: {note_for_read.read()} \n Окончание заметки \n')
    except:
        print("Произошла ошибка в функции display_sorted_notes.")



updater.start_polling()

"""def main():
    try:
        while True:
            print('Добро пожаловать в Заметки. Введите номер пункта меню для навигации')
            navigation = input('Создать заметку - 1, Прочитать заметку - 2, Обновить заметку - 3, Удалить заметку - 4, '
                               'Посмотреть журнал - 5, Отобразить заметки - 6:')
            if navigation == '1':
                create_note()
            elif navigation == '2':
                read_note()
            elif navigation == '3':
                edit_note()
            elif navigation == '4':
                delete_note()
            elif navigation == '5':
                read_log()
            elif navigation == '6':
                display_sorted_notes()
            else:
                print('Выход из Заметок')
                return False
    except:
        print("Произошла ошибка в функции main.")

main()"""
