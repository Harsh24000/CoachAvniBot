#!/usr/bin/env python3
"""
COACH AVNI - PERSONALITY ENGINE (VOICE INPUT HARDENED EDITION)
100% of your 61 baseline questions, logic flows, and layout variables are preserved.

Fixes Deployed:
- Decoupled handle_text_or_transcription from update.message.text to avoid AttributeError on Voice notes.
- Hardened double-click callback exceptions against 'Message is not modified' Telegram interruptions.
- Maintained voiceless text replies (Coach Avni answers back purely with high-performance text).
"""

import os
import sys
import html
import logging
from io import BytesIO
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler, 
    filters, ContextTypes
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
CALENDLY_LINK = os.getenv("CALENDLY_LINK", "https://calendly.com/coach_avni/strategy-session")

if not TOKEN:
    print("CRITICAL CRASH PREVENTED: TELEGRAM_TOKEN missing inside environment variables.")
    sys.exit(1)

openai_client = None
if OPENAI_KEY:
    try:
        openai_client = OpenAI(api_key=OPENAI_KEY)
    except Exception as e:
        print(f"Warning: Could not initialize OpenAI Engine Client: {e}")

ID_MAP = {f"q{i}": f"v{i}" for i in range(1, 62)}
BRANCH_MAP = {"q23_diabetes": "vdia", "q23_thyroid": "vthy", "q23_pcos": "vpco"}
ID_MAP.update(BRANCH_MAP)
REV_MAP = {v: k for k, v in ID_MAP.items()}

