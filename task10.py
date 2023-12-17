import datetime
import json
import logging
import psycopg2
import re

from psycopg2.extras import RealDictCursor
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes

from secrets import TOKEN, DATABASE, USER, PASSWORD


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
        try:
            self.cursor.execute(query, varz)
            res = self.cursor.fetchall()
            return res
        except:
            print("Произошла ошибка в функции select.")

    def post(self, query, varz):
        try:
            self.cursor.execute(query, varz)
            if not self.connection.autocommit:
                self.connection.commit()
        except:
            print("Произошла ошибка в функции post.")


db = Database(host='localhost', port=5432, database=DATABASE, user=USER, password=PASSWORD)

now = datetime.datetime.now()


class Calendar:

    def __init__(self, db):

        self.events = {}

    def create_event(
            self,
            chat_id,
            event_name,
            event_date,
            event_time,
            event_details):

        try:
            data = db.select('select max(id) as mx from events', varz=None)
            data = [dict(row) for row in data]
            all_ids = data[0].get('mx')
            if all_ids is None:
                event_id = 1
            else:
                event_id = all_ids + 1
            event = {
                "chat_id": chat_id,
                "id": event_id,
                "name": event_name,
                "date": event_date,
                "time": event_time,
                "details": event_details}
            db.post("insert into events (ID, NAME, DATE, TIME, DETAILS, CHAT_ID) values (%s, %s, %s, %s, %s, %s)",
                    (event_id, event_name, event_date, event_time, event_details, chat_id))
            self.events[event_id] = event
            return event_id
        except:
            print("Произошла ошибка в функции create_event.")

    def edit_event(self, event_id, event_name, event_date, event_time, event_details):
        try:
            event = {
                "id": event_id,
                "name": event_name,
                "date": event_date,
                "time": event_time,
                "details": event_details
            }
            db.post("update events set NAME=%s, DATE=%s, TIME=%s, DETAILS=%s where ID=%s",
                    (event_name, event_date, event_time, event_details, int(event_id)))
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

(SET_EVENT, SET_NAME, SET_DATE, SET_TIME, SET_DETAILS, EDIT_EVENT, EDIT_NAME, EDIT_DATE, EDIT_TIME,
 EDIT_DETAILS, DELETE) = map(chr, range(11))
END = ConversationHandler.END


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        reply_markup = ReplyKeyboardMarkup([['/set', '/list'], ['/edit', '/delete']])
        await update.message.reply_text("Что вы намереваетесь сделать?", reply_markup=reply_markup)
    except:
        print("Произошла ошибка в функции start.")


async def set_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("Введите название события")
        return SET_NAME
    except:
        print("Произошла ошибка в функции set_event.")


async def name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data['name'] = update.message.text
        await update.message.reply_text("Введите описание события")
        return SET_DETAILS
    except:
        print("Произошла ошибка в функции name.")


async def details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data['details'] = update.message.text
        await update.message.reply_text("Введите дату в формате ДД-ММ-ГГГГ")
        return SET_DATE
    except:
        print("Произошла ошибка в функции details.")


async def date_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_input = update.message.text.strip()
        if re.match(r'^\d{2}-\d{2}-\d{4}$', user_input):
            context.user_data['date'] = user_input
            await update.message.reply_text("Введите время в формате ЧЧ:ММ")
            return SET_TIME
        else:
            await update.message.reply_text("Неправильный формат даты, введите дату в формате: ДД-ММ-ГГГГ")
            return SET_DATE
    except:
        print("Произошла ошибка в функции date_question.")


async def time_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_input = update.message.text.strip()
        current_chat_id = update.message.chat_id
        if re.match(r'^\d{2}:\d{2}$', user_input) and current_chat_id:
            time_str = user_input
            calendar.create_event(
                event_name=context.user_data['name'],
                event_date=context.user_data['date'],
                event_time=time_str,
                event_details=context.user_data['details'],
                chat_id=current_chat_id,
            )
            await update.message.reply_text("Событие успешно создано")
            return END
        else:
            await update.message.reply_text("Время указано в неправильном формате")
            return SET_TIME
    except:
        print("Произошла ошибка в функции time_question.")


