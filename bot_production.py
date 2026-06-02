#!/usr/bin/env python3
"""
COACH AVNI BOT - SMOOTH FLOW VERSION (61 QUESTIONS WITH COMBINED WORK & DETAILS)
✅ Fun response → Next question (same message flow)
✅ Consolidated Screen 5 & 6 ("Work & Details")
✅ Beautiful layout grid with validation checks
✅ Full 61 questions fully preserved
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

# ============================================================================
# FUN RESPONSES
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
# ALL 61 CORE CORE SURVEY QUESTIONS
# ============================================================================
QUESTIONS = {
    1: {"type": "text", "text": "👤 What's your full name?", "section": "👤 About You", "fun_key": "general"},
    2: {"type": "text", "text": "🎂 What's your age?", "section": "👤 About You", "fun_key": "general"},
    3: {"type": "text", "text": "📏 Current height (cm)?", "section": "👤 About You", "fun_key": "general"},
    4: {"type": "text", "text": "⚖️ Current weight (kg)?", "section": "👤 About You", "fun_key": "general"},
    
    # Combined Grouped Module items (Index 5 & 6)
    5: {"type": "buttons", "text": "💼 What's your profession?", "section": "👤 About You", "fun_key": "work_time",
        "options": ["💻 Software Eng", "👨‍⚕️ Doctor", "📚 Student", "🏫 Teacher", "👔 Business", "🤵 Consultant", "🏥 Healthcare", "📊 Finance", "🎯 Sales", "➕ Other"]},
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
        "options":