SCREENS = [
    {"id": 1, "section": "👤 About You", "fields": [
        {"id": "q1", "text": "First things first, what's your full name?", "type": "text", "required": True},
        {"id": "q2", "text": "Awesome. How many years young are you?", "type": "text", "required": True},
        {"id": "q3", "text": "What's your height in cm? (No stretching the truth here!)", "type": "text", "required": True},
        {"id": "q4", "text": "And where is your current weight sitting at in kg?", "type": "text", "required": True}
    ]},
    {"id": 2, "section": "👤 About You", "fields": [
        {"id": "q5", "text": "What do you do for work? Let's see your daytime battlefield:", "type": "buttons", "required": True, "options": ["💻 Engineer", "👨‍⚕️ Doctor", "📚 Student", "👔 Business", "🤵 Consultant", "📊 Corporate"]},
        {"id": "q6", "text": "And what is your biological sex?", "type": "buttons", "required": True, "options": ["👨 Male", "👩 Female"]}
    ]},
    {"id": 3, "section": "🍏 Diet & Food", "fields": [
        {"id": "q7", "text": "Let's talk kitchen rules. What's your primary dietary style?", "type": "buttons", "required": True, "options": ["🍗 Non-Veg", "🥕 Veg", "🥚 Eggitarian", "🌱 Vegan", "☪️ Jain Vegetarian"]},
        {"id": "q8", "text": "Any foods you absolutely can't stand or refuse to eat? (Pick all that apply)", "type": "buttons_multi", "required": False, "options": ["🥒 Bitter Gourd", "🍆 Eggplant", "🍄 Mushroom", "🐟 Fish", "🥛 Dairy", "🧅 No Onion/Garlic"]}
    ]},
    {"id": 4, "section": "🍏 Diet & Food", "fields": [
        {"id": "q9", "text": "Which cuisine makes your soul happy?", "type": "buttons", "required": True, "options": ["🍛 North Indian", "🫓 South Indian", "🥗 Continental", "🥢 Asian Mix"]},
        {"id": "q10", "text": "Be honest: how dependent are you on tea or coffee?", "type": "buttons", "required": True, "options": ["☕ Yes, regularly", "🍵 Occasionally", "🚫 Total Abstinence"]}
    ]},
    {"id": 5, "section": "🌅 Your Day", "fields": [
        {"id": "q11", "text": "What time does your alarm usually go off?", "type": "buttons", "required": True, "options": ["⏰ 5:00 AM", "⏰ 6:00 AM", "⏰ 7:00 AM", "⏰ 8:00 AM+"]},
        {"id": "q12", "text": "When do you typically fuel up with breakfast?", "type": "buttons", "required": True, "options": ["🌅 8:00 AM", "🌅 9:00 AM", "🌅 10:00 AM", "⏭️ Skip Breakfast"]},
        {"id": "q13", "text": "When do you step into the work mindset?", "type": "buttons", "required": True, "options": ["💼 8:00 AM", "💼 9:00 AM", "💼 10:00 AM", "⌛ Shift Rotation"]}
    ]},
    {"id": 6, "section": "🌅 Your Day", "fields": [
        {"id": "q14", "text": "What time do you usually close your laptop or finish work?", "type": "buttons", "required": True, "options": ["⏰ 5:00 PM", "⏰ 6:00 PM", "⏰ 7:00 PM", "🌙 9:00 PM+"]},
        {"id": "q15", "text": "What's the standard window for your lunch?", "type": "buttons", "required": True, "options": ["🍱 12:30 PM", "🍱 1:30 PM", "🍱 2:30 PM", "⏳ Unfixed/Variable"]},
        {"id": "q16", "text": "When are you having your last solid meal of the day (Dinner)?", "type": "buttons", "required": True, "options": ["🍽️ 7:00 PM", "🍽️ 8:00 PM", "🍽️ 9:00 PM", "🌙 10:00 PM+"]}
    ]},
    {"id": 7, "section": "🌅 Your Day", "fields": [
        {"id": "q17", "text": "What time are your lights completely out?", "type": "buttons", "required": True, "options": ["🌙 10:00 PM", "🌙 11:00 PM", "🌙 12:00 AM", "🦉 1:00 AM+"]},
        {"id": "q18", "text": "How often are you visiting the snack cabinet between meals?", "type": "buttons", "required": True, "options": ["🍪 Constant", "🍏 Occasional", "🚫 No Snacking"]},
        {"id": "q19", "text": "How much water are you actually drinking every day?", "type": "buttons", "required": True, "options": ["🥛 < 1 Litre", "💧 1-2 Litres", "🚰 2-3 Litres", "🌊 3+ Litres"]}
    ]},
    {"id": 8, "section": "🌅 Your Day", "fields": [
        {"id": "q20", "text": "How often is takeout or restaurant food landing on your plate?", "type": "buttons", "required": True, "options": ["🍔 Daily", "🍕 2-3x / Week", "🥗 Rarely", "✅ Never"]},
        {"id": "q21", "text": "Let's talk social hours—what's your weekly relationship with alcohol?", "type": "buttons", "required": True, "options": ["🍺 High Volume", "🍷 Social/Weekend", "🚫 Completely Clean"]},
        {"id": "q22", "text": "Do you smoke or consume tobacco items?", "type": "buttons", "required": True, "options": ["🚬 Yes, daily", "💨 Socially", "🚫 No"]}
    ]},
    {"id": 9, "section": "🏥 Health", "fields": [
        {"id": "q23", "text": "Have you been diagnosed with any of these metabolic conditions?", "type": "buttons_multi", "required": False, "options": ["🔬 Diabetes", "🧬 Thyroid", "🔴 PCOS/PCOD", "❤️ Hypertension", "🍗 Fatty Liver", "✅ None"]},
        {"id": "q24", "text": "Any old or current injuries I need to protect while building your workouts?", "type": "text", "required": False},
        {"id": "q25", "text": "Do you fight any nasty allergies?", "type": "buttons", "required": True, "options": ["✅ None", "🍔 Food Specific", "💊 Pharmaceutical", "🌫️ Environmental"]}
    ]},
    {"id": 10, "section": "🏥 Health", "fields": [
        {"id": "q26", "text": "Any specific prescription meds you're currently taking?", "type": "text", "required": False},
        {"id": "q27", "text": "Time for gut check—how is your digestion behaving?", "type": "buttons", "required": True, "options": ["🟢 Smooth/Regular", "⚠️ Chronic Bloating", "🛑 Regular Constipation", "🔥 Acid Reflux"]}
    ]},
    {"id": 11, "section": "🏥 Health", "fields": [
        {"id": "q28", "text": "How intense are your sugar cravings?", "type": "buttons", "required": True, "options": ["🍩 Intense daily", "🍫 Post-meals only", "🚫 Seldom/Never"]},
        {"id": "q29", "text": "Do you hit a wall and get hit by random energy slumps?", "type": "buttons", "required": True, "options": ["🥱 Severe 3 PM crash", "🥱 Constant fatigue", "⚡ Steady performance"]}
    ]},
    {"id": 12, "section": "🏥 Health", "fields": [
        {"id": "q30", "text": "Notice anything happening with your skin or hair lately?", "type": "buttons", "required": True, "options": ["⚠️ High hair fall", "⚠️ Acne breaks", "✅ Stable/Optimal"]},
        {"id": "q31", "text": "How often do you catch yourself getting sick or feeling run down?", "type": "buttons", "required": True, "options": ["🤧 Catch colds easily", "💊 Depend on meds", "🛡️ High/Rarely sick"]}
    ]},
    {"id": 13, "section": "💊 Supplements & Habits", "fields": [
        {"id": "q32", "text": "Are you supplementing your Vitamin D3?", "type": "buttons", "required": True, "options": ["💊 Daily/Weekly", "🧪 Deficient (No Pill)", "❌ Not Tracking"]},
        {"id": "q33", "text": "What about your Vitamin B12 levels?", "type": "buttons", "required": True, "options": ["💊 Regular Intake", "🧪 Deficient", "❌ Not Tracking"]},
        {"id": "q34", "text": "Are you taking Omega-3 or Fish Oil supplements?", "type": "buttons", "required": True, "options": ["✅ Yes, daily", "❌ No Intake"]},
        {"id": "q35", "text": "Do you take a regular multivitamin?", "type": "buttons", "required": True, "options": ["✅ Consuming", "❌ No Intake"]}
    ]},
    {"id": 14, "section": "💊 Supplements & Habits", "fields": [
        {"id": "q36", "text": "Do you apply heavy hair dye or artificial treatments frequently?", "type": "buttons", "required": True, "options": ["💇 Yes, frequently", "🚫 Minimal/Never"]},
        {"id": "q37", "text": "Do you catch yourself suffering from brain fog or scattered focus?", "type": "buttons", "required": True, "options": ["🧠 Yes, regularly", "😐 Mid-day fatigue", "✅ Clear/Sharp"]},
        {"id": "q38", "text": "How often do uninvited mood swings or anxiety creep up?", "type": "buttons", "required": True, "options": ["⚡ Frequent shifts", "🌊 Under high stress", "😊 Balanced/Grounded"]}
    ]},
    {"id": 15, "section": "💊 Supplements & Habits", "fields": [
        {"id": "q39", "text": "How do you feel when you wake up in the morning?", "type": "buttons", "required": True, "options": ["🐌 Wake up tired", "⚡ Fast joint recovery", "🩹 Slow healing/Sore"]},
        {"id": "q40", "text": "Rate your overall mental stress load on a daily basis:", "type": "buttons", "required": True, "options": ["😊 1-2 (Low)", "😐 3 (Manageable)", "😫 4-5 (High)"]},
        {"id": "q41", "text": "When you sleep, are you actually out cold or tossing and turning?", "type": "buttons", "required": True, "options": ["🥱 Fragmented/Wakeful", "😐 Average Depth", "😴 Deep Nightly State"]}
    ]},
    {"id": 16, "section": "🏃 Physical Biomechanics", "fields": [
        {"id": "q42", "text": "Has anyone ever told you that you snore pretty heavily?", "type": "buttons", "required": True, "options": ["🔊 Yes, heavy snoring", "🔉 Light/Occasional", "🚫 No Snoring"]},
        {"id": "q43", "text": "What is your baseline state right after your feet hit the floor?", "type": "buttons", "required": True, "options": ["✅ Wake up fresh", "Usually groggy 🥱", "Tired/Exhausted 💤"]},
        {"id": "q44", "text": "Are dark circles making a permanent home under your eyes?", "type": "buttons", "required": True, "options": ["👁️ Prominent/Dark", "👁️ Faint", "✅ None"]}
    ]},
    {"id": 17, "section": "🏃 Physical Biomechanics", "fields": [
        {"id": "q45", "text": "Any history of weird, rapid, unexplained shifts in your weight?", "type": "buttons", "required": True, "options": ["📈 Gained fast lately", "📉 Dropped fast lately", "✅ Steady weight"]},
        {"id": "q46", "text": "Do your hands, feet, or face feel swollen and puffy often?", "type": "buttons", "required": True, "options": ["💧 Heavy ankles/hands", "💧 Face puffiness", "🚫 No"]},
        {"id": "q47", "text": "Do you get freezing cold hands or cold feet, even when it's warm?", "type": "buttons", "required": True, "options": ["🥶 Yes, constantly", "🥶 Only in winter", "🚫 No"]}
    ]},
    {"id": 18, "section": "🏃 Physical Biomechanics", "fields": [
        {"id": "q48", "text": "Are you dealing with any nagging joint or body pain?", "type": "buttons", "required": True, "options": ["💥 Lower back issue", "💥 Knee pain structural", "💥 Neck/Shoulders", "✅ Fully pain-free"]},
        {"id": "q49", "text": "How quickly do you start gasping for air when moving around?", "type": "buttons", "required": True, "options": ["🫁 Walking up stairs", "🫁 Only during sprints", "⚡ Strong cardiorespiratory"]},
        {"id": "q50", "text": "How many hours is your back glued to a desk chair every day?", "type": "buttons", "required": True, "options": ["🚶 Below 4 Hours", "😐 4 - 7 Hours", "💀 8+ Hours"]}
    ]},
    {"id": 19, "section": "🏃 Physical Biomechanics", "fields": [
        {"id": "q51", "text": "Any health issues running rampant in your immediate family tree?", "type": "buttons_multi", "required": False, "options": ["🩸 Diabetes trend", "❤️ Cardiovascular issues", "🧬 Obesity traits", "✅ Clear History"]},
        {"id": "q52", "text": "How would you describe your natural skin condition?", "type": "buttons", "required": True, "options": ["🍂 Very dry/flaky", "💧 Excess oily zone", "✨ Well-hydrated/Normal"]},
        {"id": "q53", "text": "How stable is your daily appetite?", "type": "buttons", "required": True, "options": ["🔥 Uncontrollable/Bingeing", "🧊 Low appetite/Forget to eat", "✅ Stable patterns"]}
    ]},
    {"id": 20, "section": "🎯 Targets & Objectives", "fields": [
        {"id": "q54", "text": "Have you ever tried tracking calories or macros before?", "type": "buttons", "required": True, "options": ["📈 Yes, did macros", "📉 Tried and failed", "🚫 Never tracked"]},
        {"id": "q55", "text": "If we could wave a magic wand, what's our absolute primary focus?", "type": "buttons", "required": True, "options": ["📉 Aggressive Fat Loss", "💪 Hypertrophy Lean Muscle", "⚡ Athletic Endurance", "❤️ Metabolic Correction"]},
        {"id": "q56", "text": "What has been your main roadblock to consistency in the past?", "type": "buttons", "required": True, "options": ["⏳ Extreme time deficit", "🍳 Cooking complexity", "🍿 Social/Travel habits", "🧠 Lack of internal drive"]}
    ]},
    {"id": 21, "section": "🎯 Targets & Objectives", "fields": [
        {"id": "q57", "text": "Rate your overall daily energy flow—are you a firecracker or a slow burn?", "type": "buttons", "required": True, "options": ["📈 Peak morning/low night", "📉 Flatline low energy", "⚡ High baseline all day"]},
        {"id": "q58", "text": "Realistically, how much time can you clip out for your workouts weekly?", "type": "buttons", "required": True, "options": ["⏳ Under 2 Hours", "⏳ 2 to 4 Hours", "⚡ 5+ Hours fully ready!"]}
    ]},
    {"id": 22, "section": "🎯 Targets & Objectives", "fields": [
        {"id": "q59", "text": "How often are soda, energy drinks, or sweet commercial beverages making an appearance?", "type": "buttons", "required": True, "options": ["🥤 Yes, almost daily", "🥤 Socially/Weekends", "🚫 Complete clean limit"]},
        {"id": "q60", "text": "What's our targeted countdown timeline to make this transformation real?", "type": "buttons", "required": True, "options": ["🔥 4 to 8 Weeks", "⚡ 12 Weeks (Recommended)", "⏳ Long-term shift"]}
    ]},
    {"id": 23, "section": "📸 Biometric Profiles", "fields": [
        {"id": "q61", "text": "Drop a clear front, side, or back body photo here so I can evaluate your real posture and muscle structure.", "type": "media", "required": False}
    ]}
]

