from flask import Flask, request
import telebot
import openai
import os

# --- Config ---
API_TOKEN = '7989100213:AAFLgFNp3iXdQfjL0OY-DoW43sWX8xUzms0'
OPENAI_API_KEY = os.getenv("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")  # safer this way

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)
openai.api_key = OPENAI_API_KEY


# --- ChatGPT Reply Function ---
def chat_with_gpt(message):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # You can change this if needed
            messages=[{"role": "user", "content": message}],
            temperature=0.7,
            max_tokens=150
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"OpenAI error: {e}")
        return "Sorry, I had trouble thinking. Try again later."


# --- Handle Messages ---
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    reply = chat_with_gpt(message.text)
    bot.send_message(message.chat.id, reply)


# --- Webhook Endpoint ---
@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    else:
        return 'Unsupported Media Type', 415


# --- For testing locally (not needed on Render) ---
if __name__ == '__main__':
    app.run(debug=True)
