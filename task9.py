import logging
import re
from secrets import TOKEN
import datetime
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler


now = datetime.datetime.now()

class Calendar:
    def __init__(self):
        self.events = {}


    def create_event(
            self,
            event_name,
            event_date,
            event_time,
            event_details):
        try:
            event_id = len(self.events) + 1
            event = {
                "id": event_id,
                "name": event_name,
                "date": event_date,
                "time": event_time,
                "details": event_details   }
            self.events[event_id] = event
            return event_id
        except:
            print("Произошла ошибка в функции create_event.")

    def edit_event(self, event_id, event_name, event_date, event_time, event_details):
        try:
            event = self.events[event_id]
            event = {
                "id": event_id,
                "name": event_name,
                "date": event_date,
                "time": event_time,
                "details": event_details
            }
            self.events[event_id] = event
            return event_id
        except:
            print("Произошла ошибка в функции edit_event.")

    def delete_event(self, event_id):
        try:
            del self.events[event_id]
        except:
            print("Произошла ошибка в функции delete_event.")


calendar = Calendar()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

(SET_EVENT, SET_NAME, SET_DATE, SET_TIME, SET_DETAILS, EDIT_EVENT, EDIT_NAME, EDIT_DATE, EDIT_TIME,
 EDIT_DETAILS, DELETE) = map(chr, range(11))
END = ConversationHandler.END

def start(update, context):
    try:
        reply_markup = ReplyKeyboardMarkup([['/set', '/list'], ['/edit', '/delete']])
        update.message.reply_text("Что вы намереваетесь сделать?", reply_markup=reply_markup)
    except:
        print("Произошла ошибка в функции start.")

def set_event(update, context):
    try:
        update.message.reply_text("Введите название события")
        return SET_NAME
    except:
        print("Произошла ошибка в функции set_event.")

def name(update, context):
    try:
        context.user_data['name'] = update.message.text
        update.message.reply_text("Введите описание события")
        return SET_DETAILS
    except:
        print("Произошла ошибка в функции name.")

def details(update, context):
    try:
        context.user_data['details'] = update.message.text
        update.message.reply_text("Введите дату в формате ДД-ММ-ГГГГ")
        return SET_DATE
    except:
        print("Произошла ошибка в функции details.")

def date_question(update, context):
    try:
        user_input = update.message.text.strip()
        if re.match(r'^\d{2}-\d{2}-\d{4}$', user_input):
            context.user_data['date'] = user_input
            update.message.reply_text("Введите время в формате ЧЧ:ММ")
            return SET_TIME
        else:
            update.message.reply_text("Неправильный формат даты, введите дату в формате: ДД-ММ-ГГГГ")
            return SET_DATE
    except:
         print("Произошла ошибка в функции date_question.")

def time_question(update, context):
    try:
        user_input = update.message.text.strip()
        if re.match(r'^\d{2}:\d{2}$', user_input):
            time_str = user_input

            calendar.create_event(
                event_name=context.user_data['name'],
                event_date=context.user_data['date'],
                event_time=time_str,
                event_details=context.user_data['details']
            )
            update.message.reply_text("Событие успешно создано")
            return END
        else:
            update.message.reply_text("Время указано в неправильном формате")
            return SET_TIME
    except:
        print("Произошла ошибка в функции time_question.")


def edit_event_handler(update, context):
    try:
        list_of_events(update, context)
        update.message.reply_text("Введите номер изменяемого события")
        return EDIT_EVENT
    except:
        print("Произошла ошибка в функции edit_event_handler.")
def edit_event(update, context):
    try:
        context.user_data['id'] = int(update.message.text)
        update.message.reply_text("Введите новое название события")
        return EDIT_NAME
    except:
        print("Произошла ошибка в функции edit_event.")

def edit_name(update, context):
    try:
        context.user_data['name'] = update.message.text
        update.message.reply_text("Введите новое описание события")
        return EDIT_DETAILS
    except:
        print("Произошла ошибка в функции edit_name.")