DYNAMIC_BRANCHES = {
    "🔬 Diabetes": {"id": "q23_diabetes", "text": "What was your most recent Fasting Blood Sugar or HbA1c score? (e.g., 6.4, 140 mg/dL)", "type": "text", "section": "🏥 Health Deep-Dive"},
    "🧬 Thyroid": {"id": "q23_thyroid", "text": "Are you taking thyroid medication? If yes, what is your current dosage (e.g., 50mcg Thyronorm)?", "type": "text", "section": "🏥 Health Deep-Dive"},
    "🔴 PCOS/PCOD": {"id": "q23_pcos", "text": "How predictable are your menstrual cycles right now?", "type": "buttons", "options": ["🗓️ Normal (28-35 days)", "⏳ Highly Irregular", "🛑 Missed for months"], "section": "🏥 Health Deep-Dive"}
}

class UserSession:
    def __init__(self):
        self.current_screen_idx = 0
        self.answers = {}
        self.name = None  
        self.awaiting_custom_field_id = None
        self.is_submitted = False
        self.last_activity = datetime.now()
        self.injected_branch_queue = []
        self.current_branch_field = None
        
    def calculate_readiness_score(self):
        score = 85
        water = str(self.answers.get("q19", ""))
        stress = str(self.answers.get("q40", ""))
        sleep = str(self.answers.get("q41", ""))
        if "< 1" in water: score -= 15
        if "4-5" in stress: score -= 15
        if "Fragmented" in sleep: score -= 10
        return max(10, min(100, score))

    def calculate_macro_targets(self):
        try:
            w = float(str(self.answers.get("q4", "75")).replace("kg", "").strip())
            h = float(str(self.answers.get("q3", "175")).replace("cm", "").strip())
            a = float(str(self.answers.get("q2", "30")).replace("years", "").strip())
        except ValueError:
            w, h, a = 75.0, 175.0, 30.0

        is_female = "Female" in str(self.answers.get("q6", ""))
        bmr = (10 * w) + (6.25 * h) - (5 * a) + (-161 if is_female else 5)
        tdee = bmr * 1.375

        goal = str(self.answers.get("q55", ""))
        if "Fat Loss" in goal:
            calories = tdee - 450
            protein = w * 2.2
            fat = (calories * 0.25) / 9
        elif "Hypertrophy" in goal:
            calories = tdee + 300
            protein = w * 2.0
            fat = (calories * 0.25) / 9
        else:
            calories = tdee
            protein = w * 1.8
            fat = (calories * 0.25) / 9

        carbs = (calories - (protein * 4) - (fat * 9)) / 4
        return {
            "calories": int(calories),
            "protein": int(protein),
            "carbs": int(max(20, carbs)),
            "fat": int(fat)
        }

