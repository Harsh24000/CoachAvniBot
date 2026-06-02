#!/usr/bin/env python3
"""
COACH AVNI BOT - ONE QUESTION PER SCREEN
✅ ONE question per screen only
✅ ZERO confusion
✅ Crystal clear
✅ No mixing
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
    "🔥 Crushing it! Next!",
    "💯 Love it!",
    "⚡ Perfect!",
    "🎯 Got it!",
    "✨ Amazing!",
    "🚀 Moving on!",
    "💪 Strong!",
    "👏 Great!",
]

# ============================================================================
# QUESTIONS - ONE PER SCREEN (No mixing)
# ============================================================================

QUESTIONS = [
    # Screen 1-4: Basic Info (Text)
    {"screen": 1, "section": "👤 About You", "question": "👤 What's your full name?", "type": "text", "required": True},
    {"screen": 2, "section": "👤 About You", "question": "🎂 What's your age?", "type": "text", "required": True},
    {"screen": 3, "section": "👤 About You", "question": "📏 Height (cm)?", "type": "text", "required": True},
    {"screen": 4, "section": "👤 About You", "question": "⚖️ Weight (kg)?", "type": "text", "required": True},
    
    # Screen 5: Profession
    {"screen": 5, "section": "👤 About You", "question": "💼 What's your profession?", "type": "buttons", "required": True,
     "options": ["💻 Software Eng", "👨‍⚕️ Doctor", "📚 Student", "🏫 Teacher", "👔 Business", "🤵 Consultant", "🏥 Healthcare", "📊 Finance", "🎯 Sales", "➕ Other"]},
    
    # Screen 6: Biological sex
    {"screen": 6, "section": "👤 About You", "question": "⚡ Biological sex?", "type": "buttons", "required": True,
     "options": ["👨 Male", "👩 Female", "🌈 Other"]},
    
    # Screen 7: Dietary preference
    {"screen": 7, "section": "🍽️ Diet & Food", "question": "🍽️ Dietary preference?", "type": "buttons", "required": True,
     "options": ["🍗 Non-Veg", "🥕 Vegetarian", "🥚 Eggetarian", "🌱 Vegan", "☪️ Jain"]},
    
    # Screen 8: Disliked foods
    {"screen": 8, "section": "🍽️ Diet & Food", "question": "🚫 Foods you HATE? (select multiple or skip)", "type": "buttons_multi", "required": False,
     "options": ["🥒 Bitter gourd", "🍆 Eggplant", "🍄 Mushroom", "🪴 Okra", "🌶️ Capsicum", "🧅 Onion", "🧄 Garlic", "🐟 Fish", "🥚 Egg", "🥛 Dairy"]},
    
    # Screen 9: Cuisines
    {"screen": 9, "section": "🍽️ Diet & Food", "question": "👨‍🍳 Cuisines you LOVE? (select multiple or skip)", "type": "buttons_multi", "required": False,
     "options": ["🇮🇳 North Indian", "🔥 South Indian", "🇧🇩 Bengali", "🥘 Gujarati", "🌶️ Continental", "🥡 Chinese", "🍝 Italian", "🌮 Mexican", "🍜 Thai"]},
    
    # Screen 10: Wake time
    {"screen": 10, "section": "☀️ Your Day", "question": "🌅 What time do you wake up?", "type": "buttons", "required": True,
     "options": ["⏰ 5:00", "⏰ 5:30", "⏰ 6:00", "⏰ 6:30", "⏰ 7:00", "⏰ 7:30", "⏰ 8:00", "🛏️ 8:30+"]},
    
    # Screen 11: Breakfast
    {"screen": 11, "section": "☀️ Your Day", "question": "☕ Breakfast time?", "type": "buttons", "required": True,
     "options": ["🌅 6:00", "🌅 6:30", "🌅 7:00", "🌅 7:30", "🌅 8:00", "🌅 8:30", "🌅 9:00", "⏭️ Skip"]},
    
    # Screen 12: Sleep
    {"screen": 12, "section": "☀️ Your Day", "question": "😴 Sleep time?", "type": "buttons", "required": True,
     "options": ["🌙 9:00", "🌙 9:30", "🌙 10:00", "🌙 10:30", "🌙 11:00", "🌙 11:30", "🌙 12:00", "🌙 12:30+"]},
    
    # Screen 13: Medical conditions
    {"screen": 13, "section": "🏥 Health", "question": "⚕️ Any medical conditions? (select or skip)", "type": "buttons_multi", "required": False,
     "options": ["🔬 Diabetes", "🧬 Thyroid", "🔴 PCOS", "❤️ Hypertension", "⚠️ High Cholesterol", "🍗 Fatty Liver", "✅ None"]},
    
    # Screen 14: Allergies
    {"screen": 14, "section": "🏥 Health", "question": "🤧 Any allergies?", "type": "buttons", "required": True,
     "options": ["✅ No", "🍔 Food", "🌫️ Environmental", "🔀 Both"]},
    
    # Screen 15: Injuries
    {"screen": 15, "section": "🏥 Health", "question": "🤕 Any injuries?", "type": "buttons", "required": True,
     "options": ["✅ No", "Old (healed)", "Current"]},
    
    # Screen 16: Active days
    {"screen": 16, "section": "💪 Fitness", "question": "💪 Days per week physically active?", "type": "buttons", "required": True,
     "options": ["😴 0", "🚶 1-2", "🏃 3-4", "🏋️ 5-6", "⚡ 7"]},
    
    # Screen 17: Strength training
    {"screen": 17, "section": "💪 Fitness", "question": "🏋️ Strength training experience?", "type": "buttons", "required": True,
     "options": ["👶 None", "🌱 Beginner", "💪 Intermediate", "🦾 Advanced"]},
    
    # Screen 18: Workout location
    {"screen": 18, "section": "💪 Fitness", "question": "📍 Preferred workout location?", "type": "buttons", "required": True,
     "options": ["🏢 Gym", "🏠 Home", "🌳 Outdoors", "🔀 Gym+Home", "🌍 All"]},
    
    # Screen 19: Main goal
    {"screen": 19, "section": "🎯 Your Goals", "question": "🎯 What's your PRIMARY goal?", "type": "buttons", "required": True,
     "options": ["📉 Lose weight", "💪 Build muscle", "⚡ Get stronger", "🏃 Endurance", "❤️ Better health", "✨ All"]},
    
    # Screen 20: Timeline
    {"screen": 20, "section": "🎯 Your Goals", "question": "⏱️ Timeline for goal?", "type": "buttons", "required": True,
     "options": ["🚀 1 month", "📅 3 months", "📅 6 months", "📅 1 year", "📅 1+ year"]},
    
    # Screen 21: Training days
    {"screen": 21, "section": "🤝 Commitment", "question": "📅 Training days per week?", "type": "buttons", "required": True,
     "options": ["1️⃣ 1", "2️⃣ 2", "3️⃣ 3", "4️⃣ 4", "5️⃣ 5", "6️⃣ 6", "7️⃣ 7"]},
    
    # Screen 22: Ready
    {"screen": 22, "section": "🤝 Commitment", "question": "🚀 Ready to START your transformation?", "type": "buttons", "required": True,
     "options": ["🔥 YES! 100%!", "✅ Yes, somewhat", "🤔 Maybe", "⏳ Not yet"]},
]

class UserSession:
    def __init__(self):
        self.current_question = 0
        self.all_answers = {}
        self.name = None

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

📋 Quick Assessment
✅ 22 Simple Questions
✅ ONE question per screen (CRYSTAL CLEAR!)
✅ NO confusion
✅ Fast & Easy
🎯 Your Personalized Plan

Let's go! 🚀"""
    
    keyboard = [[InlineKeyboardButton("🎯 START NOW!", callback_data="start")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def show_question(update: Update, context: ContextTypes.DEFAULT_TYPE, query=None):
    user_id = update.effective_user.id
    
    if user_id not in context.user_data:
        await start(update, context)
        return
    
    session = context.user_data[user_id]
    q_idx = session.current_question
    
    if q_idx >= len(QUESTIONS):
        final_msg = f"""🎉 ╔════════════════════════════════════════╗
   ║  ASSESSMENT COMPLETE! 🏆               ║
   ╚════════════════════════════════════════╝

👋 {session.name or 'Champion'}! You did it! 💪

Assessment done in record time! ⚡

Your fitness profile is READY!
Coaches creating your plan NOW!

📊 Next:
✅ Health score
✅ Custom plan  
✅ Transform begins!

Thank you! 🙏
Ready to CHANGE YOUR LIFE? 🚀"""
        await update.message.reply_text(final_msg)
        return
    
    q = QUESTIONS[q_idx]
    progress = int((q_idx / len(QUESTIONS)) * 100)
    bar = "█" * (progress // 5) + "░" * (20 - (progress // 5))
    
    text = f"{bar} {progress}%\n\n{q['section']}\n\n{q['question']}\n\n"
    
    if q['type'] == 'text':
        text += "*(Type your answer in chat)*"
        if query:
            await query.edit_message_text(text)
        else:
            await update.message.reply_text(text)
        return
    
    # Buttons
    buttons = []
    for i, opt in enumerate(q['options']):
        button = InlineKeyboardButton(opt, callback_data=f"ans_{q_idx}_{i}")
        
        if len(buttons) == 0 or len(buttons[-1]) >= 2:
            buttons.append([button])
        else:
            buttons[-1].append(button)
    
    # Add skip button for optional questions
    if not q['required']:
        buttons.append([InlineKeyboardButton("⏭️ SKIP", callback_data=f"skip_{q_idx}")])
    
    markup = InlineKeyboardMarkup(buttons)
    
    if query:
        await query.edit_message_text(text, reply_markup=markup)
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
        session.current_question = 0
        await show_question(update, context, query)
        return
    
    if data.startswith("ans_"):
        parts = data.split("_")
        q_idx = int(parts[1])
        ans_idx = int(parts[2])
        
        q = QUESTIONS[q_idx]
        answer = q['options'][ans_idx]
        
        session.all_answers[q_idx] = answer
        
        fun_msg = random.choice(FUN_RESPONSES)
        await query.answer(fun_msg, show_alert=False)
        
        session.current_question += 1
        await asyncio.sleep(0.5)
        await show_question(update, context, query)
    
    if data.startswith("skip_"):
        q_idx = int(data.split("_")[1])
        session.all_answers[q_idx] = "Skipped"
        
        await query.answer("⏭️ Skipped!", show_alert=False)
        
        session.current_question += 1
        await asyncio.sleep(0.5)
        await show_question(update, context, query)

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id not in context.user_data:
        await start(update, context)
        return
    
    session = context.user_data[user_id]
    q_idx = session.current_question
    
    if q_idx >= len(QUESTIONS):
        return
    
    q = QUESTIONS[q_idx]
    text = update.message.text.strip()
    
    session.all_answers[q_idx] = text
    
    if q_idx == 0:  # Name
        session.name = text
        await update.message.reply_text(f"✅ Got your name: {text}! 👋")
    else:
        await update.message.reply_text(f"✅ Saved! 👍")
    
    session.current_question += 1
    
    await asyncio.sleep(1)
    await show_question(update, context)

def main():
    print("\n" + "=" * 70)
    print("✅ ONE QUESTION PER SCREEN BOT")
    print("=" * 70)
    print("✅ ONE question per screen ONLY")
    print("✅ CRYSTAL CLEAR")
    print("✅ ZERO confusion")
    print("✅ 22 simple questions")
    print("=" * 70)
    
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    
    print("🚀 BOT RUNNING!\n")
    app.run_polling()

if __name__ == "__main__":
    main()