def edit_details(update, context):
    try:
        context.user_data['details'] = update.message.text
        update.message.reply_text("Введите новую дату в формате ДД-ММ-ГГГГ")
        return EDIT_DATE
    except:
        print("Произошла ошибка в функции edit_details.")

def edit_date_question(update, context):
    try:
        user_input = update.message.text.strip()
        if re.match(r'^\d{2}-\d{2}-\d{4}$', user_input):
            context.user_data['date'] = user_input
            update.message.reply_text("Введите новое время в формате ЧЧ:ММ")
            return EDIT_TIME
        else:
            update.message.reply_text("Неправильный формат даты, введите дату в формате: ДД-ММ-ГГГГ")
            return EDIT_DATE
    except:
         print("Произошла ошибка в функции edit_date_question.")

def edit_time_question(update, context):
    try:
        user_input = update.message.text.strip()
        if re.match(r'^\d{2}:\d{2}$', user_input):
            time_str = user_input
            calendar.edit_event(
                event_id=context.user_data['id'],
                event_name=context.user_data['name'],
                event_date=context.user_data['date'],
                event_time=time_str,
                event_details=context.user_data['details']
            )
            update.message.reply_text("Событие успешно отредактировано")
            return END
        else:
            update.message.reply_text("Время указано в неправильном формате")
            return SET_TIME
    except:
        print("Произошла ошибка в функции edit_time_question.")

def list_of_events(update, context):
    try:
        for event in calendar.events:
            context.bot.send_message(chat_id=update.message.chat_id, text=f'Всего событий: {len(calendar.events)}\n'
                  f'Номер события: {calendar.events[event]["id"]}\n'
                  f'Название события: {calendar.events[event]["name"]}\n'
                  f'Дата события: {calendar.events[event]["date"]}\n'
                  f'Время события: {calendar.events[event]["time"]}\n'
                  f'Описание события: {calendar.events[event]["details"]}\n')
            return END
    except:
        print("Произошла ошибка в функции list_of_events.")

def delete_events(update, context):
    try:
        list_of_events(update, context)
        update.message.reply_text("Введите номер удаляемого события")
        return DELETE
    except:
        print("Произошла ошибка в функции delete_events.")

def delete_handler(update, context):
    try:
        selected_event = update.message.text
        calendar.delete_event(selected_event)
        update.message.reply_text("Событие успешно удалено")
        return END
    except:
        print("Произошла ошибка в функции delete_handler.")


def main():
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('set', set_event)],
        states={
            SET_NAME: [MessageHandler(Filters.text, name)],
            SET_DETAILS: [MessageHandler(Filters.text, details)],
            SET_DATE: [MessageHandler(Filters.text, date_question)],
            SET_TIME: [MessageHandler(Filters.text, time_question)],
        },
        fallbacks=[],
        allow_reentry=True
    )
    delete_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('delete', delete_events)],
        states={
            DELETE: [MessageHandler(Filters.text, delete_handler)]
        },
        fallbacks=[],
        allow_reentry=True
    )
    edit_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('edit', edit_event_handler)],
        states={
            EDIT_EVENT: [MessageHandler(Filters.text, edit_event)],
            EDIT_NAME: [MessageHandler(Filters.text, edit_name)],
            EDIT_DETAILS: [MessageHandler(Filters.text, edit_details)],
            EDIT_DATE: [MessageHandler(Filters.text, edit_date_question)],
            EDIT_TIME: [MessageHandler(Filters.text, edit_time_question)]
        },
        fallbacks=[],
        allow_reentry=True
    )
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('list', list_of_events))
    dispatcher.add_handler(CommandHandler('delete', delete_events))
    dispatcher.add_handler(CommandHandler('edit', edit_event_handler))
    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(edit_conv_handler)
    dispatcher.add_handler(delete_conv_handler)

    updater.start_polling()
    updater.idle()
main()