def get_personalized_text(field: dict, session: UserSession) -> str:
    orig_text = field['text']
    
    if field['id'] == "q14" and session.answers.get("q5"):
        job = str(session.answers.get("q5")).split()[-1]
        orig_text = f"As a busy {job}, what time do you usually close your laptop or wrap up work?"
    elif field['id'] == "q50" and "Engineer" in str(session.answers.get("q5")):
        orig_text = "Be honest: how many hours is your back glued to that coding desk chair every day?"

    if not session.name:
        return orig_text

    name_clean = html.escape(str(session.name).split()[0].strip())
    
    replacements = {
        "q2": f"Awesome {name_clean}. How many years young are you?",
        "q3": f"What's your height in cm, {name_clean}? (No stretching the truth here!)",
        "q5": f"{name_clean}, what do you do for work? Let's see your daytime battlefield:",
        "q7": f"Let's talk kitchen rules {name_clean}. What's your primary dietary style?",
        "q9": f"Which cuisine makes your soul happy, {name_clean}?",
        "q11": f"What time does your alarm usually go off, {name_clean}?",
        "q18": f"How often are you visiting the snack cabinet between meals, {name_clean}?",
        "q23": f"Have you been diagnosed with any of these metabolic conditions, {name_clean}?",
        "q27": f"Time for a gut check {name_clean}—how is your digestion behaving?",
        "q40": f"Rate your overall mental stress load on a daily basis, {name_clean}:",
        "q55": f"If we could wave a magic wand {name_clean}, what's our absolute primary focus?",
        "q60": f"What's our targeted countdown timeline to make this transformation real, {name_clean}?"
    }
    
    if field['id'] in replacements:
        return replacements[field['id']]
        
    if field['id'] not in ["q1", "q2", "q3"]:
        return f"{name_clean}, {orig_text[0].lower() + orig_text[1:]}"
        
    return orig_text

def generate_progress_bar(pct: int) -> str:
    total_blocks = 10
    filled_blocks = int(pct / 10)
    empty_blocks = total_blocks - filled_blocks
    bar_str = "█" * filled_blocks + "░" * empty_blocks
    return f"<code>[{bar_str}] {pct}%</code>"

