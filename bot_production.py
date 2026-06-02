#!/usr/bin/env python3
"""
COACH AVNI BOT - GROUPED QUESTIONS
✅ Multiple questions per screen
✅ Answer 4-5 at once
✅ Fast completion (5-7 min)
✅ NOT boring
✅ Grouped by topic
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
    "🔥 Crushing it! Next section!",
    "💯 Love the honesty! Keep rolling!",
    "⚡ On FIRE! Next up!",
    "🎯 Perfect answers!",
    "✨ You're doing amazing!",
    "🚀 Moving right along!",
    "💪 Strong start!",
    "👏 Excellent!",
]

# ============================================================================
# GROUPED QUESTION SCREENS (Multiple questions per screen)
# ============================================================================

SCREENS = {
    1: {
        "title": "👤 About You - Basic Info",
        "questions": {
            "name": {"text": "👤 Full name?", "type": "text", "required": True},
            "age": {"text": "🎂 Age?", "type": "text", "required": True},
            "height": {"text": "📏 Height (cm)?", "type": "text", "required": True},
            "weight": {"text": "⚖️ Weight (kg)?", "type": "text", "required": True},
        }
    },
    
    2: {
        "title": "👤 About You - Work & Details",
        "questions": {
            "profession": {"text": "💼 Profession?", "type": "buttons", "required": True,
                "options": ["💻 Software Eng", "👨‍⚕️ Doctor", "📚 Student", "🏫 Teacher", "👔 Business", "🤵 Consultant", "🏥 Healthcare", "📊 Finance", "🎯 Sales", "➕ Other"]},
            "sex": {"text": "⚡ Biological sex?", "type": "buttons", "required": True,
                "options": ["👨 Male", "👩 Female", "🌈 Other"]},
        }
    },
    
    3: {
        "title": "🍽️ Diet & Food",
        "questions": {
            "dietary_pref": {"text": "🍽️ Dietary preference?", "type": "buttons", "required": True,
                "options": ["🍗 Non-Veg", "🥕 Vegetarian", "🥚 Eggetarian", "🌱 Vegan", "☪️ Jain"]},
            "disliked_foods": {"text": "🚫 Foods you HATE? (select multiple)", "type": "buttons_multi", "required": False,
                "options": ["🥒 Bitter gourd", "🍆 Eggplant", "🍄 Mushroom", "🪴 Okra", "🌶️ Capsicum", "🧅 Onion", "🧄 Garlic", "🐟 Fish", "🥚 Egg", "🥛 Dairy"]},
            "cuisines": {"text": "👨‍🍳 Cuisines you LOVE? (select multiple)", "type": "buttons_multi", "required": False,
                "options": ["🇮🇳 North Indian", "🔥 South Indian", "🇧🇩 Bengali", "🥘 Gujarati", "🌶️ Continental", "🥡 Chinese", "🍝 Italian", "🌮 Mexican", "🍜 Thai"]},
        }
    },
    
    4: {
        "title": "☀️ Your Day - Morning & Work",
        "questions": {
            "wake_time": {"text": "🌅 Wake up time?", "type": "buttons", "required": True,
                "options": ["⏰ 5:00", "⏰ 5:30", "⏰ 6:00", "⏰ 6:30", "⏰ 7:00", "⏰ 7:30", "⏰ 8:00", "🛏️ 8:30+"]},
            "breakfast_time": {"text": "☕ Breakfast time?", "type": "buttons", "required": True,
                "options": ["🌅 6:00", "🌅 6:30", "🌅 7:00", "🌅 7:30", "🌅 8:00", "🌅 8:30", "🌅 9:00", "⏭️ Skip"]},
            "work_start": {"text": "🏢 Work start?", "type": "buttons", "required": True,
                "options": ["🕐 8:00", "🕐 8:30", "🕐 9:00", "🕐 9:30", "🕐 10:00", "🎲 Variable"]},
            "work_end": {"text": "🚪 Work end?", "type": "buttons", "required": True,
                "options": ["🕔 5:00", "🕔 5:30", "🕔 6:00", "🕔 6:30", "🕔 7:00", "🕔 8:00", "🌙 9:00+"]},
        }
    },
    
    5: {
        "title": "☀️ Your Day - Meals & Eating",
        "questions": {
            "lunch_time": {"text": "🍽️ Lunch time?", "type": "buttons", "required": True,
                "options": ["🕛 12:00", "🕛 12:30", "🕛 1:00", "🕛 1:30", "🕛 2:00", "🕛 2:30", "🎲 Variable"]},
            "dinner_time": {"text": "🍴 Dinner time?", "type": "buttons", "required": True,
                "options": ["🕕 6:00", "🕕 6:30", "🕕 7:00", "🕕 7:30", "🕕 8:00", "🕕 8:30", "🕕 9:00", "🕘 9:30+"]},
            "sleep_time": {"text": "😴 Sleep time?", "type": "buttons", "required": True,
                "options": ["🌙 9:00", "🌙 9:30", "🌙 10:00", "🌙 10:30", "🌙 11:00", "🌙 11:30", "🌙 12:00", "🌙 12:30+"]},
            "snacks": {"text": "🍿 Snacks per day?", "type": "buttons", "required": True,
                "options": ["✅ 1-2x", "✅ 3+x", "⏱️ Rarely", "🚫 No"]},
            "eating_out": {"text": "🍕 Eat out?", "type": "buttons", "required": True,
                "options": ["🍽️ Never", "1x/week", "2-3x/week", "4-5x/week", "Daily"]},
        }
    },
    
    6: {
        "title": "☀️ Your Day - Weekends",
        "questions": {
            "weekend_wake": {"text": "😴 Weekend wake?", "type": "buttons", "required": True,
                "options": ["Same ⏰", "30min later", "1hr later", "1.5hr later", "2hr+ later"]},
            "weekend_sleep": {"text": "🛏️ Weekend sleep?", "type": "buttons", "required": True,
                "options": ["Same 🌙", "30min later", "1hr later", "1.5hr later", "2hr+ later"]},
        }
    },
    
    7: {
        "title": "🏥 Health - Conditions",
        "questions": {
            "medical_conditions": {"text": "⚕️ Medical conditions? (select if any)", "type": "buttons_multi", "required": False,
                "options": ["🔬 Diabetes", "🧬 Thyroid", "🔴 PCOS", "❤️ Hypertension", "⚠️ High Cholesterol", "🍗 Fatty Liver", "✅ None"]},
            "allergies": {"text": "🤧 Allergies?", "type": "buttons", "required": True,
                "options": ["✅ No", "🍔 Food", "🌫️ Environmental", "🔀 Both"]},
            "medications": {"text": "💊 On medications?", "type": "buttons", "required": True,
                "options": ["✅ No", "1-2 💊", "3-4 💉", "5+ 🏥"]},
            "digestive": {"text": "🤢 Digestive issues?", "type": "buttons", "required": True,
                "options": ["✅ No", "Sometimes", "Often", "Frequently"]},
            "injuries": {"text": "🤕 Injuries?", "type": "buttons", "required": True,
                "options": ["✅ No", "Old (healed)", "Current"]},
        }
    },
    
    8: {
        "title": "⚡ Habits - Supplements & Lifestyle",
        "questions": {
            "supplements": {"text": "💊 Supplements?", "type": "buttons", "required": True,
                "options": ["❌ No", "✅ 1-2", "✅ 3-5", "✅ 5+"]},
            "protein": {"text": "🥛 Protein powder?", "type": "buttons", "required": True,
                "options": ["👶 Never", "💪 Using", "📦 Used"]},
            "smoking": {"text": "🚬 Smoking?", "type": "buttons", "required": True,
                "options": ["✅ No", "Occasionally", "Regularly"]},
            "alcohol": {"text": "🍷 Alcohol?", "type": "buttons", "required": True,
                "options": ["✅ No", "Occasionally", "Weekly", "Multiple/week"]},
        }
    },
    
    9: {
        "title": "😴 Sleep & Stress",
        "questions": {
            "stress_level": {"text": "😰 Daily stress (1-5)?", "type": "buttons", "required": True,
                "options": ["😊 1 (Chill)", "🙂 2", "😐 3", "😕 4", "😫 5 (Insane)"]},
            "sleep_quality": {"text": "💤 Sleep quality (1-5)?", "type": "buttons", "required": True,
                "options": ["😴 1 (Bad)", "😴 2", "😴 3 (OK)", "😴 4", "😴 5 (Perfect)"]},
            "restless_sleep": {"text": "😖 Restless sleep?", "type": "buttons", "required": True,
                "options": ["✅ No", "Sometimes", "Often", "Always"]},
            "wake_refreshed": {"text": "🌅 Wake refreshed?", "type": "buttons", "required": True,
                "options": ["✅ Always", "Usually", "Sometimes", "Rarely"]},
            "meditate": {"text": "🧘 Meditate?", "type": "buttons", "required": True,
                "options": ["❌ No", "Rarely", "Sometimes", "✅ Regularly"]},
        }
    },
    
    10: {
        "title": "💪 Fitness - Activity Level",
        "questions": {
            "active_days": {"text": "💪 Active days/week?", "type": "buttons", "required": True,
                "options": ["😴 0", "🚶 1-2", "🏃 3-4", "🏋️ 5-6", "⚡ 7"]},
            "strength_exp": {"text": "🏋️ Strength training?", "type": "buttons", "required": True,
                "options": ["👶 None", "🌱 Beginner", "💪 Intermediate", "🦾 Advanced"]},
            "strength_freq": {"text": "🏋️ Strength freq?", "type": "buttons", "required": True,
                "options": ["Never", "1-2x/week", "3-4x/week", "5-6x/week", "Daily"]},
            "cardio_freq": {"text": "🏃 Cardio freq?", "type": "buttons", "required": True,
                "options": ["Never", "1-2x/week", "3-4x/week", "5-6x/week", "Daily"]},
            "yoga_freq": {"text": "🧘 Yoga freq?", "type": "buttons", "required": True,
                "options": ["Never", "1-2x/week", "3-4x/week", "5-6x/week", "Daily"]},
        }
    },
    
    11: {
        "title": "💪 Fitness - More Details",
        "questions": {
            "sports": {"text": "⚽ Sports/activities?", "type": "buttons", "required": True,
                "options": ["❌ No", "1-2x/week", "3-4x/week", "5-6x/week", "Daily"]},
            "sitting_hours": {"text": "🪑 Sitting hours/day?", "type": "buttons", "required": True,
                "options": ["🚶 0-2", "😐 2-4", "😴 4-6", "😵 6-8", "💀 8+"]},
            "workout_place": {"text": "📍 Workout location?", "type": "buttons", "required": True,
                "options": ["🏢 Gym", "🏠 Home", "🌳 Outdoors", "🔀 Gym+Home", "🌍 All"]},
        }
    },
    
    12: {
        "title": "👨‍🍳 Food & Cooking",
        "questions": {
            "cooking": {"text": "👨‍🍳 How often cook?", "type": "buttons", "required": True,
                "options": ["❌ Never", "1-2x/week", "3-4x/week", "5-6x/week", "Daily"]},
            "budget": {"text": "💰 Food budget?", "type": "buttons", "required": True,
                "options": ["💸 Budget", "💵 Moderate", "💎 Premium", "🤷 No pref"]},
            "meal_prep": {"text": "📦 Meal prep?", "type": "buttons", "required": True,
                "options": ["✅ Yes", "Sometimes", "Rarely", "❌ No"]},
        }
    },
    
    13: {
        "title": "🎯 Your Goals - Overview",
        "questions": {
            "main_goal": {"text": "🎯 PRIMARY goal?", "type": "buttons", "required": True,
                "options": ["📉 Lose weight", "💪 Build muscle", "⚡ Get stronger", "🏃 Endurance", "❤️ Better health", "✨ All"]},
            "weight_loss": {"text": "📊 Target loss?", "type": "buttons", "required": False,
                "options": ["5 kg", "10 kg", "15 kg", "20+ kg", "N/A"]},
            "timeline": {"text": "⏱️ Timeline?", "type": "buttons", "required": True,
                "options": ["🚀 1 month", "📅 3 mo", "📅 6 mo", "📅 1 yr", "📅 1+ yr"]},
            "tried_before": {"text": "🔄 Tried before?", "type": "buttons", "required": True,
                "options": ["❌ No", "✅ Once", "✅ 2-3x", "✅ Many"]},
        }
    },
    
    14: {
        "title": "🎯 Your Goals - Barriers & Willingness",
        "questions": {
            "barrier": {"text": "🚧 BIGGEST barrier?", "type": "buttons", "required": True,
                "options": ["⏰ Time", "💰 Money", "😴 Motivation", "👥 Support", "📚 Knowledge", "🌀 Multiple", "✨ None"]},
            "worked_coach": {"text": "🏆 Coach before?", "type": "buttons", "required": True,
                "options": ["❌ No", "📱 Online", "👨‍🏫 In-person", "🔀 Both"]},
            "diet_changes": {"text": "🥗 Diet changes?", "type": "buttons", "required": True,
                "options": ["🔥 Big", "⚡ Moderate", "🌱 Small", "💤 Minimal"]},
            "exercise_willing": {"text": "💪 Exercise days?", "type": "buttons", "required": True,
                "options": ["✅ 7 days", "✅ 5-6 days", "✅ 3-4 days", "😐 1-2 days"]},
        }
    },
    
    15: {
        "title": "🤝 Commitment - Final Questions",
        "questions": {
            "training_days": {"text": "📅 Training days/week?", "type": "buttons", "required": True,
                "options": ["1️⃣ 1", "2️⃣ 2", "3️⃣ 3", "4️⃣ 4", "5️⃣ 5", "6️⃣ 6", "7️⃣ 7"]},
            "reduce_eating": {"text": "🍕 Reduce eating out?", "type": "buttons", "required": True,
                "options": ["✅ Yes", "😐 Somewhat", "❌ No"]},
            "reduce_drinking": {"text": "🍷 Reduce drinking?", "type": "buttons", "required": True,
                "options": ["✅ Yes", "😐 Somewhat", "❌ No"]},
            "food_journal": {"text": "📝 Food journal?", "type": "buttons", "required": True,
                "options": ["✅ Yes", "Sometimes", "❌ No"]},
            "ready": {"text": "🚀 Ready to START?", "type": "buttons", "required": True,
                "options": ["🔥 YES 100%!", "✅ Yes, somewhat", "🤔 Maybe", "⏳ Not yet"]},
        }
    },
}

class UserSession:
    def __init__(self):
        self.current_screen = 1
        self.current_inputs = {}
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

📋 QUICK Assessment (5-7 minutes!)
✅ 15 Grouped Question Screens
✅ Answer 4-5 at once (NOT one-by-one!)
✅ Fast & Engaging
🎯 Your Personalized Plan
⚡ Zero boredom!

Let's SPEED this up! 🚀"""
    
    keyboard = [[InlineKeyboardButton("🎯 LET'S GO! START NOW!", callback_data="start")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def show_screen(update: Update, context: ContextTypes.DEFAULT_TYPE, query=None):
    user_id = update.effective_user.id
    
    if user_id not in context.user_data:
        await start(update, context)
        return
    
    session = context.user_data[user_id]
    screen_num = session.current_screen
    
    if screen_num > 15:
        final_msg = f"""🎉 ╔════════════════════════════════════════╗
   ║  ASSESSMENT COMPLETE! 🏆               ║
   ╚════════════════════════════════════════╝

👋 {session.name or 'Champion'}! Amazing job! 💪

You finished in lightning speed! ⚡
(Usually takes 10+ mins, you did it faster!)

Your detailed fitness profile is READY!
Our coaches will create your plan NOW!

📊 Next steps:
✅ Health score calculated
✅ Custom plan generated
✅ Your transform begins!

Thank you for your commitment! 🙏
Ready to CHANGE YOUR LIFE? 🚀"""
        await update.message.reply_text(final_msg)
        return
    
    screen = SCREENS[screen_num]
    progress = int((screen_num / 15) * 100)
    bar = "█" * (progress // 5) + "░" * (20 - (progress // 5))
    
    text = f"{bar} {progress}%\n\n{screen['title']}\n\n"
    
    # Build message with all questions for this screen
    buttons = []
    q_num = 0
    
    for field_key, q_data in screen['questions'].items():
        text += f"{q_data['text']}\n"
        q_num += 1
        
        if q_data['type'] == 'buttons':
            # Add button options
            for i, opt in enumerate(q_data['options']):
                buttons.append([InlineKeyboardButton(opt, callback_data=f"ans_{screen_num}_{field_key}_{i}")])
        elif q_data['type'] == 'buttons_multi':
            # Multi-select buttons
            for i, opt in enumerate(q_data['options']):
                buttons.append([InlineKeyboardButton(opt, callback_data=f"multi_{screen_num}_{field_key}_{i}")])
        elif q_data['type'] == 'text':
            # Text input questions get special handling
            pass
    
    # Add Submit button
    buttons.append([InlineKeyboardButton("✅ NEXT SECTION →", callback_data=f"next_{screen_num}")])
    
    markup = InlineKeyboardMarkup(buttons)
    
    if query:
        try:
            await query.edit_message_text(text, reply_markup=markup)
        except:
            await query.edit_message_text(text + "\n(Please answer text fields in chat)")
    else:
        await update.message.reply_text(text + "\n*For text questions, type answers in chat*", reply_markup=markup)

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
        # Handle answer button click
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
        
    if data.startswith("next_"):
        screen_num = int(data.split("_")[1])
        screen = SCREENS[screen_num]
        
        # Check text inputs
        text_fields = [k for k, v in screen['questions'].items() if v['type'] == 'text']
        missing = [k for k in text_fields if k not in session.current_inputs]
        
        if missing:
            await query.answer(f"⚠️ Please answer text questions first!", show_alert=True)
            return
        
        session.current_screen += 1
        session.current_inputs = {}
        await show_screen(update, context, query)

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id not in context.user_data:
        await start(update, context)
        return
    
    session = context.user_data[user_id]
    screen_num = session.current_screen
    screen = SCREENS[screen_num]
    
    # Parse text input - format: "field_value" or "field1_value1 field2_value2"
    text = update.message.text.strip()
    
    # Simple version: user types "age 28 height 170 weight 70 name Harsh"
    parts = text.split()
    
    text_fields = {k: v for k, v in screen['questions'].items() if v['type'] == 'text'}
    
    # Store the answers
    for field_key in text_fields:
        if field_key == 'name':
            session.current_inputs[field_key] = text
            session.all_answers[field_key] = text
            session.name = text
            await update.message.reply_text(f"✅ Got your name: {text}! 👋")
        else:
            session.current_inputs[field_key] = text
            session.all_answers[field_key] = text
            await update.message.reply_text(f"✅ Saved! {text} 👍")

def main():
    print("\n" + "=" * 70)
    print("🚀 GROUPED QUESTIONS BOT - FAST!")
    print("=" * 70)
    print("✅ 15 Screens (not 61 one-by-one!)")
    print("✅ Answer 4-5 questions at once")
    print("✅ Completes in 5-7 minutes")
    print("✅ FUN & ENGAGING")
    print("=" * 70)
    
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    
    print("🚀 BOT RUNNING!\n")
    app.run_polling()

if __name__ == "__main__":
    main()
