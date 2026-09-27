import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

# ----------------- تنظیمات اصلی -----------------
# توکن جدیدی که از BotFather گرفتید را اینجا بگذارید
BOT_TOKEN = "8578324939:AAGItZRgCsimC-zCnmYDvu4kze1CaQux7II"

# آیدی کانال شما با علامت @ (ربات حتماً باید ادمین این کانال باشد)
CHANNEL_USERNAME = "@xyyje" 

# لینک دعوت عمومی کانال برای کلیک کاربر
CHANNEL_LINK = "https://t.me/xyyje"
# ------------------------------------------------

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# تابع بررسی عضویت در کانال
async def is_user_member(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> bool:
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        # وضعیت‌های معتبر: عضو عادی، سازنده کانال یا ادمین
        if member.status in ["member", "administrator", "creator"]:
            return True
        return False
    except Exception as e:
        # اگر ربات در کانال ادمین نباشد خطا می‌دهد؛ در این صورت عبور می‌دهد تا ربات قفل نشود
        logging.error(f"خطا در بررسی عضویت کانال: {e}")
        return True

# کیبورد بازی‌ها (وب‌اپ استاندارد داخل تلگرام)
def get_games_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                "♟️ بازی شطرنج",
                web_app=WebAppInfo(url="https://lichess.org")
            )
        ],
        [
            InlineKeyboardButton(
                "⭕ دوز (Tic-Tac-Toe)",
                web_app=WebAppInfo(url="https://playtictactoe.org")
            ),
            InlineKeyboardButton(
                "🐍 بازی مار (Snake)",
                web_app=WebAppInfo(url="https://playsnake.org")
            )
        ],
        [
            InlineKeyboardButton(
                "🔢 بازی ۲۰۴۸",
                web_app=WebAppInfo(url="https://play2048.co")
            )
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# کیبورد عضویت اجباری
def get_join_keyboard():
    keyboard = [
        [InlineKeyboardButton("📢 عضویت در کانال", url=CHANNEL_LINK)],
        [InlineKeyboardButton("🔄 تایید عضویت و ورود به بازی‌ها", callback_data="check_membership")]
    ]
    return InlineKeyboardMarkup(keyboard)

# دستور /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id

    # بررسی عضویت کاربر در کانال
    is_member = await is_user_member(context, user_id)

    if not is_member:
        text = (
            f"سلام {user.first_name} عزیز! 🌸\n\n"
            f"⚠️ برای استفاده از بازی‌ها و ربات، ابتدا باید در کانال ما عضو شوید:\n"
            f"{CHANNEL_USERNAME}\n\n"
            f"بعد از عضویت روی دکمه «تایید عضویت» بزنید 👇"
        )
        await update.message.reply_text(text, reply_markup=get_join_keyboard())
    else:
        text = (
            f"سلام {user.first_name}! 🎮 به ربات بازی خوش آمدید.\n"
            f"هر بازی را که دوست دارید انتخاب کنید و لذت ببرید:"
        )
        await update.message.reply_text(text, reply_markup=get_games_keyboard())

# بررسی کلیک روی دکمه تایید عضویت
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "check_membership":
        user_id = query.from_user.id
        is_member = await is_user_member(context, user_id)

        if is_member:
            await query.edit_message_text(
                "✅ عضویت شما تایید شد! حالا بازی مورد نظرتان را انتخاب کنید: 🎮",
                reply_markup=get_games_keyboard()
            )
        else:
            await query.answer("❌ هنوز در کانال عضو نشده‌اید! لطفاً ابتدا عضو شوید.", show_alert=True)

def main():
    print("ربات در حال راه‌اندازی است...")
    app = Application.builder().token(BOT_TOKEN).build()

    # ثبت هندلرها
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))

    print("ربات فعال شد و برای تمام کاربران در دسترس است. ✅")
    app.run_polling()

if __name__ == "__main__":
    main()
