#!/usr/bin/env python3
"""
COACH AVNI BOT - MEALZY STYLE
✅ All Mealzy Questions
✅ Minimal Typing (Max Buttons)
✅ Same Structure
✅ Uses Your Name
"""

import os
import sys
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TOKEN:
    print("ERROR: TELEGRAM_TOKEN not found in .env")
    sys.exit(1)

# ============================================================================
# MEALZY-STYLE QUESTIONS - MINIMAL TYPING, MAXIMUM BUTTONS
# ============================================================================

QUESTIONS = {
    # 1. ABOUT YOU (Personal Data)
    1: {"type": "text", "text": "What's your full name?", "section": "About You"},
    2: {"type": "text", "text": "What's your age?", "section": "About You"},
    3: {"type": "text", "text": "Current height (cm)?", "section": "About You"},
    4: {"type": "text", "text": "Current weight (kg)?", "section": "About You"},
    5: {"type": "buttons", "text": "What's your profession?", "section": "About You",
        "options": ["Software Engineer", "Doctor", "Student", "Teacher", "Business Owner", "Consultant", "Other"]},
    6: {"type": "buttons", "text": "Biological sex?", "section": "About You",
        "options": ["Male", "Female", "Other"]},
    
    # 2. DIET & FOOD
    7: {"type": "buttons", "text": "Dietary preference?", "section": "Diet & Food",
        "options": ["Non-Vegetarian", "Vegetarian", "Eggetarian", "Vegan", "Jain"]},
    8: {"type": "buttons_custom", "text": "Foods you dislike or avoid?", "section": "Diet & Food",
        "options": ["Bitter gourd", "Eggplant", "Mushroom", "Okra", "Capsicum", "Onion", "Garlic", "Fish", "Egg", "Dairy"]},
    9: {"type": "buttons_custom", "text": "Cuisines you enjoy?", "section": "Diet & Food",
        "options": ["North Indian", "South Indian", "Bengali", "Gujarati", "Maharashtrian", "Continental", "Chinese", "Italian", "Mexican", "Japanese", "Thai", "Mediterranean"]},
    
    # 3. YOUR DAY
    10: {"type": "text", "text": "Describe your daily routine (e.g., wake time, work hours, meals, sleep)", "section": "Your Day"},
    11: {"type": "text", "text": "Describe your current diet (breakfast, lunch, dinner, snacks)", "section": "Your Day"},
    12: {"type": "text", "text": "Describe your average weekend", "section": "Your Day"},
    
    # 4. HEALTH
    13: {"type": "buttons_custom", "text": "Any medical conditions?", "section": "Health",
        "options": ["Diabetes", "Thyroid", "PCOS/PCOD", "Hypertension", "High Cholesterol", "Fatty Liver", "None"]},
    14: {"type": "text", "text": "Any allergies or food intolerances?", "section": "Health"},
    15: {"type": "text", "text": "Current medications?", "section": "Health"},
    16: {"type": "text", "text": "Any digestive issues? (e.g., bloating, acidity, constipation)", "section": "Health"},
    17: {"type": "text", "text": "Any injuries or physical limitations?", "section": "Health"},
    
    # 5. SUPPLEMENTS & HABITS
    18: {"type": "text", "text": "Do you use any supplements? (e.g., Multivitamin, Fish Oil)", "section": "Supplements & Habits"},
    19: {"type": "buttons", "text": "Protein supplement experience?", "section": "Supplements & Habits",
        "options": ["Yes, currently using", "Used before", "Never used"]},
    20: {"type": "buttons", "text": "Do you smoke?", "section": "Supplements & Habits",
        "options": ["No", "Occasionally", "Regularly"]},
    21: {"type": "buttons", "text": "Do you drink alcohol?", "section": "Supplements & Habits",
        "options": ["No", "Occasionally", "Regularly"]},
    22: {"type": "buttons", "text": "How often do you eat out?", "section": "Supplements & Habits",
        "options": ["Never", "1-2 times/week", "2-3 times/week", "4+ times/week"]},
    
    # 6. SLEEP & STRESS
    23: {"type": "buttons", "text": "Rate your daily stress level (1-10)", "section": "Sleep & Stress",
        "options": ["1 (Very Low)", "2", "3", "4", "5 (Moderate)", "6", "7", "8", "9", "10 (Very High)"]},
    24: {"type": "buttons", "text": "Rate your sleep quality (1-10)", "section": "Sleep & Stress",
        "options": ["1 (Very Poor)", "2", "3", "4", "5 (Fair)", "6", "7", "8", "9", "10 (Excellent)"]},
    25: {"type": "buttons", "text": "Is your sleep restless?", "section": "Sleep & Stress",
        "options": ["Yes", "No"]},
    26: {"type": "buttons", "text": "Do you wake up feeling refreshed?", "section": "Sleep & Stress",
        "options": ["Yes", "No"]},
    27: {"type": "buttons", "text": "Do you meditate?", "section": "Sleep & Stress",
        "options": ["Yes", "No"]},
    28: {"type": "text", "text": "What are your major stressors?", "section": "Sleep & Stress"},
    
    # 7. FITNESS
    29: {"type": "buttons", "text": "Days per week physically active (0-7)?", "section": "Fitness",
        "options": ["0", "1", "2", "3", "4", "5", "6", "7"]},
    30: {"type": "buttons", "text": "Resistance training experience?", "section": "Fitness",
        "options": ["None", "Beginner (<6mo)", "Intermediate (6mo-2yr)", "Advanced (2+ yr)"]},
    31: {"type": "text", "text": "What do your current workouts look like?", "section": "Fitness"},
    32: {"type": "text", "text": "Other activities you enjoy?", "section": "Fitness"},
    33: {"type": "text", "text": "How many hours sitting per day?", "section": "Fitness"},
    34: {"type": "buttons", "text": "Where do you prefer to work out?", "section": "Fitness",
        "options": ["Gym", "Home", "Both", "Outdoors"]},
    
    # 8. FOOD & COOKING
    35: {"type": "buttons", "text": "How often do you cook?", "section": "Food & Cooking",
        "options": ["Never", "Sometimes", "Often", "Daily"]},
    36: {"type": "buttons", "text": "Food budget preference?", "section": "Food & Cooking",
        "options": ["Budget-friendly", "Medium", "Premium"]},
    
    # 9. YOUR GOALS
    37: {"type": "text", "text": "Describe your fitness goals (what do you want to achieve?)", "section": "Your Goals"},
    38: {"type": "text", "text": "What body type are you working toward?", "section": "Your Goals"},
    39: {"type": "text", "text": "Timeline to achieve your goals?", "section": "Your Goals"},
    40: {"type": "text", "text": "Why do you want to achieve this goal?", "section": "Your Goals"},
    41: {"type": "text", "text": "Have you tried achieving this before? What approach did you take?", "section": "Your Goals"},
    42: {"type": "text", "text": "Have you worked with a coach? How was the experience?", "section": "Your Goals"},
    43: {"type": "text", "text": "What's your biggest barrier to achieving this goal?", "section": "Your Goals"},
    44: {"type": "text", "text": "Any specific performance goals? (e.g., run 5K in 30 min, deadlift 100kg)", "section": "Your Goals"},
    45: {"type": "text", "text": "Does your health status affect your life quality?", "section": "Your Goals"},
    46: {"type": "text", "text": "How will you feel achieving this goal?", "section": "Your Goals"},
    47: {"type": "text", "text": "How will you feel if you don't achieve it?", "section": "Your Goals"},
    
    # 10. COMMITMENT
    48: {"type": "buttons", "text": "Days per week willing to train (1-7)?", "section": "Commitment",
        "options": ["1", "2", "3", "4", "5", "6", "7"]},
    49: {"type": "buttons", "text": "Willing to reduce eating out?", "section": "Commitment",
        "options": ["Yes", "No"]},
    50: {"type": "buttons", "text": "Willing to reduce drinking?", "section": "Commitment",
        "options": ["Yes", "No"]},
    51: {"type": "text", "text": "Food groups you're not willing to give up?", "section": "Commitment"},
    52: {"type": "text", "text": "Anything else your coach should know?", "section": "Commitment"},
}