def get_funny_instant_reaction(field_id: str, value: str) -> str:
    v = str(value)
    val_clean = html.escape(v)
    reactions = {
        "q1": f"Nice to meet you, {val_clean}! Let's customize your fitness mapping engine immediately. 🚀",
        "q2": "Age is just a software parameter. We are about to optimize your cellular biology split anyway! 🧬",
        "q5": {
            "💻 Engineer": "An Engineer! Excellent. Prepare to treat your macronutrients like clean lines of production code. Just don't spend three weeks refactoring your breakfast setup. 😉",
            "👨‍⚕️ Doctor": "A Doctor! Absolute respect for those continuous shifts. Let's make sure you aren't ignoring your own metabolic warning lights while managing everyone else's.",
            "📊 Corporate": "Ah, corporate life! High status, higher sitting hours. Let's make sure your performance targets apply to your health markers too.",
            "📚 Student": "Student life! Powered entirely by cheap noodles, bad posture, and cramming sessions. Time to upgrade the baseline fuel profile."
        },
        "q6": {
            "👨 Male": "Understood. Tailoring hormone calibration and heavy load training patterns for male endocrine baselines. 💪",
            "👩 Female": "Understood. Adjusting micronutrient structures matching female bio-rhythm and system demands. ✨"
        },
        "q7": {
            "🍗 Non-Veg": "Non-veg targets locked down. Hitting our daily protein profile just got 10x easier.",
            "🥕 Veg": "Vegetarian it is! Don't worry, my protocols don't involve dumping endless bowls of raw spinach and tofu on your desk.",
            "🌱 Vegan": "Vegan! Plant-powered engine. We will need to be surgically tactical with your essential amino-acid pairing, but we'll smash it."
        },
        "q10": {
            "☕ Yes, regularly": "Regular caffeine dependency? Let's check if that coffee is actually a tactical pre-workout or just a structural crutch holding up your sleep deficit. ☕",
            "🚫 Total Abstinence": "Zero caffeine? Wow, clean energy matrix running on pure biological ATP. Mad respect! 🙌"
        },
        "q11": {
            "⏰ 5:00 AM": "5 AM club! Early bird advantage. Your biological circadian clock is already primed for high-performance structure.",
            "⏰ 8:00 AM+": "Waking past 8 AM? Night-owl patterns or corporate burnout recovery? We will calibrate the routine to match your schedule."
        },
        "q17": {
            "🦉 1:00 AM+": "Going down past 1 AM?! Ouch. Those late-night blue screens are completely rewriting your cortisol signals. Let's work on fixing that sleep window. 🦉"
        },
        "q18": {
            "🍪 Constant": "Constant snacking? Remember: every random cookie run triggers an instant digestive spike, meaning your body never actually gets a chance to look at its fat storage units! 🛑"
        },
        "q19": {
            "🥛 < 1 Litre": "Wait... less than 1L of water?! Your cellular matrix is practically wading through thick sludge right now. Drop the phone and drink a glass immediately! 🚰",
            "🌊 3+ Litres": "Over 3 Litres? Hydro-champion status unlocked! Your kidney clearance and metabolic pathways thank you. 🌊"
        },
        "q20": {
            "🍔 Daily": "Daily takeout?! Your poor liver is practically fighting a daily tactical war against hidden restaurant fats and processed oils. Time for a hard reset! 🚨",
            "🍕 2-3x / Week": "2-3 restaurant meals a week is exactly where hidden sodium blocks sneak up on you. We will optimize this balance."
        },
        "q21": {
            "🍺 High Volume": "High-volume alcohol? That's an instant system pause on fat oxidation. Your liver will drop everything to clear that out first. We need to negotiate this down! 📉"
        },
        "q28": {
            "🍩 Intense daily": "Intense sugar cravings aren't a character defect or lack of willpower; it's your gut microbiome yelling for fast energy because your glucose baseline is bouncing around."
        },
        "q29": {
            "🥱 Severe 3 PM crash": "Ah, the legendary 3 PM mid-day wall. That's your high-carb lunch crashing down hard. We will replace that energy rollercoaster with steady performance fuel. 📉"
        },
        "q40": {
            "😫 4-5 (High)": "High stress limits. Chronic cortisol is a major roadblock to lean body targets. We are placing heavy emphasis on recovery protocols for you. 🧘‍♂️"
        },
        "q50": {
            "💀 8+ Hours": "8+ hours locked into a desk chair is absolute kryptonite for glute activation and posture alignment. We will introduce micro-movement protocols to counter this. 🛋️"
        },
        "q53": {
            "🔥 Uncontrollable/Bingeing": "Appetite all over the place? That's usually just your leptin and ghrelin signaling getting confused by irregular meal patterns. Easy fix."
        },
        "q55": {
            "📉 Aggressive Fat Loss": "Aggressive fat loss! Bold approach. It requires high operational focus, but we are building a metabolic engine to handle it cleanly.",
            "💪 Hypertrophy Lean Muscle": "Lean muscle hypertrophy! Excellent. Time to set up consistent progressive overload structures and track your protein synthesis."
        }
    }
    if field_id in reactions:
        if isinstance(reactions[field_id], dict):
            for key, msg in reactions[field_id].items():
                if key in v: return f"💬 <b>Coach Avni:</b> {msg}"
        else:
            return f"💬 <b>Coach Avni:</b> {reactions[field_id]}"
    return None

def check_screen_satisfied(session, screen_data) -> bool:
    for field in screen_data['fields']:
        ans = session.answers.get(field['id'])
        if field['required'] and (ans is None or (isinstance(ans, list) and len(ans) == 0)):
            return False
    return True