async def edit_event_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await list_of_events(update, context)
        await update.message.reply_text("Введите номер изменяемого события")
        return EDIT_EVENT
    except:
        print("Произошла ошибка в функции edit_event_handler.")


async def edit_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data['id'] = int(update.message.text)
        await update.message.reply_text("Введите новое название события")
        return EDIT_NAME
    except:
        print("Произошла ошибка в функции edit_event.")


async def edit_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data['name'] = update.message.text
        await update.message.reply_text("Введите новое описание события")
        return EDIT_DETAILS
    except:
        print("Произошла ошибка в функции edit_name.")


async def edit_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data['details'] = update.message.text
        await update.message.reply_text("Введите новую дату в формате ДД-ММ-ГГГГ")
        return EDIT_DATE
    except:
        print("Произошла ошибка в функции edit_details.")


async def edit_date_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_input = update.message.text.strip()
        if re.match(r'^\d{2}-\d{2}-\d{4}$', user_input):
            context.user_data['date'] = user_input
            await update.message.reply_text("Введите новое время в формате ЧЧ:ММ")
            return EDIT_TIME
        else:
            await update.message.reply_text("Неправильный формат даты, введите дату в формате: ДД-ММ-ГГГГ")
            return EDIT_DATE
    except:
        print("Произошла ошибка в функции edit_date_question.")


async def edit_time_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_input = update.message.text.strip()
        current_chat_id = update.message.chat_id
        if re.match(r'^\d{2}:\d{2}$', user_input) and current_chat_id:
            time_str = user_input
            calendar.edit_event(
                event_id=context.user_data['id'],
                event_name=context.user_data['name'],
                event_date=context.user_data['date'],
                event_time=time_str,
                event_details=context.user_data['details'],
            )
            await update.message.reply_text("Событие успешно отредактировано")
            return END

        else:
            await update.message.reply_text("Время указано в неправильном формате")
            return EDIT_TIME
    except:
        print("Произошла ошибка в функции edit_time_question.")


async def list_of_events(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chat_id = update.message.chat_id
        events = db.select(f"select * from events where CHAT_ID={chat_id}", varz=None)
        json_events = json.dumps(events, ensure_ascii=False, indent=4, default=str)
        if json_events == "[]":
            await context.bot.send_message(chat_id=update.message.chat_id, text=f'Список событий пуст')
        else:
            await context.bot.send_message(chat_id=update.message.chat_id, text=f'Данные о событиях: {json_events}')
    except:
        print("Произошла ошибка в функции delete_events.")


async def delete_events(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await list_of_events(update, context)
        await update.message.reply_text("Введите номер удаляемого события")
        return DELETE
    except:
        print("Произошла ошибка в функции delete_events.")


async def delete_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        selected_event = int(update.message.text)
        db.post(f'delete from events where id={selected_event}', varz=None)
        await update.message.reply_text(f"Событие под номером: {selected_event} успешно удалено")
        return END
    except:
        print("Произошла ошибка в функции delete_handler.")


def main():
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('set', set_event)],
        states={
            SET_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],
            SET_DETAILS: [MessageHandler(filters.TEXT & ~filters.COMMAND, details)],
            SET_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, date_question)],
            SET_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, time_question)],
        },
        fallbacks=[],
        allow_reentry=True
    )
    delete_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('delete', delete_events)],
        states={
            DELETE: [MessageHandler(filters.TEXT & ~filters.COMMAND, delete_handler)]
        },
        fallbacks=[],
        allow_reentry=True
    )
    edit_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('edit', edit_event_handler)],
        states={
            EDIT_EVENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_event)],
            EDIT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_name)],
            EDIT_DETAILS: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_details)],
            EDIT_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_date_question)],
            EDIT_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_time_question)]
        },
        fallbacks=[],
        allow_reentry=True
    )
    application.add_handler(delete_conv_handler)
    application.add_handler(edit_conv_handler)
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('list', list_of_events))
    application.add_handler(CommandHandler('delete', delete_events))
    application.add_handler(CommandHandler('edit', edit_event_handler))
    application.add_handler(conv_handler)
    application.run_polling(allowed_updates=Update.ALL_TYPES)


main()