# Sections for progress
SECTIONS = [
    "About You",
    "Diet & Food",
    "Your Day",
    "Health",
    "Supplements & Habits",
    "Sleep & Stress",
    "Fitness",
    "Food & Cooking",
    "Your Goals",
    "Commitment"
]

# ============================================================================
# USER SESSION
# ============================================================================

class UserSession:
    def __init__(self):
        self.current_q = 1
        self.answers = {}
        self.name = None
        self.waiting_custom = None

# ============================================================================
# BOT HANDLERS
# ============================================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start assessment"""
    user_id = update.effective_user.id
    context.user_data[user_id] = UserSession()
    
    text = """🤖 Welcome to Mealzy Coach!

📋 Complete Fitness Assessment
✅ 52 Smart Questions
✅ Minimal Typing (Max Buttons!)
📊 Personalized Plan
🎯 Real Results

Let's go! 🚀"""
    
    keyboard = [[InlineKeyboardButton("▶️ START ASSESSMENT", callback_data="start")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE, query=None):
    """Display current question"""
    user_id = update.effective_user.id
    
    if user_id not in context.user_data:
        await start(update, context)
        return
    
    session = context.user_data[user_id]
    q_num = session.current_q
    
    # Check if done
    if q_num > 52:
        await update.message.reply_text("✅ Assessment complete! Thank you!")
        return
    
    question = QUESTIONS[q_num]
    section = question.get("section", "")
    progress = int(((q_num - 1) / 52) * 100)
    bar = "█" * (progress // 5) + "░" * (20 - (progress // 5))
    
    # Progress with name
    name_part = f"\n👋 {session.name}" if session.name else ""
    text = f"{bar} {progress}% | {section}{name_part}\n\n{question['text']}"
    
    # Text input
    if question['type'] == 'text':
        if query:
            await query.edit_message_text(text)
        else:
            await update.message.reply_text(text)
        return
    
    # Button questions
    buttons = [
        [InlineKeyboardButton(opt, callback_data=f"a_{q_num}_{i}")]
        for i, opt in enumerate(question['options'])
    ]
    
    # Add custom if needed
    if question['type'] == 'buttons_custom':
        buttons.append([InlineKeyboardButton("✏️ Custom", callback_data=f"c_{q_num}")])
    
    markup = InlineKeyboardMarkup(buttons)
    
    if query:
        await query.edit_message_text(text, reply_markup=markup)
    else:
        await update.message.reply_text(text, reply_markup=markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks"""
    query = update.callback_query
    user_id = query.from_user.id
    
    if user_id not in context.user_data:
        await start(update, context)
        return
    
    await query.answer()
    session = context.user_data[user_id]
    data = query.data
    
    # Start
    if data == "start":
        session.current_q = 1
        await ask_question(update, context, query)
        return
    
    # Answer
    if data.startswith("a_"):
        parts = data.split("_")
        q_num = int(parts[1])
        ans_idx = int(parts[2])
        
        question = QUESTIONS[q_num]
        answer = question['options'][ans_idx]
        session.answers[q_num] = answer
        
        session.current_q = q_num + 1
        
        if session.name:
            await query.edit_message_text(f"✅ Got it, {session.name}!\n⏳ Next...")
        
        await ask_question(update, context, query)
        return
    
    # Custom
    if data.startswith("c_"):
        q_num = int(data.split("_")[1])
        session.waiting_custom = q_num
        await query.edit_message_text("📝 Type your custom answer:")

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text input"""
    user_id = update.effective_user.id
    
    if user_id not in context.user_data:
        await start(update, context)
        return
    
    session = context.user_data[user_id]
    text = update.message.text.strip()
    
    # Custom answer
    if session.waiting_custom:
        q_num = session.waiting_custom
        session.answers[q_num] = text
        session.waiting_custom = None
        session.current_q = q_num + 1
        
        if session.name:
            await update.message.reply_text(f"✅ {session.name}, got: {text}\n⏳ Next...")
        
        await ask_question(update, context)
        return
    
    q_num = session.current_q
    
    # Validate age
    if q_num == 2:
        try:
            age = int(text)
            if not 13 <= age <= 100:
                await update.message.reply_text("❌ Age 13-100. Try again:")
                return
        except:
            await update.message.reply_text("❌ Enter a number:")
            return
    
    # Store name
    if q_num == 1:
        session.name = text
    
    session.answers[q_num] = text
    session.current_q += 1
    
    if session.name:
        await update.message.reply_text(f"✅ Thanks, {session.name}!\n⏳ Next...")
    
    if session.current_q > 52:
        await update.message.reply_text("🎉 Assessment complete! Thank you for your detailed responses!")
    else:
        await ask_question(update, context)

def main():
    """Start bot"""
    print("\n" + "=" * 70)
    print("🤖 MEALZY-STYLE COACH BOT")
    print("=" * 70)
    print("✅ 52 Questions (Mealzy Structure)")
    print("✅ Minimal Typing (Max Buttons)")
    print("✅ All Mealzy Questions Included")
    print("✅ Uses Your Name")
    print("✅ Production Ready")
    print("=" * 70)
    
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    
    print("🚀 BOT RUNNING!\n")
    app.run_polling()

if __name__ == "__main__":
    main()
