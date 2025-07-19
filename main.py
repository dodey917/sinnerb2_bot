from flask import Flask, request
import telegram
from telegram.ext import Dispatcher, CommandHandler

app = Flask(__name__)
TOKEN = "7989100213:AAFLgFNp3iXdQfjL0OY-DoW43sWX8xUzms0"  # Replace with your token
bot = telegram.Bot(token=TOKEN)

@app.route('/')
def home():
    return "Bot is running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    update = telegram.Update.de_json(request.get_json(), bot)
    dispatcher.process_update(update)
    return 'ok'

def start(update, context):
    update.message.reply_text('Hello! I am your bot.')

# Set up command handlers
dispatcher = Dispatcher(bot, None, workers=0)
dispatcher.add_handler(CommandHandler("start", start))

if __name__ == '__main__':
    # Set webhook
    bot.set_webhook(url="https://your-render-service.onrender.com/webhook")
    app.run(host='0.0.0.0', port=10000)
