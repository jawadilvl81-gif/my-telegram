import os
import shutil
import asyncio
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler, CallbackQueryHandler
import yt_dlp
import json

TOKEN = "8550991202:AAEviAwUOn4aeZSSNf-7850sVOHuB-GwM0w"
ADMIN_ID = 1319884774

WAITING_FOR_COUNT = 1
stop_requested = False
user_data = {}

# Database (Render/Replit pe file save hogi)
DB_FILE = "approved_users.json"

if os.path.exists(DB_FILE):
    with open(DB_FILE, "r") as f:
        approved_users = json.load(f)
else:
    approved_users = {}  # {user_id: {"expiry": "2025-12-30", "name": "Jawad"}}

# Saari categories (150+ waali) yahan paste kar dena (pehle waali list)

CATEGORIES = { ... }  # ← pehle waali poori list daal dena

def save_db():
    with open(DB_FILE, "w") as f:
        json.dump(approved_users, f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if str(user_id) in approved_users:
        expiry = approved_users[str(user_id)]["expiry"]
        if datetime.strptime(expiry, "%Y-%m-%d") > datetime.now():
            await update.message.reply_text(
                f"Welcome back bhai! 🔥\nTera access hai: {expiry} tak\n\n"
                "Categories: /milf /teen /indian /anal /big /hentai /bbc etc\n"
                "Search: /search indian bhabhi\nRukna ho to /cnahi"
            )
            return
        else:
            del approved_users[str(user_id)]
            save_db()

    # Agar approve nahi hai to request bhejega admin ko
    keyboard = [[InlineKeyboardButton("✅ Approve Kar Do", callback_data=f"approve_{user_id}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await context.bot.send_message(
        ADMIN_ID,
        f"Naya user request kar raha hai:\n"
        f"Name: {update.effective_user.first_name}\n"
        f"Username: @{update.effective_user.username or 'None'}\n"
        f"User ID: {user_id}",
        reply_markup=reply_markup
    )
    
    await update.message.reply_text("Bhai tera request admin ko chala gaya hai.\nJab approve karega tab use kar payega. Thoda wait kar 😇")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        await query.edit_message_text("Sirf admin hi approve kar sakta hai bhai 😅")
        return

    if query.data.startswith("approve_"):
        new_user_id = query.data.split("_")[1]
        
        keyboard = [
            [InlineKeyboardButton("7 Days", callback_data=f"7_{new_user_id}"),
             InlineKeyboardButton("30 Days", callback_data=f"30_{new_user_id}")],
            [InlineKeyboardButton("90 Days", callback_data=f"90_{new_user_id}"),
             InlineKeyboardButton("Lifetime", callback_data=f"life_{new_user_id}")]
        ]
        await query.edit_message_text("Kitne din ka access du?", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data.startswith(("7_", "30_", "90_", "life_")):
        days, user_id = (query.data.split("_") if not query.data.startswith("life") else ("lifetime", query.data.split("_")[1]))
        
        expiry = "2099-12-31" if days == "lifetime" else (datetime.now() + timedelta(days=int(days))).strftime("%Y-%m-%d")
        
        approved_users[user_id] = {"expiry": expiry, "approved_by": "admin"}
        save_db()
        
        await context.bot.send_message(user_id, f"Congratulations bhai! 🎉\nTera access approve ho gaya hai!\nValid till: {expiry}\nAb full maza le /milf /teen /indian etc likh ke!")
        await query.edit_message_text(f"User {user_id} ko {days} days ka access de diya gaya ✅")

# Baaki saare handlers same (category_handler, search_handler, ask_count, download_and_send etc)

# Sirf start aur category/search mein yeh check daal dena:
async def category_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) not in approved_users or datetime.strptime(approved_users[str(update.effective_user.id)]["expiry"], "%Y-%m-%d") < datetime.now():
        await update.message.reply_text("Bhai tera access nahi hai ya expire ho gaya.\n/start kar ke request bhej")
        return ConversationHandler.END
    # ...baaki code same

# Same search_handler mein bhi yeh check laga dena

def main():
    if not os.path.exists("downloads"):
        os.makedirs("downloads")

    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            *[CommandHandler(cat, category_handler) for cat in CATEGORIES],
            CommandHandler("search", search_handler)
        ],
        states={WAITING_FOR_COUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_count)],
        fallbacks=[CommandHandler(["cnahi","stop"], stop_command)]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(CommandHandler(["cnahi","stop"], stop_command))
    app.add_handler(conv_handler)

    print("Private Pornhub Bot with Admin Approval LIVE hai!")
    app.run_polling()

if __name__ == '__main__':
    main()
