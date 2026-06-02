#!/usr/bin/env python3
"""
COACH AVNI BOT - PRODUCTION VERSION
✅ Shows answered questions with ✅
✅ Divider line after each
✅ Next unanswered question [Tap below]
✅ "Select [Question]" header
✅ Professional UI
"""

import os
import sys
import random
import asyncio
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TOKEN:
    print("ERROR: TELEGRAM_TOKEN not found in .env")
    sys.exit(1)

FUN_RESPONSES = ["🔥 Great!", "💯 Love it!", "⚡ Perfect!", "🎯 Got it!", "✨ Amazing!"]

SCREENS = {
    1: {
        "title": "👤 Basic Info",
        "questions": {
            "name": {"q": "👤 Full name?", "type": "text", "req": True},
            "age": {"q": "🎂 Age?", "type": "text", "req": True},
            "height": {"q": "📏 Height (cm)?", "type": "text", "req": True},
            "weight": {"q": "⚖️ Weight (kg)?", "type": "text", "req": True},
        }
    },
    
    2: {
        "title": "💼 Work & Details",
        "questions": {
            "profession": {
                "q": "💼 Profession?",
                "type": "buttons",
                "req": True,
                "opts": ["💻 Software Eng", "👨‍⚕️ Doctor", "📚 Student", "🏫 Teacher", "👔 Business", "🤵 Consultant", "🏥 Healthcare", "📊 Finance", "🎯 Sales", "➕ Other"]
            },
            "sex": {
                "q": "⚡ Biological sex?",
                "type": "buttons",
                "req": True,
                "opts": ["👨 Male", "👩 Female", "🌈 Other"]
            },
        }
    },
    
    3: {
        "title": "🍽️ Diet & Food",
        "questions": {
            "dietary_pref": {
                "q": "🍽️ Dietary preference?",
                "type": "buttons",
                "req": True,
                "opts": ["🍗 Non-Veg", "🥕 Vegetarian", "🥚 Eggetarian", "🌱 Vegan", "☪️ Jain"]
            },
            "disliked_foods": {
                "q": "🚫 Dislike any foods?",
                "type": "buttons_multi",
                "req": False,
                "opts": ["🥒 Bitter gourd", "🍆 Eggplant", "🍄 Mushroom", "🧅 Onion", "🧄 Garlic"]
            },
        }
    },
    
    4: {
        "title": "☀️ Your Day",
        "questions": {
            "wake_time": {
                "q": "🌅 Wake time?",
                "type": "buttons",
                "req": True,
                "opts": ["⏰ 5:00", "⏰ 6:00", "⏰ 7:00", "⏰ 8:00", "🛏️ 8:30+"]
            },
            "sleep_time": {
                "q": "😴 Sleep time?",
                "type": "buttons",
                "req": True,
                "opts": ["🌙 9:00", "🌙 10:00", "🌙 11:00", "🌙 12:00", "🌙 12:30+"]
            },
        }
    },
    
    5: {
        "title": "🏥 Health",
        "questions": {
            "allergies": {
                "q": "🤧 Allergies?",
                "type": "buttons",
                "req": True,
                "opts": ["✅ No", "🍔 Food", "🌫️ Environmental", "🔀 Both"]
            },
            "injuries": {
                "q": "🤕 Injuries?",
                "type": "buttons",
                "req": True,
                "opts": ["✅ No", "Old (healed)", "Current"]
            },
        }
    },
    
    6: {
        "title": "💪 Fitness",
        "questions": {
            "active_days": {
                "q": "💪 Active days/week?",
                "type": "buttons",
                "req": True,
                "opts": ["😴 0", "🚶 1-2", "🏃 3-4", "🏋️ 5-6", "⚡ 7"]
            },
            "strength_exp": {
                "q": "🏋️ Strength training?",
                "type": "buttons",
                "req": True,
                "opts": ["👶 None", "🌱 Beginner", "💪 Intermediate", "🦾 Advanced"]
            },
        }
    },
    
    7: {
        "title": "🎯 Goals",
        "questions": {
            "main_goal": {
                "q": "🎯 Main goal?",
                "type": "buttons",
                "req": True,
                "opts": ["📉 Lose weight", "💪 Build muscle", "⚡ Get stronger", "❤️ Better health"]
            },
            "timeline": {
                "q": "⏱️ Timeline?",
                "type": "buttons",
                "req": True,
                "opts": ["🚀 1 month", "📅 3 months", "📅 6 months", "📅 1 year"]
            },
        }
    },
    
    8: {
        "title": "🤝 Ready?",
        "questions": {
            "ready": {
                "q": "🚀 Ready to START?",
                "type": "buttons",
                "req": True,
                "opts": ["🔥 YES! 100%!", "✅ Yes", "🤔 Maybe", "⏳ Not yet"]
            },
        }
    },
}

