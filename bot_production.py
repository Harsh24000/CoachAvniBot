#!/usr/bin/env python3
"""
COACH AVNI BOT - CLEAN VERSION
✅ NO horizontal divider lines
✅ Chat history
✅ Answers in chat
✅ Custom answers
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
                "opts": ["💻 Software Eng", "👨‍⚕️ Doctor", "📚 Student", "🏫 Teacher", "👔 Business", "🤵 Consultant", "🏥 Healthcare", "📊 Finance", "🎯 Sales"],
                "custom": True
            },
            "sex": {
                "q": "⚡ Biological sex?",
                "type": "buttons",
                "req": True,
                "opts": ["👨 Male", "👩 Female", "🌈 Other"],
                "custom": False
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
                "opts": ["🍗 Non-Veg", "🥕 Vegetarian", "🥚 Eggetarian", "🌱 Vegan", "☪️ Jain"],
                "custom": True
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
                "opts": ["⏰ 5:00", "⏰ 6:00", "⏰ 7:00", "⏰ 8:00", "🛏️ 8:30+"],
                "custom": True
            },
            "sleep_time": {
                "q": "😴 Sleep time?",
                "type": "buttons",
                "req": True,
                "opts": ["🌙 9:00", "🌙 10:00", "🌙 11:00", "🌙 12:00", "🌙 12:30+"],
                "custom": True
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
                "opts": ["✅ No", "🍔 Food", "🌫️ Environmental", "🔀 Both"],
                "custom": False
            },
            "injuries": {
                "q": "🤕 Injuries?",
                "type": "buttons",
                "req": True,
                "opts": ["✅ No", "Old (healed)", "Current"],
                "custom": False
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
                "opts": ["😴 0", "🚶 1-2", "🏃 3-4", "🏋️ 5-6", "⚡ 7"],
                "custom": False
            },
            "strength_exp": {
                "q": "🏋️ Strength training?",
                "type": "buttons",
                "req": True,
                "opts": ["👶 None", "🌱 Beginner", "💪 Intermediate", "🦾 Advanced"],
                "custom": False
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
                "opts": ["📉 Lose weight", "💪 Build muscle", "⚡ Get stronger", "❤️ Better health"],
                "custom": True
            },
            "timeline": {
                "q": "⏱️ Timeline?",
                "type": "buttons",
                "req": True,
                "opts": ["🚀 1 month", "📅 3 months", "📅 6 months", "📅 1 year"],
                "custom": False
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
                "opts": ["🔥 YES! 100%!", "✅ Yes", "🤔 Maybe", "⏳ Not yet"],
                "custom": False
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
        self.waiting_custom = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    context.user_data[user_id] = UserSession()
    
    text = """🤖 MEALZY COACH 🎉

💪 Transform Your Body
✨ Transform Your Life

📋 Quick Assessment - 7 min
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

Your profile READY!
Coaches creating plan!

Thank you! 🙏"""
        if query:
            await query.edit_message_text(msg)
        else:
            await update.message.reply_text(msg)
        return
    
    screen = SCREENS[sn]
    prog = int((sn / 8) * 100)
    bar = "█" * (prog // 5) + "░" * (20 - (prog // 5))
    
    # Build message text
    text = f"{bar} {prog}%\n\n{screen['title']}\n\n"
    
    # Show ALL answered questions with checkmarks
    for fkey, qdata in screen['questions'].items():
        if fkey in session.inputs:
            text += f"{qdata['q']} ✅\n"
    
    # Show first unanswered question
    buttons = []
    first_unanswered = None
    
    for fkey, qdata in screen['questions'].items():
        if fkey not in session.inputs:
            if first_unanswered is None:
                first_unanswered = (fkey, qdata)
    
    # Display unanswered question
    if first_unanswered:
        fkey, qdata = first_unanswered
        text += f"\n{qdata['q']} [Tap below]\n\n"
        text += f"Select {qdata['q'].split('?')[0].strip()}\n\n"
        
        # Create buttons
        for i, opt in enumerate(qdata['opts']):
            btn = InlineKeyboardButton(opt, callback_data=f"a_{sn}_{fkey}_{i}")
            if not buttons or len(buttons[-1]) >= 2:
                buttons.append([btn])
            else:
                buttons[-1].append(btn)
        
        # Add custom button if allowed
        if qdata.get('custom'):
            buttons.append([InlineKeyboardButton("📝 Custom", callback_data=f"c_{sn}_{fkey}")])
    
    # Next button
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
        
        # SHOW ANSWER IN CHAT
        qtxt = qdata['q'].replace("?", "").strip()
        await update.callback_query.message.reply_text(f"✅ {qtxt}\n→ {ans}")
        
        await asyncio.sleep(0.5)
        await show_screen(update, context, query)
    
    # Custom answer button
    if data.startswith("c_"):
        parts = data.split("_")
        sn = int(parts[1])
        fkey = parts[2]
        
        sess.waiting_custom = (sn, fkey)
        
        screen = SCREENS[sn]
        qdata = screen['questions'][fkey]
        qtxt = qdata['q'].replace("?", "").strip()
        
        await update.callback_query.message.reply_text(f"📝 Type your answer for:\n{qtxt}")
        
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
        await show_screen(update, context, query)

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    
    if uid not in context.user_data:
        await start(update, context)
        return
    
    sess = context.user_data[uid]
    txt = update.message.text.strip()
    
    # Handle custom answer
    if sess.waiting_custom:
        sn, fkey = sess.waiting_custom
        screen = SCREENS[sn]
        qdata = screen['questions'][fkey]
        
        sess.inputs[fkey] = txt
        sess.answers[fkey] = txt
        sess.waiting_custom = None
        
        # SHOW ANSWER IN CHAT
        qtxt = qdata['q'].replace("?", "").strip()
        await update.message.reply_text(f"✅ {qtxt}\n→ {txt}")
        
        await asyncio.sleep(1)
        await show_screen(update, context)
        return
    
    # Handle regular text input
    sn = sess.screen
    screen = SCREENS[sn]
    
    # Find first unanswered text field
    text_fields = [k for k, v in screen['questions'].items() if v['type'] == 'text' and k not in sess.inputs]
    
    if not text_fields:
        return
    
    fkey = text_fields[0]
    qdata = screen['questions'][fkey]
    
    sess.inputs[fkey] = txt
    sess.answers[fkey] = txt
    
    qtxt = qdata['q'].replace("?", "").strip()
    if fkey == 'name':
        sess.name = txt
    
    # SHOW ANSWER IN CHAT
    await update.message.reply_text(f"✅ {qtxt}\n→ {txt}")
    
    await asyncio.sleep(1)
    await show_screen(update, context)

def main():
    print("\n" + "=" * 70)
    print("✅ CLEAN BOT - NO DIVIDER LINES")
    print("=" * 70)
    print("✅ Chat history")
    print("✅ Answers in chat")
    print("✅ Custom answers")
    print("✅ NO divider lines")
    print("=" * 70)
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    
    print("🚀 BOT RUNNING!\n")
    app.run_polling()

if __name__ == "__main__":
    main()
