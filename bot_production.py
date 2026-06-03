#!/usr/bin/env python3
"""
COACH AVNI - HUMANIZED AI MASTER CONVERSATION ENGINE
Upgrades: Complete conversational overhaul. Injects personality, context-aware coaching commentary,
witty remarks, and supportive reality checks into the full 61-question flow.
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

# PDF Layout Libraries
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
CALENDLY_LINK = os.getenv("CALENDLY_LINK", "https://calendly.com/coach_avni/strategy-session")

if not TOKEN:
    print("ERROR: TELEGRAM_TOKEN missing from environment configuration.")
    sys.exit(1)

# Compressed translation key map engine to bypass Telegram's strict 64-Byte callback data limits
ID_MAP = {f"q{i}": f"v{i}" for i in range(1, 62)}
REV_MAP = {v: k for k, v in ID_MAP.items()}

# All 61 Questions spanning across all your onboarding components
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
        {"id": "q61", "text": "Drop a clear front, side, or back body photo here so I can evaluate your real posture and muscle structure. (Totally confidential between us!)", "type": "media", "required": False}
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

# INTELLIGENT HUMAN-LIKE COMMENTARY LOGIC
def check_metabolic_indicators(session) -> str:
    commentary = []
    
    # Extract recent key insights
    name = session.name if session.name != "there" else "My friend"
    job = str(session.answers.get("q5", ""))
    water = str(session.answers.get("q19", ""))
    cravings = str(session.answers.get("q28", ""))
    crash = str(session.answers.get("q29", ""))
    sitting = str(session.answers.get("q50", ""))
    goal = str(session.answers.get("q55", ""))

    # Coach Avni dynamic situational analysis feedback
    if session.current_screen_idx == 1 and session.name != "there":
        return f"👋 <b>Welcome {name}!</b> Let's get down to business. I'm going to look under your metabolic hood. Ready?"
    
    if "💻" in job or "📊" in job or "🤵" in job:
        commentary.append(f"👨‍💻 <i>Coach Note:</i> Ah, desk warrior life. We are definitely going to have to watch out for your hip flexors and lower back posture, {name}.")
        
    if "< 1" in water:
        commentary.append("🚰 <i>Hold up:</i> Less than 1L of water? Your metabolism is running on pure friction right now. Let's fix that.")
        
    if "Intense daily" in cravings:
        commentary.append("🍩 <i>Reality Check:</i> Those daily sugar cravings aren't a 'willpower' issue. Your current gut microbes are hijacking your choices.")

    if "Severe 3 PM crash" in crash:
        commentary.append("🥱 <i>Aha!</i> That 3 PM crash means your insulin is on a chaotic rollercoaster. We're going to stabilize your macros to end that.")

    if "8+" in sitting:
        commentary.append("🛋️ <i>Warning:</i> Sitting for over 8 hours actively downregulates your lipolytic enzymes (fat burning). We need tactical movement breaks.")

    if "Aggressive Fat Loss" in goal:
        commentary.append("🔥 <i>Love the ambition:</i> Aggressive fat loss requires absolute biological compliance. Let's build the engine for it.")

    if not commentary:
        return f"✨ <b>Looking good, {name}.</b> Collected data metrics are tracking normally. Keep moving forward!"
        
    # Return only the most relevant piece of advice to avoid clutter
    return commentary[-1]

def generate_onboarding_pdf(session) -> BytesIO:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Heading1'], fontSize=20, leading=24, textColor=colors.HexColor("#1A365D"), spaceAfter=12
    )
    body_style = ParagraphStyle(
        'BodyTextCustom', parent=styles['Normal'], fontSize=10, leading=14, textColor=colors.HexColor("#2D3748")
    )
    
    story.append(Paragraph(f"COACH AVNI — COMPLETE ASSESSMENT STRATEGY DOSSIER", title_style))
    story.append(Paragraph(f"<b>Client Profile Target Name:</b> {session.name}", body_style))
    story.append(Paragraph(f"<b>Metabolic Readiness Score:</b> {session.calculate_readiness_score()}/100", body_style))
    story.append(Spacer(1, 15))
    
    data = [["Assessment Metric Pillar", "Customer Onboarding Response Log"]]
    for screen in SCREENS:
        for field in screen['fields']:
            ans = session.answers.get(field['id'])
            if ans:
                val_str = ", ".join(ans) if isinstance(ans, list) else str(ans)
                clean_lbl = field['text']
                data.append([Paragraph(clean_lbl, body_style), Paragraph(val_str, body_style)])
                
    t = Table(data, colWidths=[270, 230])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (1,0), colors.HexColor("#1A365D")),
        ('TEXTCOLOR', (0,0), (1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#F7FAFC"), colors.white]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
    ]))
    story.append(t)
    
    doc.build(story)
    buffer.seek(0)
    return buffer

def get_section_start_index(section_name: str) -> int:
    for idx, screen in enumerate(SCREENS):
        if screen['section'] == section_name:
            return idx
    return 0

def check_screen_satisfied(session, screen_data) -> bool:
    for field in screen_data['fields']:
        ans = session.answers.get(field['id'])
        if field['required'] and (ans is None or (isinstance(ans, list) and len(ans) == 0)):
            return False
    return True

async def render_screen(update: Update, context: ContextTypes.DEFAULT_TYPE, query=None, chat_id=None):
    user_id = update.effective_user.id
    if not chat_id: chat_id = update.effective_chat.id
    session = context.user_data[user_id]
    
    # 1. System Review & Modify Screen Layer
    if session.current_screen_idx >= len(SCREENS) and not session.is_submitted:
        review_text = f"📋 <b>Alright {session.name}, let's look at the summary board before locking it down:</b>\n\n"
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
        keyboard.append([InlineKeyboardButton("🚀 LOOKS PERFECT, LET'S INITIATE", callback_data="final_submit")])
        
        if query: await query.edit_message_text(review_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")
        else: await context.bot.send_message(chat_id, text=review_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")
        return

    # 2. System Final Success Page with Active Calendly Endpoint Link
    if session.current_screen_idx >= len(SCREENS) and session.is_submitted:
        score = session.calculate_readiness_score()
        success_text = (
            f"🎯 <b>BOOM! DATA PACKET LOCKED IN SUCCESSFULLY.</b>\n\n"
            f"📈 <b>Your Metabolic Readiness Baseline: {score}/100</b>\n"
            f"Everything is securely mapped inside my framework.\n\n"
            f"I have just compiled your comprehensive tactical profile brief. "
            f"<b>Final Move:</b> Hit the Calendly link below right now so we can jump on your strategy kickoff call and map out the exact plan."
        )
        keyboard = [
            [InlineKeyboardButton("📅 LOCK IN YOUR STRATEGY KICKOFF CALL HERE", url=CALENDLY_LINK)],
            [InlineKeyboardButton("🔄 Wait, let me adjust an answer", callback_data="reopen_form")]
        ]
        if query: await query.edit_message_text(success_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")
        else: await context.bot.send_message(chat_id, text=success_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")
        return

    # 3. Standard Sequential Screen Questionnaire Engine Render Block
    screen_data = SCREENS[session.current_screen_idx]
    progress = int((session.current_screen_idx / len(SCREENS)) * 100)
    live_coach_commentary = check_metabolic_indicators(session)
    
    text = (
        f"📊 <b>Progress: {progress}% deep</b> | Phase: <i>{screen_data['section']}</i>\n"
        f"💬 -----------------------------------------\n"
        f"{live_coach_commentary}\n"
        f"--------------------------------------------\n\n"
    )
    
    for field in screen_data['fields']:
        ans = session.answers.get(field['id'])
        if session.awaiting_custom_field_id == field['id']:
            text += f"❓ <b>{field['text']}</b>\n✍️ <i>[Go ahead, type your honest answer into the chat...]</i>\n\n"
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
            keyboard.append([InlineKeyboardButton(f"⬇️ Select for: {field['text'].split('?')[0]} ⬇️", callback_data="ignore")])
            row, short_id = [], ID_MAP[field['id']]
            for idx, opt in enumerate(field['options']):
                lbl = opt
                ans = session.answers.get(field['id'])
                if field['type'] == 'buttons' and ans == opt: lbl = f"🔥 {opt} [SELECTED]"
                elif field['type'] == 'buttons_multi' and ans and opt in ans: lbl = f"🔥 {opt} [ADDED]"
                row.append(InlineKeyboardButton(lbl, callback_data=f"s_{short_id}_{idx}"))
                if len(row) == 2:
                    keyboard.append(row)
                    row = []
            if row: keyboard.append(row)
            keyboard.append([InlineKeyboardButton("✍️ Give Custom Answer", callback_data=f"c_{short_id}")])
        elif field['type'] == 'media':
            keyboard.append([InlineKeyboardButton("⏭️ Skip Upload (Can do this later)", callback_data="skip_media")])

    nav_row = []
    if session.current_screen_idx > 0:
        nav_row.append(InlineKeyboardButton("⬅️ BACK", callback_data="back_screen"))
    if has_multi or is_multi_question:
        if check_screen_satisfied(session, screen_data): 
            nav_row.append(InlineKeyboardButton("MOVE ON ➡️", callback_data="next_screen"))
        else: 
            nav_row.append(InlineKeyboardButton("🔒 Finish questions above to unlock next phase", callback_data="locked"))
    if nav_row: 
        keyboard.append(nav_row)

    try:
        if query: await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")
        else: await context.bot.send_message(chat_id, text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")
    except Exception: pass

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    context.user_data[user_id] = UserSession()
    text = (
        "🔥 <b>Welcome to the Coach Avni Executive Protocol Funnel.</b>\n\n"
        "I don't do generic cookie-cutter meal plans. We are going to map out your specific lifestyle biomechanics "
        "so we can unlock consistent high energy and permanent fat adaptation.\n\n"
        "Let's check out what's going on under your hood 👇"
    )
    keyboard = [[InlineKeyboardButton("⚡ START YOUR ASSESSMENT INTERFACE", callback_data="start")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    session = context.user_data.get(user_id)
    if not session: return await query.answer("Session expired! Let's restart with /start.", show_alert=True)
    
    data = query.data
    if data in ["ignore", "locked"]: return await query.answer()
    
    if data == "start":
        session.current_screen_idx = 0
        await query.answer()
        await render_screen(update, context, query)
        return

    if data == "back_screen":
        await query.answer()
        if session.current_screen_idx > 0: 
            session.current_screen_idx -= 1
            session.awaiting_custom_field_id = None
        await render_screen(update, context, query)
        return
        
    if data == "next_screen":
        await query.answer()
        session.current_screen_idx += 1
        await render_screen(update, context, query)
        return

    if data.startswith("edit_sec_"):
        await query.answer()
        target_section = data.replace("edit_sec_", "")
        session.current_screen_idx = get_section_start_index(target_section)
        await render_screen(update, context, query)
        return
        
    if data == "final_submit":
        await query.answer("💾 Printing your Strategy Brief Profile PDF...", show_alert=True)
        session.is_submitted = True
        await render_screen(update, context, query)
        
        pdf_file = generate_onboarding_pdf(session)
        await context.bot.send_document(
            chat_id=query.message.chat_id,
            document=pdf_file,
            filename=f"Coach_Avni_{session.name.replace(' ', '_')}_Strategy_Brief.pdf",
            caption="📄 <b>Here is your Strategic Assessment Profile Dossier. Keep this safe.</b>",
            parse_mode="HTML"
        )
        return
        
    if data == "reopen_form":
        await query.answer()
        session.is_submitted = False
        await render_screen(update, context, query)
        return

    if data == "skip_media":
        await query.answer()
        session.answers["q61"] = "Skipped by client"
        session.current_screen_idx += 1
        await render_screen(update, context, query)
        return

    if data.startswith("c_"):
        field_id = REV_MAP[data.split("_")[1]]
        session.awaiting_custom_field_id = field_id
        await query.answer("⌨️ Fire away into the message box!")
        await render_screen(update, context, query)
        return
        
    if data.startswith("s_"):
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
            
        await query.answer()
        has_multi = any(f['type'] == 'buttons_multi' for f in screen_data['fields'])
        is_multi_question = len(screen_data['fields']) > 1
        
        if not has_multi and not is_multi_question: 
            session.current_screen_idx += 1
        await render_screen(update, context, query)

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = context.user_data.get(user_id)
    if not session or session.current_screen_idx >= len(SCREENS): return
    text = update.message.text.strip()
    
    if session.awaiting_custom_field_id:
        session.answers[session.awaiting_custom_field_id] = text
        session.awaiting_custom_field_id = None
        if check_screen_satisfied(session, SCREENS[session.current_screen_idx]): 
            session.current_screen_idx += 1
        await render_screen(update, context, chat_id=update.message.chat_id)
        return

    screen_data = SCREENS[session.current_screen_idx]
    txt_fields = [f for f in screen_data['fields'] if f['type'] == 'text']
    if not txt_fields: return
    
    for field in txt_fields:
        if not session.answers.get(field['id']):
            session.answers[field['id']] = text
            if field['id'] == 'q1': session.name = text
            break
            
    if check_screen_satisfied(session, screen_data):
        session.current_screen_idx += 1
        
    await render_screen(update, context, chat_id=update.message.chat_id)

async def media_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = context.user_data.get(user_id)
    if not session or session.current_screen_idx >= len(SCREENS): return
    session.answers["q61"] = "Biometric Reference Photo Saved Confidentially ✅"
    session.current_screen_idx += 1
    await render_screen(update, context, chat_id=update.message.chat_id)

def main():
    print("🚀 COACH AVNI HUMANIZED EMBEDDED CONVERSATION ENGINE IS ONLINE")
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL, media_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    
    app.run_polling()

if __name__ == "__main__":
    main()
