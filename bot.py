import os
import logging
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from flask import Flask, request, jsonify
import asyncio

# Configuration - MUST CHANGE THESE!
TOKEN = "7989100213:AAFLgFNp3iXdQfjL0OY-DoW43sWX8xUzms0"
WEBHOOK_URL = "https://sinnerb2-bot.onrender.com/webhook"  # CHANGE TO YOUR RENDER URL
PORT = 10000  # Must match Render environment
HOST = "0.0.0.0"

# Initialize Flask
app = Flask(__name__)

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Telegram Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! I'm your SinnerB2 Bot!")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🔊 Echo: {update.message.text}")

def create_app():
    """Create Telegram application"""
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    return application

# Initialize
telegram_app = create_app()

# Flask Routes
@app.route('/')
def home():
    return "🤖 Bot is running!"

@app.route('/webhook', methods=['POST'])
async def webhook():
    json_data = await request.get_json()
    update = Update.de_json(json_data, telegram_app.bot)
    await telegram_app.process_update(update)
    return jsonify({"status": "ok"})

async def main():
    """Configure and start everything"""
    # Set bot commands
    await telegram_app.bot.set_my_commands([
        BotCommand("start", "Start the bot"),
        BotCommand("help", "Get help")
    ])
    
    # Set webhook
    await telegram_app.bot.set_webhook(
        url=WEBHOOK_URL,
        drop_pending_updates=True,
        allowed_updates=["message", "edited_message"]
    )
    logger.info(f"✅ Webhook set to: {WEBHOOK_URL}")
    
    # Start Flask
    from waitress import serve
    serve(app, host=HOST, port=PORT)

if __name__ == '__main__':
    # Run async setup
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
