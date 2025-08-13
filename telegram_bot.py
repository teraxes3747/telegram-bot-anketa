import logging
import requests
import json
import re
from datetime import datetime
import time

# Настройки ботов
QUESTIONNAIRE_BOT_TOKEN = "8159114689:AAF4hvVIoM0suy96MA97ywamFVkA5tsgGrg"  # Бот который спрашивает
RECEIVER_BOT_TOKEN = "8123260024:AAH_j10hELrWoUNwy1o4eaauQL7-wIhw8i4"   # Бот который получает и пересылает
YOUR_CHAT_ID = "7580196939"  # ВАШИ ID

QUESTIONNAIRE_API_URL = f"https://api.telegram.org/bot{QUESTIONNAIRE_BOT_TOKEN}"
RECEIVER_API_URL = f"https://api.telegram.org/bot{RECEIVER_BOT_TOKEN}"

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Состояния пользователей
user_states = {}
user_profiles = {}

# Константы состояний
class States:
    START = "start"
    NAME = "name"
    AGE = "age"
    TELEGRAM = "telegram"
    WORK_CHOICE = "work_choice"
    WORK_DETAILS = "work_details"
    STUDY_PLACE = "study_place"
    STUDY_SPECIALITY = "study_speciality"
    HOBBIES = "hobbies"
    JOB_SEARCH = "job_search"
    OTHER_ACTIVITY = "other_activity"
    CITY = "city"
    INTERESTS = "interests"
    PHONE = "phone"
    EMAIL = "email"

def send_message_questionnaire(chat_id, text, reply_markup=None):
    """Отправляет сообщение через бот-анкету"""
    url = f"{QUESTIONNAIRE_API_URL}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    if reply_markup:
        data['reply_markup'] = json.dumps(reply_markup)
    
    try:
        response = requests.post(url, data=data)
        return response.json()
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения через анкету-бот: {e}")
        return None

def send_message_receiver(chat_id, text):
    """Отправляет сообщение через бот-получатель"""
    url = f"{RECEIVER_API_URL}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    
    try:
        response = requests.post(url, data=data)
        return response.json()
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения через получатель-бот: {e}")
        return None

def send_to_receiver_bot(profile, user_id):
    """Отправляет анкету на бот-получатель"""
    message = f"🆕 <b>НОВАЯ АНКЕТА</b>\n"
    message += "=" * 25 + "\n\n"
    message += f"👤 <b>Имя:</b> {profile.get('name', 'Не указано')}\n"
    message += f"🎂 <b>Возраст:</b> {profile.get('age', 'Не указано')} лет\n"
    message += f"📱 <b>Telegram:</b> {profile.get('telegram', 'Не указано')}\n"
    message += f"💼 <b>Деятельность:</b> {profile.get('work_hobby', 'Не указано')}\n"
    
    if profile.get('city'):
        message += f"🏙️ <b>Город:</b> {profile['city']}\n"
    
    if profile.get('interests'):
        message += f"⭐ <b>Интересы:</b> {profile['interests']}\n"
    
    if profile.get('phone'):
        message += f"📞 <b>Телефон:</b> {profile['phone']}\n"
    
    if profile.get('email'):
        message += f"📧 <b>Email:</b> {profile['email']}\n"
    
    message += f"\n👤 <b>ID пользователя:</b> <code>{user_id}</code>\n"
    message += f"📅 <b>Дата:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}"
    
    # Отправляем через второй бот на ваш ID
    send_message_receiver(YOUR_CHAT_ID, message)

def handle_start(chat_id, user_id):
    """Обработка команды /start"""
    user_states[user_id] = States.NAME
    user_profiles[user_id] = {}
    
    welcome_text = """🌟 <b>ДОБРО ПОЖАЛОВАТЬ В АНКЕТУ!</b> 🌟

Привет! Я помогу заполнить анкету.
Все данные будут переданы администратору.

Давай начнем! 👇

<b>Как тебя зовут?</b>
(минимум 2 символа)"""
    
    send_message_questionnaire(chat_id, welcome_text)

def handle_message(chat_id, user_id, text):
    """Обработка сообщений от пользователя"""
    current_state = user_states.get(user_id, States.START)
    
    if current_state == States.NAME:
        handle_name(chat_id, user_id, text)
    elif current_state == States.AGE:
        handle_age(chat_id, user_id, text)
    elif current_state == States.TELEGRAM:
        handle_telegram(chat_id, user_id, text)
    elif current_state == States.WORK_CHOICE:
        handle_work_choice(chat_id, user_id, text)
    elif current_state == States.WORK_DETAILS:
        handle_work_details(chat_id, user_id, text)
    elif current_state == States.STUDY_PLACE:
        handle_study_place(chat_id, user_id, text)
    elif current_state == States.STUDY_SPECIALITY:
        handle_study_speciality(chat_id, user_id, text)
    elif current_state == States.HOBBIES:
        handle_hobbies(chat_id, user_id, text)
    elif current_state == States.JOB_SEARCH:
        handle_job_search(chat_id, user_id, text)
    elif current_state == States.OTHER_ACTIVITY:
        handle_other_activity(chat_id, user_id, text)
    elif current_state == States.CITY:
        handle_city(chat_id, user_id, text)
    elif current_state == States.INTERESTS:
        handle_interests(chat_id, user_id, text)
    elif current_state == States.PHONE:
        handle_phone(chat_id, user_id, text)
    elif current_state == States.EMAIL:
        handle_email(chat_id, user_id, text)

