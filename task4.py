import datetime
from os.path import isfile, getsize
from os import remove, listdir

now = datetime.datetime.now()


def build_note(note_name, note_text):
    with open(note_name, "w") as new_note:
        new_note.write(note_text + "\n" + "\n" + str(now.strftime("%d-%m-%Y %H:%M")))
    print(f'Заметка {note_name} успешно создана {str(now.strftime("%d-%m-%Y %H:%M"))}')
    with open('note_log.txt', 'a') as log:
        log.writelines(f'Заметка {note_name} успешно создана {str(now.strftime("%d-%m-%Y %H:%M"))}' + '\n')


def edit_note():
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


def create_note():
    note_name = input("Введите название заметки:")
    note_text = input("Напишите заметку:")
    build_note(note_name, note_text)


def read_note():
    note_for_read = input("Введите название заметки для просмотра:")
    if isfile(note_for_read):
        with open(note_for_read, "r") as note:
            print('Содержимое заметки:%s%s' % ('\n', note.read()))
    else:
        print(f'Файла с названием {note_for_read} не имеется в списке заметок')


def read_log():
    with open("note_log.txt", "r") as log:
        print(f'Журнал действий: \n{log.read()}')


def delete_note():
    note_for_delete = input("Введите название заметки для удаления:")
    if isfile(note_for_delete):
        remove(note_for_delete)
        print(f'Заметка {note_for_delete} успешно удалена')
        with open('note_log.txt', 'a') as log:
            log.writelines(f'Заметка {note_for_delete} успешно удалена {str(now.strftime("%d-%m-%Y %H:%M"))}' + '\n')
    else:
        print(f'Файла с названием {note_for_delete} не имеется в списке заметок')

def display_notes():
    notes_list = [note for note in listdir() if note.endswith(".txt")]
    reversed_notes_list = sorted(notes_list, key=lambda x: os.stat(x).st_size, reverse=True)
    for note in reversed_notes_list:
        with open(note, "r") as note_for_read:
            print(f'Название заметки: {note} \n Содержимое заметки: {note_for_read.read()} \n Окончание заметки \n')

def main():
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
            display_notes()
        else:
            print('Выход из Заметок')
            return False

main()


