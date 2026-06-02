#!/usr/bin/env python3
"""
COACH AVNI BOT - ALL 61 QUESTIONS GROUPED
✅ 100% of the 61 questions migrated from bot_smooth_flow.py
✅ Multiple related button groups displayed per screen
✅ Dynamic message updating with instant checkmarks (✅)
✅ Clean app-like assessment layout
"""

import os
import sys
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
# ALL 61 QUESTIONS MAP INTO ARCHITECTURAL SCREENS
# ============================================================================

SCREENS = [
    # --- TEXT INPUT SCREENS (Kept independent for typing experience) ---
    {"id": 1, "section": "👤 About You", "fields": [
        {"id": "q1", "text": "👤 What's your full name?", "type": "text", "required": True}
    ]},
    {"id": 2, "section": "👤 About You", "fields": [
        {"id": "q2", "text": "🎂 What's your age?", "type": "text", "required": True}
    ]},
    {"id": 3, "section": "👤 About You", "fields": [
        {"id": "q3", "text": "📏 Current height (cm)?", "type": "text", "required": True}
    ]},
    {"id": 4, "section": "👤 About You", "fields": [
        {"id": "q4", "text": "⚖️ Current weight (kg)?", "type": "text", "required": True}
    ]},
    
    # --- SCREEN 5: Profession & Sex ---
    {"id": 5, "section": "👤 About You", "fields": [
        {"id": "q5", "text": "💼 What's your profession?", "type": "buttons", "required": True,
         "options": ["💻 Software Engineer", "👨‍⚕️ Doctor", "📚 Student", "🏫 Teacher", "👔 Business Owner", "🤵 Consultant", "🏥 Healthcare", "📊 Finance", "🎯 Sales", "➕ Other"]},
        {"id": "q6", "text": "⚡ Biological sex?", "type": "buttons", "required": True,
         "options": ["👨 Male", "👩 Female", "🌈 Other"]}
    ]},
    
    # --- SCREEN 6: Dietary & Preferences ---
    {"id": 6, "section": "🍽️ Diet & Food", "fields": [
        {"id": "q7", "text": "🍽️ Dietary preference?", "type": "buttons", "required": True,
         "options": ["🍗 Non-Vegetarian", "🥕 Vegetarian", "🥚 Eggetarian", "🌱 Vegan", "☪️ Jain"]},
        {"id": "q8", "text": "🚫 Foods you HATE? (Select multiple/any)", "type": "buttons_multi", "required": False,
         "options": ["🥒 Bitter gourd", "🍆 Eggplant", "🍄 Mushroom", "🪴 Okra", "🌶️ Capsicum", "🧅 Onion", "🧄 Garlic", "🐟 Fish", "🥚 Egg", "🥛 Dairy"]},
        {"id": "q9", "text": "👨‍🍳 Cuisines you LOVE? (Select multiple/any)", "type": "buttons_multi", "required": False,
         "options": ["🇮🇳 North Indian", "🔥 South Indian", "🇧🇩 Bengali", "🥘 Gujarati", "🌶️ Continental", "🥡 Chinese", "🍝 Italian", "🌮 Mexican", "🍜 Thai"]}
    ]},
    
    # --- SCREEN 7: Morning Schedule ---
    {"id": 7, "section": "☀️ Your Day", "fields": [
        {"id": "q10", "text": "🌅 What time do you wake up?", "type": "buttons", "required": True,
         "options": ["⏰ 5:00 AM", "⏰ 5:30 AM", "⏰ 6:00 AM", "⏰ 6:30 AM", "⏰ 7:00 AM", "⏰ 7:30 AM", "⏰ 8:00 AM", "🛏️ 8:30 AM+"]},
        {"id": "q11", "text": "☕ Breakfast time?", "type": "buttons", "required": True,
         "options": ["🌅 6:00 AM", "🌅 6:30 AM", "🌅 7:00 AM", "🌅 7:30 AM", "🌅 8:00 AM", "🌅 8:30 AM", "🌅 9:00 AM", "⏭️ Skip"]}
    ]},
    
    # --- SCREEN 8: Work Routine ---
    {"id": 8, "section": "☀️ Your Day", "fields": [
        {"id": "q12", "text": "🏢 Work start time?", "type": "buttons", "required": True,
         "options": ["🕐 8:00 AM", "🕐 8:30 AM", "🕐 9:00 AM", "🕐 9:30 AM", "🕐 10:00 AM", "🎲 Variable"]},
        {"id": "q13", "text": "🚪 Work end time?", "type": "buttons", "required": True,
         "options": ["🕔 5:00 PM", "🕔 5:30 PM", "🕔 6:00 PM", "🕔 6:30 PM", "🕔 7:00 PM", "🕔 8:00 PM", "🌙 9:00 PM+"]}
    ]},
    
    # --- SCREEN 9: Mid-day & Evening Meals ---
    {"id": 9, "section": "☀️ Your Day", "fields": [
        {"id": "q14", "text": "🍽️ Lunch time?", "type": "buttons", "required": True,
         "options": ["🕛 12:00 PM", "🕛 12:30 PM", "🕛 1:00 PM", "🕛 1:30 PM", "🕛 2:00 PM", "🕛 2:30 PM", "🎲 Variable"]},
        {"id": "q15", "text": "🍴 Dinner time?", "type": "buttons", "required": True,
         "options": ["🕕 6:00 PM", "🕕 6:30 PM", "🕕 7:00 PM", "🕕 7:30 PM", "🕕 8:00 PM", "🕕 8:30 PM", "🕕 9:00 PM", "🕘 9:30 PM+"]}
    ]},
    
    # --- SCREEN 10: Night & Snacks ---
    {"id": 10, "section": "☀️ Your Day", "fields": [
        {"id": "q16", "text": "😴 Sleep time?", "type": "buttons", "required": True,
         "options": ["🌙 9:00 PM", "🌙 9:30 PM", "🌙 10:00 PM", "🌙 10:30 PM", "🌙 11:00 PM", "🌙 11:30 PM", "🌙 12:00 AM", "🌙 12:30 AM+"]},
        {"id": "q17", "text": "🍿 Snacks during the day?", "type": "buttons", "required": True,
         "options": ["✅ Yes, 1-2 times", "✅ Yes, 3+ times", "⏱️ Rarely", "🚫 No"]}
    ]},
    
    # --- SCREEN 11: Weekend Variations ---
    {"id": 11, "section": "☀️ Your Day", "fields": [
        {"id": "q18", "text": "🍕 Eat out for meals?", "type": "buttons", "required": True,
         "options": ["🍽️ Never", "🥗 Breakfast", "🍜 Lunch", "🍛 Dinner", "🎉 Multiple meals"]},
        {"id": "q19", "text": "😴 Weekend wake time?", "type": "buttons", "required": True,
         "options": ["Same as weekday ⏰", "30 min later 😴", "1 hour later 💤", "1.5 hours later 🛌", "2+ hours later 🌙"]},
        {"id": "q20", "text": "🛏️ Weekend sleep time?", "type": "buttons", "required": True,
         "options": ["Same as weekday 🌙", "30 min later 😴", "1 hour later 💤", "1.5 hours later 🛌", "2+ hours later 🛏️"]}
    ]},
    
    # --- SCREEN 12: Medical & Allergies ---
    {"id": 12, "section": "🏥 Health", "fields": [
        {"id": "q21", "text": "⚕️ Medical conditions? (Select all)", "type": "buttons_multi", "required": False,
         "options": ["🔬 Diabetes", "🧬 Thyroid", "🔴 PCOS/PCOD", "❤️ Hypertension", "⚠️ High Cholesterol", "🍗 Fatty Liver", "✅ None"]},
        {"id": "q22", "text": "🤧 Any allergies?", "type": "buttons", "required": True,
         "options": ["✅ No", "🍔 Food allergies", "🌫️ Environmental", "🔀 Both"]}
    ]},
    
    # --- SCREEN 13: Medications & Digestion ---
    {"id": 13, "section": "🏥 Health", "fields": [
        {"id": "q23", "text": "💊 On medications?", "type": "buttons", "required": True,
         "options": ["✅ No", "1-2 medications 💊", "3-4 medications 💉", "5+ medications 🏥"]},
        {"id": "q24", "text": "🤢 Digestive issues?", "type": "buttons", "required": True,
         "options": ["✅ No", "Sometimes 😐", "Often 😕", "Frequently 😣"]}
    ]},
    
    # --- SCREEN 14: Injuries ---
    {"id": 14, "section": "🏥 Health", "fields": [
        {"id": "q25", "text": "🤕 Got any injuries?", "type": "buttons", "required": True,
         "options": ["✅ No", "Old injury (healed) 🩹", "Current injury ⚠️"]},
        {"id": "q26", "text": "📍 Injury location?", "type": "buttons", "required": True,
         "options": ["🔴 Lower back", "🔴 Knee", "🔴 Shoulder", "🔴 Elbow", "🔴 Wrist", "🔴 Multiple", "✅ N/A"]}
    ]},
    
    # --- SCREEN 15: Habits & Supplements ---
    {"id": 15, "section": "⚡ Supplements & Habits", "fields": [
        {"id": "q27", "text": "💊 Do you take supplements?", "type": "buttons", "required": True,
         "options": ["❌ No", "✅ Yes, 1-2", "✅ Yes, 3-5", "✅ Yes, 5+"]},
        {"id": "q28", "text": "🥛 Protein powder experience?", "type": "buttons", "required": True,
         "options": ["👶 Never", "💪 Using now", "📦 Used before"]}
    ]},
    
    # --- SCREEN 16: Vices & Frequencies ---
    {"id": 16, "section": "⚡ Supplements & Habits", "fields": [
        {"id": "q29", "text": "🚬 Do you smoke?", "type": "buttons", "required": True,
         "options": ["✅ No", "🚭 Occasionally", "⚠️ Regularly"]},
        {"id": "q30", "text": "🍷 Do you drink alcohol?", "type": "buttons", "required": True,
         "options": ["✅ No", "🍻 Occasionally", "📅 Weekly", "🎉 Multiple times/week"]},
        {"id": "q31", "text": "🍕 Eating out frequency?", "type": "buttons", "required": True,
         "options": ["❌ Never", "1x/week 🍽️", "2-3x/week 🍜", "4-5x/week 🍛", "☀️ Daily"]}
    ]},
    
    # --- SCREEN 17: Stress & Sleep Metrics ---
    {"id": 17, "section": "😴 Sleep & Stress", "fields": [
        {"id": "q32", "text": "😰 Rate daily stress (1-5)", "type": "buttons", "required": True,
         "options": ["😊 1 (Chill)", "🙂 2", "😐 3 (Neutral)", "😕 4", "😫 5 (Insane)"]},
        {"id": "q33", "text": "💤 Rate sleep quality (1-5)", "type": "buttons", "required": True,
         "options": ["😴 1 (Terrible)", "😴 2", "😴 3 (Okay)", "😴 4", "😴 5 (Perfect!)"]}
    ]},
    
    # --- SCREEN 18: Restlessness & Mornings ---
    {"id": 18, "section": "😴 Sleep & Stress", "fields": [
        {"id": "q34", "text": "😖 Is sleep restless?", "type": "buttons", "required": True,
         "options": ["✅ No", "Sometimes 😐", "Often 😕", "Always 😣"]},
        {"id": "q35", "text": "🌅 Wake up feeling fresh?", "type": "buttons", "required": True,
         "options": ["✅ Always", "😊 Usually", "😐 Sometimes", "😴 Rarely"]}
    ]},
    
    # --- SCREEN 19: Mindfulness & Triggers ---
    {"id": 19, "section": "😴 Sleep & Stress", "fields": [
        {"id": "q36", "text": "🧘 Do you meditate?", "type": "buttons", "required": True,
         "options": ["❌ No", "🙏 Rarely", "🧘 Sometimes", "✅ Regularly"]},
        {"id": "q37", "text": "🔥 What stresses you most?", "type": "buttons", "required": True,
         "options": ["💼 Work", "❤️ Health", "💔 Relationships", "💰 Money", "⏰ Time", "🌪️ Multiple", "😊 Nothing"]}
    ]},
    
    # --- SCREEN 20: General Activity ---
    {"id": 20, "section": "💪 Fitness", "fields": [
        {"id": "q38", "text": "💪 Days/week physically active?", "type": "buttons", "required": True,
         "options": ["😴 0 (Lazy)", "🚶 1-2", "🏃 3-4", "🏋️ 5-6", "⚡ 7 (Daily)"]},
        {"id": "q39", "text": "🏋️ Strength training exp?", "type": "buttons", "required": True,
         "options": ["👶 None", "🌱 Beginner", "💪 Intermediate", "🦾 Advanced"]}
    ]},
    
    # --- SCREEN 21: Training Frequencies ---
    {"id": 21, "section": "💪 Fitness", "fields": [
        {"id": "q40", "text": "🏋️ Weight training frequency?", "type": "buttons", "required": True,
         "options": ["❌ Never", "1-2x/week 💪", "3-4x/week 🏋️", "5-6x/week 🦾", "Daily ⚡"]},
        {"id": "q41", "text": "🏃 Cardio frequency?", "type": "buttons", "required": True,
         "options": ["❌ Never", "1-2x/week 🚴", "3-4x/week 🏃", "5-6x/week 🤸", "Daily 🚀"]}
    ]},
    
    # --- SCREEN 22: Flexibility & Recreations ---
    {"id": 22, "section": "💪 Fitness", "fields": [
        {"id": "q42", "text": "🧘 Yoga/stretching frequency?", "type": "buttons", "required": True,
         "options": ["❌ Never", "1-2x/week 🧘", "3-4x/week 🤸", "5-6x/week 🙏", "Daily ✨"]},
        {"id": "q43", "text": "⚽ Sports/fun activities?", "type": "buttons", "required": True,
         "options": ["❌ No", "1-2x/week ⚽", "3-4x/week 🏀", "5-6x/week 🎾", "Daily 🏐"]}
    ]},
    
    # --- SCREEN 23: Posture & Venues ---
    {"id": 23, "section": "💪 Fitness", "fields": [
        {"id": "q44", "text": "🪑 Hours sitting per day?", "type": "buttons", "required": True,
         "options": ["🚶 0-2 hours", "😐 2-4 hours", "😴 4-6 hours", "😵 6-8 hours", "💀 8+ hours"]},
        {"id": "q45", "text": "📍 Preferred workout spot?", "type": "buttons", "required": True,
         "options": ["🏢 Gym", "🏠 Home", "🌳 Outdoors", "🔀 Gym & Home", "🌍 Mix all"]}
    ]},
    
    # --- SCREEN 24: Kitchen Habits ---
    {"id": 24, "section": "👨‍🍳 Food & Cooking", "fields": [
        {"id": "q46", "text": "👨‍🍳 How often do you cook?", "type": "buttons", "required": True,
         "options": ["❌ Never", "1-2x/week 🍳", "3-4x/week 🥘", "5-6x/week 👨‍🍳", "Daily 🍲"]},
        {"id": "q47", "text": "💰 Food budget preference?", "type": "buttons", "required": True,
         "options": ["💸 Budget-friendly", "💵 Moderate", "💎 Premium", "🤷 No preference"]},
        {"id": "q48", "text": "📦 Can you meal prep?", "type": "buttons", "required": True,
         "options": ["✅ Yes", "Sometimes 😐", "Rarely 😕", "❌ No"]}
    ]},
    
    # --- SCREEN 25: Primary Objectives ---
    {"id": 25, "section": "🎯 Your Goals", "fields": [
        {"id": "q49", "text": "🎯 PRIMARY goal?", "type": "buttons", "required": True,
         "options": ["📉 Lose weight", "💪 Build muscle", "⚡ Get stronger", "🏃 Endurance", "❤️ Better health", "✨ All of above"]},
        {"id": "q50", "text": "📊 Target weight loss?", "type": "buttons", "required": True,
         "options": ["5 kg 📉", "10 kg 📉", "15 kg 📉", "20+ kg 📉", "N/A ✅"]},
        {"id": "q51", "text": "⏱️ Timeline for goal?", "type": "buttons", "required": True,
         "options": ["🚀 1 month", "📅 3 months", "📅 6 months", "📅 1 year", "📅 1+ year"]}
    ]},
    
    # --- SCREEN 26: History & Blockages ---
    {"id": 26, "section": "🎯 Your Goals", "fields": [
        {"id": "q52", "text": "🔄 Tried before?", "type": "buttons", "required": True,
         "options": ["❌ No", "✅ Once", "✅ 2-3 times", "✅ Many times"]},
        {"id": "q53", "text": "🚧 BIGGEST barrier?", "type": "buttons", "required": True,
         "options": ["⏰ Time", "💰 Money", "😴 Motivation", "👥 Support", "📚 Knowledge", "🌀 Multiple", "✨ None"]},
        {"id": "q54", "text": "🏆 Worked with coach before?", "type": "buttons", "required": True,
         "options": ["❌ No", "📱 Online", "👨‍🏫 In-person", "🔀 Both"]}
    ]},
    
    # --- SCREEN 27: Flexibility to Adjustment ---
    {"id": 27, "section": "🎯 Your Goals", "fields": [
        {"id": "q55", "text": "🥗 Change eating habits?", "type": "buttons", "required": True,
         "options": ["🔥 Big changes", "⚡ Moderate", "🌱 Small", "💤 Minimal"]},
        {"id": "q56", "text": "💪 Willing to exercise?", "type": "buttons", "required": True,
         "options": ["✅ 7 days/week", "✅ 5-6 days", "✅ 3-4 days", "😐 1-2 days"]}
    ]},
    
    # --- SCREEN 28: Dietary Commitments ---
    {"id": 28, "section": "🤝 Commitment", "fields": [
        {"id": "q57", "text": "📅 Days/week training?", "type": "buttons", "required": True,
         "options": ["1️⃣ 1 day", "2️⃣ 2 days", "3️⃣ 3 days", "4️⃣ 4 days", "5️⃣ 5 days", "6️⃣ 6 days", "7️⃣ 7 days"]},
        {"id": "q58", "text": "🍕 Reduce eating out?", "type": "buttons", "required": True,
         "options": ["✅ Yes", "😐 Somewhat", "❌ No"]},
        {"id": "q59", "text": "🍷 Reduce drinking?", "type": "buttons", "required": True,
         "options": ["✅ Yes", "😐 Somewhat", "❌ No"]}
    ]},
    
    # --- SCREEN 29: Final Initialization ---
    {"id": 29, "section": "🤝 Commitment", "fields": [
        {"id": "q60", "text": "📝 Keep food journal?", "type": "buttons", "required": True,
         "options": ["✅ Yes", "Sometimes 😐", "❌ No"]},
        {"id": "q61", "text": "🚀 Ready to START?", "type": "buttons", "required": True,
         "options": ["🔥 YES! 100%!", "✅ Yes, somewhat", "🤔 Maybe", "⏳ Not yet"]}
    ]}
]

