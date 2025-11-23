from typing import Optional
from app.config import settings

# Telegram Bot
async def send_telegram_notification(message: str) -> bool:
    """Отправка уведомления в Telegram"""
    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        return False
    
    try:
        from telegram import Bot
        
        bot = Bot(token=settings.telegram_bot_token)
        await bot.send_message(
            chat_id=settings.telegram_chat_id,
            text=f"🔔 QuickLead Manager\n\n{message}",
            parse_mode="HTML"
        )
        return True
    except Exception as e:
        print(f"Telegram notification error: {e}")
        return False


# Slack
async def send_slack_notification(message: str) -> bool:
    """Отправка уведомления в Slack"""
    if not settings.slack_bot_token or not settings.slack_channel:
        return False
    
    try:
        from slack_sdk.web.async_client import AsyncWebClient
        
        client = AsyncWebClient(token=settings.slack_bot_token)
        
        response = await client.chat_postMessage(
            channel=settings.slack_channel,
            text=f"🔔 QuickLead Manager\n\n{message}"
        )
        
        return response["ok"]
    except Exception as e:
        print(f"Slack notification error: {e}")
        return False


def format_lead_notification(lead_data: dict) -> str:
    """Форматирование уведомления о новой заявке"""
    message = f"📝 Новая заявка #{lead_data['id']}\n\n"
    
    if lead_data.get('name'):
        message += f"👤 Имя: {lead_data['name']}\n"
    if lead_data.get('phone'):
        message += f"📞 Телефон: {lead_data['phone']}\n"
    if lead_data.get('email'):
        message += f"📧 Email: {lead_data['email']}\n"
    if lead_data.get('message'):
        message += f"💬 Сообщение: {lead_data['message']}\n"
    
    if lead_data.get('utm', {}):
        utm = lead_data['utm']
        utm_info = []
        if utm.get('source'):
            utm_info.append(f"источник: {utm['source']}")
        if utm.get('campaign'):
            utm_info.append(f"кампания: {utm['campaign']}")
        if utm_info:
            message += f"📊 UTM: {', '.join(utm_info)}\n"
    
    message += f"\n⏰ Время: {lead_data.get('created_at', 'Неизвестно')}"
    
    return message
