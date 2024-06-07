from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.decl_api import declarative_base
from pyrogram import Client, filters
from datetime import datetime

# Конфигурация базы данных
DB_URL = 'sqlite:///sales_funnel.db'
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()


# Модель для таблицы пользователей
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now)
    status = Column(String, default='alive')
    status_updated_at = Column(DateTime, default=datetime.now)


# Инициализация базы данных
Base.metadata.create_all(engine)

# Инициализация Pyrogram клиента
api_id = 'API_ID'
api_hash = 'API_HASH'
bot_token = 'BOT_ID'
app = Client('my_bot')


def check_triggers(text):
    triggers = ['прекрасно', 'ожидать']
    for trigger in triggers:
        if trigger in text.lower():
            return True
    return False


@app.on_message(filters.command("start"))
async def start_command(client, message):
    user_id = message.chat.id
    session = Session()
    user = session.query(User).filter_by(id=user_id).first()
    if not user:
        user = User(id=user_id)
        session.add(user)
        session.commit()
    await message.reply("Привет! Я запущен и готов принимать ваши сообщения.")
    session.close()


@app.on_message(filters.text & filters.private)
async def send_message(client, message):
    session = Session()
    users = session.query(User).filter_by(status='alive').all()

    for user in users:
        try:
            if check_triggers(message.text):
                user.status = 'finished'
                user.status_updated_at = datetime.now()
                session.commit()
                continue

            await client.send_message(user.id, message.text)
            user.status_updated_at = datetime.now()
            session.commit()
        except Exception as e:
            user.status = 'dead'
            user.status_updated_at = datetime.now()
            session.commit()
            print(f'Error sending message to user {user.id}: {e}')

    session.close()


@app.on_message(filters.text & filters.private)
async def reply_message(client, message):
    await message.reply(message.text)


app.run()
