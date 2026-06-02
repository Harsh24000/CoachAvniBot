#!/usr/bin/env python3
"""
COACH AVNI BOT - ALL 61 QUESTIONS MASTER PRODUCTION ENGINE
Contains the complete comprehensive dataset (Questions 1 to 61) spanning all sections.
Features: 2-Way Navigation Hierarchy (⬅️ BACK / CONTINUE ➡️), Live Risk Metrics,
ReportLab Auto-PDF Brief Compiler, Calendly Strategy CTA, & 64-Byte Payload Limit Protection.
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
ID_MAP = {
    f"q{i}": f"v{i}" for i in range(1, 62)
}
REV_MAP = {v: k for k, v in ID_MAP.items()}

# All 61 Questions spanning across all your onboarding components
SCREENS = [
    {"id": 1, "section": "👤 About You", "fields": [
        {"id": "q1", "text": "What is your full name?", "type": "text", "required": True},
        {"id": "q2", "text": "What is your current age?", "type": "text", "required": True},
        {"id": "q3", "text": "Current height (in cm)?", "type": "text", "required": True},
        {"id": "q4", "text": "Current weight (in kg)?", "type": "text", "required": True}
    ]},
    {"id": 2, "section": "👤 About You", "fields": [
        {"id": "q5", "text": "What is your occupation/profession?", "type": "buttons", "required": True, "options": ["💻 Engineer", "👨‍⚕️ Doctor", "📚 Student", "👔 Business", "🤵 Consultant", "📊 Corporate"]},
        {"id": "q6", "text": "What is your biological sex?", "type": "buttons", "required": True, "options": ["👨 Male", "👩 Female"]}
    ]},
    {"id": 3, "section": "🍏 Diet & Food", "fields": [
        {"id": "q7", "text": "Select your core dietary preference (Type)?", "type": "buttons", "required": True, "options": ["🍗 Non-Veg", "🥕 Veg", "🥚 Eggitarian", "🌱 Vegan", "☪️ Jain Vegetarian"]},
        {"id": "q8", "text": "Foods you absolutely HATE or avoid? (Multi-select)", "type": "buttons_multi", "required": False, "options": ["🥒 Bitter Gourd", "🍆 Eggplant", "🍄 Mushroom", "🐟 Fish", "🥛 Dairy", "🧅 No Onion/Garlic"]}
    ]},
    {"id": 4, "section": "🍏 Diet & Food", "fields": [
        {"id": "q9", "text": "What are your structural Cuisine Preferences?", "type": "buttons", "required": True, "options": ["🍛 North Indian", "🫓 South Indian", "🥗 Continental", "🥢 Asian Mix"]},
        {"id": "q10", "text": "Do you consume tea or coffee regularly?", "type": "buttons", "required": True, "options": ["☕ Yes, regularly", "🍵 Occasionally", "🚫 Total Abstinence"]}
    ]},
    {"id": 5, "section": "🌅 Your Day", "fields": [
        {"id": "q11", "text": "What time do you wake up?", "type": "buttons", "required": True, "options": ["⏰ 5:00 AM", "⏰ 6:00 AM", "⏰ 7:00 AM", "⏰ 8:00 AM+"]},
        {"id": "q12", "text": "What time do you eat breakfast?", "type": "buttons", "required": True, "options": ["🌅 8:00 AM", "🌅 9:00 AM", "🌅 10:00 AM", "⏭️ Skip Breakfast"]},
        {"id": "q13", "text": "When do you start your work day?", "type": "buttons", "required": True, "options": ["💼 8:00 AM", "💼 9:00 AM", "💼 10:00 AM", "⌛ Shift Rotation"]}
    ]},
    {"id": 6, "section": "🌅 Your Day", "fields": [
        {"id": "q14", "text": "What time do you finish work?", "type": "buttons", "required": True, "options": ["⏰ 5:00 PM", "⏰ 6:00 PM", "⏰ 7:00 PM", "🌙 9:00 PM+"]},
        {"id": "q15", "text": "What time do you eat lunch?", "type": "buttons", "required": True, "options": ["🍱 12:30 PM", "🍱 1:30 PM", "🍱 2:30 PM", "⏳ Unfixed/Variable"]},
        {"id": "q16", "text": "What time do you eat dinner?", "type": "buttons", "required": True, "options": ["🍽️ 7:00 PM", "🍽️ 8:00 PM", "🍽️ 9:00 PM", "🌙 10:00 PM+"]}
    ]},
    {"id": 7, "section": "🌅 Your Day", "fields": [
        {"id": "q17", "text": "What time do you typically sleep?", "type": "buttons", "required": True, "options": ["🌙 10:00 PM", "🌙 11:00 PM", "🌙 12:00 AM", "🦉 1:00 AM+"]},
        {"id": "q18", "text": "Frequency of mid-day snacking?", "type": "buttons", "required": True, "options": ["🍪 Constant", "🍏 Occasional", "🚫 No Snacking"]},
        {"id": "q19", "text": "Daily water fluid volume tracking?", "type": "buttons", "required": True, "options": ["🥛 < 1 Litre", "💧 1-2 Litres", "🚰 2-3 Litres", "🌊 3+ Litres"]}
    ]},
    {"id": 8, "section": "🌅 Your Day", "fields": [
        {"id": "q20", "text": "How often do you consume outside/packaged food?", "type": "buttons", "required": True, "options": ["🍔 Daily", "🍕 2-3x / Week", "🥗 Rarely", "✅ Never"]},
        {"id": "q21", "text": "Weekly alcohol intake configurations?", "type": "buttons", "required": True, "options": ["🍺 High Volume", "🍷 Social/Weekend", "🚫 Completely Clean"]},
        {"id": "q22", "text": "Do you smoke or consume tobacco items?", "type": "buttons", "required": True, "options": ["🚬 Yes, daily", "💨 Socially", "🚫 No"]}
    ]},
    {"id": 9, "section": "🏥 Health", "fields": [
        {"id": "q23", "text": "Diagnosed clinical issues (Conditions)?", "type": "buttons_multi", "required": False, "options": ["🔬 Diabetes", "🧬 Thyroid", "🔴 PCOS/PCOD", "❤️ Hypertension", "🍗 Fatty Liver", "✅ None"]},
        {"id": "q24", "text": "Any history of specific physical injuries?", "type": "text", "required": False},
        {"id": "q25", "text": "Do you present with internal allergies detailed?", "type": "buttons", "required": True, "options": ["✅ None", "🍔 Food Specific", "💊 Pharmaceutical", "🌫️ Environmental"]}
    ]},
    {"id": 10, "section": "🏥 Health", "fields": [
        {"id": "q26", "text": "Are you currently taking any regular prescription medications?", "type": "text", "required": False},
        {"id": "q27", "text": "Describe your digestion and bowel issues?", "type": "buttons", "required": True, "options": ["🟢 Smooth/Regular", "⚠️ Chronic Bloating", "🛑 Regular Constipation", "🔥 Acid Reflux"]}
    ]},
    {"id": 11, "section": "🏥 Health", "fields": [
        {"id": "q28", "text": "Do you suffer from frequent sweet or sugar cravings?", "type": "buttons", "required": True, "options": ["🍩 Intense daily", "🍫 Post-meals only", "🚫 Seldom/Never"]},
        {"id": "q29", "text": "Do you experience regular energy slumps?", "type": "buttons", "required": True, "options": ["🥱 Severe 3 PM crash", "🥱 Constant fatigue", "⚡ Steady performance"]}
    ]},
    {"id": 12, "section": "🏥 Health", "fields": [
        {"id": "q30", "text": "Current skin or hair health tracking status?", "type": "buttons", "required": True, "options": ["⚠️ High hair fall", "⚠️ Acne breaks", "✅ Stable/Optimal"]},
        {"id": "q31", "text": "Describe your baseline immune defense system?", "type": "buttons", "required": True, "options": ["🤧 Catch colds easily", "💊 Depend on meds", "🛡️ High/Rarely sick"]}
    ]},
    {"id": 13, "section": "💊 Supplements & Habits", "fields": [
        {"id": "q32", "text": "Vitamin D3 Supplementation status?", "type": "buttons", "required": True, "options": ["💊 Daily/Weekly", "🧪 Deficient (No Pill)", "❌ Not Tracking"]},
        {"id": "q33", "text": "Vitamin B12 Supplementation status?", "type": "buttons", "required": True, "options": ["💊 Regular Intake", "🧪 Deficient", "❌ Not Tracking"]},
        {"id": "q34", "text": "Omega-3 / Fish Oil Habits?", "type": "buttons", "required": True, "options": ["✅ Yes, daily", "❌ No Intake"]},
        {"id": "q35", "text": "General Multivitamins usage?", "type": "buttons", "required": True, "options": ["✅ Consuming", "❌ No Intake"]}
    ]},
    {"id": 14, "section": "💊 Supplements & Habits", "fields": [
        {"id": "q36", "text": "Do you use hair dye or chemicals often?", "type": "buttons", "required": True, "options": ["💇 Yes, frequently", "🚫 Minimal/Never"]},
        {"id": "q37", "text": "Do you suffer from brain fog or lack of focus?", "type": "buttons", "required": True, "options": ["🧠 Yes, regularly", "😐 Mid-day fatigue", "✅ Clear/Sharp"]},
        {"id": "q38", "text": "Are you prone to mood swings or anxiety?", "type": "buttons", "required": True, "options": ["⚡ Frequent shifts", "🌊 Under high stress", "😊 Balanced/Grounded"]}
    ]},
    {"id": 15, "section": "💊 Supplements & Habits", "fields": [
        {"id": "q39", "text": "How do you rate your body recovery cycles?", "type": "buttons", "required": True, "options": ["🐌 Wake up tired", "⚡ Fast joint recovery", "🩹 Slow healing/Sore"]},
        {"id": "q40", "text": "Current mental stress levels?", "type": "buttons", "required": True, "options": ["😊 1-2 (Low)", "😐 3 (Manageable)", "😫 4-5 (High)"]},
        {"id": "q41", "text": "Sleep deepness quality profile?", "type": "buttons", "required": True, "options": ["🥱 Fragmented/Wakeful", "😐 Average Depth", "😴 Deep Nightly State"]}
    ]},
    {"id": 16, "section": "🏃 Physical Biomechanics", "fields": [
        {"id": "q42", "text": "Rate of physical snoring occurrences?", "type": "buttons", "required": True, "options": ["🔊 Yes, heavy snoring", "🔉 Light/Occasional", "🚫 No Snoring"]},
        {"id": "q43", "text": "Morning fatigue state status?", "type": "buttons", "required": True, "options": ["✅ Wake up fresh", "Usually groggy 🥱", "Tired/Exhausted 💤"]},
        {"id": "q44", "text": "Do you have dark circles under your eyes?", "type": "buttons", "required": True, "options": ["👁️ Prominent/Dark", "👁️ Faint", "✅ None"]}
    ]},
    {"id": 17, "section": "🏃 Physical Biomechanics", "fields": [
        {"id": "q45", "text": "Any history of rapid, unexplained weight shifts?", "type": "buttons", "required": True, "options": ["📈 Gained fast lately", "📉 Dropped fast lately", "✅ Steady weight"]},
        {"id": "q46", "text": "Are you prone to continuous water retention/bloating?", "type": "buttons", "required": True, "options": ["💧 Heavy ankles/hands", "💧 Face puffiness", "🚫 No"]},
        {"id": "q47", "text": "Do you have chronic cold hands or cold feet?", "type": "buttons", "required": True, "options": ["🥶 Yes, constantly", "🥶 Only in winter", "🚫 No"]}
    ]},
    {"id": 18, "section": "🏃 Physical Biomechanics", "fields": [
        {"id": "q48", "text": "Do you suffer from chronic joint or body pains?", "type": "buttons", "required": True, "options": ["💥 Lower back issue", "💥 Knee pain structural", "💥 Neck/Shoulders", "✅ Fully pain-free"]},
        {"id": "q49", "text": "How quickly do you experience shortness of breath?", "type": "buttons", "required": True, "options": ["🫁 Walking up stairs", "🫁 Only during sprints", "⚡ Strong cardiorespiratory"]},
        {"id": "q50", "text": "Continuous hours spent sitting at a desk daily?", "type": "buttons", "required": True, "options": ["🚶 Below 4 Hours", "😐 4 - 7 Hours", "💀 8+ Hours"]}
    ]},
    {"id": 19, "section": "🏃 Physical Biomechanics", "fields": [
        {"id": "q51", "text": "Any history of family lifestyle diseases?", "type": "buttons_multi", "required": False, "options": ["🩸 Diabetes trend", "❤️ Cardiovascular issues", "🧬 Obesity traits", "✅ Clear History"]},
        {"id": "q52", "text": "Rate your daily structural skin health look?", "type": "buttons", "required": True, "options": ["🍂 Very dry/flaky", "💧 Excess oily zone", "✨ Well-hydrated/Normal"]},
        {"id": "q53", "text": "Describe your appetite stability profile?", "type": "buttons", "required": True, "options": ["🔥 Uncontrollable/Bingeing", "🧊 Low appetite/Forget to eat", "✅ Stable patterns"]}
    ]},
    {"id": 20, "section": "🎯 Targets & Objectives", "fields": [
        {"id": "q54", "text": "Have you ever tried an official caloric tracking plan before?", "type": "buttons", "required": True, "options": ["📈 Yes, did macros", "📉 Tried and failed", "🚫 Never tracked"]},
        {"id": "q55", "text": "What is your core primary health objective?", "type": "buttons", "required": True, "options": ["📉 Aggressive Fat Loss", "💪 Hypertrophy Lean Muscle", "⚡ Athletic Endurance", "❤️ Metabolic Correction"]},
        {"id": "q56", "text": "What is your main structural barrier to consistency?", "type": "buttons", "required": True, "options": ["⏳ Extreme time deficit", "🍳 Cooking complexity", "🍿 Social/Travel habits", "🧠 Lack of internal drive"]}
    ]},
    {"id": 21, "section": "🎯 Targets & Objectives", "fields": [
        {"id": "q57", "text": "Rate your overall daily energy level consistency?", "type": "buttons", "required": True, "options": ["📈 Peak morning/low night", "📉 Flatline low energy", "⚡ High baseline all day"]},
        {"id": "q58", "text": "How much time can you allocate to exercise weekly?", "type": "buttons", "required": True, "options": ["⏳ Under 2 Hours", "⏳ 2 to 4 Hours", "⚡ 5+ Hours fully ready!"]}
    ]},
    {"id": 22, "section": "🎯 Targets & Objectives", "fields": [
        {"id": "q59", "text": "Do you drink soda, carbonated beverages, or energy drinks?", "type": "buttons", "required": True, "options": ["🥤 Yes, almost daily", "🥤 Socially/Weekends", "🚫 Complete clean limit"]},
        {"id": "q60", "text": "What is your target timeline to reach this structural milestone?", "type": "buttons", "required": True, "options": ["🔥 4 to 8 Weeks", "⚡ 12 Weeks (Recommended)", "⏳ Long-term shift"]}
    ]},
    {"id": 23, "section": "📸 Biometric Profiles", "fields": [
        {"id": "q61", "text": "Upload front, side, or back body profiles for direct visual composition metrics.", "type": "media", "required": False}
    ]}
]

class UserSession:
    def __init__(self):
        self.current_screen_idx = 0
        self.answers = {}
        self.name = "Valued Client"
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

def check_metabolic_indicators(session) -> str:
    indicators = []
    water = str(session.answers.get("q19", ""))
    sitting = str(session.answers.get("q50", ""))
    energy = str(session.answers.get("q29", ""))
    
    if "< 1" in water:
        indicators.append("🚨 <b>HYDRATION WARNING:</b> Cellular water deficit can slow down metabolic rates.")
    if "8+" in sitting or "💀" in sitting:
        indicators.append("🛋️ <b>POSTURAL HAZARD:</b> High sitting hours detected. Lower back tension risk.")
    if "3 PM crash" in energy or "Constant" in energy:
        indicators.append("🥱 <b>ENERGY CRASH TRACE:</b> High blood sugar variability. Target macro stabilization.")
        
    if not indicators:
        return "✨ <b>Current Biomarkers:</b> Stable metabolic parameters logged."
    return "\n".join(indicators)

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
    
    story.append(Paragraph(f"COACH AVNI — COMPLETE CLIENT ONBOARDING REPORT", title_style))
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
    
    if session.current_screen_idx >= len(SCREENS) and not session.is_submitted:
        review_text = "📋 <b>Review & Confirm Your Onboarding Answers</b>\n\n"
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
            row.append(InlineKeyboardButton(f"✏️ {sec.split()[-1]}", callback_data=f"edit_sec_{sec}"))
            if len(row) == 2:
                keyboard.append(row)
                row = []
        if row: keyboard.append(row)
        keyboard.append([InlineKeyboardButton("🚀 LOCK PROFILE & SECURE WELCOME KIT", callback_data="final_submit")])
        
        if query: await query.edit_message_text(review_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")
        else: await context.bot.send_message(chat_id, text=review_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")
        return

    if session.current_screen_idx >= len(SCREENS) and session.is_submitted:
        score = session.calculate_readiness_score()
        success_text = (
            f"🧠 <b>BIO-METRIC ONBOARDING REGISTERED SUCCESSFULLY</b>\n\n"
            f"📊 <b>Metabolic Score Metric: {score}/100</b>\n"
            f"✅ <b>Status:</b> Completely Configured.\n\n"
            f"Your tailored onboarding protocol file brief has been generated. "
            f"<b>Next Step:</b> Book your strategy kickoff call directly via Calendly below."
        )
        keyboard = [
            [InlineKeyboardButton("📅 BOOK KICKOFF CALL VIA CALENDLY", url=CALENDLY_LINK)],
            [InlineKeyboardButton("🔄 REVIEW/OPEN DATA ENTRIES", callback_data="reopen_form")]
        ]
        if query: await query.edit_message_text(success_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")
        else: await context.bot.send_message(chat_id, text=success_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")
        return

    screen_data = SCREENS[session.current_screen_idx]
    progress = int((session.current_screen_idx / len(SCREENS)) * 100)
    live_risk_bar = check_metabolic_indicators(session)
    
    text = (
        f"⚙️ <b>Evaluation Setup: {progress}% Complete</b>\n"
        f"Module: <i>{screen_data['section']}</i>\n"
        f"-----------------------------------------\n"
        f"{live_risk_bar}\n"
        f"-----------------------------------------\n\n"
    )
    
    for field in screen_data['fields']:
        ans = session.answers.get(field['id'])
        if session.awaiting_custom_field_id == field['id']:
            text += f"❓ <b>{field['text']}</b>\n✍️ <code>[Waiting for input context...]</code>\n\n"
        elif ans:
            display = ", ".join(ans) if isinstance(ans, list) else str(ans)
            text += f"✅ <b>{field['text']}</b>\n👉 <i>{display}</i>\n\n"
        else:
            text += f"👉 <b>{field['text']}</b>\n\n"

    keyboard = []
    has_multi = any(f['type'] == 'buttons_multi' for f in screen_data['fields'])
    is_multi_question = len(screen_data['fields']) > 1
    
    for field in screen_data['fields']:
        if field['type'] in ['buttons', 'buttons_multi']:
            keyboard.append([InlineKeyboardButton(f"✨ {field['text'].split('?')[0]}? ✨", callback_data="ignore")])
            row, short_id = [], ID_MAP[field['id']]
            for idx, opt in enumerate(field['options']):
                lbl = opt
                ans = session.answers.get(field['id'])
                if field['type'] == 'buttons' and ans == opt: lbl = f"🔥 {opt} ✅"
                elif field['type'] == 'buttons_multi' and ans and opt in ans: lbl = f"🔥 {opt} ✅"
                row.append(InlineKeyboardButton(lbl, callback_data=f"s_{short_id}_{idx}"))
                if len(row) == 2:
                    keyboard.append(row)
                    row = []
            if row: keyboard.append(row)
            keyboard.append([InlineKeyboardButton("✍️ Custom Input", callback_data=f"c_{short_id}")])
        elif field['type'] == 'media':
            keyboard.append([InlineKeyboardButton("⏭️ Skip Profile Image Uploads", callback_data="skip_media")])

    nav_row = []
    if session.current_screen_idx > 0:
        nav_row.append(InlineKeyboardButton("⬅️ BACK", callback_data="back_screen"))
    if has_multi or is_multi_question:
        if check_screen_satisfied(session, screen_data): 
            nav_row.append(InlineKeyboardButton("CONTINUE ➡️", callback_data="next_screen"))
        else: 
            nav_row.append(InlineKeyboardButton("🔒 Finish Selection Profile", callback_data="locked"))
    if nav_row: 
        keyboard.append(nav_row)

    try:
        if query: await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")
        else: await context.bot.send_message(chat_id, text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")
    except Exception: pass

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    context.user_data[user_id] = UserSession()
    text = "🧠 <b>Welcome to Coach Avni's Complete Assessment Node.</b>\nPress initialization below to map out your full onboarding profile."
    keyboard = [[InlineKeyboardButton("⚡ INITIATE SYSTEM", callback_data="start")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    session = context.user_data.get(user_id)
    if not session: return await query.answer("System reset. Tap /start.", show_alert=True)
    
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
        await query.answer("💾 Compiling Complete Onboarding PDF...", show_alert=True)
        session.is_submitted = True
        await render_screen(update, context, query)
        
        pdf_file = generate_onboarding_pdf(session)
        await context.bot.send_document(
            chat_id=query.message.chat_id,
            document=pdf_file,
            filename=f"Coach_Avni_{session.name.replace(' ', '_')}_Onboarding_Profile.pdf",
            caption="📄 <b>Your Complete Strategic Profile Report</b>",
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
        session.answers["q61"] = "Bypassed / Not Provided"
        session.current_screen_idx += 1
        await render_screen(update, context, query)
        return

    if data.startswith("c_"):
        field_id = REV_MAP[data.split("_")[1]]
        session.awaiting_custom_field_id = field_id
        await query.answer("⌨️ Type your response inside the message bar.")
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
    session.answers["q61"] = "Visual Biometric Profiles Uploaded and Logged ✅"
    session.current_screen_idx += 1
    await render_screen(update, context, chat_id=update.message.chat_id)

def main():
    print("🚀 COACH AVNI SYNCED ENGINE ACTIVE & POLLING LIVE")
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL, media_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    
    app.run_polling()

if __name__ == "__main__":
    main()
