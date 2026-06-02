#!/usr/bin/env python3
"""
COACH AVNI BOT - SMART INTELLIGENCE ENGINE EDITION
✅ Smart: Auto-advances single-choice button screens instantly upon completion (No tedious double clicks).
✅ Smart: Dynamic live "Coach Insights" injected based on preceding metric answers.
✅ Smart: Cross-field dependency mapping (Selecting 'No Injuries' auto-populates focus zones & advances).
✅ Fixed: Preserves short-code hash layout safely below Telegram's 64-byte limit with zero collisions.
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
# UNIQUE SHORT-CODE MAPPING MATRIX (Zero Collisions Guarantee)
# ============================================================================
ID_MAP = {
    "q1": "n", "q2": "ag", "q3": "ht", "q4": "wt", "q5": "pf", "q6": "sx",
    "q7": "dp", "q8": "fh", "q9": "cl", "q10": "wu", "q11": "bt", "q12": "wst",
    "q13": "wen", "q14": "lt", "q15": "dt", "q16": "st", "q17": "sn", "q_water": "w",
    "q18": "eo", "q19": "ww", "q20": "wb", "q21": "cc", "q_specific_health": "sh",
    "q22": "al", "q23": "dpr", "q24": "dc", "q25": "si", "q26": "da", "q27": "su",
    "q_supp_d3": "d3", "q_supp_b12": "b12", "q_supp_fishoil": "fo", "q_supp_multi": "mv",
    "q28": "ps", "q29": "sm", "q30": "af", "q31": "rm", "q32": "sl", "q33": "sd",
    "q34": "rt", "q35": "mf", "q36": "mp", "q37": "sf", "q38": "ad", "q_steps": "sp",
    "q39": "wl", "q40": "wse", "q41": "cf", "q42": "ya", "q43": "ts", "q44": "ds",
    "q45": "tl", "q46": "ckf", "q47": "bf", "q48": "mpr", "q49": "po", "q50": "wsh",
    "q51": "ah", "q52": "pa", "q53": "rb", "q54": "ec", "q55": "om", "q56": "wex",
    "q57": "aw", "q58": "ce", "q59": "aa", "q60": "ml", "q61": "mr", "q_photos": "ph"
}

REV_MAP = {v: k for k, v in ID_MAP.items()}

# ============================================================================
# COMPREHENSIVE ONBOARDING CORE QUESTIONNAIRE DATA OBJECT
# ============================================================================
SCREENS = [
    {"id": 1, "section": "👤 About You", "fields": [{"id": "q1", "text": "👤 What's your full name?", "type": "text", "required": True}]},
    {"id": 2, "section": "👤 About You", "fields": [{"id": "q2", "text": "🎂 What's your age?", "type": "text", "required": True}]},
    {"id": 3, "section": "👤 About You", "fields": [{"id": "q3", "text": "📏 Current height (cm)?", "type": "text", "required": True}]},
    {"id": 4, "section": "👤 About You", "fields": [{"id": "q4", "text": "⚖️ Current weight (kg)?", "type": "text", "required": True}]},
    
    {"id": 5, "section": "💼 Work & Details", "fields": [
        {"id": "q5", "text": "💼 What's your profession?", "type": "buttons", "required": True, "options": ["💻 Engineer", "👨‍⚕️ Doctor", "📚 Student", "🏫 Teacher", "👔 Business Owner", "🤵 Consultant", "📊 Finance", "🎯 Sales"]},
        {"id": "q6", "text": "⚡ Biological sex?", "type": "buttons", "required": True, "options": ["👨 Male", "👩 Female"]}
    ]},
    
    {"id": 6, "section": "🍽️ Diet & Preferences", "fields": [
        {"id": "q7", "text": "🍽️ Dietary preference?", "type": "buttons", "required": True, "options": ["🍗 Non-Veg", "🥕 Veg", "🥚 Eggitarian", "🌱 Vegan", "☪️ Jain"]},
        {"id": "q8", "text": "🚫 Foods you HATE? (Multi-select)", "type": "buttons_multi", "required": False, "options": ["🥒 Bitter Gourd", "🍆 Eggplant", "🍄 Mushroom", "🪴 Okra", "🧅 Onion", "🧄 Garlic", "🐟 Fish", "🥚 Egg", "🥛 Dairy"]},
        {"id": "q9", "text": "👨‍🍳 Cuisines you LOVE? (Multi-select)", "type": "buttons_multi", "required": False, "options": ["🇮🇳 North Indian", "🔥 South Indian", "🇧🇩 Bengali", "🥘 Gujarati", "🥡 Chinese", "🍝 Italian", "🌮 Mexican"]}
    ]},
    
    {"id": 7, "section": "☀️ Your Day: Morning Routine", "fields": [
        {"id": "q10", "text": "🌅 What time do you wake up?", "type": "buttons", "required": True, "options": ["⏰ 5:00 AM", "⏰ 6:00 AM", "⏰ 7:00 AM", "⏰ 8:00 AM", "🛏️ 8:30 AM+"]},
        {"id": "q11", "text": "☕ Regular breakfast time?", "type": "buttons", "required": True, "options": ["🌅 7:00 AM", "🌅 8:00 AM", "🌅 9:00 AM", "🌅 10:00 AM", "⏭️ Skip Breakfast"]},
        {"id": "q12", "text": "🏢 When does your work start?", "type": "buttons", "required": True, "options": ["🕐 8:00 AM", "🕐 9:00 AM", "🕐 10:00 AM", "🎲 Shift Based / Variable"]}
    ]},
    
    {"id": 8, "section": "☀️ Your Day: Evening & Sleep", "fields": [
        {"id": "q13", "text": "🚪 When do you finish work?", "type": "buttons", "required": True, "options": ["🕔 5:00 PM", "🕔 6:00 PM", "🕔 7:00 PM", "🌙 8:00 PM+"]},
        {"id": "q14", "text": "🍽️ Regular lunch time?", "type": "buttons", "required": True, "options": ["🕛 12:00 PM", "🕛 1:00 PM", "🕛 2:00 PM"]},
        {"id": "q15", "text": "🍴 Regular dinner time?", "type": "buttons", "required": True, "options": ["🕕 7:00 PM", "🕕 8:00 PM", "🕕 9:00 PM", "🕘 10:00 PM+"]},
        {"id": "q16", "text": "😴 When do you go to sleep?", "type": "buttons", "required": True, "options": ["🌙 10:00 PM", "🌙 11:00 PM", "🌙 12:00 AM", "🌙 1:00 AM+"]}
    ]},
    
    {"id": 9, "section": "🥤 Hydration & Snacking", "fields": [
        {"id": "q17", "text": "🍿 Do you have mid-day snacks?", "type": "buttons", "required": True, "options": ["✅ Yes, 1-2 times", "✅ Yes, 3+ times", "⏱️ Rarely", "🚫 No"]},
        {"id": "q_water", "text": "💧 Daily water consumption level?", "type": "buttons", "required": True, "options": ["🥛 Less than 1 Litre", "💧 1 - 2 Litres", "🚰 2 - 3 Litres", "🌊 More than 3 Litres"]}
    ]},
    
    {"id": 10, "section": "☀️ Your Day: Weekends", "fields": [
        {"id": "q18", "text": "🍕 Frequency of eating out?", "type": "buttons", "required": True, "options": ["🍽️ Never", "🥗 Breakfast only", "🍜 Lunch only", "🍛 Dinner only", "🎉 Multiple meals"]},
        {"id": "q19", "text": "😴 Weekend wakeup change?", "type": "buttons", "required": True, "options": ["Same as weekday ⏰", "1 hour later 💤", "2+ hours later 🛏️"]},
        {"id": "q20", "text": "🛏️ Weekend bedtime change?", "type": "buttons", "required": True, "options": ["Same as weekday 🌙", "1 hour later 💤", "2+ hours later 🛏️"]}
    ]},
    
    {"id": 11, "section": "🏥 Health & Diagnostics", "fields": [
        {"id": "q21", "text": "⚕️ Diagnosed clinical conditions? (Select all)", "type": "buttons_multi", "required": False, "options": ["🔬 Diabetes", "🧬 Thyroid", "🔴 PCOS/PCOD", "❤️ Hypertension", "⚠️ Cholesterol", "🍗 Fatty Liver", "✅ None"]},
        {"id": "q_specific_health", "text": "🔍 Do you deal with targeted symptoms?", "type": "buttons_multi", "required": False, "options": ["🎈 Chronic Bloating", "💩 Constipation", "🔥 Acid Reflux / Acidity", "😴 Fatigue / Low Energy", "💇 Hair Thinning/Loss", "✨ None"]},
        {"id": "q22", "text": "🤧 Any known allergies?", "type": "buttons", "required": True, "options": ["✅ No Allergies", "🍔 Food Specific", "🌫️ Environmental"]}
    ]},
    
    {"id": 12, "section": "🏥 Health: Interventions & Mobility", "fields": [
        {"id": "q23", "text": "💊 Current daily prescriptions?", "type": "buttons", "required": True, "options": ["✅ None", "1-2 Medications 💊", "3+ Medications 🏥"]},
        {"id": "q24", "text": "🤢 General metabolic/digestive comfort?", "type": "buttons", "required": True, "options": ["✅ Great", "Sometimes uneasy 😐", "Frequent issues 😣"]},
        {"id": "q25", "text": "🤕 Structural injuries?", "type": "buttons", "required": True, "options": ["✅ No", "Old injury (Healed) 🩹", "Active acute injury ⚠️"]},
        {"id": "q26", "text": "📍 Focus areas of discomfort?", "type": "buttons", "required": True, "options": ["🔴 Lower Back", "🔴 Knee Joints", "🔴 Shoulder / Neck", "✅ Not Applicable"]}
    ]},
    
    {"id": 13, "section": "💊 Supplement Matrix Part 1", "fields": [
        {"id": "q27", "text": "💊 General base supplement usage?", "type": "buttons", "required": True, "options": ["❌ None", "✅ 1-2 daily", "✅ 3+ daily"]},
        {"id": "q_supp_d3", "text": "☀️ Vitamin D3 routine?", "type": "buttons", "required": True, "options": ["📦 Take it regularly", "⚠️ Deficient / Prescribed", "❌ Never take it"]},
        {"id": "q_supp_b12", "text": "🧠 Vitamin B12 routine?", "type": "buttons", "required": True, "options": ["📦 Take it regularly", "⚠️ Deficient / Prescribed", "❌ Never take it"]}
    ]},
    
    {"id": 14, "section": "💊 Supplement Matrix Part 2", "fields": [
        {"id": "q_supp_fishoil", "text": "🐟 Omega-3 / Fish Oil routine?", "type": "buttons", "required": True, "options": ["📦 Take it regularly", "🌱 Vegan Alternative", "❌ Do not take"]},
        {"id": "q_supp_multi", "text": "🎨 Daily Multivitamin routine?", "type": "buttons", "required": True, "options": ["📦 Take regularly", "⏱️ Off & On", "❌ Do not take"]},
        {"id": "q28", "text": "🥛 Protein supplement baseline?", "type": "buttons", "required": True, "options": ["👶 Never used", "💪 Taking currently", "📦 Used in the past"]}
    ]},
    
    {"id": 15, "section": "⚡ Social Baseline & Vices", "fields": [
        {"id": "q29", "text": "🚬 Smoking habit status?", "type": "buttons", "required": True, "options": ["✅ Non-smoker", "🚭 Social/Occasional", "⚠️ Regular user"]},
        {"id": "q30", "text": "🍷 Alcohol frequency?", "type": "buttons", "required": True, "options": ["✅ Abstain", "🍻 Occasional social", "📅 Weekly routine", "🎉 Multiple times/week"]},
        {"id": "q31", "text": "🍕 Outside restaurant meals?", "type": "buttons", "required": True, "options": ["❌ Rare/Never", "1x per week 🍽️", "2-3x per week 🍜", "4+ times/week 🍛"]}
    ]},
    
    {"id": 16, "section": "😴 Stress & Sleep Quality", "fields": [
        {"id": "q32", "text": "😰 Mental stress levels?", "type": "buttons", "required": True, "options": ["😊 1-2 (Low/Chill)", "😐 3 (Manageable)", "😫 4-5 (High/Overwhelming)"]},
        {"id": "q33", "text": "💤 Sleep deepness level?", "type": "buttons", "required": True, "options": ["😴 1-2 (Fragmented)", "😴 3 (Average)", "😴 4-5 (Deep/Restful)"]},
        {"id": "q34", "text": "😖 Is your sleep restless/tossing?", "type": "buttons", "required": True, "options": ["✅ Quiet sleep", "Sometimes 😐", "Always dynamic/restless 😣"]},
        {"id": "q35", "text": "🌅 Morning fatigue state?", "type": "buttons", "required": True, "options": ["✅ Wake up fresh", "Usually groggy 😊", "Tired/Exhausted 😴"]}
    ]},
    
    {"id": 17, "section": "🧘 Mindfulness & Ambience", "fields": [
        {"id": "q36", "text": "🧘 Dedicated meditation/breathing work?", "type": "buttons", "required": True, "options": ["❌ No intentional practices", "🧘 Occasionally", "✅ Consistent daily habit"]},
        {"id": "q37", "text": "🔥 Dominant external stress factor?", "type": "buttons", "required": True, "options": ["💼 Career/Workload", "❤️ Family/Life Balance", "💰 Financial Planning"]},
        {"id": "q38", "text": "💪 Active days per week baseline?", "type": "buttons", "required": True, "options": ["🪑 Completely Sedentary", "🚶 1-2 Days", "🏃 3-4 Days", "🏋️ 5+ Days"]}
    ]},
    
    {"id": 18, "section": "💪 Physical Mechanics & Steps", "fields": [
        {"id": "q_steps", "text": "🚶 Average structural steps daily?", "type": "buttons", "required": True, "options": ["🐌 Under 3,000 steps", "🚶 3,000 - 5,000 steps", "🏃 5,000 - 8,000 steps", "⚡ 10,000+ steps!"]},
        {"id": "q39", "text": "🏋️ Resistance weight lifting knowledge?", "type": "buttons", "required": True, "options": ["👶 Absolute Beginner", "🌱 Know basics", "💪 Intermediate/Advanced"]},
        {"id": "q40", "text": "🏋️ Weekly structured weight sessions?", "type": "buttons", "required": True, "options": ["❌ None", "1-2 days/week 💪", "3-4 days/week 🏋️", "5+ days/week 🦾"]}
    ]},
    
    {"id": 19, "section": "💪 Fitness Variety & Settings", "fields": [
        {"id": "q41", "text": "🏃 Cardio/Endurance frequency?", "type": "buttons", "required": True, "options": ["❌ Never", "1-2x per week 🚴", "3+ times/week 🚀"]},
        {"id": "q42", "text": "🧘 Flexibility/Yoga allocation?", "type": "buttons", "required": True, "options": ["❌ None", "1-2x per week 🧘", "3+ times/week ✨"]},
        {"id": "q43", "text": "⚽ Recreational team sports?", "type": "buttons", "required": True, "options": ["❌ No regular games", "1-2x per week ⚽", "3+ times/week 🏆"]}
    ]},
    
    {"id": 20, "section": "🪑 Environment & Kitchen Setup", "fields": [
        {"id": "q44", "text": "🪑 Daily continuous desk sitting?", "type": "buttons", "required": True, "options": ["🚶 Below 4 Hours", "😐 4 - 7 Hours", "💀 8+ Hours (Heavy Sedentary)"]},
        {"id": "q45", "text": "📍 Where do you target training?", "type": "buttons", "required": True, "options": ["🏢 Commercial Gym", "🏠 Home Setup", "🌳 Parks / Outdoors"]},
        {"id": "q46", "text": "👨‍🍳 Cooking frequency?", "type": "buttons", "required": True, "options": ["❌ Never cook", "🍳 1-3x per week", "👨‍🍳 Daily fresh cooking"]}
    ]},
    
    {"id": 21, "section": "🎯 Targets & Kitchen Logistics", "fields": [
        {"id": "q47", "text": "💰 Shopping budget flexibility?", "type": "buttons", "required": True, "options": ["💸 Strictly Budget Friendly", "💵 Standard/Moderate", "💎 Premium Ingredients Only"]},
        {"id": "q48", "text": "📦 Can you structure meal preps in advance?", "type": "buttons", "required": True, "options": ["✅ Yes completely", "Partially on weekends 😐", "❌ Not possible"]},
        {"id": "q49", "text": "🎯 Core primary physical objective?", "type": "buttons", "required": True, "options": ["📉 Aggressive Fat Loss", "💪 Hypertrophy Lean Muscle", "⚡ Athletic Strength & Endurance", "❤️ Metabolic/Biomarker Correction"]}
    ]},
    
    {"id": 22, "section": "🎯 Targets & Historical Background", "fields": [
        {"id": "q50", "text": "📊 Desired weight scale shift?", "type": "buttons", "required": True, "options": ["1-5 kg 📉", "5-10 kg 📉", "10-20 kg 📉", "Maintain/Gain Scale 🏋️"]},
        {"id": "q51", "text": "⏱️ Target achievement horizon?", "type": "buttons", "required": True, "options": ["🚀 Short-term (8-12 weeks)", "📅 Medium-term (6 months)", "📅 Lifestyle Change (1+ Year)"]},
        {"id": "q52", "text": "🔄 Past dietary/fitness attempts?", "type": "buttons", "required": True, "options": ["❌ First serious attempt", "✅ Tried once before", "✅ Ongoing cycle of attempts"]},
        {"id": "q53", "text": "🚧 Historical root barrier?", "type": "buttons", "required": True, "options": ["⏰ Time/Schedule", "🍕 Social Pressure/Cravings", "😴 Low Accountability", "✨ No major block"]}
    ]},
    
    {"id": 23, "section": "🤝 Commitments & Final Action", "fields": [
        {"id": "q54", "text": "🏆 Previous experience with professional coaches?", "type": "buttons", "required": True, "options": ["❌ Never", "📱 Online coaching apps", "👨‍🏫 1-on-1 personal trainers"]},
        {"id": "q55", "text": "🥗 Readiness to optimize meal plans?", "type": "buttons", "required": True, "options": ["🔥 Full structural overhaul", "⚡ Moderate compromises", "🌱 Step-by-step gradual pacing"]},
        {"id": "q56", "text": "💪 Workout execution readiness?", "type": "buttons", "required": True, "options": ["✅ Ready for 5-6 days", "✅ Ready for 3-4 days", "😐 Max 1-2 days per week"]},
        {"id": "q57", "text": "📅 Training allocation windows?", "type": "buttons", "required": True, "options": ["🌅 Fixed Mornings", "🌆 Fixed Evenings", "🎲 Highly dynamic schedules"]}
    ]},
    
    {"id": 24, "section": "🤝 Accountability Alignment", "fields": [
        {"id": "q58", "text": "🍕 Willingness to curb external ultra-processed treats?", "type": "buttons", "required": True, "options": ["✅ Ready to restrict completely", "😐 Need deliberate cheat slots", "❌ Hard to adjust"]},
        {"id": "q59", "text": "🍷 Willingness to adjust alcohol frequency?", "type": "buttons", "required": True, "options": ["✅ Fully compliant", "😐 Can scale back slightly", "❌ Cannot alter habits", "🤷 Non-Drinker"]},
        {"id": "q60", "text": "📝 Will you maintain logging and communication updates?", "type": "buttons", "required": True, "options": ["✅ 100% committed", "😐 Will attempt my best", "❌ Friction with tracking"]},
        {"id": "q61", "text": "🚀 Are you mentally ready to begin?", "type": "buttons", "required": True, "options": ["🔥 READY NOW. LET'S GO!", "⏳ Finalizing mental readiness"]}
    ]},

    {"id": 25, "section": "📸 Full-Body Assessment Photo", "fields": [
        {"id": "q_photos", "text": "📸 [Optional] Please upload a front/side full-body photo to assist with fat composition analysis.", "type": "media", "required": False}
    ]}
]

class UserSession:
    def __init__(self):
        self.current_screen_idx = 0
        self.answers = {}
        self.name = None
        self.awaiting_custom_field_id = None

# ============================================================================
# SMART INTELLIGENCE INJECTION ENGINES
# ============================================================================
def generate_coach_insight(session) -> str:
    """Reads current profile context and generates real-time predictive health logs."""
    insights = []
    
    if session.answers.get("q_water") == "🥛 Less than 1 Litre":
        insights.append("⚠️ <b>Hydration Deficit</b>: Consuming <1L drops baseline metabolic rate. We'll fix this first.")
    if session.answers.get("q32") and "4-5" in str(session.answers.get("q32")):
        insights.append("📉 <b>High Cortisol Risk</b>: High stress impedes recovery. Adding morning parasympathetic routines.")
    if session.answers.get("q35") and "Tired" in str(session.answers.get("q35")):
        insights.append("😴 <b>REM Deprivation</b>: Morning fatigue indicates low slow-wave sleep. Night windows will adjust.")
    if session.answers.get("q44") and "Heavy Sedentary" in str(session.answers.get("q44")):
        insights.append("🪑 <b>Postural Loading</b>: 8+ hrs desk sitting detected. Simple structural 'movement snacks' will be assigned.")
        
    if insights:
        return "💡 <b>LIVE COACH ASSESSMENT:</b>\n" + "\n".join(insights[-2:]) + "\n\n"
    return ""

def generate_diagnostic_dossier(session) -> str:
    """Compiles answers into an elegantly categorized final report for the coach."""
    def get_ans(qid, alt="Not provided"):
        v = session.answers.get(qid, alt)
        return ", ".join(v) if isinstance(v, list) else str(v)

    return (
        f"📋 <b>╔════════════════════════════════════════╗</b>\n"
        f"   <b>║     ONBOARDING DIAGNOSTIC COMPLETE     ║</b>\n"
        f"   <b>╚════════════════════════════════════════╝</b>\n\n"
        f"👤 <b>METRIC PROFILE:</b> {session.name or 'Champion'}\n"
        f"• Age/Height/Weight: {get_ans('q2')} yrs / {get_ans('q3')} cm / {get_ans('q4')} kg\n"
        f"• Diet Baseline: {get_ans('q7')} | Objective: {get_ans('q49')}\n\n"
        f"🥤 <b>METABOLIC LAYER:</b>\n"
        f"• Hydration Class: {get_ans('q_water')}\n"
        f"• Clinical Marks: {get_ans('q21')} | Symptoms: {get_ans('q_specific_health')}\n\n"
        f"😴 <b>CIRCADIAN & LIFESTYLE TIER:</b>\n"
        f"• Sleep Quality: Deepness [{get_ans('q33')}] | Fatigue: [{get_ans('q35')}]\n"
        f"• Stress Factor: {get_ans('q37')} | Stress Level: {get_ans('q32')}\n\n"
        f"🏋️ <b>TRAINING & STRUCTURAL BASE:</b>\n"
        f"• Steps: {get_ans('q_steps')} | Sessions: {get_ans('q40')}\n"
        f"• Orthopedic Safe-Zone: {get_ans('q25')} (Focus Area: {get_ans('q26')})\n\n"
        f"🔥 <i>Your onboarding strategy is locked into our engine. Let's make progress happen!</i>"
    )

def check_screen_satisfied(session, screen_data) -> bool:
    """Verifies if all mandatory fields are selected to safely proceed."""
    for field in screen_data['fields']:
        ans = session.answers.get(field['id'])
        if field['required'] and (ans is None or (isinstance(ans, list) and len(ans) == 0)):
            return False
    return True

# ============================================================================
# INTERFACE RENDERING ENGINE
# ============================================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    context.user_data[user_id] = UserSession()
    
    text = (
        "🤖 <b>╔════════════════════════════════════════╗</b>\n"
        "   <b>║       MEALZY SMART INTELLIGENCE        ║</b>\n"
        "   <b>║                                        ║</b>\n"
        "   <b>║     ⚡ Auto-Advance System Engine      ║</b>\n"
        "   <b>║     💡 Live Context Coaching Logs      ║</b>\n"
        "   <b>║     🛠️ Zero Collision Framework        ║</b>\n"
        "   <b>╚════════════════════════════════════════╝</b>\n\n"
        "🚀 <b>Intelligent onboarding sequence initialized.</b>"
    )
    keyboard = [[InlineKeyboardButton("🎯 BEGIN INTELLIGENT INTAKE", callback_data="start")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")

async def render_screen(update: Update, context: ContextTypes.DEFAULT_TYPE, query=None):
    user_id = update.effective_user.id
    session = context.user_data[user_id]
    
    if session.current_screen_idx >= len(SCREENS):
        dossier_text = generate_diagnostic_dossier(session)
        if query:
            await query.edit_message_text(dossier_text, parse_mode="HTML")
        else:
            await update.message.reply_text(dossier_text, parse_mode="HTML")
        return

    screen_data = SCREENS[session.current_screen_idx]
    progress = int((session.current_screen_idx / len(SCREENS)) * 100)
    bar = "█" * (progress // 10) + "░" * (10 - (progress // 10))
    
    # Injects live micro-coaching snippets dynamically at the top of the interface
    insight_header = generate_coach_insight(session)
    name_info = f" (User: {session.name})" if session.name else ""
    text_lines = [f"{bar} {progress}% | <b>{screen_data['section']}</b>{name_info}", "", insight_header]
    
    for field in screen_data['fields']:
        ans = session.answers.get(field['id'])
        is_answered = ans is not None and (not isinstance(ans, list) or len(ans) > 0)
        
        if session.awaiting_custom_field_id == field['id']:
            text_lines.append(f"✍️ <b>{field['text']}</b>\n⚡ <code>[Awaiting your custom typed response...]</code> ⌨️")
        elif is_answered:
            display_val = ', '.join(ans) if isinstance(ans, list) else str(ans)
            text_lines.append(f"❓ <b>{field['text']}</b>\n👉 Selected: <i>{display_val}</i> ✅")
        else:
            if field['type'] == 'text':
                text_lines.append(f"❓ <b>{field['text']}</b>\n🛸 [Type your answer directly in the text field below]")
            elif field['type'] == 'media':
                text_lines.append(f"❓ <b>{field['text']}</b>\n📸 [Upload photo or press bypass option below]")
            else:
                text_lines.append(f"❓ <b>{field['text']}</b>\n👉 [Tap grid options to record choices]")
        text_lines.append("")

    text = "\n".join(text_lines)
    keyboard = []
    has_multi = any(f['type'] == 'buttons_multi' for f in screen_data['fields'])
    
    for field in screen_data['fields']:
        if field['type'] in ['buttons', 'buttons_multi']:
            clean_q = field['text'].split('?')[0] + "?"
            keyboard.append([InlineKeyboardButton(f"── {clean_q} ──", callback_data="ignore")])
            
            row = []
            short_field_id = ID_MAP[field['id']]
            
            for idx, opt in enumerate(field['options']):
                display_opt = opt
                ans = session.answers.get(field['id'])
                
                if field['type'] == 'buttons' and ans == opt:
                    display_opt = f"⭐ {opt}"
                elif field['type'] == 'buttons_multi' and ans and isinstance(ans, list) and opt in ans:
                    display_opt = f"⭐ {opt}"
                    
                row.append(InlineKeyboardButton(display_opt, callback_data=f"s_{short_field_id}_{idx}"))
                if len(row) == 2:
                    keyboard.append(row)
                    row = []
            if row:
                keyboard.append(row)
            
            custom_label = "✍️ Custom / Other"
            ans = session.answers.get(field['id'])
            if ans and not isinstance(ans, list) and ans not in field['options']:
                custom_label = f"⭐ Custom: {ans}"
            keyboard.append([InlineKeyboardButton(custom_label, callback_data=f"c_{short_field_id}")])
        elif field['type'] == 'media':
            keyboard.append([InlineKeyboardButton("⏭️ Skip Assessment Photo", callback_data="skip_media")])
    
    # Smart Visibility Control: If it's single choice, auto-advance makes the Confirm button redundant
    if has_multi:
        if check_screen_satisfied(session, screen_data):
            keyboard.append([InlineKeyboardButton("⚡ CONFIRM & CONTINUE ➡️", callback_data="next_screen")])
        else:
            keyboard.append([InlineKeyboardButton("🔒 Awaiting Options", callback_data="locked")])
    elif any(f['type'] == 'text' for f in screen_data['fields']):
        keyboard.append([InlineKeyboardButton("🔒 Awaiting Text Input", callback_data="locked")])

    markup = InlineKeyboardMarkup(keyboard) if keyboard else None
    try:
        if query:
            await query.edit_message_text(text, reply_markup=markup, parse_mode="HTML")
        else:
            await update.message.reply_text(text, reply_markup=markup, parse_mode="HTML")
    except Exception:
        pass

# ============================================================================
# ACTION & POLLING HANDLERS
# ============================================================================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    session = context.user_data[user_id]
    data = query.data
    
    if data == "start":
        await query.answer()
        session.current_screen_idx = 0
        await render_screen(update, context, query)
        return
    if data in ["ignore", "locked"]:
        await query.answer("⚠️ Please fulfill the options on screen to proceed!", show_alert=(data=="locked"))
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
        field_id = REV_MAP[data.split("_")[1]]
        session.awaiting_custom_field_id = field_id
        await query.answer("⌨️ Type your custom response directly in the message box!", show_alert=True)
        await render_screen(update, context, query)
        return
        
    if data.startswith("s_"):
        parts = data.split("_")
        field_id = REV_MAP[parts[1]]
        opt_idx = int(parts[2])
        
        screen_data = SCREENS[session.current_screen_idx]
        field = next((f for f in screen_data['fields'] if f['id'] == field_id), None)
        if not field:
            await query.answer()
            return
            
        selected_opt = field['options'][opt_idx]
        session.awaiting_custom_field_id = None
        
        if field['type'] == 'buttons':
            session.answers[field_id] = selected_opt
            # SMART CONDITIONAL ENTRY: Skip discomfort localization if no injury exists
            if field_id == "q25" and selected_opt == "✅ No":
                session.answers["q26"] = "✅ Not Applicable"
        elif field['type'] == 'buttons_multi':
            current_ans = session.answers.get(field_id, [])
            if not isinstance(current_ans, list): current_ans = []
            if selected_opt in current_ans:
                current_ans.remove(selected_opt)
            else:
                current_ans.append(selected_opt)
            session.answers[field_id] = current_ans
            
        await query.answer()

        # SMART AUTO-ADVANCE ENGINE: Checks if all criteria are satisfied on single-choice screens
        has_multi = any(f['type'] == 'buttons_multi' for f in screen_data['fields'])
        if not has_multi and check_screen_satisfied(session, screen_data):
            session.current_screen_idx += 1
            
        await render_screen(update, context, query)

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = context.user_data[user_id]
    text = update.message.text.strip()
    
    if session.awaiting_custom_field_id:
        session.answers[session.awaiting_custom_field_id] = text
        session.awaiting_custom_field_id = None
        # Auto-advances if custom input satisfied a single-choice screen completely
        screen_data = SCREENS[session.current_screen_idx]
        if not any(f['type'] == 'buttons_multi' for f in screen_data['fields']) and check_screen_satisfied(session, screen_data):
            session.current_screen_idx += 1
        await render_screen(update, context)
        return

    if session.current_screen_idx >= len(SCREENS): return
    screen_data = SCREENS[session.current_screen_idx]
    text_fields = [f for f in screen_data['fields'] if f['type'] == 'text']
    
    if not text_fields:
        await update.message.reply_text("⚠️ Use the inline screen grid layout buttons, or choose 'Custom / Other' to write answers manually.")
        return
        
    field = text_fields[0]
    if field['id'] == 'q2':
        try:
            age = int(text)
            if not 10 <= age <= 100:
                await update.message.reply_text("❌ Please specify a realistic age metric (10 - 100):")
                return
        except ValueError:
            await update.message.reply_text("❌ Numerical values only:")
            return

    session.answers[field['id']] = text
    if field['id'] == 'q1': session.name = text

    session.current_screen_idx += 1
    await render_screen(update, context)

async def media_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = context.user_data[user_id]
    if session.current_screen_idx >= len(SCREENS): return
    
    screen_data = SCREENS[session.current_screen_idx]
    if not any(f['type'] == 'media' for f in screen_data['fields']):
        await update.message.reply_text("⚠️ This step requires button metrics selection.")
        return
        
    file_id = update.message.photo[-1].file_id if update.message.photo else update.message.document.file_id
    session.answers["q_photos"] = f"File Verified [ID: {file_id[:12]}...]"
    
    session.current_screen_idx += 1
    await render_screen(update, context)

def main():
    print("\n" + "=" * 80)
    print("🚀 COACH AVNI BOT - SMART INTELLIGENCE ENGINE DEPLOYED SUCCESSFULLY")
    print("=" * 80)
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL, media_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
