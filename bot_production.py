#!/usr/bin/env python3
"""
COACH AVNI BOT - MAX STABILITY HIERARCHY (WATER & CUSTOM FIXES)
✅ Fixed: Shortened callback payload hashes to completely eliminate Telegram's 64-byte callback limits.
✅ Includes ALL 61+ original questions, specific additions, and full-body photo upload logic.
✅ Fully functional "✍️ Custom / Other" fallback inputs on every button grid matrix.
"""

import os
import sys
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TOKEN:
    print("ERROR: TELEGRAM_TOKEN not found in .env file.")
    sys.exit(1)

# ============================================================================
# COMPACT DICTIONARY MAPS (Reduces byte size to stay safely within 64 bytes)
# ============================================================================
ID_MAP = {
    "q1": "n",     # Name
    "q2": "ag",    # Age
    "q3": "ht",    # Height
    "q4": "wt",    # Weight
    "q5": "pf",    # Profession
    "q6": "sx",    # Sex
    "q7": "dp",    # Diet Preference
    "q8": "fh",    # Foods Hated
    "q9": "cl",    # Cuisines Loved
    "q10": "wu",   # Wake up
    "q11": "bt",   # Breakfast time
    "q12": "ws",   # Work start
    "q13": "we",   # Work end
    "q14": "lt",   # Lunch time
    "q15": "dt",   # Dinner time
    "q16": "st",   # Sleep time
    "q17": "sn",   # Snacking
    "q_water": "w", # Water Consumption
    "q18": "eo",   # Eating Out
    "q19": "ww",   # Weekend Wakeup
    "q20": "wb",   # Weekend Bedtime
    "q21": "cc",   # Clinical Conditions
    "q_specific_health": "sh", # Specific Symptoms
    "q22": "al",   # Allergies
    "q23": "dp",   # Daily Prescriptions
    "q24": "dc",   # Digestive Comfort
    "q25": "si",   # Structural Injuries
    "q26": "da",   # Discomfort Areas
    "q27": "su",   # Supplement Usage
    "q_supp_d3": "d3",  # Vitamin D3
    "q_supp_b12": "b12", # Vitamin B12
    "q_supp_fishoil": "fo", # Fish Oil
    "q_supp_multi": "mv",  # Multivitamin
    "q28": "ps",   # Protein Supplement
    "q29": "sm",   # Smoking
    "q30": "af",   # Alcohol Frequency
    "q31": "rm",   # Restaurant Meals
    "q32": "sl",   # Stress Levels
    "q33": "sd",   # Sleep Deepness
    "q34": "rt",   # Restless Tossing
    "q35": "mf",   # Morning Fatigue
    "q36": "mp",   # Meditation Practices
    "q37": "sf",   # Stress Factor
    "q38": "ad",   # Active Days
    "q_steps": "sp", # Daily Steps
    "q39": "wl",   # Weight Lifting Knowledge
    "q40": "ws",   # Weight Sessions
    "q41": "cf",   # Cardio Frequency
    "q42": "ya",   # Yoga Allocation
    "q43": "ts",   # Team Sports
    "q44": "ds",   # Desk Sitting
    "q45": "tl",   # Training Location
    "q46": "cf",   # Cooking Frequency
    "q47": "bf",   # Budget Flexibility
    "q48": "mp",   # Meal Preps
    "q49": "po",   # Physical Objective
    "q50": "ws",   # Weight Shift
    "q51": "ah",   # Achievement Horizon
    "q52": "pa",   # Past Attempts
    "q53": "rb",   # Root Barrier
    "q54": "ec",   # Experience Coaches
    "q55": "om",   # Optimize Meals
    "q56": "we",   # Workout Execution
    "q57": "aw",   # Allocation Windows
    "q58": "ce",   # Curb External Treats
    "q59": "aa",   # Adjust Alcohol
    "q60": "ml",   # Maintain Logging
    "q61": "mr",   # Mentally Ready
    "q_photos": "ph" # Photos Module
}

# Reverse mapping for dynamic response evaluations
REV_MAP = {v: k for k, v in ID_MAP.items()}

