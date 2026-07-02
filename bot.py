# -*- coding: utf-8 -*-
"""
Telegram Bot Builder
ربات‌ساز تلگرام با سیستم امتیاز، رفرال، جوین اجباری و ۳۰۰ قالب آماده

نصب:
pip install -r requirements.txt

اجرا:
python bot.py
"""

import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ================= تنظیمات اصلی =================

BOT_TOKEN = "8954722038:AAEnMgBh8fcVBETUneE7DVq5cE2wlNZkLik"

# آیدی پشتیبانی بدون @
SUPPORT_USERNAME = "@D4RKDRAGUN"

# کانال جوین اجباری
FORCE_CHANNEL_USERNAME = "@Hack_R4ei30"
FORCE_CHANNEL_LINK = "https://t.me/Hack_R4ei30"

# مقدار امتیاز برای هر زیرمجموعه
REFERRAL_REWARD = 2

# نام دیتابیس
DB_NAME = "bot_builder.db"

# ================= دیتابیس =================

conn = sqlite3.connect(DB_NAME, check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    points INTEGER DEFAULT 0,
    ref_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    template_id INTEGER,
    template_name TEXT,
    cost INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()


# ================= قالب‌ها =================

BOT_TYPES = [
    "خدمات مجازی",
    "سنگ کاغذ قیچی",
    "فروشگاهی",
    "ثبت سفارش",
    "پشتیبانی آنلاین",
    "دانلودر",
    "مسابقه",
    "فال و سرگرمی",
    "آموزشی",
    "نوبت‌دهی",
    "مدیریت کانال",
    "ارسال ناشناس",
    "دریافت شماره",
    "ربات عضویت ویژه",
    "ربات آزمون",
    "ربات موزیک",
    "ربات لینک‌ساز",
    "ربات پیام‌رسان",
    "ربات تبلیغات",
    "ربات قرعه‌کشی",
]

TEMPLATES = {}

for i in range(1, 301):
    bot_type = BOT_TYPES[(i - 1) % len(BOT_TYPES)]
    cost = 5 + ((i - 1) % 20)
    TEMPLATES[i] = {
        "name": f"قالب {i} - {bot_type}",
        "type": bot_type,
        "cost": cost,
        "description": f"این قالب برای ساخت ربات {bot_type} آماده شده است."
    }


# ================= توابع کمکی =================

def add_user(user_id: int, ref_by: int | None = None):
    cur.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    exists = cur.fetchone()

    if exists:
        return False

    if ref_by == user_id:
        ref_by = None

    cur.execute(
        "INSERT INTO users(user_id, points, ref_by) VALUES(?, ?, ?)",
        (user_id, 0, ref_by)
    )
    conn.commit()

    if ref_by:
        cur.execute("SELECT user_id FROM users WHERE user_id = ?", (ref_by,))
        ref_exists = cur.fetchone()

        if ref_exists:
            cur.execute(
                "UPDATE users SET points = points + ? WHERE user_id = ?",
                (REFERRAL_REWARD, ref_by)
            )
            conn.commit()

    return True


def get_points(user_id: int) -> int:
    cur.execute("SELECT points FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    return int(row[0]) if row else 0


def change_points(user_id: int, amount: int):
    cur.execute(
        "UPDATE users SET points = points + ? WHERE user_id = ?",
        (amount, user_id)
    )
    conn.commit()


def save_order(user_id: int, template_id: int, template_name: str, cost: int):
    cur.execute(
        """
        INSERT INTO orders(user_id, template_id, template_name, cost)
        VALUES(?, ?, ?, ?)
        """,
        (user_id, template_id, template_name, cost)
    )
    conn.commit()


async def is_joined(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> bool:
    try:
        member = await context.bot.get_chat_member(FORCE_CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False


def main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("ساخت ربات 🤖", callback_data="templates_1")],
        [InlineKeyboardButton("امتیاز من 💰", callback_data="points")],
        [InlineKeyboardButton("لینک دعوت من 🔗", callback_data="referral")],
        [InlineKeyboardButton("خرید امتیاز 💳", url=f"https://t.me/{SUPPORT_USERNAME}")],
        [InlineKeyboardButton("پشتیبانی 👨‍💻", url=f"https://t.me/{SUPPORT_USERNAME}")]
    ])


def join_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("عضویت در کانال", url=FORCE_CHANNEL_LINK)],
        [InlineKeyboardButton("عضو شدم ✅", callback_data="check_join")]
    ])


async def send_force_join_message(update: Update):
    text = """
برای استفاده از ربات ابتدا باید عضو کانال زیر شوید:

بعد از عضویت، روی «عضو شدم» بزنید.
"""
    if update.message:
        await update.message.reply_text(text, reply_markup=join_keyboard())
    else:
        await update.callback_query.edit_message_text(text, reply_markup=join_keyboard())


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    points = get_points(user_id)
    bot_username = context.bot.username
    ref_link = f"https://t.me/{bot_username}?start={user_id}"

    text = f"""
سلام 👋
به ربات‌ساز خوش آمدید.

امتیاز شما: {points}

با دعوت هر زیرمجموعه، {REFERRAL_REWARD} امتیاز دریافت می‌کنید.

لینک دعوت شما:
{ref_link}
"""

    if update.message:
        await update.message.reply_text(text, reply_markup=main_keyboard())
    else:
        await update.callback_query.edit_message_text(text, reply_markup=main_keyboard())