def handle_name(chat_id, user_id, text):
    """Обработка имени"""
    if len(text.strip()) >= 2:
        user_profiles[user_id]['name'] = text.strip().title()
        user_states[user_id] = States.AGE
        send_message_questionnaire(chat_id, f"Отлично, {text.strip()}! 👍\n\n<b>Сколько тебе лет?</b>\n(от 1 до 120)")
    else:
        send_message_questionnaire(chat_id, "❌ Имя должно содержать минимум 2 символа. Попробуй еще раз:")

def handle_age(chat_id, user_id, text):
    """Обработка возраста"""
    try:
        age = int(text.strip())
        if 1 <= age <= 120:
            user_profiles[user_id]['age'] = age
            user_states[user_id] = States.TELEGRAM
            send_message_questionnaire(chat_id, f"Понял, тебе {age} лет! 🎂\n\n<b>Какой у тебя ник в Telegram?</b>\n(можно написать 'нет')")
        else:
            send_message_questionnaire(chat_id, "❌ Возраст должен быть от 1 до 120 лет. Попробуй еще раз:")
    except ValueError:
        send_message_questionnaire(chat_id, "❌ Пожалуйста, введи число (твой возраст):")

def handle_telegram(chat_id, user_id, text):
    """Обработка Telegram ника"""
    text = text.strip()
    if text.lower() in ['нет', 'не хочу', 'пропустить', '']:
        user_profiles[user_id]['telegram'] = "Не указан"
    else:
        if text.startswith('@'):
            text = text[1:]
        user_profiles[user_id]['telegram'] = f"@{text}" if text else "Не указан"
    
    user_states[user_id] = States.WORK_CHOICE
    
    keyboard = {
        'keyboard': [
            ['1️⃣ Работаю', '2️⃣ Учусь'],
            ['3️⃣ Есть хобби', '4️⃣ В поиске работы'],
            ['5️⃣ Другое']
        ],
        'resize_keyboard': True,
        'one_time_keyboard': True
    }
    
    send_message_questionnaire(chat_id, 
        "Отлично! 📱\n\n<b>Расскажи о своей деятельности:</b>\nВыбери подходящий вариант ↓", 
        keyboard)

def handle_work_choice(chat_id, user_id, text):
    """Обработка выбора деятельности"""
    choice = text.strip().lower()
    
    if choice in ['1', '1️⃣ работаю', 'работаю']:
        user_states[user_id] = States.WORK_DETAILS
        send_message_questionnaire(chat_id, "💼 <b>Кем ты работаешь?</b>\n(напиши должность и компанию)")
    elif choice in ['2', '2️⃣ учусь', 'учусь']:
        user_states[user_id] = States.STUDY_PLACE
        send_message_questionnaire(chat_id, "🎓 <b>Где ты учишься?</b>\n(школа, университет, курсы)")
    elif choice in ['3', '3️⃣ есть хобби', 'есть хобби']:
        user_states[user_id] = States.HOBBIES
        send_message_questionnaire(chat_id, "🎨 <b>Какие у тебя хобби?</b>\n(расскажи подробнее)")
    elif choice in ['4', '4️⃣ в поиске работы', 'в поиске работы']:
        user_states[user_id] = States.JOB_SEARCH
        send_message_questionnaire(chat_id, "🔍 <b>Какую работу ищешь?</b>\n(можно написать 'любую')")
    elif choice in ['5', '5️⃣ другое', 'другое']:
        user_states[user_id] = States.OTHER_ACTIVITY
        send_message_questionnaire(chat_id, "✍️ <b>Опиши свою деятельность:</b>")
    else:
        send_message_questionnaire(chat_id, "❌ Пожалуйста, выбери один из вариантов (1-5):")

def handle_work_details(chat_id, user_id, text):
    user_profiles[user_id]['work_hobby'] = f"Работа: {text.strip()}"
    ask_city(chat_id, user_id)

def handle_study_place(chat_id, user_id, text):
    user_profiles[user_id]['study_place'] = text.strip()
    user_states[user_id] = States.STUDY_SPECIALITY
    send_message_questionnaire(chat_id, "📚 <b>Какая специальность?</b>\n(можно написать 'не определился')")

