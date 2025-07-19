import os
from flask import Flask, request
import telebot

TOKEN = os.getenv("7989100213:AAFLgFNp3iXdQfjL0OY-DoW43sWX8xUzms0")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Replace with your channel's username or numeric ID
CHANNEL_ID = "@your_channel_username"  # Example: @myupdateschannel

# Respond to any message (private or group)
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_type = message.chat.type
    user_text = message.text.lower()

    # Respond differently based on chat type
    if chat_type == "private":
        response = generate_reply(user_text)
        bot.send_message(message.chat.id, response)
    elif chat_type in ["group", "supergroup"]:
        if "sinnerb2" in user_text:
            bot.send_message(message.chat.id, "👋 Did someone call me?")
    elif chat_type == "channel":
        # Optional: post to channel automatically
        bot.send_message(CHANNEL_ID, "Channel message received.")

# Simple reply logic
def generate_reply(text):
    if "hello" in text:
        return "Hello! How can I assist you today?"
    elif "help" in text:
        return "I'm here to help! Just ask anything."
    elif "who are you" in text:
        return "I'm sinnerb2_bot, your AI assistant. 😈"
    else:
        return f"You said: {text}"

@app.route("/webhook", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.get_data().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/", methods=["GET"])
def home():
    return "Bot is running!", 200

if __name__ == "__main__":
    app.run()
