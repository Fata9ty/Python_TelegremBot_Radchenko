import logging
import re
from secrets import TOKEN, DATABASE, USER, PASSWORD
import datetime
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
import psycopg2
from psycopg2.extras import RealDictCursor


class Database:

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super().__new__(cls)
            return cls.instance

    def __init__(self, host, port, database, user, password, autocommit=False):

        self.connection = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
        )
        if autocommit:
            self.connection.autocommit = True
        self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)

    def select(self, query, varz):

        self.cursor.execute(query, varz)
        res = self.cursor.fetchall()
        return res

    def post(self, query, varz):

        self.cursor.execute(query, varz)
        if not self.connection.autocommit:
            self.connection.commit()


db = Database(host='localhost', port=5432, database=DATABASE, user=USER, password=PASSWORD)

now = datetime.datetime.now()


class Calendar:

    def __init__(self, db):

        self.events = {}

    def create_event(

        self,
        event_name,
        event_date,
        event_time,
        event_details):

        data = db.select('select max(id) as mx from events', varz=None)
        data = [dict(row) for row in data]
        all_ids = data[0].get('mx')
        event_id = all_ids + 1
        event = {
            "id": event_id,
            "name": event_name,
            "date": event_date,
            "time": event_time,
            "details": event_details}
        db.post("insert into events (ID, NAME, DATE, TIME, DETAILS) values (%s, %s, %s, %s, %s)", (event_id, event_name, event_date, event_time, event_details))
        self.events[event_id] = event
        return event_id

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


calendar = Calendar(db)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

SET_NAME, SET_DATE, SET_TIME, SET_DETAILS, SET_DELETE = map(chr, range(5))
print(db.select('select id from events', varz=None))


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
    else:
        update.message.reply_text("Время указано в неправильном формате")
        return SET_TIME




def list_of_events(update, context):
    try:
        events = db.select("select * from events", varz=None)
        context.bot.send_message(chat_id=update.message.chat_id, text=f'Данные о событиях: {events}')
        return ConversationHandler.END
    except:
        print("Произошла ошибка в функции list_of_events.")


def delete_events(update, context):
    try:
        list_of_events(update, context)
        update.message.reply_text("Введите номер удаляемого события")
        return SET_DELETE
    except:
        print("Произошла ошибка в функции delete_events.")

def delete_handler(update, context):
    try:
        selected_event = update.message.text
        db.post('delete * from events where id=%s', selected_event)
        update.message.reply_text("Событие успешно удалено")
        return ConversationHandler.END
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