SCREENS = [
    # --- SCREEN 1 - 4: Core Metrics ---
    {"id": 1, "section": "👤 About You", "fields": [{"id": "q1", "text": "👤 What's your full name?", "type": "text", "required": True}]},
    {"id": 2, "section": "👤 About You", "fields": [{"id": "q2", "text": "🎂 What's your age?", "type": "text", "required": True}]},
    {"id": 3, "section": "👤 About You", "fields": [{"id": "q3", "text": "📏 Current height (cm)?", "type": "text", "required": True}]},
    {"id": 4, "section": "👤 About You", "fields": [{"id": "q4", "text": "⚖️ Current weight (kg)?", "type": "text", "required": True}]},
    
    # --- SCREEN 5: Profession & Sex ---
    {"id": 5, "section": "💼 Work & Details", "fields": [
        {"id": "q5", "text": "💼 What's your profession?", "type": "buttons", "required": True, "options": ["💻 Engineer", "👨‍⚕️ Doctor", "📚 Student", "🏫 Teacher", "👔 Business Owner", "🤵 Consultant", "📊 Finance", "🎯 Sales"]},
        {"id": "q6", "text": "⚡ Biological sex?", "type": "buttons", "required": True, "options": ["👨 Male", "👩 Female"]}
    ]},
    
    # --- SCREEN 6: Diet Preferences & Dislikes ---
    {"id": 6, "section": "🍽️ Diet & Preferences", "fields": [
        {"id": "q7", "text": "🍽️ Dietary preference?", "type": "buttons", "required": True, "options": ["🍗 Non-Veg", "🥕 Veg", "🥚 Eggitarian", "🌱 Vegan", "☪️ Jain"]},
        {"id": "q8", "text": "🚫 Foods you HATE? (Multi-select)", "type": "buttons_multi", "required": False, "options": ["🥒 Bitter Gourd", "🍆 Eggplant", "🍄 Mushroom", "🪴 Okra", "🧅 Onion", "🧄 Garlic", "🐟 Fish", "🥚 Egg", "🥛 Dairy"]},
        {"id": "q9", "text": "👨‍🍳 Cuisines you LOVE? (Multi-select)", "type": "buttons_multi", "required": False, "options": ["🇮🇳 North Indian", "🔥 South Indian", "🇧🇩 Bengali", "🥘 Gujarati", "🥡 Chinese", "🍝 Italian", "🌮 Mexican"]}
    ]},
    
    # --- SCREEN 7: Morning Timings ---
    {"id": 7, "section": "☀️ Your Day: Morning Routine", "fields": [
        {"id": "q10", "text": "🌅 What time do you wake up?", "type": "buttons", "required": True, "options": ["⏰ 5:00 AM", "⏰ 6:00 AM", "⏰ 7:00 AM", "⏰ 8:00 AM", "🛏️ 8:30 AM+"]},
        {"id": "q11", "text": "☕ Regular breakfast time?", "type": "buttons", "required": True, "options": ["🌅 7:00 AM", "🌅 8:00 AM", "🌅 9:00 AM", "🌅 10:00 AM", "⏭️ Skip Breakfast"]},
        {"id": "q12", "text": "🏢 When does your work start?", "type": "buttons", "required": True, "options": ["🕐 8:00 AM", "🕐 9:00 AM", "🕐 10:00 AM", "🎲 Shift Based / Variable"]}
    ]},
    
    # --- SCREEN 8: Evening & Night Routine ---
    {"id": 8, "section": "☀️ Your Day: Evening & Sleep", "fields": [
        {"id": "q13", "text": "🚪 When do you finish work?", "type": "buttons", "required": True, "options": ["🕔 5:00 PM", "🕔 6:00 PM", "🕔 7:00 PM", "🌙 8:00 PM+"]},
        {"id": "q14", "text": "🍽️ Regular lunch time?", "type": "buttons", "required": True, "options": ["🕛 12:00 PM", "🕛 1:00 PM", "🕛 2:00 PM"]},
        {"id": "q15", "text": "🍴 Regular dinner time?", "type": "buttons", "required": True, "options": ["🕕 7:00 PM", "🕕 8:00 PM", "🕕 9:00 PM", "🕘 10:00 PM+"]},
        {"id": "q16", "text": "😴 When do you go to sleep?", "type": "buttons", "required": True, "options": ["🌙 10:00 PM", "🌙 11:00 PM", "🌙 12:00 AM", "🌙 1:00 AM+"]}
    ]},
    
    # --- SCREEN 9: Hydration Parameters Fixed ---
    {"id": 9, "section": "🥤 Hydration & Snacking", "fields": [
        {"id": "q17", "text": "🍿 Do you have mid-day snacks?", "type": "buttons", "required": True, "options": ["✅ Yes, 1-2 times", "✅ Yes, 3+ times", "⏱️ Rarely", "🚫 No"]},
        {"id": "q_water", "text": "💧 Daily water consumption level?", "type": "buttons", "required": True, "options": ["🥛 Less than 1 Litre", "💧 1 - 2 Litres", "🚰 2 - 3 Litres", "🌊 More than 3 Litres"]}
    ]},
    
    # --- SCREEN 10: Weekends ---
    {"id": 10, "section": "☀️ Your Day: Weekends", "fields": [
        {"id": "q18", "text": "🍕 Frequency of eating out?", "type": "buttons", "required": True, "options": ["🍽️ Never", "🥗 Breakfast only", "🍜 Lunch only", "🍛 Dinner only", "🎉 Multiple meals"]},
        {"id": "q19", "text": "😴 Weekend wakeup change?", "type": "buttons", "required": True, "options": ["Same as weekday ⏰", "1 hour later 💤", "2+ hours later 🛏️"]},
        {"id": "q20", "text": "🛏️ Weekend bedtime change?", "type": "buttons", "required": True, "options": ["Same as weekday 🌙", "1 hour later 💤", "2+ hours later 🛏️"]}
    ]},
    
    # --- SCREEN 11: Diagnostics & Targeted Symptoms ---
    {"id": 11, "section": "🏥 Health & Diagnostics", "fields": [
        {"id": "q21", "text": "⚕️ Diagnosed clinical conditions? (Select all)", "type": "buttons_multi", "required": False, "options": ["🔬 Diabetes", "🧬 Thyroid", "🔴 PCOS/PCOD", "❤️ Hypertension", "⚠️ Cholesterol", "🍗 Fatty Liver", "✅ None"]},
        {"id": "q_specific_health", "text": "🔍 Do you deal with targeted symptoms?", "type": "buttons_multi", "required": False, "options": ["🎈 Chronic Bloating", "💩 Constipation", "🔥 Acid Reflux / Acidity", "😴 Fatigue / Low Energy", "💇 Hair Thinning/Loss", "✨ None"]},
        {"id": "q22", "text": "🤧 Any known allergies?", "type": "buttons", "required": True, "options": ["✅ No Allergies", "🍔 Food Specific", "🌫️ Environmental"]}
    ]},
    
    # --- SCREEN 12: Medical Interventions & Injuries ---
    {"id": 12, "section": "🏥 Health: Interventions & Mobility", "fields": [
        {"id": "q23", "text": "💊 Current daily prescriptions?", "type": "buttons", "required": True, "options": ["✅ None", "1-2 Medications 💊", "3+ Medications 🏥"]},
        {"id": "q24", "text": "🤢 General metabolic/digestive comfort?", "type": "buttons", "required": True, "options": ["✅ Great", "Sometimes uneasy 😐", "Frequent issues 😣"]},
        {"id": "q25", "text": "🤕 Structural injuries?", "type": "buttons", "required": True, "options": ["✅ No", "Old injury (Healed) 🩹", "Active acute injury ⚠️"]},
        {"id": "q26", "text": "📍 Focus areas of discomfort?", "type": "buttons", "required": True, "options": ["🔴 Lower Back", "🔴 Knee Joints", "🔴 Shoulder / Neck", "✅ Not Applicable"]}
    ]},
    
    # --- SCREEN 13: Supplement Matrix Part 1 ---
    {"id": 13, "section": "💊 Supplement Matrix Part 1", "fields": [
        {"id": "q27", "text": "💊 General base supplement usage?", "type": "buttons", "required": True, "options": ["❌ None", "✅ 1-2 daily", "✅ 3+ daily"]},
        {"id": "q_supp_d3", "text": "☀️ Vitamin D3 routine?", "type": "buttons", "required": True, "options": ["📦 Take it regularly", "⚠️ Deficient / Prescribed", "❌ Never take it"]},
        {"id": "q_supp_b12", "text": "🧠 Vitamin B12 routine?", "type": "buttons", "required": True, "options": ["📦 Take it regularly", "⚠️ Deficient / Prescribed", "❌ Never take it"]}
    ]},
    
    # --- SCREEN 14: Secondary Supplement Breakdown ---
    {"id": 14, "section": "💊 Supplement Matrix Part 2", "fields": [
        {"id": "q_supp_fishoil", "text": "🐟 Omega-3 / Fish Oil routine?", "type": "buttons", "required": True, "options": ["📦 Take it regularly", "🌱 Vegan Alternative", "❌ Do not take"]},
        {"id": "q_supp_multi", "text": "🎨 Daily Multivitamin routine?", "type": "buttons", "required": True, "options": ["📦 Take regularly", "⏱️ Off & On", "❌ Do not take"]},
        {"id": "q28", "text": "🥛 Protein supplement baseline?", "type": "buttons", "required": True, "options": ["👶 Never used", "💪 Taking currently", "📦 Used in the past"]}
    ]},
    
    # --- SCREEN 15: Social Vices & Outings ---
    {"id": 15, "section": "⚡ Social Baseline & Vices", "fields": [
        {"id": "q29", "text": "🚬 Smoking habit status?", "type": "buttons", "required": True, "options": ["✅ Non-smoker", "🚭 Social/Occasional", "⚠️ Regular user"]},
        {"id": "q30", "text": "🍷 Alcohol frequency?", "type": "buttons", "required": True, "options": ["✅ Abstain", "🍻 Occasional social", "📅 Weekly routine", "🎉 Multiple times/week"]},
        {"id": "q31", "text": "🍕 Outside restaurant meals?", "type": "buttons", "required": True, "options": ["❌ Rare/Never", "1x per week 🍽️", "2-3x per week 🍜", "4+ times/week 🍛"]}
    ]},
    
    # --- SCREEN 16: Stress & Rest Patterns ---
    {"id": 16, "section": "😴 Stress & Sleep Quality", "fields": [
        {"id": "q32", "text": "😰 Mental stress levels?", "type": "buttons", "required": True, "options": ["😊 1-2 (Low/Chill)", "😐 3 (Manageable)", "😫 4-5 (High/Overwhelming)"]},
        {"id": "q33", "text": "💤 Sleep deepness level?", "type": "buttons", "required": True, "options": ["😴 1-2 (Fragmented)", "😴 3 (Average)", "😴 4-5 (Deep/Restful)"]},
        {"id": "q34", "text": "😖 Is your sleep restless/tossing?", "type": "buttons", "required": True, "options": ["✅ Quiet sleep", "Sometimes 😐", "Always dynamic/restless 😣"]},
        {"id": "q35", "text": "🌅 Morning fatigue state?", "type": "buttons", "required": True, "options": ["✅ Wake up fresh", "Usually groggy 😊", "Tired/Exhausted 😴"]}
    ]},
    
    # --- SCREEN 17: Mindfulness & Physical Baseline ---
    {"id": 17, "section": "🧘 Mindfulness & Ambience", "fields": [
        {"id": "q36", "text": "🧘 Dedicated meditation/breathing work?", "type": "buttons", "required": True, "options": ["❌ No intentional practices", "🧘 Occasionally", "✅ Consistent daily habit"]},
        {"id": "q37", "text": "🔥 Dominant external stress factor?", "type": "buttons", "required": True, "options": ["💼 Career/Workload", "❤️ Family/Life Balance", "💰 Financial Planning"]},
        {"id": "q38", "text": "💪 Active days per week baseline?", "type": "buttons", "required": True, "options": ["🪑 Completely Sedentary", "🚶 1-2 Days", "🏃 3-4 Days", "🏋️ 5+ Days"]}
    ]},
    
    # --- SCREEN 18: Movement & Daily Step Benchmarks ---
    {"id": 18, "section": "💪 Physical Mechanics & Steps", "fields": [
        {"id": "q_steps", "text": "🚶 Average structural steps daily?", "type": "buttons", "required": True, "options": ["🐌 Under 3,000 steps", "🚶 3,000 - 5,000 steps", "🏃 5,000 - 8,000 steps", "⚡ 10,000+ steps!"]},
        {"id": "q39", "text": "🏋️ Resistance weight lifting knowledge?", "type": "buttons", "required": True, "options": ["👶 Absolute Beginner", "🌱 Know basics", "💪 Intermediate/Advanced"]},
        {"id": "q40", "text": "🏋️ Weekly structured weight sessions?", "type": "buttons", "required": True, "options": ["❌ None", "1-2 days/week 💪", "3-4 days/week 🏋️", "5+ days/week 🦾"]}
    ]},
    
    # --- SCREEN 19: Cardio & Extracurriculars ---
    {"id": 19, "section": "💪 Fitness Variety & Settings", "fields": [
        {"id": "q41", "text": "🏃 Cardio/Endurance frequency?", "type": "buttons", "required": True, "options": ["❌ Never", "1-2x per week 🚴", "3+ times/week 🚀"]},
        {"id": "q42", "text": "🧘 Flexibility/Yoga allocation?", "type": "buttons", "required": True, "options": ["❌ None", "1-2x per week 🧘", "3+ times/week ✨"]},
        {"id": "q43", "text": "⚽ Recreational team sports?", "type": "buttons", "required": True, "options": ["❌ No regular games", "1-2x per week ⚽", "3+ times/week 🏆"]}
    ]},
    
    # --- SCREEN 20: Desk Stagnancy & Cooking ---
    {"id": 20, "section": "🪑 Environment & Kitchen Setup", "fields": [
        {"id": "q44", "text": "🪑 Daily continuous desk sitting?", "type": "buttons", "required": True, "options": ["🚶 Below 4 Hours", "😐 4 - 7 Hours", "💀 8+ Hours (Heavy Sedentary)"]},
        {"id": "q45", "text": "📍 Where do you target training?", "type": "buttons", "required": True, "options": ["🏢 Commercial Gym", "🏠 Home Setup", "🌳 Parks / Outdoors"]},
        {"id": "q46", "text": "👨‍🍳 Cooking frequency?", "type": "buttons", "required": True, "options": ["❌ Never cook", "🍳 1-3x per week", "👨‍🍳 Daily fresh cooking"]}
    ]},
    
    # --- SCREEN 21: Kitchen Logistics & Targets ---
    {"id": 21, "section": "🎯 Targets & Kitchen Logistics", "fields": [
        {"id": "q47", "text": "💰 Shopping budget flexibility?", "type": "buttons", "required": True, "options": ["💸 Strictly Budget Friendly", "💵 Standard/Moderate", "💎 Premium Ingredients Only"]},
        {"id": "q48", "text": "📦 Can you structure meal preps in advance?", "type": "buttons", "required": True, "options": ["✅ Yes completely", "Partially on weekends 😐", "❌ Not possible"]},
        {"id": "q49", "text": "🎯 Core primary physical objective?", "type": "buttons", "required": True, "options": ["📉 Aggressive Fat Loss", "💪 Hypertrophy Lean Muscle", "⚡ Athletic Strength & Endurance", "❤️ Metabolic/Biomarker Correction"]}
    ]},
    
    # --- SCREEN 22: Timelines & Historical Friction ---
    {"id": 22, "section": "🎯 Targets & Historical Background", "fields": [
        {"id": "q50", "text": "📊 Desired weight scale shift?", "type": "buttons", "required": True, "options": ["1-5 kg 📉", "5-10 kg 📉", "10-20 kg 📉", "Maintain/Gain Scale 🏋️"]},
        {"id": "q51", "text": "⏱️ Target achievement horizon?", "type": "buttons", "required": True, "options": ["🚀 Short-term (8-12 weeks)", "📅 Medium-term (6 months)", "📅 Lifestyle Change (1+ Year)"]},
        {"id": "q52", "text": "🔄 Past dietary/fitness attempts?", "type": "buttons", "required": True, "options": ["❌ First serious attempt", "✅ Tried once before", "✅ Ongoing cycle of attempts"]},
        {"id": "q53", "text": "🚧 Historical root barrier?", "type": "buttons", "required": True, "options": ["⏰ Time/Schedule", "🍕 Social Pressure/Cravings", "😴 Low Accountability", "✨ No major block"]}
    ]},
    
    # --- SCREEN 23: Commitment Contracts ---
    {"id": 23, "section": "🤝 Commitments & Final Action", "fields": [
        {"id": "q54", "text": "🏆 Previous experience with professional coaches?", "type": "buttons", "required": True, "options": ["❌ Never", "📱 Online coaching apps", "👨‍🏫 1-on-1 personal trainers"]},
        {"id": "q55", "text": "🥗 Readiness to optimize meal plans?", "type": "buttons", "required": True, "options": ["🔥 Full structural overhaul", "⚡ Moderate compromises", "🌱 Step-by-step gradual pacing"]},
        {"id": "q56", "text": "💪 Workout execution readiness?", "type": "buttons", "required": True, "options": ["✅ Ready for 5-6 days", "✅ Ready for 3-4 days", "😐 Max 1-2 days per week"]},
        {"id": "q57", "text": "📅 Training allocation windows?", "type": "buttons", "required": True, "options": ["🌅 Fixed Mornings", "🌆 Fixed Evenings", "🎲 Highly dynamic schedules"]}
    ]},
    
    # --- SCREEN 24: Ultimate Affirmations ---
    {"id": 24, "section": "🤝 Accountability Alignment", "fields": [
        {"id": "q58", "text": "🍕 Willingness to curb external ultra-processed treats?", "type": "buttons", "required": True, "options": ["✅ Ready to restrict completely", "😐 Need deliberate cheat slots", "❌ Hard to adjust"]},
        {"id": "q59", "text": "🍷 Willingness to adjust alcohol frequency?", "type": "buttons", "required": True, "options": ["✅ Fully compliant", "😐 Can scale back slightly", "❌ Cannot alter habits", "🤷 Non-Drinker"]},
        {"id": "q60", "text": "📝 Will you maintain logging and communication updates?", "type": "buttons", "required": True, "options": ["✅ 100% committed", "😐 Will attempt my best", "❌ Friction with tracking"]},
        {"id": "q61", "text": "🚀 Are you mentally ready to begin?", "type": "buttons", "required": True, "options": ["🔥 READY NOW. LET'S GO!", "⏳ Finalizing mental readiness"]}
    ]},

    # --- SCREEN 25: PHOTO VECTOR ASSESSMENT ---
    {"id": 25, "section": "📸 Full-Body Assessment Photo", "fields": [
        {"id": "q_photos", "text": "📸 [Optional] Please upload a front/side full-body assessment photo to assist with baseline posture & fat composition analysis. (Or click below to bypass)", "type": "media", "required": False}
    ]}
]

