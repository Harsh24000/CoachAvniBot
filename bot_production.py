#!/usr/bin/env python3
"""
COACH AVNI BOT - GROUPED + CHAT HISTORY
✅ Group 3-4 related questions per screen
✅ Clear separation between groups
✅ Show answers in chat (history)
✅ Fast & engaging
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

FUN_RESPONSES = [
    "🔥 Great answers!",
    "💯 Love it!",
    "⚡ Perfect!",
    "🎯 Got it!",
    "✨ Amazing!",
]

# ============================================================================
# SCREENS - GROUP 3-4 RELATED QUESTIONS CLEARLY SEPARATED
# ============================================================================

SCREENS = {
    1: {
        "title": "👤 About You - Basic Info",
        "section": "👤 About You",
        "questions": {
            "name": {"text": "👤 Full name?", "type": "text", "required": True},
            "age": {"text": "🎂 Age?", "type": "text", "required": True},
            "height": {"text": "📏 Height (cm)?", "type": "text", "required": True},
            "weight": {"text": "⚖️ Weight (kg)?", "type": "text", "required": True},
        }
    },
    
    2: {
        "title": "💼 Work & Details",
        "section": "👤 About You",
        "questions": {
            "profession": {
                "text": "💼 Profession?", 
                "type": "buttons", 
                "required": True,
                "options": ["💻 Software Eng", "👨‍⚕️ Doctor", "📚 Student", "🏫 Teacher", "👔 Business", "🤵 Consultant", "🏥 Healthcare", "📊 Finance", "🎯 Sales", "➕ Other"]
            },
            "sex": {
                "text": "⚡ Biological sex?", 
                "type": "buttons", 
                "required": True,
                "options": ["👨 Male", "👩 Female", "🌈 Other"]
            },
        }
    },
    
    3: {
        "title": "🍽️ Diet & Food",
        "section": "🍽️ Diet & Food",
        "questions": {
            "dietary_pref": {
                "text": "🍽️ Dietary preference?", 
                "type": "buttons", 
                "required": True,
                "options": ["🍗 Non-Veg", "🥕 Vegetarian", "🥚 Eggetarian", "🌱 Vegan", "☪️ Jain"]
            },
            "disliked_foods": {
                "text": "🚫 Dislike any foods?", 
                "type": "buttons_multi", 
                "required": False,
                "options": ["🥒 Bitter gourd", "🍆 Eggplant", "🍄 Mushroom", "🧅 Onion", "🧄 Garlic"]
            },
            "cuisines": {
                "text": "👨‍🍳 Love which cuisines?", 
                "type": "buttons_multi", 
                "required": False,
                "options": ["🇮🇳 North Indian", "🔥 South Indian", "🥘 Gujarati", "🌶️ Continental", "🍝 Italian"]
            },
        }
    },
    
    4: {
        "title": "☀️ Your Daily Times",
        "section": "☀️ Your Day",
        "questions": {
            "wake_time": {
                "text": "🌅 Wake time?",
                "type": "buttons",
                "required": True,
                "options": ["⏰ 5:00", "⏰ 6:00", "⏰ 7:00", "⏰ 8:00", "🛏️ 8:30+"]
            },
            "breakfast_time": {
                "text": "☕ Breakfast?",
                "type": "buttons",
                "required": True,
                "options": ["🌅 6:00", "🌅 7:00", "🌅 8:00", "🌅 9:00", "⏭️ Skip"]
            },
            "sleep_time": {
                "text": "😴 Sleep time?",
                "type": "buttons",
                "required": True,
                "options": ["🌙 9:00", "🌙 10:00", "🌙 11:00", "🌙 12:00", "🌙 12:30+"]
            },
        }
    },
    
    5: {
        "title": "🏥 Health",
        "section": "🏥 Health",
        "questions": {
            "medical_conditions": {
                "text": "⚕️ Medical conditions?",
                "type": "buttons_multi",
                "required": False,
                "options": ["🔬 Diabetes", "🧬 Thyroid", "🔴 PCOS", "❤️ Hypertension", "✅ None"]
            },
            "allergies": {
                "text": "🤧 Allergies?",
                "type": "buttons",
                "required": True,
                "options": ["✅ No", "🍔 Food", "🌫️ Environmental", "🔀 Both"]
            },
            "injuries": {
                "text": "🤕 Injuries?",
                "type": "buttons",
                "required": True,
                "options": ["✅ No", "Old (healed)", "Current"]
            },
        }
    },
    
    6: {
        "title": "💪 Fitness",
        "section": "💪 Fitness",
        "questions": {
            "active_days": {
                "text": "💪 Active days/week?",
                "type": "buttons",
                "required": True,
                "options": ["😴 0", "🚶 1-2", "🏃 3-4", "🏋️ 5-6", "⚡ 7"]
            },
            "strength_exp": {
                "text": "🏋️ Strength training?",
                "type": "buttons",
                "required": True,
                "options": ["👶 None", "🌱 Beginner", "💪 Intermediate", "🦾 Advanced"]
            },
            "workout_place": {
                "text": "📍 Workout location?",
                "type": "buttons",
                "required": True,
                "options": ["🏢 Gym", "🏠 Home", "🌳 Outdoors", "🔀 Mix", "🌍 All"]
            },
        }
    },
    
    7: {
        "title": "🎯 Your Goals",
        "section": "🎯 Your Goals",
        "questions": {
            "main_goal": {
                "text": "🎯 Main goal?",
                "type": "buttons",
                "required": True,
                "options": ["📉 Lose weight", "💪 Build muscle", "⚡ Get stronger", "❤️ Better health", "✨ All"]
            },
            "timeline": {
                "text": "⏱️ Timeline?",
                "type": "buttons",
                "required": True,
                "options": ["🚀 1 month", "📅 3 months", "📅 6 months", "📅 1 year", "📅 1+ year"]
            },
            "commitment": {
                "text": "📅 Training days/week?",
                "type": "buttons",
                "required": True,
                "options": ["1️⃣ 1", "2️⃣ 2", "3️⃣ 3", "4️⃣ 4", "5️⃣ 5", "6️⃣ 6", "7️⃣ 7"]
            },
        }
    },
    
    8: {
        "title": "🤝 Ready?",
        "section": "🤝 Commitment",
        "questions": {
            "ready": {
                "text": "🚀 Ready to START?",
                "type": "buttons",
                "required": True,
                "options": ["🔥 YES! 100%!", "✅ Yes, somewhat", "🤔 Maybe", "⏳ Not yet"]
            },
        }
    },
}

class UserSession:
    def __init__(self):
        self.current_screen = 1
        self.current_inputs = {}
        self.all_answers = {}
        self.name = None
        self.pending_text_fields = []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    context.user_data[user_id] = UserSession()
    
    text = """🤖 ╔════════════════════════════════════════╗
   ║  WELCOME TO MEALZY COACH! 🎉           ║
   ║                                         ║
   ║  💪 Transform Your Body               ║
   ║  🧠 Transform Your Mind               ║
   ║  ✨ Transform Your Life               ║
   ╚════════════════════════════════════════╝