async def deliver_final_success_ui(update: Update, context: ContextTypes.DEFAULT_TYPE, target_chat_id):
    user_id = update.effective_user.id
    session = context.user_data[user_id]
    session.is_submitted = True
    
    score = session.calculate_readiness_score()
    macros = session.calculate_macro_targets()
    name_display = session.name if session.name else "Champion"
    
    success_text = (
        f"🧠 <b>BIO-METRIC ONBOARDING REGISTERED SUCCESSFULLY</b>\n\n"
        f"👤 <b>Athlete Registered:</b> {html.escape(name_display)}\n"
        f"📊 <b>Metabolic Score Metric:</b> {score}/100\n"
        f"✅ <b>Status:</b> Completely Configured.\n\n"
        f"⚡ <b>FEATURE 2: INITIAL TARGET MACRO CALIBRATION</b>\n"
        f"• <b>Daily Target Energy budget:</b> <code>{macros['calories']} kcal</code>\n"
        f"• <b>Protein Allocation:</b> <code>{macros['protein']}g</code>\n"
        f"• <b>Carbs Allocation:</b> <code>{macros['carbs']}g</code>\n"
        f"• <b>Fats Allocation:</b> <code>{macros['fat']}g</code>\n\n"
        f"Your tailored onboarding protocol file brief has been generated.\n"
        f"<b>Next Step:</b> Book your strategy kickoff call directly via Calendly below."
    )
    
    keyboard = [
        [InlineKeyboardButton("📅 BOOK KICKOFF CALL VIA CALENDLY", url=CALENDLY_LINK)],
        [InlineKeyboardButton("🔄 REVIEW/OPEN DATA ENTRIES", callback_data="review_board_fallback")]
    ]
    await context.bot.send_message(chat_id=target_chat_id, text=success_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")
    
    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        story = []
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=18, leading=22, textColor=colors.HexColor("#1A365D"), spaceAfter=12)
        body_style = ParagraphStyle('BodyTextCustom', parent=styles['Normal'], fontSize=10, leading=14, textColor=colors.HexColor("#2D3748"))
        
        story.append(Paragraph(f"COACH AVNI — STRATEGIC BIOMETRIC BRIEF", title_style))
        story.append(Paragraph(f"<b>Client Target:</b> {html.escape(name_display)}", body_style))
        story.append(Paragraph(f"<b>Metabolic Blueprint Score:</b> {score}/100", body_style))
        story.append(Paragraph(f"<b>AI Computed Calories:</b> {macros['calories']} kcal (P: {macros['protein']}g, C: {macros['carbs']}g, F: {macros['fat']}g)", body_style))
        story.append(Spacer(1, 15))
        
        table_data = [["Assessment Metric Pillar", "Customer Onboarding Response Log"]]
        for screen in SCREENS:
            for field in screen['fields']:
                ans = session.answers.get(field['id'])
                if ans:
                    val_str = ", ".join(ans) if isinstance(ans, list) else str(ans)
                    table_data.append([Paragraph(html.escape(field['text']), body_style), Paragraph(html.escape(val_str), body_style)])
                    
        t = Table(table_data, colWidths=[270, 230])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (1,0), colors.HexColor("#1A365D")),
            ('TEXTCOLOR', (0,0), (1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#F7FAFC"), colors.white]),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ]))
        story.append(t)
        doc.build(story)
        buffer.seek(0)
        await context.bot.send_document(
            chat_id=target_chat_id,
            document=buffer,
            filename=f"Coach_Avni_{name_display.replace(' ', '_')}_Profile.pdf",
            caption="📄 Your Complete Strategic Profile Report",
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"PDF generation failed: {e}")

async def render_screen(update: Update, context: ContextTypes.DEFAULT_TYPE, target_message_id=None, target_chat_id=None):
    try:
        user_id = update.effective_user.id
        if not target_chat_id: target_chat_id = update.effective_chat.id
        session = context.user_data[user_id]
        session.last_activity = datetime.now()
        
        if session.current_branch_field:
            field = session.current_branch_field
            text = f"📝 <b>Phase: {html.escape(field['section'])}</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            ans = session.answers.get(field['id'])
            p_text = get_personalized_text(field, session)
            
            if session.awaiting_custom_field_id == field['id']:
                text += f"❓ <b>{html.escape(p_text)}</b>\n✍️ <i>[Type custom text or hold 🎙️ Mic to record voice answer...]</i>\n\n"
            elif ans:
                text += f"✅ <b>{html.escape(p_text)}</b>\n👉 <code>{html.escape(str(ans))}</code>\n\n"
            else:
                text += f"👉 <b>{html.escape(p_text)}</b>\n\n"
                
            keyboard = []
            if field['type'] == 'buttons':
                short_id = ID_MAP[field['id']]
                for idx, opt in enumerate(field['options']):
                    lbl = opt if ans != opt else f"🔥 {opt} ✓"
                    keyboard.append([InlineKeyboardButton(lbl, callback_data=f"s_{short_id}_{idx}")])
            
            nav_row = [InlineKeyboardButton("CONTINUE ➡️", callback_data="next_branch")]
            keyboard.append(nav_row)
            
            if target_message_id:
                try:
                    await context.bot.edit_message_text(text, chat_id=target_chat_id, message_id=target_message_id, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")
                    return
                except Exception as e:
                    if "Message is not modified" in str(e): return
                    logger.error(f"Error editing branch message: {e}")
            await context.bot.send_message(target_chat_id, text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")
            return

        if session.current_screen_idx >= len(SCREENS):
            await deliver_final_success_ui(update, context, target_chat_id)
            return

        screen_data = SCREENS[session.current_screen_idx]
        progress = int((session.current_screen_idx / len(SCREENS)) * 100)
        progress_bar = generate_progress_bar(progress)
        
        text = f"📝 <b>Phase: {html.escape(screen_data['section'])}</b>\nProgress: {progress_bar}\n━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        for field in screen_data['fields']:
            ans = session.answers.get(field['id'])
            p_text = get_personalized_text(field, session)
                
            if session.awaiting_custom_field_id == field['id']:
                text += f"❓ <b>{html.escape(p_text)}</b>\n✍️ <i>[Type text or hold 🎙️ Mic to record voice answer...]</i>\n\n"
            elif ans:
                display = ", ".join(ans) if isinstance(ans, list) else str(ans)
                text += f"✅ <b>{html.escape(p_text)}</b>\n👉 <code>{html.escape(display)}</code>\n\n"
            else:
                text += f"👉 <b>{html.escape(p_text)}</b>\n\n"

        keyboard = []
        has_multi = any(f['type'] == 'buttons_multi' for f in screen_data['fields'])
        is_multi_question = len(screen_data['fields']) > 1
        
        for field in screen_data['fields']:
            if field['type'] in ['buttons', 'buttons_multi']:
                p_text = get_personalized_text(field, session)
                clean_hdr = html.escape(p_text.split('?')[0].split(':')[0].strip())
                keyboard.append([InlineKeyboardButton(f"⬇️ {clean_hdr} ⬇️", callback_data="ignore")])
                row, short_id = [], ID_MAP[field['id']]
                for idx, opt in enumerate(field['options']):
                    lbl = opt
                    ans = session.answers.get(field['id'])
                    if field['type'] == 'buttons' and ans == opt: lbl = f"🔥 {opt} ✓"
                    elif field['type'] == 'buttons_multi' and ans and opt in ans: lbl = f"🔥 {opt} ✓"
                    row.append(InlineKeyboardButton(lbl, callback_data=f"s_{short_id}_{idx}"))
                    if len(row) == 2:
                        keyboard.append(row)
                        row = []
                if row: keyboard.append(row)
                keyboard.append([InlineKeyboardButton("🎙️ Speak / Type Custom Answer", callback_data=f"c_{short_id}")])
            elif field['type'] == 'media':
                keyboard.append([InlineKeyboardButton("⏭️ Skip Upload (Can do this later)", callback_data="skip_media")])

        nav_row = []
        if session.current_screen_idx > 0:
            nav_row.append(InlineKeyboardButton("⬅️ BACK", callback_data="back_screen"))
        if has_multi or is_multi_question:
            if check_screen_satisfied(session, screen_data): 
                nav_row.append(InlineKeyboardButton("CONTINUE ➡️", callback_data="next_screen"))
            else: 
                nav_row.append(InlineKeyboardButton("🔒 Finish answers to un-lock", callback_data="locked"))
        if nav_row: keyboard.append(nav_row)

        if target_message_id:
            try:
                await context.bot.edit_message_text(text, chat_id=target_chat_id, message_id=target_message_id, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")
                return
            except Exception as e:
                if "Message is not modified" in str(e): return
                logger.error(f"Error editing screen message: {e}")

        await context.bot.send_message(chat_id=target_chat_id, text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")
    except Exception as fatal_render_err:
        logger.error(f"Render engine bypass protected a crash event: {fatal_render_err}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    context.user_data[user_id] = UserSession()
    text = (
        "🔥 <b>Welcome to Coach Avni's Strategic Onboarding Funnel.</b>\n\n"
        "We are mapping your specific lifestyle baseline metrics.\n\n"
        "Let's see what's going on under your hood 👇"
    )
    keyboard = [[InlineKeyboardButton("⚡ INITIALIZE ASSESSMENT PROTOCOL", callback_data="start")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    session = context.user_data.get(user_id)
    if not session: return await query.answer("Session timed out! Tap /start fresh.", show_alert=True)
    
    data = query.data
    if data in ["ignore", "locked"]: return await query.answer()
    
    if data in ["start", "resume_onboarding"]:
        await query.answer()
        try: await query.message.delete()
        except Exception: pass
        await render_screen(update, context, target_chat_id=query.message.chat_id)
        return

    if data == "next_branch":
        await query.answer()
        try: await query.message.delete()
        except Exception: pass
        if session.injected_branch_queue:
            session.current_branch_field = session.injected_branch_queue.pop(0)
        else:
            session.current_branch_field = None
            session.current_screen_idx += 1
        await render_screen(update, context, target_chat_id=query.message.chat_id)
        return

    if data == "back_screen":
        await query.answer()
        try: await query.message.delete()
        except Exception: pass
        if session.current_screen_idx > 0: session.current_screen_idx -= 1
        await render_screen(update, context, target_chat_id=query.message.chat_id)
        return
        
    if data == "next_screen":
        await query.answer()
        screen_data = SCREENS[session.current_screen_idx]
        try: await query.message.delete()
        except Exception: pass
        
        for field in screen_data['fields']:
            ans = session.answers.get(field['id'])
            if field['id'] == "q23" and isinstance(ans, list):
                for metabolic_cond in ans:
                    if metabolic_cond in DYNAMIC_BRANCHES:
                        session.injected_branch_queue.append(DYNAMIC_BRANCHES[metabolic_cond])

        if session.injected_branch_queue:
            session.current_branch_field = session.injected_branch_queue.pop(0)
        else:
            session.current_screen_idx += 1
            
        await render_screen(update, context, target_chat_id=query.message.chat_id)
        return

    if data == "review_board_fallback":
        await query.answer("📋 Fetching configured database records...", show_alert=True)
        review_text = f"📋 <b>Onboarding Database Entries Profile:</b>\n\n"
        for screen in SCREENS:
            review_text += f"🔸 <b>{screen['section'].upper()}</b>\n"
            for field in screen['fields']:
                ans = session.answers.get(field['id'], "—")
                val_str = ", ".join(ans) if isinstance(ans, list) else str(ans)
                review_text += f" • {html.escape(field['text'])}: <code>{html.escape(val_str)}</code>\n"
            review_text += "\n"
        await context.bot.send_message(chat_id=query.message.chat_id, text=review_text, parse_mode="HTML")
        return

    if data == "skip_media":
        await query.answer()
        try: await query.message.delete()
        except Exception: pass
        session.answers["q61"] = "Skipped"
        session.current_screen_idx += 1
        await render_screen(update, context, target_chat_id=query.message.chat_id)
        return

    if data.startswith("c_"):
        await query.answer()
        field_id = REV_MAP[data.split("_")[1]]
        session.awaiting_custom_field_id = field_id
        await render_screen(update, context, target_message_id=query.message.message_id, target_chat_id=query.message.chat_id)
        return
        
    if data.startswith("s_"):
        await query.answer()
        parts = data.split("_")
        field_id = REV_MAP[parts[1]]
        opt_idx = int(parts[2])
        
        if session.current_branch_field and session.current_branch_field['id'] == field_id:
            selected = session.current_branch_field['options'][opt_idx]
            session.answers[field_id] = selected
            await render_screen(update, context, target_message_id=query.message.message_id, target_chat_id=query.message.chat_id)
            return

        screen_data = SCREENS[session.current_screen_idx]
        field = next((f for f in screen_data['fields'] if f['id'] == field_id), None)
        if not field: return
        
        selected = field['options'][opt_idx]
        session.awaiting_custom_field_id = None
        
        if field['type'] == 'buttons':
            session.answers[field_id] = selected
        elif field['type'] == 'buttons_multi':
            curr = session.answers.get(field_id, [])
            if not isinstance(curr, list): curr = []
            if selected in curr: curr.remove(selected)
            else: curr.append(selected)
            session.answers[field_id] = curr
            
        has_multi = any(f['type'] == 'buttons_multi' for f in screen_data['fields'])
        is_multi_question = len(screen_data['fields']) > 1
        
        if not has_multi and not is_multi_question:
            try: await query.message.delete()
            except Exception: pass
            
            msg = get_funny_instant_reaction(field_id, selected)
            if msg:
                await context.bot.send_message(chat_id=query.message.chat_id, text=msg, parse_mode="HTML")
                
            session.current_screen_idx += 1
            await render_screen(update, context, target_chat_id=query.message.chat_id)
        else:
            try:
                await render_screen(update, context, target_message_id=query.message.message_id, target_chat_id=query.message.chat_id)
            except Exception as double_click_err:
                if "Message is not modified" in str(double_click_err):
                    pass

async def handle_text_or_transcription(text: str, update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    user_id = update.effective_user.id
    session = context.user_data.get(user_id)
    
    if session.awaiting_custom_field_id:
        f_id = session.awaiting_custom_field_id
        session.answers[f_id] = text
        if f_id == 'q1': session.name = text
        session.awaiting_custom_field_id = None
        
        msg = get_funny_instant_reaction(f_id, text)
        if msg:
            await context.bot.send_message(chat_id=chat_id, text=msg, parse_mode="HTML")
            
        if session.current_branch_field:
            pass
        elif check_screen_satisfied(session, SCREENS[session.current_screen_idx]): 
            session.current_screen_idx += 1
        await render_screen(update, context, target_chat_id=chat_id)
        return

    if session.current_branch_field:
        session.answers[session.current_branch_field['id']] = text
        if session.injected_branch_queue:
            session.current_branch_field = session.injected_branch_queue.pop(0)
        else:
            session.current_branch_field = None
            session.current_screen_idx += 1
        await render_screen(update, context, target_chat_id=chat_id)
        return

    screen_data = SCREENS[session.current_screen_idx]
    txt_fields = [f for f in screen_data['fields'] if f['type'] == 'text']
    if not txt_fields: return
    
    for field in txt_fields:
        if not session.answers.get(field['id']):
            session.answers[field['id']] = text
            if field['id'] == 'q1': session.name = text
            
            msg = get_funny_instant_reaction(field['id'], text)
            if msg:
                await context.bot.send_message(chat_id=chat_id, text=msg, parse_mode="HTML")
            break
            
    if check_screen_satisfied(session, screen_data):
        session.current_screen_idx += 1
        
    await render_screen(update, context, target_chat_id=chat_id)

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = context.user_data.get(user_id)
    if not session or (session.current_screen_idx >= len(SCREENS) and not session.current_branch_field): return
    await handle_text_or_transcription(update.message.text.strip(), update, context, update.message.chat_id)

async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = context.user_data.get(user_id)
    if not session or (session.current_screen_idx >= len(SCREENS) and not session.current_branch_field): return
    
    if not openai_client:
        await update.message.reply_text("❌ Voice parsing engine is currently not active on this backend.")
        return

    chat_id = update.message.chat_id
    status_msg = await context.bot.send_message(chat_id=chat_id, text="🎙️ <i>Coach Avni is transcribing your voice answer...</i>", parse_mode="HTML")
    
    try:
        voice_file = await context.bot.get_file(update.message.voice.file_id)
        voice_buffer = BytesIO()
        await voice_file.download_to_memory(out=voice_buffer)
        voice_buffer.seek(0)
        voice_buffer.name = "voice.ogg"

        transcript = openai_client.audio.transcriptions.create(
            model="whisper-1",
            file=voice_buffer
        )
        parsed_text = transcript.text.strip()
        
        await context.bot.delete_message(chat_id=chat_id, message_id=status_msg.message_id)
        if parsed_text:
            await handle_text_or_transcription(parsed_text, update, context, chat_id)
        else:
            await context.bot.send_message(chat_id=chat_id, text="⚠️ Audio file detected, but no clear text was extracted. Please try speaking closer to your device.")
    except Exception as e:
        logger.error(f"Voice transcription sequence failed safely: {e}")
        try:
            await context.bot.edit_message_text("❌ Transcription network timeout. Please type your custom answer or check your connection status.", chat_id=chat_id, message_id=status_msg.message_id)
        except Exception: pass

async def media_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = context.user_data.get(user_id)
    if not session or session.current_screen_idx >= len(SCREENS): return
    session.answers["q61"] = "Biometric Photo Cache Verified ✓"
    await context.bot.send_message(chat_id=update.message.chat_id, text="💬 <b>Coach Avni:</b> Photo locked in. I will analyze your structural alignment before our call.", parse_mode="HTML")
    session.current_screen_idx += 1
    await render_screen(update, context, target_chat_id=update.message.chat_id)

def main():
    print("🚀 HARDENED DUAL VOICE/TEXT ENGINE DEPLOYED — HOTPATCH ACTIVE")
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.VOICE, voice_handler))
    app.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL, media_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    
    app.run_polling()

if __name__ == "__main__":
    main()