class UserSession:
    def __init__(self):
        self.screen = 1
        self.inputs = {}
        self.answers = {}
        self.name = None
        self.pending_text = []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    context.user_data[user_id] = UserSession()
    
    text = """🤖 MEALZY COACH 🎉

💪 Transform Your Body
✨ Transform Your Life

📋 Quick Assessment
✅ 8 Screens
✅ Professional UI
✅ 7 minutes

Let's go! 🚀"""
    
    keyboard = [[InlineKeyboardButton("🎯 START", callback_data="start")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def show_screen(update: Update, context: ContextTypes.DEFAULT_TYPE, query=None):
    user_id = update.effective_user.id
    
    if user_id not in context.user_data:
        await start(update, context)
        return
    
    session = context.user_data[user_id]
    sn = session.screen
    
    if sn > 8:
        msg = f"""🎉 COMPLETE! 🏆

👋 {session.name or 'Champion'}!

Your profile is READY!
Coaches creating plan NOW!

Thank you! 🙏
Ready to TRANSFORM? 🚀"""
        await update.message.reply_text(msg)
        return
    
    screen = SCREENS[sn]
    prog = int((sn / 8) * 100)
    bar = "█" * (prog // 5) + "░" * (20 - (prog // 5))
    
    # Get text fields
    text_fields = [k for k, v in screen['questions'].items() if v['type'] == 'text']
    unanswered_text = [k for k in text_fields if k not in session.inputs]
    session.pending_text = unanswered_text
    
    # Build message
    text = f"{bar} {prog}%\n\n{screen['title']}\n\n"
    
    buttons = []
    first_unanswered = None
    
    # Show answered questions with checkmark
    for fkey, qdata in screen['questions'].items():
        if qdata['type'] == 'text' and fkey in session.inputs:
            text += f"{qdata['q']} ✅\n"
            text += "━" * 50 + "\n\n"
            continue
        
        if fkey not in session.inputs:
            if first_unanswered is None:
                first_unanswered = (fkey, qdata)
    
    # Show first unanswered question
    if first_unanswered:
        fkey, qdata = first_unanswered
        text += f"{qdata['q']} [Tap below]\n"
        text += "━" * 50 + "\n\n"
        
        # Add section header
        q_name = qdata['q'].split('?')[0].strip()
        text += f"Select {q_name}\n\n"
        
        # Buttons for this question
        if qdata['type'] in ['buttons', 'buttons_multi']:
            for i, opt in enumerate(qdata['opts']):
                btn = InlineKeyboardButton(opt, callback_data=f"a_{sn}_{fkey}_{i}")
                if not buttons or len(buttons[-1]) >= 2:
                    buttons.append([btn])
                else:
                    buttons[-1].append(btn)
    
    # Handle text inputs
    for fkey, qdata in screen['questions'].items():
        if qdata['type'] == 'text' and fkey not in session.inputs:
            text += f"{qdata['q']}\n"
            text += "*(Type in chat)*\n\n"
    
    buttons.append([InlineKeyboardButton("✅ NEXT →", callback_data=f"nx_{sn}")])
    
    markup = InlineKeyboardMarkup(buttons)
    
    if query:
        await query.edit_message_text(text, reply_markup=markup)
    else:
        await update.message.reply_text(text, reply_markup=markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    
    if uid not in context.user_data:
        await start(update, context)
        return
    
    await query.answer()
    sess = context.user_data[uid]
    data = query.data
    
    if data == "start":
        sess.screen = 1
        await show_screen(update, context, query)
        return
    
    if data.startswith("a_"):
        parts = data.split("_")
        sn = int(parts[1])
        fkey = parts[2]
        aidx = int(parts[3])
        
        screen = SCREENS[sn]
        qdata = screen['questions'][fkey]
        ans = qdata['opts'][aidx]
        
        sess.inputs[fkey] = ans
        sess.answers[fkey] = ans
        
        fun = random.choice(FUN_RESPONSES)
        await query.answer(fun, show_alert=False)
        
        # Show in chat
        qtxt = qdata['q'].replace("?", "").strip()
        await update.callback_query.message.reply_text(f"✅ {qtxt}\n→ {ans}")
        
        await asyncio.sleep(0.5)
        await show_screen(update, context, query)
        
    if data.startswith("nx_"):
        sn = int(data.split("_")[1])
        screen = SCREENS[sn]
        
        # Check required
        for fkey, qdata in screen['questions'].items():
            if qdata['req'] and fkey not in sess.inputs:
                await query.answer("⚠️ Answer all!", show_alert=True)
                return
        
        sess.screen += 1
        sess.inputs = {}
        sess.pending_text = []
        await show_screen(update, context, query)

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    
    if uid not in context.user_data:
        await start(update, context)
        return
    
    sess = context.user_data[uid]
    sn = sess.screen
    screen = SCREENS[sn]
    txt = update.message.text.strip()
    
    if not sess.pending_text:
        return
    
    fkey = sess.pending_text[0]
    qdata = screen['questions'][fkey]
    
    sess.inputs[fkey] = txt
    sess.answers[fkey] = txt
    
    qtxt = qdata['q'].replace("?", "").strip()
    if fkey == 'name':
        sess.name = txt
    
    await update.message.reply_text(f"✅ {qtxt}\n→ {txt}")
    sess.pending_text.pop(0)
    
    await asyncio.sleep(1)
    await show_screen(update, context)

def main():
    print("\n" + "=" * 70)
    print("✅ PRODUCTION BOT - FINAL VERSION")
    print("=" * 70)
    print("✅ Shows answered questions with ✅")
    print("✅ Dividers between questions")
    print("✅ Unanswered question [Tap below]")
    print("✅ 'Select [Question]' header")
    print("✅ Professional UI")
    print("=" * 70)
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    
    print("🚀 BOT RUNNING!\n")
    app.run_polling()

if __name__ == "__main__":
    main()
