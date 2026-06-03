#!/usr/bin/env python3
"""
COACH AVNI - PREMIUM CONVERSATION ENGINE (SMART SCREEN-FLOW EDITION)
Fixes: Multi-question screens update silently until completely satisfied.
Standalone witty remarks only drop into permanent chat history when a screen is fully answered.
"""

import os
import sys
from io import BytesIO
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler, 
    filters, ContextTypes
)

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
CALENDLY_LINK = os.getenv("CALENDLY_LINK", "https://calendly.com/coach_avni/strategy-session")

if not TOKEN:
    print("CRITICAL: TELEGRAM_TOKEN missing.")
    sys.exit(1)

ID_MAP = {f"q{i}": f"v{i}" for i in range(1, 62)}
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

class UserSession:
    def __init__(self):
        self.current_screen_idx = 0
        self.answers = {}
        self.name = "there"
        self.awaiting_custom_field_id = None
        self.is_submitted = False
        
    def calculate_readiness_score(self):
        score = 85
        water = str(self.answers.get("q19", ""))
        stress = str(self.answers.get("q40", ""))
        sleep = str(self.answers.get("q41", ""))
        if "< 1" in water: score -= 15
        if "4-5" in stress: score -= 15
        if "Fragmented" in sleep: score -= 10
        return max(10, min(100, score))

def get_funny_instant_reaction(field_id: str, value: str) -> str:
    v = str(value)
    reactions = {
        "q2": "Age is just a baseline number. We are about to optimize your cellular age anyway! 🧬",
        "q5": {
            "💻 Engineer": "An Engineer! Prepare to analyze your macros like code. Just don't over-engineer the workout. 😉",
            "👨‍⚕️ Doctor": "A Doctor! Respect for the brutal shifts. Let's make sure you aren't ignoring your own charts.",
            "📊 Corporate": "Corporate life! High status, higher sitting hours. Time to optimize your corporate engine."
        },
        "q6": {
            "👨 Male": "Got it, optimizing hormones and training split for male biology profile. 💪",
            "👩 Female": "Got it, designing meal structures matching female endocrine optimization profiles. ✨"
        },
        "q7": {
            "🍗 Non-Veg": "Non-veg makes hitting our daily complete protein targets much easier. Perfect.",
            "🥕 Veg": "Vegetarian it is. Don't worry, I won't just dump paneer and cucumbers on your plate.",
            "🌱 Vegan": "Vegan! Plant-powered engine. We will need to be tactical with amino-acid pairing."
        },
        "q10": {
            "☕ Yes, regularly": "Regular caffeine dependency? Let's make sure it's not masking deep system fatigue. ☕",
            "🚫 Total Abstinence": "Zero caffeine? Wow, running on pure natural ATP. Love to see it! 🙌"
        },
        "q11": {
            "⏰ 5:00 AM": "5 AM club! Early bird efficiency. Your circadian rhythms are already in prime position.",
            "⏰ 8:00 AM+": "Waking up past 8 AM? Night owl tendencies or corporate recovery mode? We will adapt."
        },
        "q17": {
            "🦉 1:00 AM+": "Past 1 AM? Ouch. Those blue screens are actively tricking your brain into thinking it's noon. 🦉"
        },
        "q19": {
            "🥛 < 1 Litre": "Wait... less than 1L of water?! Your blood is practically running on thick sludge right now. Drink up! 🚰",
            "🌊 3+ Litres": "Over 3 Litres? Hydro-homie status unlocked! Your metabolic processes thank you. 🌊"
        },
        "q20": {
            "🍔 Daily": "Daily takeout?! Safe to say your body is swimming in industrial seed oils. Time for an intervention! 🚨"
        },
        "q28": {
            "🍩 Intense daily": "Intense daily sugar cravings? Remember: that's your gut microbiome screaming for bad fuel, not a lack of willpower."
        },
        "q29": {
            "🥱 Severe 3 PM crash": "Ah, the classic 3 PM energy flatline. That's your glucose spiking up and crashing hard. We'll end that rollercoaster. 📉"
        },
        "q40": {
            "😫 4-5 (High)": "High stress overload. Cortisol is the ultimate enemy of fat loss. We are heavily prioritizing recovery protocols for you. 🧘‍♂️"
        },
        "q50": {
            "💀 8+ Hours": "8+ hours glued to a desk chair is the absolute kryptonite for active posture. We will introduce micro-movements. 🛋️"
        },
        "q55": {
            "📉 Aggressive Fat Loss": "Aggressive fat loss! Bold goal. It requires absolute operational compliance. Let's build the engine.",
            "💪 Hypertrophy Lean Muscle": "Lean muscle hypertrophy! Time to trigger progressive overload and optimize your amino synthesis."
        }
    }
    
    if field_id in reactions:
        if isinstance(reactions[field_id], dict):
            for key, msg in reactions[field_id].items():
                if key in v: return f"🎙️ <b>Coach Avni:</b> {msg}"
        else:
            return f"🎙️ <b>Coach Avni:</b> {reactions[field_id]}"
    return f"🎙️ <b>Coach Avni:</b> Configured standard profile log for {field_id.upper()}."