📋 Quick Assessment (7 minutes!)
✅ 8 Grouped Question Screens
✅ Clear separation between groups
✅ See your answers in chat
✅ Fast & Easy
🎯 Your Personalized Plan

Let's go! 🚀"""
    
    keyboard = [[InlineKeyboardButton("🎯 START NOW!", callback_data="start")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def show_screen(update: Update, context: ContextTypes.DEFAULT_TYPE, query=None):
    user_id = update.effective_user.id
    
    if user_id not in context.user_data:
        await start(update, context)
        return
    
    session = context.user_data[user_id]
    screen_num = session.current_screen
    
    if screen_num > 8:
        final_msg = f"""🎉 ╔════════════════════════════════════════╗
   ║  ASSESSMENT COMPLETE! 🏆               ║
   ╚════════════════════════════════════════╝

👋 {session.name or 'Champion'}! You did it! 💪

Assessment finished! ⚡

Your fitness profile is READY!
Coaches creating your plan NOW!

📊 Next:
✅ Health score calculated
✅ Custom plan generated
✅ Transform begins!

Thank you! 🙏
Ready to CHANGE YOUR LIFE? 🚀"""
        await update.message.reply_text(final_msg)
        return
    
    screen = SCREENS[screen_num]
    progress = int((screen_num / 8) * 100)
    bar = "█" * (progress // 5) + "░" * (20 - (progress // 5))
    
    text = f"{bar} {progress}%\n\n{screen['title']}\n\n"
    
    # Get text fields that need answers
    text_fields = [k for k, v in screen['questions'].items() if v['type'] == 'text']
    unanswered_text = [k for k in text_fields if k not in session.current_inputs]
    
    session.pending_text_fields = unanswered_text
    
    # Build buttons - GROUP BY QUESTION WITH CLEAR SEPARATION
    buttons = []
    
    for field_key, q_data in screen['questions'].items():
        # Skip answered text fields
        if q_data['type'] == 'text' and field_key in session.current_inputs:
            continue
        
        # Add question text
        text += f"{q_data['text']}\n"
        
        # Add buttons for this question
        if q_data['type'] in ['buttons', 'buttons_multi']:
            options = q_data['options']
            for i, opt in enumerate(options):
                button = InlineKeyboardButton(opt, callback_data=f"ans_{screen_num}_{field_key}_{i}")
                
                # 2 buttons per row
                if not buttons or len(buttons[-1]) >= 2:
                    buttons.append([button])
                else:
                    buttons[-1].append(button)
            
            # Add spacing after question group
            text += "\n"
        elif q_data['type'] == 'text':
            text += f"*(Type in chat)*\n\n"
    
    # Next button
    buttons.append([InlineKeyboardButton("✅ NEXT →", callback_data=f"next_{screen_num}")])
    
    markup = InlineKeyboardMarkup(buttons)
    
    if query:
        try:
            await query.edit_message_text(text, reply_markup=markup)
        except:
            pass
    else:
        await update.message.reply_text(text, reply_markup=markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    
    if user_id not in context.user_data:
        await start(update, context)
        return
    
    await query.answer()
    session = context.user_data[user_id]
    data = query.data
    
    if data == "start":
        session.current_screen = 1
        await show_screen(update, context, query)
        return
    
    if data.startswith("ans_"):
        parts = data.split("_")
        screen_num = int(parts[1])
        field_key = parts[2]
        ans_idx = int(parts[3])
        
        screen = SCREENS[screen_num]
        q_data = screen['questions'][field_key]
        answer = q_data['options'][ans_idx]
        
        session.current_inputs[field_key] = answer
        session.all_answers[field_key] = answer
        
        fun_msg = random.choice(FUN_RESPONSES)
        await query.answer(fun_msg, show_alert=False)
        
        # Show answer in chat (history)
        q_text = q_data['text'].replace("?", "").strip()
        await update.callback_query.message.reply_text(f"✅ {q_text}: {answer}")
        
        await asyncio.sleep(0.5)
        await show_screen(update, context, query)
        
    if data.startswith("next_"):
        screen_num = int(data.split("_")[1])
        screen = SCREENS[screen_num]
        
        # Check all required fields answered
        for field_key, q_data in screen['questions'].items():
            if q_data['required'] and field_key not in session.current_inputs:
                await query.answer("⚠️ Answer all questions first!", show_alert=True)
                return
        
        session.current_screen += 1
        session.current_inputs = {}
        session.pending_text_fields = []
        await show_screen(update, context, query)

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id not in context.user_data:
        await start(update, context)
        return
    
    session = context.user_data[user_id]
    screen_num = session.current_screen
    screen = SCREENS[screen_num]
    text = update.message.text.strip()
    
    if not session.pending_text_fields:
        return
    
    field_key = session.pending_text_fields[0]
    q_data = screen['questions'][field_key]
    
    session.current_inputs[field_key] = text
    session.all_answers[field_key] = text
    
    # Show answer in chat (history)
    q_text = q_data['text'].replace("?", "").strip()
    if field_key == 'name':
        session.name = text
        await update.message.reply_text(f"✅ {q_text}: {text}")
    else:
        await update.message.reply_text(f"✅ {q_text}: {text}")
    
    session.pending_text_fields.pop(0)
    
    await asyncio.sleep(1)
    await show_screen(update, context)

def main():
    print("\n" + "=" * 70)
    print("✅ GROUPED + CHAT HISTORY BOT")
    print("=" * 70)
    print("✅ Group 3-4 related questions per screen")
    print("✅ Clear separation between groups")
    print("✅ Show answers in chat (history)")
    print("✅ Fast & engaging")
    print("=" * 70)
    
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    
    print("🚀 BOT RUNNING!\n")
    app.run_polling()

if __name__ == "__main__":
    main()