def templates_keyboard(page: int):
    per_page = 10
    start_id = (page - 1) * per_page + 1
    end_id = min(start_id + per_page - 1, 300)

    keyboard = []

    for template_id in range(start_id, end_id + 1):
        template = TEMPLATES[template_id]
        keyboard.append([
            InlineKeyboardButton(
                f"{template['name']} | {template['cost']} امتیاز",
                callback_data=f"template_{template_id}"
            )
        ])

    nav = []
    if page > 1:
        nav.append(InlineKeyboardButton("قبلی ⬅️", callback_data=f"templates_{page - 1}"))

    if end_id < 300:
        nav.append(InlineKeyboardButton("بعدی ➡️", callback_data=f"templates_{page + 1}"))

    if nav:
        keyboard.append(nav)

    keyboard.append([InlineKeyboardButton("بازگشت به منو 🔙", callback_data="back_home")])

    return InlineKeyboardMarkup(keyboard)


# ================= هندلرها =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    ref_by = None
    if context.args:
        try:
            ref_by = int(context.args[0])
        except ValueError:
            ref_by = None

    add_user(user_id, ref_by)

    if not await is_joined(context, user_id):
        await send_force_join_message(update)
        return

    await show_main_menu(update, context)


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data

    add_user(user_id)

    if data == "check_join":
        if await is_joined(context, user_id):
            await show_main_menu(update, context)
        else:
            await query.edit_message_text(
                "هنوز عضو کانال نشده‌اید. لطفاً اول عضو شوید.",
                reply_markup=join_keyboard()
            )
        return

    if not await is_joined(context, user_id):
        await send_force_join_message(update)
        return

    if data == "back_home":
        await show_main_menu(update, context)
        return

    if data == "points":
        points = get_points(user_id)
        await query.edit_message_text(
            f"امتیاز فعلی شما: {points}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("خرید امتیاز 💳", url=f"https://t.me/{SUPPORT_USERNAME}")],
                [InlineKeyboardButton("بازگشت 🔙", callback_data="back_home")]
            ])
        )
        return

    if data == "referral":
        bot_username = context.bot.username
        ref_link = f"https://t.me/{bot_username}?start={user_id}"

        await query.edit_message_text(
            f"""
لینک دعوت اختصاصی شما:

{ref_link}

با هر زیرمجموعه موفق، {REFERRAL_REWARD} امتیاز می‌گیرید.
""",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("بازگشت 🔙", callback_data="back_home")]
            ])
        )
        return

    if data.startswith("templates_"):
        page = int(data.split("_")[1])
        await query.edit_message_text(
            f"لیست قالب‌های ربات‌ساز\nصفحه {page} از 30",
            reply_markup=templates_keyboard(page)
        )
        return

    if data.startswith("template_"):
        template_id = int(data.split("_")[1])
        template = TEMPLATES.get(template_id)

        if not template:
            await query.edit_message_text("قالب پیدا نشد.")
            return

        points = get_points(user_id)
        cost = template["cost"]

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("ساخت این ربات ✅", callback_data=f"buy_{template_id}")],
            [InlineKeyboardButton("بازگشت به قالب‌ها 🔙", callback_data="templates_1")]
        ])

        await query.edit_message_text(
            f"""
{template['name']}

نوع:
{template['type']}

توضیح:
{template['description']}

هزینه ساخت:
{cost} امتیاز

امتیاز شما:
{points}
""",
            reply_markup=keyboard
        )
        return

    if data.startswith("buy_"):
        template_id = int(data.split("_")[1])
        template = TEMPLATES.get(template_id)

        if not template:
            await query.edit_message_text("قالب پیدا نشد.")
            return

        points = get_points(user_id)
        cost = template["cost"]

        if points < cost:
            await query.edit_message_text(
                f"""
امتیاز شما کافی نیست.

قالب انتخابی:
{template['name']}

هزینه:
{cost} امتیاز

امتیاز شما:
{points}

برای خرید امتیاز به پشتیبانی پیام دهید:
@{SUPPORT_USERNAME}
""",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("خرید امتیاز 💳", url=f"https://t.me/{SUPPORT_USERNAME}")],
                    [InlineKeyboardButton("بازگشت 🔙", callback_data="back_home")]
                ])
            )
            return

        change_points(user_id, -cost)
        save_order(user_id, template_id, template["name"], cost)

        await query.edit_message_text(
            f"""
ربات شما با موفقیت ساخته شد ✅

قالب:
{template['name']}

امتیاز کسر شده:
{cost}

امتیاز باقی‌مانده:
{get_points(user_id)}

برای دریافت فایل یا فعال‌سازی نهایی به پشتیبانی پیام دهید:
@{SUPPORT_USERNAME}
""",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("پشتیبانی 👨‍💻", url=f"https://t.me/{SUPPORT_USERNAME}")],
                [InlineKeyboardButton("بازگشت به منو 🔙", callback_data="back_home")]
            ])
        )
        return


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        """
راهنما:

/start شروع ربات

امکانات:
- جوین اجباری
- سیستم امتیاز
- سیستم زیرمجموعه‌گیری
- ۳۰۰ قالب ربات
- کسر امتیاز برای هر قالب
- اتصال به پشتیبانی برای خرید امتیاز
"""
    )


def main():
    if BOT_TOKEN == "توکن_ربات_خودت_را_اینجا_بگذار":
        print("لطفاً ابتدا BOT_TOKEN را داخل فایل bot.py وارد کنید.")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(callback_handler))

    print("ربات روشن شد...")
    app.run_polling()


if __name__ == "__main__":
    main()