def check_screen_satisfied(session, screen_data) -> bool:
    for field in screen_data['fields']:
        ans = session.answers.get(field['id'])
        if field['required'] and (ans is None or (isinstance(ans, list) and len(ans) == 0)):
            return False
    return True

async def render_screen(update: Update, context: ContextTypes.DEFAULT_TYPE, message_id=None, chat_id=None):
    user_id = update.effective_user.id
    if not chat_id: chat_id = update.effective_chat.id
    session = context.user_data[user_id]
    
    # Summary Review Phase
    if session.current_screen_idx >= len(SCREENS) and not session.is_submitted:
        review_text = f"📋 <b>Alright {session.name}, here is your full profile board. Review before locking it down:</b>\n\n"
        processed_sections = []
        for screen in SCREENS:
            sec_name = screen['section']
            if sec_name in processed_sections: continue
            processed_sections.append(sec_name)
            review_text += f"🔸 <b>{sec_name.upper()}</b>\n"
            sec_fields = [f for s in SCREENS if s['section'] == sec_name for f in s['fields']]
            for field in sec_fields:
                ans = session.answers.get(field['id'], "—")
                val_str = ", ".join(ans) if isinstance(ans, list) else str(ans)
                review_text += f" • {field['text']}: <code>{val_str}</code>\n"
            review_text += "\n"
            
        keyboard = []
        row = []
        for sec in processed_sections:
            row.append(InlineKeyboardButton(f"✏️ Fix {sec.split()[-1]}", callback_data=f"edit_sec_{sec}"))
            if len(row) == 2:
                keyboard.append(row)
                row = []
        if row: keyboard.append(row)
        keyboard.append([InlineKeyboardButton("🚀 LOOKS PERFECT, SUBMIT PROFILE", callback_data="final_submit")])
        
        await context.bot.send_message(chat_id, text=review_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")
        return

    # Call Booking Phase
    if session.current_screen_idx >= len(SCREENS) and session.is_submitted:
        score = session.calculate_readiness_score()
        success_text = (
            f"🎯 <b>DATA LOGGED IN SAFELY.</b>\n\n"
            f"📈 <b>Metabolic Readiness Score: {score}/100</b>\n\n"
            f"<b>Final Move:</b> Use the active scheduler link below right now to lock in your live Strategy Kickoff Call!"
        )
        keyboard = [[InlineKeyboardButton("📅 BOOK STRATEGY KICKOFF CALL HERE", url=CALENDLY_LINK)]]
        await context.bot.send_message(chat_id, text=success_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")
        return

    # Active Questionnaire Presentation
    screen_data = SCREENS[session.current_screen_idx]
    progress = int((session.current_screen_idx / len(SCREENS)) * 100)
    
    text = f"📝 <b>Phase: {screen_data['section']}</b> (Progress: `{progress}%`)\n━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    for field in screen_data['fields']:
        ans = session.answers.get(field['id'])
        if session.awaiting_custom_field_id == field['id']:
            text += f"❓ <b>{field['text']}</b>\n✍️ <i>[Type custom input directly into chat box...]</i>\n\n"
        elif ans:
            display = ", ".join(ans) if isinstance(ans, list) else str(ans)
            text += f"✅ <b>{field['text']}</b>\n👉 <code>{display}</code>\n\n"
        else:
            text += f"👉 <b>{field['text']}</b>\n\n"

    keyboard = []
    has_multi = any(f['type'] == 'buttons_multi' for f in screen_data['fields'])
    is_multi_question = len(screen_data['fields']) > 1
    
    for field in screen_data['fields']:
        if field['type'] in ['buttons', 'buttons_multi']:
            clean_hdr = field['text'].split('?')[0].split(':')[0].strip()
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
            keyboard.append([InlineKeyboardButton("✍️ Type Custom Answer", callback_data=f"c_{short_id}")])
        elif field['type'] == 'media':
            keyboard.append([InlineKeyboardButton("⏭️ Skip Upload", callback_data="skip_media")])

    nav_row = []
    if session.current_screen_idx > 0:
        nav_row.append(InlineKeyboardButton("⬅️ BACK", callback_data="back_screen"))
    if has_multi or is_multi_question:
        if check_screen_satisfied(session, screen_data): 
            nav_row.append(InlineKeyboardButton("CONTINUE ➡️", callback_data="next_screen"))
        else: 
            nav_row.append(InlineKeyboardButton("🔒 Finish all answers above", callback_data="locked"))
    if nav_row: keyboard.append(nav_row)

    # SMART INTERFACE ENGINE: Update current message if on a multi-question screen, else push forward freshly
    if message_id:
        try:
            await context.bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")
            return
        except Exception: pass

    await context.bot.send_message(chat_id, text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")

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
    
    if data == "start":
        await query.answer()
        try: await query.message.delete()
        except Exception: pass
        session.current_screen_idx = 0
        await render_screen(update, context, chat_id=query.message.chat_id)
        return

    if data == "back_screen":
        await query.answer()
        try: await query.message.delete()
        except Exception: pass
        if session.current_screen_idx > 0: session.current_screen_idx -= 1
        await render_screen(update, context, chat_id=query.message.chat_id)
        return
        
    if data == "next_screen":
        await query.answer()
        # SCREEN ADVANCEMENT: Drop reactions permanently into historical text layout
        screen_data = SCREENS[session.current_screen_idx]
        try: await query.message.delete()
        except Exception: pass
        
        for field in screen_data['fields']:
            ans = session.answers.get(field['id'])
            if ans and field['type'] == 'buttons':
                await context.bot.send_message(chat_id=query.message.chat_id, text=get_funny_instant_reaction(field['id'], ans), parse_mode="HTML")
                
        session.current_screen_idx += 1
        await render_screen(update, context, chat_id=query.message.chat_id)
        return

    if data.startswith("edit_sec_"):
        await query.answer()
        try: await query.message.delete()
        except Exception: pass
        target_section = data.replace("edit_sec_", "")
        session.current_screen_idx = next((i for i, s in enumerate(SCREENS) if s['section'] == target_section), 0)
        await render_screen(update, context, chat_id=query.message.chat_id)
        return
        
    if data == "final_submit":
        await query.answer("💾 Finalizing profile dossier...", show_alert=True)
        try: await query.message.delete()
        except Exception: pass
        session.is_submitted = True
        
        # Safe execution of dynamic PDF rendering engine
        try:
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
            story = []
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=18, leading=22, textColor=colors.HexColor("#1A365D"), spaceAfter=12)
            body_style = ParagraphStyle('BodyTextCustom', parent=styles['Normal'], fontSize=10, leading=14, textColor=colors.HexColor("#2D3748"))
            
            story.append(Paragraph(f"COACH AVNI — STRATEGIC BIOMETRIC BRIEF", title_style))
            story.append(Paragraph(f"<b>Client Target:</b> {session.name}", body_style))
            story.append(Paragraph(f"<b>Metabolic Blueprint Score:</b> {session.calculate_readiness_score()}/100", body_style))
            story.append(Spacer(1, 15))
            
            table_data = [["Assessment Metric Pillar", "Customer Onboarding Response Log"]]
            for screen in SCREENS:
                for field in screen['fields']:
                    ans = session.answers.get(field['id'])
                    if ans:
                        val_str = ", ".join(ans) if isinstance(ans, list) else str(ans)
                        table_data.append([Paragraph(field['text'], body_style), Paragraph(val_str, body_style)])
                        
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
                chat_id=query.message.chat_id,
                document=buffer,
                filename=f"Coach_Avni_{session.name.replace(' ', '_')}_Brief.pdf",
                caption="📄 <b>Here is your strategic diagnostic summary asset. Keep this close.</b>",
                parse_mode="HTML"
            )
        except Exception: pass
        
        await render_screen(update, context, chat_id=query.message.chat_id)
        return

    if data == "skip_media":
        await query.answer()
        try: await query.message.delete()
        except Exception: pass
        session.answers["q61"] = "Skipped"
        session.current_screen_idx += 1
        await render_screen(update, context, chat_id=query.message.chat_id)
        return

    if data.startswith("c_"):
        await query.answer()
        field_id = REV_MAP[data.split("_")[1]]
        session.awaiting_custom_field_id = field_id
        await render_screen(update, context, message_id=query.message.message_id, chat_id=query.message.chat_id)
        return
        
    if data.startswith("s_"):
        await query.answer()
        parts = data.split("_")
        field_id = REV_MAP[parts[1]]
        opt_idx = int(parts[2])
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
        
        # SMART LAYER FLOW CHECK
        if not has_multi and not is_multi_question:
            # Single question screen: Clean old message, output witty chat commentary, advance cleanly
            try: await query.message.delete()
            except Exception: pass
            await context.bot.send_message(chat_id=query.message.chat_id, text=get_funny_instant_reaction(field_id, selected), parse_mode="HTML")
            session.current_screen_idx += 1
            await render_screen(update, context, chat_id=query.message.chat_id)
        else:
            # Multi-question screen: Edit current message layout quietly so user can tap remaining choices
            if check_screen_satisfied(session, screen_data):
                try: await query.message.delete()
                except Exception: pass
                # Dump reactions for all questions on this completed screen into chat history blocks
                for f in screen_data['fields']:
                    ans = session.answers.get(f['id'])
                    if ans and f['type'] == 'buttons':
                        await context.bot.send_message(chat_id=query.message.chat_id, text=get_funny_instant_reaction(f['id'], ans), parse_mode="HTML")
                session.current_screen_idx += 1
                await render_screen(update, context, chat_id=query.message.chat_id)
            else:
                await render_screen(update, context, message_id=query.message.message_id, chat_id=query.message.chat_id)

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = context.user_data.get(user_id)
    if not session or session.current_screen_idx >= len(SCREENS): return
    text = update.message.text.strip()
    chat_id = update.message.chat_id
    
    if session.awaiting_custom_field_id:
        session.answers[session.awaiting_custom_field_id] = text
        session.awaiting_custom_field_id = None
        await context.bot.send_message(chat_id=chat_id, text=get_funny_instant_reaction(session.awaiting_custom_field_id, text), parse_mode="HTML")
        if check_screen_satisfied(session, SCREENS[session.current_screen_idx]): 
            session.current_screen_idx += 1
        await render_screen(update, context, chat_id=chat_id)
        return

    screen_data = SCREENS[session.current_screen_idx]
    txt_fields = [f for f in screen_data['fields'] if f['type'] == 'text']
    if not txt_fields: return
    
    for field in txt_fields:
        if not session.answers.get(field['id']):
            session.answers[field['id']] = text
            if field['id'] == 'q1': session.name = text
            await context.bot.send_message(chat_id=chat_id, text=get_funny_instant_reaction(field['id'], text), parse_mode="HTML")
            break
            
    if check_screen_satisfied(session, screen_data):
        session.current_screen_idx += 1
        
    await render_screen(update, context, chat_id=chat_id)

async def media_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = context.user_data.get(user_id)
    if not session or session.current_screen_idx >= len(SCREENS): return
    session.answers["q61"] = "Biometric Photo Cache Verified ✓"
    await context.bot.send_message(chat_id=update.message.chat_id, text="🎙️ <b>Coach Avni:</b> Photo locked in. I will analyze your structural alignment before our call.", parse_mode="HTML")
    session.current_screen_idx += 1
    await render_screen(update, context, chat_id=update.message.chat_id)

def main():
    print("🚀 COACH AVNI ONLINE — SCREEN INTERACTION PIPELINE ACTIVE")
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL, media_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    
    app.run_polling()

if __name__ == "__main__":
    main()
