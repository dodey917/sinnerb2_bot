import os
from flask import Flask, request
import telebot

# Bot token (secure in production via env var)
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or "7989100213:AAFLgFNp3iXdQfjL0OY-DoW43sWX8xUzms0"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Respond to all messages
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_text = message.text
    response = generate_reply(user_text)
    bot.send_message(message.chat.id, response)

# Simple AI-like response logic
def generate_reply(text):
    text = text.lower()
    if "hello" in text or "hi" in text:
        return "Hey there! How can I help you today?"
    elif "who are you" in text:
        return "I'm sinnerb2_bot, your friendly Telegram chatbot! 😈"
    elif "help" in text:
        return "You can ask me anything. I’ll try to answer or just chat with you."
    else:
        return f"You said: {text}"

# Webhook route
@app.route("/webhook", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

# Health check
@app.route("/", methods=["GET"])
def index():
    return "Bot is running!", 200

if __name__ == "__main__":
    app.run(debug=True)