class UserSession:
    def __init__(self):
        self.current_screen_idx = 0
        self.answers = {}
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

📋 Comprehensive Fitness Profile
⚡ All 61 Specific Questions Migrated!
✅ Clean App-like Layout
✅ Interactive Checkmarks

Let's do this! 🚀"""
    
    keyboard = [[InlineKeyboardButton("🎯 LET'S START!", callback_data="start")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def render_screen(update: Update, context: ContextTypes.DEFAULT_TYPE, query=None):
    user_id = update.effective_user.id
    if user_id not in context.user_data:
        await start(update, context)
        return
        
    session = context.user_data[user_id]
    
    if session.current_screen_idx >= len(SCREENS):
        final_msg = f"""🎉 ╔════════════════════════════════════════╗
   ║  ASSESSMENT COMPLETE! 🏆               ║
   ╚════════════════════════════════════════╝

👋 {session.name or 'Champion'}! You successfully finished all 61 questions! 💪

Your structured health details are recorded. 
Our matching platform is preparing your strategy! 🚀"""
        
        if query:
            await query.edit_message_text(final_msg)
        else:
            await update.message.reply_text(final_msg)
        return

    screen_data = SCREENS[session.current_screen_idx]
    
    # Progress Calculation
    progress = int((session.current_screen_idx / len(SCREENS)) * 100)
    bar = "█" * (progress // 10) + "░" * (10 - (progress // 10))
    
    name_part = f" (Hi {session.name}!)" if session.name else ""
    text_lines = [f"{bar} {progress}% | *{screen_data['section']}*{name_part}", ""]
    
    all_required_answered = True
    
    for field in screen_data['fields']:
        ans = session.answers.get(field['id'])
        is_answered = ans is not None and (not isinstance(ans, list) or len(ans) > 0)
        
        if field['required'] and not is_answered:
            all_required_answered = False
            
        if is_answered:
            if field['type'] == 'buttons_multi':
                text_lines.append(f"{field['text']}\n👉 Selected: _{', '.join(ans)}_ ✅")
            else:
                text_lines.append(f"{field['text']}\n👉 Selected: _{ans}_ ✅")
        else:
            if field['type'] == 'text':
                text_lines.append(f"{field['text']} [Type in chat below] ⌨️")
            else:
                text_lines.append(f"{field['text']} [Tap below to pick] ✔️")
        text_lines.append("")

    text = "\n".join(text_lines)
    keyboard = []
    
    for field in screen_data['fields']:
        if field['type'] in ['buttons', 'buttons_multi']:
            # Non-clickable Question Header Row inside the inline keyboard
            clean_q = field['text'].split('?')[0] + "?"
            keyboard.append([InlineKeyboardButton(f"🔹 {clean_q}", callback_data="ignore")])
            
            row = []
            for idx, opt in enumerate(field['options']):
                display_opt = opt
                ans = session.answers.get(field['id'])
                
                if field['type'] == 'buttons' and ans == opt:
                    display_opt = f"✅ {opt}"
                elif field['type'] == 'buttons_multi' and ans and opt in ans:
                    display_opt = f"✅ {opt}"
                    
                cb_data = f"sel_{field['id']}_{idx}"
                row.append(InlineKeyboardButton(display_opt, callback_data=cb_data))
                
                if len(row) == 2:
                    keyboard.append(row)
                    row = []
            if row:
                keyboard.append(row)
    
    # Add navigation row
    if any(f['type'] in ['buttons', 'buttons_multi'] for f in screen_data['fields']):
        if all_required_answered:
            keyboard.append([InlineKeyboardButton("⚡ NEXT SCREEN ➡️", callback_data="next_screen")])
        else:
            keyboard.append([InlineKeyboardButton("🔒 Finish Required Items Above", callback_data="locked")])

    markup = InlineKeyboardMarkup(keyboard) if keyboard else None
    
    try:
        if query:
            await query.edit_message_text(text, reply_markup=markup, parse_mode="Markdown")
        else:
            await update.message.reply_text(text, reply_markup=markup, parse_mode="Markdown")
    except Exception as e:
        # Prevent crashes if content updates are strictly identical
        pass

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    
    if user_id not in context.user_data:
        await start(update, context)
        return
        
    session = context.user_data[user_id]
    data = query.data
    
    if data == "start":
        await query.answer()
        session.current_screen_idx = 0
        await render_screen(update, context, query)
        return
        
    if data == "ignore":
        await query.answer()
        return
        
    if data == "locked":
        await query.answer("⚠️ Please pick an answer for the required questions on this screen first!", show_alert=True)
        return
        
    if data == "next_screen":
        await query.answer()
        session.current_screen_idx += 1
        await render_screen(update, context, query)
        return
        
    if data.startswith("sel_"):
        parts = data.split("_")
        field_id = parts[1]
        opt_idx = int(parts[2])
        
        screen_data = SCREENS[session.current_screen_idx]
        field = next((f for f in screen_data['fields'] if f['id'] == field_id), None)
        
        if not field:
            await query.answer()
            return
            
        selected_opt = field['options'][opt_idx]
        
        if field['type'] == 'buttons':
            session.answers[field_id] = selected_opt
        elif field['type'] == 'buttons_multi':
            current_ans = session.answers.get(field_id, [])
            if selected_opt in current_ans:
                current_ans.remove(selected_opt)
            else:
                current_ans.append(selected_opt)
            session.answers[field_id] = current_ans
            
        await query.answer()
        await render_screen(update, context, query)

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id not in context.user_data:
        await start(update, context)
        return
        
    session = context.user_data[user_id]
    if session.current_screen_idx >= len(SCREENS):
        return
        
    screen_data = SCREENS[session.current_screen_idx]
    text_fields = [f for f in screen_data['fields'] if f['type'] == 'text']
    
    if not text_fields:
        await update.message.reply_text("Please use the inline buttons above to complete this step! 👆")
        return
        
    field = text_fields[0]
    text = update.message.text.strip()
    
    # Input validation checks matching your legacy constraints
    if field['id'] == 'q2': # Age verification
        try:
            age = int(text)
            if not 13 <= age <= 100:
                await update.message.reply_text("❌ Age must be between 13 and 100! Try again:")
                return
        except ValueError:
            await update.message.reply_text("❌ Please enter a valid number for age:")
            return

    session.answers[field['id']] = text
    
    if field['id'] == 'q1':
        session.name = text

    session.current_screen_idx += 1
    await render_screen(update, context)

def main():
    print("\n" + "=" * 70)
    print("🚀 61-QUESTION APP-FLOW INTERACTIVE TELEGRAM BOT")
    print("=" * 70)
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    
    app.run_polling()

if __name__ == "__main__":
    main()
