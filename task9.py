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

SET_NAME, SET_DATE, SET_TIME, SET_DETAILS, SET_DELETE = map(chr, range(5))


def start(update, context):
    try:
        reply_markup = ReplyKeyboardMarkup([['/set', '/list'], ['/delete']])
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
            return ConversationHandler.END
        else:
            update.message.reply_text("Время указано в неправильном формате")
            return SET_TIME
    except:
        print("Произошла ошибка в функции time_question.")

def list_of_events(update, context):
    try:
        for event in calendar.events:
            context.bot.send_message(chat_id=update.message.chat_id, text=f'Всего событий: {len(calendar.events)}\n'
                  f'Номер события: {calendar.events[event]["id"]}\n'
                  f'Название события: {calendar.events[event]["name"]}\n'
                  f'Дата события: {calendar.events[event]["date"]}\n'
                  f'Время события: {calendar.events[event]["time"]}\n'
                  f'Описание события: {calendar.events[event]["details"]}\n')
            return ConversationHandler.END
    except:
        print("Произошла ошибка в функции list_of_events.")

def delete_events(update, context):
    list_of_events(update, context)
    update.message.reply_text("Введите номер удаляемого события")
    return SET_DELETE

def delete_handler(update, context):
    selected_event = update.message.text
    calendar.delete_event(selected_event)
    update.message.reply_text("Событие успешно удалено")
    return ConversationHandler.END


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
            SET_DELETE: [MessageHandler(Filters.text, delete_handler)]
        },
        fallbacks=[],
        allow_reentry=True
    )

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('list', list_of_events))
    dispatcher.add_handler(CommandHandler('delete', delete_events))
    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()
main()