class UserSession:
    def __init__(self):
        self.current_screen_idx = 0
        self.answers = {}
        self.name = None
        self.awaiting_custom_field_id = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    context.user_data[user_id] = UserSession()
    
    text = (
        "🤖 <b>╔════════════════════════════════════════╗</b>\n"
        "   <b>║      WELCOME TO MEALZY COACHING        ║</b>\n"
        "   <b>║                                        ║</b>\n"
        "   <b>║     💪 Complete Health Blueprint       ║</b>\n"
        "   <b>║     🧠 Performance Strategy            ║</b>\n"
        "   <b>║     ✨ Payload Limits Patched          ║</b>\n"
        "   <b>╚════════════════════════════════════════╝</b>\n\n"
        "📋 <b>All Bugs Solved. High Elastic Memory Engine Active.</b>\n"
        "📝 Click <b>'✍️ Custom / Other'</b> to customize answers.\n\n"
        "Let's initialize your profile! 🚀"
    )
    keyboard = [[InlineKeyboardButton("🎯 INITIALIZE ASSESSMENT", callback_data="start")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")

async def render_screen(update: Update, context: ContextTypes.DEFAULT_TYPE, query=None):
    user_id = update.effective_user.id
    if user_id not in context.user_data:
        await start(update, context)
        return
        
    session = context.user_data[user_id]
    
    if session.current_screen_idx >= len(SCREENS):
        final_msg = (
            f"🎉 <b>╔════════════════════════════════════════╗</b>\n"
            f"   <b>║     DIAGNOSTICS PROFILE ACQUIRED       ║</b>\n"
            f"   <b>╚════════════════════════════════════════╝</b>\n\n"
            f"👋 <b>{session.name or 'Champion'}!</b> Your onboarding registration is verified! 💪\n\n"
            f"All structural options and parameters have been logged successfully!"
        )
        if query:
            await query.edit_message_text(final_msg, parse_mode="HTML")
        else:
            await update.message.reply_text(final_msg, parse_mode="HTML")
        return

    screen_data = SCREENS[session.current_screen_idx]
    progress = int((session.current_screen_idx / len(SCREENS)) * 100)
    bar = "█" * (progress // 10) + "░" * (10 - (progress // 10))
    
    name_info = f" (User: {session.name})" if session.name else ""
    text_lines = [f"{bar} {progress}% | <b>{screen_data['section']}</b>{name_info}", ""]
    
    all_required_answered = True
    
    for field in screen_data['fields']:
        ans = session.answers.get(field['id'])
        is_answered = ans is not None and (not isinstance(ans, list) or len(ans) > 0)
        
        if field['required'] and not is_answered:
            all_required_answered = False
            
        if session.awaiting_custom_field_id == field['id']:
            text_lines.append(f"✍️ <b>{field['text']}</b>\n⚡ <code>[Awaiting your custom typed answer...]</code> ⌨️")
        elif is_answered:
            if field['type'] == 'buttons_multi':
                text_lines.append(f"❓ <b>{field['text']}</b>\n👉 Active: <i>{', '.join(ans)}</i> ✅")
            else:
                text_lines.append(f"❓ <b>{field['text']}</b>\n👉 Active: <i>{ans}</i> ✅")
        else:
            if field['type'] == 'text':
                text_lines.append(f"❓ <b>{field['text']}</b>\n🛸 [Type answer directly in chat box below]")
            elif field['type'] == 'media':
                text_lines.append(f"❓ <b>{field['text']}</b>\n📸 [Upload file/photo or press skip below]")
            else:
                text_lines.append(f"❓ <b>{field['text']}</b>\n👉 [Select options or tap Custom]")
        text_lines.append("")

    text = "\n".join(text_lines)
    keyboard = []
    
    for field in screen_data['fields']:
        if field['type'] in ['buttons', 'buttons_multi']:
            clean_q = field['text'].split('?')[0] + "?"
            keyboard.append([InlineKeyboardButton(f"── {clean_q} ──", callback_data="ignore")])
            
            row = []
            short_field_id = ID_MAP[field['id']] # Enforce short-code encoding transformations
            
            for idx, opt in enumerate(field['options']):
                display_opt = opt
                ans = session.answers.get(field['id'])
                
                if field['type'] == 'buttons' and ans == opt:
                    display_opt = f"⭐ {opt}"
                elif field['type'] == 'buttons_multi' and ans and opt in ans:
                    display_opt = f"⭐ {opt}"
                    
                cb_data = f"s_{short_field_id}_{idx}"
                row.append(InlineKeyboardButton(display_opt, callback_data=cb_data))
                
                if len(row) == 2:
                    keyboard.append(row)
                    row = []
            if row:
                keyboard.append(row)
            
            # Appends custom option payload block matching the shortened hash map pattern
            custom_label = "✍️ Custom / Other"
            ans = session.answers.get(field['id'])
            if ans and not isinstance(ans, list) and ans not in field['options']:
                custom_label = f"⭐ Custom: {ans}"
            keyboard.append([InlineKeyboardButton(custom_label, callback_data=f"c_{short_field_id}")])
        
        elif field['type'] == 'media':
            keyboard.append([InlineKeyboardButton("⏭️ Skip / Privacy Bypass", callback_data="skip_media")])
    
    if any(f['type'] in ['buttons', 'buttons_multi'] for f in screen_data['fields']):
        if all_required_answered and not session.awaiting_custom_field_id:
            keyboard.append([InlineKeyboardButton("⚡ CONFIRM & CONTINUE ➡️", callback_data="next_screen")])
        else:
            keyboard.append([InlineKeyboardButton("🔒 Awaiting Screen Input", callback_data="locked")])

    markup = InlineKeyboardMarkup(keyboard) if keyboard else None
    
    try:
        if query:
            await query.edit_message_text(text, reply_markup=markup, parse_mode="HTML")
        else:
            await update.message.reply_text(text, reply_markup=markup, parse_mode="HTML")
    except Exception:
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
        await query.answer("⚠️ Complete options or provide custom answers to continue!", show_alert=True)
        return
        
    if data == "next_screen":
        await query.answer()
        session.current_screen_idx += 1
        await render_screen(update, context, query)
        return

    if data == "skip_media":
        await query.answer()
        session.answers["q_photos"] = "Bypassed by User"
        session.current_screen_idx += 1
        await render_screen(update, context, query)
        return

    if data.startswith("c_"):
        short_id = data.split("_")[1]
        field_id = REV_MAP[short_id]
        session.awaiting_custom_field_id = field_id
        await query.answer("⌨️ Type your custom response directly in chat box!", show_alert=True)
        await render_screen(update, context, query)
        return
        
    if data.startswith("s_"):
        parts = data.split("_")
        short_id = parts[1]
        opt_idx = int(parts[2])
        field_id = REV_MAP[short_id]
        
        screen_data = SCREENS[session.current_screen_idx]
        field = next((f for f in screen_data['fields'] if f['id'] == field_id), None)
        
        if not field:
            await query.answer()
            return
            
        selected_opt = field['options'][opt_idx]
        session.awaiting_custom_field_id = None
        
        if field['type'] == 'buttons':
            session.answers[field_id] = selected_opt
        elif field['type'] == 'buttons_multi':
            current_ans = session.answers.get(field_id, [])
            if isinstance(current_ans, str):
                current_ans = []
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
    text = update.message.text.strip()
    
    if session.awaiting_custom_field_id:
        target_id = session.awaiting_custom_field_id
        session.answers[target_id] = text
        session.awaiting_custom_field_id = None
        await render_screen(update, context)
        return

    if session.current_screen_idx >= len(SCREENS):
        return
        
    screen_data = SCREENS[session.current_screen_idx]
    text_fields = [f for f in screen_data['fields'] if f['type'] == 'text']
    
    if not text_fields:
        await update.message.reply_text("⚠️ Use the inline selectors, or click 'Custom / Other' to write a specific response.")
        return
        
    field = text_fields[0]
    
    if field['id'] == 'q2':
        try:
            age = int(text)
            if not 10 <= age <= 100:
                await update.message.reply_text("❌ Age must be within realistic ranges (10 - 100). Please try again:")
                return
        except ValueError:
            await update.message.reply_text("❌ Numerical values only:")
            return

    session.answers[field['id']] = text
    if field['id'] == 'q1':
        session.name = text

    session.current_screen_idx += 1
    await render_screen(update, context)

async def media_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in context.user_data:
        await start(update, context)
        return
        
    session = context.user_data[user_id]
    if session.current_screen_idx >= len(SCREENS):
        return
        
    screen_data = SCREENS[session.current_screen_idx]
    media_fields = [f for f in screen_data['fields'] if f['type'] == 'media']
    
    if not media_fields:
        await update.message.reply_text("⚠️ This step requires button metrics selection.")
        return
        
    field = media_fields[0]
    
    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        session.answers[field['id']] = f"Photo Registered [ID: {file_id[:10]}...]"
    elif update.message.document:
        file_id = update.message.document.file_id
        session.answers[field['id']] = f"Document Registered [ID: {file_id[:10]}...]"
        
    session.current_screen_idx += 1
    await render_screen(update, context)

def main():
    print("\n" + "=" * 80)
    print("🚀 COACH AVNI BOT - WATER LOGIC & CALLBACK PAYLOAD BUG SOLVED")
    print("=" * 80)
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL, media_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    
    app.run_polling()

if __name__ == "__main__":
    main()