def handle_study_speciality(chat_id, user_id, text):
    study_info = f"Учёба: {user_profiles[user_id]['study_place']}"
    if text.strip().lower() not in ['не определился', 'нет']:
        study_info += f", специальность: {text.strip()}"
    user_profiles[user_id]['work_hobby'] = study_info
    ask_city(chat_id, user_id)

def handle_hobbies(chat_id, user_id, text):
    user_profiles[user_id]['work_hobby'] = f"Хобби: {text.strip()}"
    ask_city(chat_id, user_id)

def handle_job_search(chat_id, user_id, text):
    work_info = "В поиске работы"
    if text.strip().lower() not in ['любую', 'не знаю']:
        work_info += f", ищу: {text.strip()}"
    user_profiles[user_id]['work_hobby'] = work_info
    ask_city(chat_id, user_id)

def handle_other_activity(chat_id, user_id, text):
    user_profiles[user_id]['work_hobby'] = text.strip()
    ask_city(chat_id, user_id)

def ask_city(chat_id, user_id):
    user_states[user_id] = States.CITY
    send_message_questionnaire(chat_id, "🏙️ <b>В каком городе живешь?</b>\n(можно написать 'не хочу указывать')")

def handle_city(chat_id, user_id, text):
    if text.strip().lower() not in ['не хочу указывать', 'нет', 'пропустить']:
        user_profiles[user_id]['city'] = text.strip().title()
    
    user_states[user_id] = States.INTERESTS
    send_message_questionnaire(chat_id, "⭐ <b>Какие у тебя интересы?</b>\n(можно написать 'нет')")

def handle_interests(chat_id, user_id, text):
    if text.strip().lower() not in ['нет', 'пропустить']:
        user_profiles[user_id]['interests'] = text.strip()
    
    user_states[user_id] = States.PHONE
    send_message_questionnaire(chat_id, "📞 <b>Твой номер телефона?</b>\n(можно написать 'нет')")

def handle_phone(chat_id, user_id, text):
    if text.strip().lower() not in ['нет', 'пропустить']:
        user_profiles[user_id]['phone'] = text.strip()
    
    user_states[user_id] = States.EMAIL
    send_message_questionnaire(chat_id, "📧 <b>Твой email?</b>\n(можно написать 'нет')")

def handle_email(chat_id, user_id, text):
    if text.strip().lower() not in ['нет', 'пропустить']:
        user_profiles[user_id]['email'] = text.strip()
    
    finish_survey(chat_id, user_id)

def finish_survey(chat_id, user_id):
    """Завершение анкеты"""
    profile = user_profiles[user_id]
    
    # Показываем результат пользователю
    result_text = "🎉 <b>АНКЕТА ЗАПОЛНЕНА!</b>\n\n"
    result_text += "📋 <b>Твои данные:</b>\n"
    result_text += f"👤 Имя: {profile.get('name', 'Не указано')}\n"
    result_text += f"🎂 Возраст: {profile.get('age', 'Не указано')} лет\n"
    result_text += f"💼 Деятельность: {profile.get('work_hobby', 'Не указано')}\n"
    result_text += "\n📤 <b>Отправляю данные...</b>"
    
    send_message_questionnaire(chat_id, result_text)
    
    # Отправляем через второй бот к вам
    send_to_receiver_bot(profile, user_id)
    
    # Финальное сообщение
    send_message_questionnaire(chat_id, "✅ <b>Данные отправлены!</b>\n\nСпасибо! 🙏\n\nДля новой анкеты: /start")
    
    # Очищаем данные
    if user_id in user_states:
        del user_states[user_id]
    if user_id in user_profiles:
        del user_profiles[user_id]

def get_updates(bot_token, offset=None):
    """Получает обновления"""
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    params = {'timeout': 30}
    if offset:
        params['offset'] = offset
    
    try:
        response = requests.get(url, params=params)
        return response.json()
    except Exception as e:
        logger.error(f"Ошибка получения обновлений: {e}")
        return None

def main():
    """Основная функция"""
    logger.info("🤖 Единый бот запущен!")
    logger.info("📝 Анкеты через первый бот -> второй бот -> вам")
    
    offset = None
    
    while True:
        try:
            # Получаем сообщения для бота-анкеты
            updates = get_updates(QUESTIONNAIRE_BOT_TOKEN, offset)
            
            if updates and updates.get('ok'):
                for update in updates.get('result', []):
                    offset = update['update_id'] + 1
                    
                    if 'message' in update:
                        message = update['message']
                        chat_id = message['chat']['id']
                        user_id = message['from']['id']
                        
                        if 'text' in message:
                            text = message['text']
                            
                            if text == '/start':
                                handle_start(chat_id, user_id)
                            else:
                                handle_message(chat_id, user_id, text)
            
            time.sleep(1)
            
        except KeyboardInterrupt:
            logger.info("🛑 Бот остановлен")
            break
        except Exception as e:
            logger.error(f"Ошибка: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
