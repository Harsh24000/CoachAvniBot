#!/usr/bin/env python3
"""
COACH AVNI BOT - PRODUCTION VERSION
✅ Fun response → Next question (same message flow)
✅ NO intermediate text
✅ Clean button layouts
✅ Zero syntax issues
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
    print("ERROR: TELEGRAM_TOKEN not found in environment variables.")
    sys.exit(1)

# ============================================================================
# FUN RESPONSES (Categorized Dictionary)
# ============================================================================
FUN_RESPONSES = {
    "wake_time": [
        "🌅 Early bird or night owl? We know! 😄",
        "☀️ Serious dedication to life!",
        "⏰ Morning person energy STRONG! 💪",
        "🛏️ Those extra 30 mins hit different! 😴",
        "🌄 Sunrise warrior spotted! ☀️",
    ],
    "breakfast": [
        "🍳 Breakfast of champions! 💪",
        "☕ Wake up and smell the coffee!",
        "🥐 Breaking the fast like a boss!",
        "🍲 Your digestive system thanks you! 🙏",
        "🥣 Fuel up! 🔋",
    ],
    "work_time": [
        "💼 9 to 5 grind! Let's go!",
        "🏢 Make those spreadsheets shine! ✨",
        "🚀 Work mode: ACTIVATED! 🎯",
        "👨‍💼 Show that office who's boss!",
        "⏱️ Dominate the day! 💪",
    ],
    "lunch": [
        "🍽️ Lunch break = victory time! 🏆",
        "🍱 Fueling up for the grind!",
        "🥗 Feed yourself like a legend!",
        "😋 Mid-day snack APPROVED! ✅",
        "🍜 Lunch time = YOU time! 🎉",
    ],
    "dinner": [
        "🍽️ Final meal - make it count! 👑",
        "🍕 Dinner satisfaction loading... 😋",
        "🥘 Best meal incoming!",
        "🍗 Evening fuel! 🌙",
        "🍲 Your taste buds will party! 🎉",
    ],
    "sleep": [
        "😴 Beauty sleep incoming! 💤",
        "🛏️ Recharge time! 🔋",
        "🌙 Sweet dreams! ✨",
        "😪 Your body deserves this!",
        "🛌 Best meditation ever! 🧘‍♂️",
    ],
    "snacks": [
        "🍿 Snack game: UNLOCKED! 🔓",
        "🥜 Mid-day munchies are REAL! 😄",
        "🍌 Real MVP of the day! 💪",
        "🍪 Guilt-free snacking! 😉",
        "🍩 Snack breaks FTW! 😋",
    ],
    "fitness": [
        "💪 Getting fit like a BOSS! 🦾",
        "🏋️ Iron pumper spotted! 🏋️‍♂️",
        "🚴 Cardio legend incoming! 🏃‍♂️",
        "🤸 Flexibility = Life goals! 🧘",
        "⛹️ Athletic vibes! 🏀",
    ],
    "stress": [
        "😰 Stress = Life testing you! 💪",
        "🧘 Find your zen! ☮️",
        "😅 Stress levels: Real but manageable!",
        "🎯 You got this! 🚀",
        "💆 Time to relax! ☮️",
    ],
    "sleep_quality": [
        "😴 Quality sleep = Quality life! ✨",
        "🛌 Your body rebuilding! 🧬",
        "💤 Sleep like a baby! ⚔️",
        "🌙 Protect sleep like snacks! 🛡️",
        "😪 Underrated superpower! 🦸",
    ],
    "goals": [
        "🎯 GOAL-GETTER ENERGY! 🚀",
        "💪 That's a SOLID goal!",
        "🏆 Championship mindset! 🥇",
        "✨ Your future self celebrating!",
        "🔥 YOUR transformation! 📖",
    ],
    "commitment": [
        "🤝 LOVE that commitment! 💪",
        "🎯 This energy? PERFECT! 🚀",
        "💯 All-in mentality? YES! 🔥",
        "⚡ Ready to change life? LET'S GO! 🚀",
        "🏆 Champions are made! 👑",
    ],
    "general": [
        "✅ Crushing it! 🚀",
        "💯 Love the honesty! Let's keep rolling! 🎢",
        "⚡ On FIRE! 🔥",
        "🎯 Perfect! Moving forward! 👉",
        "✨ Nailed it! 👇",
    ]
}

# ============================================================================
# QUESTIONS (61-Question Dictionary)
# ============================================================================
QUESTIONS = {
    1: {"type": "text", "text": "👤 What's your full name?", "section": "👤 About You", "fun_key": "general"},
    2: {"type": "text", "text": "🎂 What's your age?", "section": "👤 About You", "fun_key": "general"},
    3: {"type": "text", "text": "📏 Current height (cm)?", "section": "👤 About You", "fun_key": "general"},
    4: {"type": "text", "text": "⚖️ Current weight (kg)?", "section": "👤 About You", "fun_key": "general"},
    5: {"type": "buttons", "text": "💼 What's your profession?", "section": "👤 About You", "fun_key": "work_time",
        "options": ["💻 Software Engineer", "👨‍⚕️ Doctor", "📚 Student", "🏫 Teacher", "👔 Business Owner", "🤵 Consultant", "🏥 Healthcare", "📊 Finance", "🎯 Sales", "➕ Other"]},
    6: {"type": "buttons", "text": "⚡ Biological sex?", "section": "👤 About You", "fun_key": "general",
        "options": ["👨 Male", "👩 Female", "🌈 Other"]},
    7: {"type": "buttons", "text": "🍽️ Dietary preference?", "section": "🍽️ Diet & Food", "fun_key": "breakfast",
        "options": ["🍗 Non-Vegetarian", "🥕 Vegetarian", "🥚 Eggetarian", "🌱 Vegan", "☪️ Jain"]},
    8: {"type": "buttons_custom", "text": "🚫 Foods you HATE?", "section": "🍽️ Diet & Food", "fun_key": "snacks",
        "options": ["🥒 Bitter gourd", "🍆 Eggplant", "🍄 Mushroom", "🪴 Okra", "🌶️ Capsicum", "🧅 Onion", "🧄 Garlic", "🐟 Fish", "🥚 Egg", "🥛 Dairy"]},
    9: {"type": "buttons_custom", "text": "👨‍🍳 Cuisines you LOVE?", "section": "🍽️ Diet & Food", "fun_key": "lunch",
        "options": ["🇮🇳 North Indian", "🔥 South Indian", "🇧🇩 Bengali", "🥘 Gujarati", "🌶️ Continental", "🥡 Chinese", "🍝 Italian", "🌮 Mexican", "🍜 Thai"]},
    10: {"type": "buttons", "text": "🌅 What time do you wake up?", "section": "☀️ Your Day", "fun_key": "wake_time",
        "options": ["⏰ 5:00 AM", "⏰ 5:30 AM", "⏰ 6:00 AM", "⏰ 6:30 AM", "⏰ 7:00 AM", "⏰ 7:30 AM", "⏰ 8:00 AM", "🛏️ 8:30 AM+"]},
    11: {"type": "buttons", "text": "☕ Breakfast time?", "section": "☀️ Your Day", "fun_key": "breakfast",
        "options": ["🌅 6:00 AM", "🌅 6:30 AM", "🌅 7:00 AM", "🌅 7:30 AM", "🌅 8:00 AM", "🌅 8:30 AM", "🌅 9:00 AM", "⏭️ Skip"]},
    12: {"type": "buttons", "text": "🏢 Work start time?", "section": "☀️ Your Day", "fun_key": "work_time",
        "options": ["🕐 8:00 AM", "🕐 8:30 AM", "🕐 9:00 AM", "🕐 9:30 AM", "🕐 10:00 AM", "🎲 Variable"]},
    13: {"type": "buttons", "text": "🚪 Work end time?", "section": "☀️ Your Day", "fun_key": "work_time",
        "options": ["🕔 5:00 PM", "🕔 5:30 PM", "🕔 6:00 PM", "🕔 6:30 PM", "🕔 7:00 PM", "🕔 8:00 PM", "🌙 9:00 PM+"]},
    14: {"type": "buttons", "text": "🍽️ Lunch time?", "section": "☀️ Your Day", "fun_key": "lunch",
        "options": ["🕛 12:00 PM", "🕛 12:30 PM", "🕛 1:00 PM", "🕛 1:30 PM", "🕛 2:00 PM", "🕛 2:30 PM", "🎲 Variable"]},
    15: {"type": "buttons", "text": "🍴 Dinner time?", "section": "☀️ Your Day", "fun_key": "dinner",
        "options": ["🕕 6:00 PM", "🕕 6:30 PM", "🕕 7:00 PM", "🕕 7:30 PM", "🕕 8:00 PM", "🕕 8:30 PM", "🕕 9:00 PM", "🕘 9:30 PM+"]},
    16: {"type": "buttons", "text": "😴 Sleep time?", "section": "☀️ Your Day", "fun_key": "sleep",
        "options": ["🌙 9:00 PM", "🌙 9:30 PM", "🌙 10:00 PM", "🌙 10:30 PM", "🌙 11:00 PM", "🌙 11:30 PM", "🌙 12:00 AM", "🌙 12:30 AM+"]},
    17: {"type": "buttons", "text": "🍿 Snacks during the day?", "section": "☀️ Your Day", "fun_key": "snacks",
        "options": ["✅ Yes, 1-2 times", "✅ Yes, 3+ times", "⏱️ Rarely", "🚫 No"]},
    18: {"type": "buttons", "text": "🍕 Eat out for meals?", "section": "☀️ Your Day", "fun_key": "lunch",
        "options": ["🍽️ Never", "🥗 Breakfast", "🍜 Lunch", "🍛 Dinner", "🎉 Multiple meals"]},
    19: {"type": "buttons", "text": "😴 Weekend wake time?", "section": "☀️ Your Day", "fun_key": "wake_time",
        "options": ["Same as weekday ⏰", "30 min later 😴", "1 hour later 💤", "1.5 hours later 🛌", "2+ hours later 🌙"]},
    20: {"type": "buttons", "text": "🛏️ Weekend sleep time?", "section": "☀️ Your Day", "fun_key": "sleep",
        "options": ["Same as weekday 🌙", "30 min later 😴", "1 hour later 💤", "1.5 hours later 🛌", "2+ hours later 🛏️"]},
    21: {"type": "buttons_custom", "text": "⚕️ Medical conditions?", "section": "🏥 Health", "fun_key": "general",
        "options": ["🔬 Diabetes", "🧬 Thyroid", "🔴 PCOS/PCOD", "❤️ Hypertension", "⚠️ High Cholesterol", "🍗 Fatty Liver", "✅ None"]},
    22: {"type": "buttons", "text": "🤧 Any allergies?", "section": "🏥 Health", "fun_key": "general",
        "options": ["✅ No", "🍔 Food allergies", "🌫️ Environmental", "🔀 Both"]},
    23: {"type": "buttons", "text": "💊 On medications?", "section": "🏥 Health", "fun_key": "general",
        "options": ["✅ No", "1-2 medications 💊", "3-4 medications 💉", "5+ medications 🏥"]},
    24: {"type": "buttons", "text": "🤢 Digestive issues?", "section": "🏥 Health", "fun_key": "general",
        "options": ["✅ No", "Sometimes 😐", "Often 😕", "Frequently 😣"]},
    25: {"type": "buttons", "text": "🤕 Got any injuries?", "section": "🏥 Health", "fun_key": "general",
        "options": ["✅ No", "Old injury (healed) 🩹", "Current injury ⚠️"]},
    26: {"type": "buttons", "text": "📍 Injury location?", "section": "🏥 Health", "fun_key": "general",
        "options": ["🔴 Lower back", "🔴 Knee", "🔴 Shoulder", "🔴 Elbow", "🔴 Wrist", "🔴 Multiple", "✅ N/A"]},
    27: {"type": "buttons", "text": "💊 Do you take supplements?", "section": "⚡ Supplements & Habits", "fun_key": "general",
        "options": ["❌ No", "✅ Yes, 1-2", "✅ Yes, 3-5", "✅ Yes, 5+"]},
    28: {"type": "buttons", "text": "🥛 Protein powder experience?", "section": "⚡ Supplements & Habits", "fun_key": "fitness",
        "options": ["👶 Never", "💪 Using now", "📦 Used before"]},
    29: {"type": "buttons", "text": "🚬 Do you smoke?", "section": "⚡ Supplements & Habits", "fun_key": "general",
        "options": ["✅ No", "🚭 Occasionally", "⚠️ Regularly"]},
    30: {"type": "buttons", "text": "🍷 Do you drink alcohol?", "section": "⚡ Supplements & Habits", "fun_key": "general",
        "options": ["✅ No", "🍻 Occasionally", "📅 Weekly", "🎉 Multiple times/week"]},
    31: {"type": "buttons", "text": "🍕 Eating out frequency?", "section": "⚡ Supplements & Habits", "fun_key": "lunch",
        "options": ["❌ Never", "1x/week 🍽️", "2-3x/week 🍜", "4-5x/week 🍛", "☀️ Daily"]},
    32: {"type": "buttons", "text": "😰 Rate daily stress (1-5)", "section": "😴 Sleep & Stress", "fun_key": "stress",
        "options": ["😊 1 (Chill)", "🙂 2", "😐 3 (Neutral)", "😕 4", "😫 5 (Insane)"]},
    33: {"type": "buttons", "text": "💤 Rate sleep quality (1-5)", "section": "😴 Sleep & Stress", "fun_key": "sleep_quality",
        "options": ["😴 1 (Terrible)", "😴 2", "😴 3 (Okay)", "😴 4", "😴 5 (Perfect!)"]},
    34: {"type": "buttons", "text": "😖 Is sleep restless?", "section": "😴 Sleep & Stress", "fun_key": "sleep_quality",
        "options": ["✅ No", "Sometimes 😐", "Often 😕", "Always 😣"]},
    35: {"type": "buttons", "text": "🌅 Wake up feeling fresh?", "section": "😴 Sleep & Stress", "fun_key": "wake_time",
        "options": ["✅ Always", "😊 Usually", "😐 Sometimes", "😴 Rarely"]},
    36: {"type": "buttons", "text": "🧘 Do you meditate?", "section": "😴 Sleep & Stress", "fun_key": "stress",
        "options": ["❌ No", "🙏 Rarely", "🧘 Sometimes", "✅ Regularly"]},
    37: {"type": "buttons", "text": "🔥 What stresses you most?", "section": "😴 Sleep & Stress", "fun_key": "stress",
        "options": ["💼 Work", "❤️ Health", "💔 Relationships", "💰 Money", "⏰ Time", "🌪️ Multiple", "😊 Nothing"]},
    38: {"type": "buttons", "text": "💪 Days/week physically active?", "section": "💪 Fitness", "fun_key": "fitness",
        "options": ["😴 0 (Lazy)", "🚶 1-2", "🏃 3-4", "🏋️ 5-6", "⚡ 7 (Daily)"]},
    39: {"type": "buttons", "text": "🏋️ Strength training exp?", "section": "💪 Fitness", "fun_key": "fitness",
        "options": ["👶 None", "🌱 Beginner", "💪 Intermediate", "🦾 Advanced"]},
    40: {"type": "buttons", "text": "🏋️ Weight training frequency?", "section": "💪 Fitness", "fun_key": "fitness",
        "options": ["❌ Never", "1-2x/week 💪", "3-4x/week 🏋️", "5-6x/week 🦾", "Daily ⚡"]},
    41: {"type": "buttons", "text": "🏃 Cardio frequency?", "section": "💪 Fitness", "fun_key": "fitness",
        "options": ["❌ Never", "1-2x/week 🚴", "3-4x/week 🏃", "5-6x/week 🤸", "Daily 🚀"]},
    42: {"type": "buttons", "text": "🧘 Yoga/stretching frequency?", "section": "💪 Fitness", "fun_key": "fitness",
        "options": ["❌ Never", "1-2x/week 🧘", "3-4x/week 🤸", "5-6x/week 🙏", "Daily ✨"]},
    43: {"type": "buttons", "text": "⚽ Sports/fun activities?", "section": "💪 Fitness", "fun_key": "fitness",
        "options": ["❌ No", "1-2x/week ⚽", "3-4x/week 🏀", "5-6x/week 🎾", "Daily 🏐"]},
    44: {"type": "buttons", "text": "🪑 Hours sitting per day?", "section": "💪 Fitness", "fun_key": "general",
        "options": ["🚶 0-2 hours", "😐 2-4 hours", "😴 4-6 hours", "😵 6-8 hours", "💀 8+ hours"]},
    45: {"type": "buttons", "text": "📍 Preferred workout spot?", "section": "💪 Fitness", "fun_key": "fitness",
        "options": ["🏢 Gym", "🏠 Home", "🌳 Outdoors", "🔀 Gym & Home", "🌍 Mix all"]},
    46: {"type": "buttons", "text": "👨‍🍳 How often do you cook?", "section": "👨‍🍳 Food & Cooking", "fun_key": "lunch",
        "options": ["❌ Never", "1-2x/week 🍳", "3-4x/week 🥘", "5-6x/week 👨‍🍳", "Daily 🍲"]},
    47: {"type": "buttons", "text": "💰 Food budget preference?", "section": "👨‍🍳 Food & Cooking", "fun_key": "lunch",
        "options": ["💸 Budget-friendly", "💵 Moderate", "💎 Premium", "🤷 No preference"]},
    48: {"type": "buttons", "text": "📦 Can you meal prep?", "section": "👨‍🍳 Food & Cooking", "fun_key": "lunch",
        "options": ["✅ Yes", "Sometimes 😐", "Rarely 😕", "❌ No"]},
    49: {"type": "buttons", "text": "🎯 PRIMARY goal?", "section": "🎯 Your Goals", "fun_key": "goals",
        "options": ["📉 Lose weight", "💪 Build muscle", "⚡ Get stronger", "🏃 Endurance", "❤️ Better health", "✨ All of above"]},
    50: {"type": "buttons", "text": "📊 Target weight loss?", "section": "🎯 Your Goals", "fun_key": "goals",
        "options": ["5 kg 📉", "10 kg 📉", "15 kg 📉", "20+ kg 📉", "N/A ✅"]},
    51: {"type": "buttons", "text": "⏱️ Timeline for goal?", "section": "🎯 Your Goals", "fun_key": "goals",
        "options": ["🚀 1 month", "📅 3 months", "📅 6 months", "📅 1 year", "📅 1+ year"]},
    52: {"type": "buttons", "text": "🔄 Tried before?", "section": "🎯 Your Goals", "fun_key": "general",
        "options": ["❌ No", "✅ Once", "✅ 2-3 times", "✅ Many times"]},
    53: {"type": "buttons", "text": "🚧 BIGGEST barrier?", "section": "🎯 Your Goals", "fun_key": "stress",
        "options": ["⏰ Time", "💰 Money", "😴 Motivation", "👥 Support", "📚 Knowledge", "🌀 Multiple", "✨ None"]},
    54: {"type": "buttons", "text": "🏆 Worked with coach before?", "section": "🎯 Your Goals", "fun_key": "goals",
        "options": ["❌ No", "📱 Online", "👨‍🏫 In-person", "🔀 Both"]},
    55: {"type": "buttons", "text": "🥗 Change eating habits?", "section": "🎯 Your Goals", "fun_key": "lunch",
        "options": ["🔥 Big changes", "⚡ Moderate", "🌱 Small", "💤 Minimal"]},
    56: {"type": "buttons", "text": "💪 Willing to exercise?", "section": "🎯 Your Goals", "fun_key": "fitness",
        "options": ["✅ 7 days/week", "✅ 5-6 days", "✅ 3-4 days", "😐 1-2 days"]},
    57: {"type": "buttons", "text": "📅 Days/week training?", "section": "🤝 Commitment", "fun_key": "commitment",
        "options": ["1️⃣ 1 day", "2️⃣ 2 days", "3️⃣ 3 days", "4️⃣ 4 days", "5️⃣ 5 days", "6️⃣ 6 days", "7️⃣ 7 days"]},
    58: {"type": "buttons", "text": "🍕 Reduce eating out?", "section": "🤝 Commitment", "fun_key": "commitment",
        "options": ["✅ Yes", "😐 Somewhat", "❌ No"]},
    59: {"type": "buttons", "text": "🍷 Reduce drinking?", "section": "🤝 Commitment", "fun_key": "commitment",
        "options": ["✅ Yes", "😐 Somewhat", "❌ No"]},
    60: {"type": "buttons", "text": "📝 Keep food journal?", "section": "🤝 Commitment", "fun_key": "commitment",
        "options": ["✅ Yes", "Sometimes 😐", "❌ No"]},
    61: {"type": "buttons", "text": "🚀 Ready to START?", "section": "🤝 Commitment", "fun_key": "commitment",
        "options": ["🔥 YES! 100%!", "✅ Yes, somewhat", "🤔 Maybe", "⏳ Not yet"]},
}

class UserSession:
    def __init__(self):
        self.current_q = 1
        self.answers = {}
        self.name = None
        self.waiting_custom = None

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

📋 Complete Fitness Assessment
✅ 61 FUN Questions (Zero Boring!)
✅ ZERO Typing (Just Click!)
🎯 Your Personalized Plan

Let's make this FUN! 🚀"""
    
    keyboard = [[InlineKeyboardButton("🎯 LET'S GO! START NOW!", callback_data="start")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE, query=None):
    user_id = update.effective_user.id
    
    if user_id not in context.user_data:
        await start(update, context)
        return
    
    session = context.user_data[user_id]
    q_num = session.current_q
    
    if q_num > 61:
        final_msg = f"""🎉 ╔════════════════════════════════════════╗
   ║  ASSESSMENT COMPLETE! 🏆               ║
   ╚════════════════════════════════════════╝

👋 {session.name or 'Champion'}! You crushed it! 💪

Your fitness profile is ready! Our coaches are on it."""
        if query:
            await query.edit_message_text(final_msg)
        else:
            await update.message.reply_text(final_msg)
        return
    
    question = QUESTIONS[q_num]
    section = question.get("section", "")
    progress = int(((q_num - 1) / 61) * 100)
    bar = "█" * (progress // 5) + "░" * (20 - (progress // 5))
    
    name_part = f"\n👋 Hey {session.name}" if session.name else ""
    text = f"{bar} {progress}% | {section}{name_part}\n\n{question['text']}"
    
    if question['type'] == 'text':
        if query:
            await query.edit_message_text(text)
        else:
            await update.message.reply_text(text)
        return
    
    # Clean Grid Layout formatting (2 items per row max)
    buttons = []
    current_row = []
    for i, opt in enumerate(question['options']):
        button = InlineKeyboardButton(opt, callback_data=f"a_{q_num}_{i}")
        current_row.append(button)
        if len(current_row) == 2:
            buttons.append(current_row)
            current_row = []
    if current_row:
        buttons.append(current_row)
        
    if question['type'] == 'buttons_custom':
        buttons.append([InlineKeyboardButton("✏️ Custom Answer", callback_data=f"c_{q_num}")])
    
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
        session.current_q = 1
        await ask_question(update, context, query)
        return
    
    if data.startswith("a_"):
        parts = data.split("_")
        q_num = int(parts[1])
        ans_idx = int(parts[2])
        
        question = QUESTIONS[q_num]
        answer = question['options'][ans_idx]
        session.answers[q_num] = answer
        session.current_q = q_num + 1
        
        fun_key = question.get("fun_key", "general")
        fun_responses = FUN_RESPONSES.get(fun_key, FUN_RESPONSES["general"])
        fun_msg = random.choice(fun_responses)
        
        response_msg = f"✅ Thanks, {session.name}!\n{fun_msg}" if session.name else f"✅ {fun_msg}"
        
        await query.edit_message_text(response_msg)
        await asyncio.sleep(1.5)
        await ask_question(update, context, query)
        return
    
    if data.startswith("c_"):
        q_num = int(data.split("_")[1])
        session.waiting_custom = q_num
        await query.edit_message_text("📝 Type your custom answer below:")

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in context.user_data:
        await start(update, context)
        return
        
    session = context.user_data[user_id]
    text = update.message.text.strip()
    
    if session.waiting_custom:
        q_num = session.waiting_custom
        session.answers[q_num] = text
        session.waiting_custom = None
        session.current_q = q_num + 1
        
        fun_msg = random.choice(FUN_RESPONSES["general"])
        response_msg = f"✅ Thanks, {session.name}!\n{fun_msg}\n\n📝 \"{text}\" - Noted!" if session.name else f"✅ {fun_msg}\n\n📝 \"{text}\" - Noted!"
        
        await update.message.reply_text(response_msg)
        await asyncio.sleep(1.5)
        await ask_question(update, context)
        return
    
    q_num = session.current_q
    
    if q_num == 1:
        session.name = text
    elif q_num == 2:
        try:
            age = int(text)
            if not 13 <= age <= 100:
                await update.message.reply_text("❌ Age should be between 13 and 100! Try again:")
                return
        except ValueError:
            await update.message.reply_text("❌ That's not a valid number! 🤔 Try again:")
            return
            
    session.answers[q_num] = text
    session.current_q += 1
    
    fun_msg = random.choice(FUN_RESPONSES["general"])
    response_msg = f"✅ Thanks, {session.name}!\n{fun_msg}" if session.name else f"✅ {fun_msg}"
    
    await update.message.reply_text(response_msg)
    await asyncio.sleep(1.5)
    await ask_question(update, context)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    print("🚀 BOT PRODUCTION INSTANCE RUNNING...")
    app.run_polling()

if __name__ == "__main__":
    main()
