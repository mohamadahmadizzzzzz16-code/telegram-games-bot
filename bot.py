import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
    WebAppInfo,
    MenuButtonWebApp,
)
from telegram.constants import ChatMemberStatus
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

logging.basicConfig(level=logging.INFO)

# توکن ربات
TOKEN = "8578324939:AAH3FBOsT8XijFMqu5bR8-lU8xWaMfqvVPE"

# مشخصات کانال
CHANNEL_USERNAME = "@xyyje"
CHANNEL_JOIN_LINK = "https://t.me/xyyje"

# لینک‌های بازی‌ها
GAMES = {
    # شطرنج
    "chess_board": "https://lichess.org/analysis",
    "chess_ai": "https://lichess.org/?any#ai",
    "chess_friend": "https://lichess.org/?any#friend",
    # سایر بازی‌ها
    "tictactoe": "https://playtictactoe.org/",
    "2048": "https://play2048.co/",
    # ماربازی دارای دکمه‌های جهت‌نما لمسی روی صفحه مخصوص موبایل
    "snake": "https://playsnake.org/",
}

# کیبورد ثابت زیر چت
def get_bottom_keyboard():
    return ReplyKeyboardMarkup(
        [[KeyboardButton("🎮 انتخاب و شروع بازی‌ها")]],
        resize_keyboard=True
    )

# منوی شیشه‌ای کامل بازی‌ها
def get_games_menu():
    keyboard = [
        # بخش شطرنج
        [
            InlineKeyboardButton(
                "♟ شطرنج: تخته لمسی دستی",
                web_app=WebAppInfo(url=GAMES["chess_board"])
            )
        ],
        [
            InlineKeyboardButton(
                "🤖 شطرنج: بازی با هوش مصنوعی (AI)",
                web_app=WebAppInfo(url=GAMES["chess_ai"])
            )
        ],
        [
            InlineKeyboardButton(
                "👥 شطرنج: بازی دونفره با دوستان",
                web_app=WebAppInfo(url=GAMES["chess_friend"])
            )
        ],
        # بخش سایر بازی‌ها
        [
            InlineKeyboardButton(
                "🐍 ماربازی کلاسیک (با کلیدهای جهتی ⬅️⬆️⬇️➡️)",
                web_app=WebAppInfo(url=GAMES["snake"])
            )
        ],
        [
            InlineKeyboardButton(
                "⭕❌ بازی دوز (Tic-Tac-Toe)",
                web_app=WebAppInfo(url=GAMES["tictactoe"])
            )
        ],
        [
            InlineKeyboardButton(
                "🔢 بازی فکری 2048",
                web_app=WebAppInfo(url=GAMES["2048"])
            )
        ],
    ]
    return InlineKeyboardMarkup(keyboard)

# منوی قفل عضویت در کانال
def get_join_menu():
    keyboard = [
        [InlineKeyboardButton("📢 عضویت در کانال", url=CHANNEL_JOIN_LINK)],
        [InlineKeyboardButton("🔄 بررسی عضویت و ورود", callback_data="check_join")],
    ]
    return InlineKeyboardMarkup(keyboard)

# دکمه شیشه‌ای شروع اولیه
def get_start_button_menu():
    keyboard = [
        [InlineKeyboardButton("🚀 ورود به گیم‌سنتر", callback_data="open_games")]
    ]
    return InlineKeyboardMarkup(keyboard)

# تابع بررسی عضویت در کانال
async def is_member(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> bool:
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in (
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.OWNER,
        )
    except Exception as e:
        logging.warning(f"Error checking membership: {e}")
        return False

# تنظیم دکمه آبی‌رنگ منوی پایین صفحه تلگرام
async def setup_menu_button(bot, chat_id: int):
    try:
        await bot.set_chat_menu_button(
            chat_id=chat_id,
            menu_button=MenuButtonWebApp(
                text="🎮 Open Games",
                web_app=WebAppInfo(url=GAMES["chess_board"])
            )
        )
    except Exception as e:
        logging.warning(f"MenuButton error: {e}")

# دستور start/
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name

    await setup_menu_button(context.bot, update.effective_chat.id)

    # بررسی عضویت
    if not await is_member(context, user_id):
        await update.message.reply_text(
            f"سلام {user_name} عزیز! 👋\n\n"
            "⚠️ برای استفاده از بازی‌ها، ابتدا در کانال ما عضو شوید:\n"
            f"{CHANNEL_USERNAME}\n\n"
            "سپس روی دکمه «بررسی عضویت و ورود» بزنید:",
            reply_markup=get_join_menu()
        )
        return

    await update.message.reply_text(
        f"سلام {user_name} عزیز! به گیم‌سنتر تلگرام خوش آمدید 🕹\n\n"
        "برای مشاهده و شروع بازی‌ها روی دکمه زیر بزنید:",
        reply_markup=get_start_button_menu()
    )
    await update.message.reply_text(
        "دکمه دسترسی سریع نیز در پایین صفحه فعال شد 👇",
        reply_markup=get_bottom_keyboard()
    )

# مدیریت کلیک دکمه‌های شیشه‌ای
async def on_button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "check_join":
        if await is_member(context, user_id):
            await query.edit_message_text(
                "✅ عضویت شما تأیید شد!\n\n🎮 بازی مورد نظر خود را انتخاب کنید:",
                reply_markup=get_games_menu()
            )
        else:
            await query.answer("❌ هنوز عضو کانال نشده‌اید!", show_alert=True)

    elif query.data == "open_games":
        if not await is_member(context, user_id):
            await query.edit_message_text(
                "⚠️ شما هنوز در کانال عضو نیستید. لطفاً ابتدا عضو شوید:",
                reply_markup=get_join_menu()
            )
            return

        await query.edit_message_text(
            "🎮 لطفاً بازی مورد نظر خود را انتخاب کنید:",
            reply_markup=get_games_menu()
        )

# مدیریت کلیک دکمه پایین صفحه (ReplyKeyboard)
async def handle_bottom_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    if "بازی‌ها" in text:
        if not await is_member(context, user_id):
            await update.message.reply_text(
                "⚠️ شما هنوز در کانال عضو نیستید. لطفاً ابتدا عضو شوید:",
                reply_markup=get_join_menu()
            )
            return

        await update.message.reply_text(
            "🎮 لیست بازی‌ها آماده است، یکی را انتخاب کنید:",
            reply_markup=get_games_menu()
        )

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(on_button_click))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_bottom_buttons))

    print("--- گیم سنتر با تمام بازی‌ها و دکمه‌ها فعال شد ---")
    app.run_polling()

if __name__ == "__main__":
    main()
