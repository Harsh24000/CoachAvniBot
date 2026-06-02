#!/usr/bin/env python3
"""
COACH AVNI BOT - THE PURE ONBOARDING EDITION (FEATURES 2, 3, 4 LOADED)
Features Added:
- Feature 2: Live Dynamic Summaries & Metabolic Risk Indicators during selection.
- Feature 3: Smart PDF Generation Engine via ReportLab (Deploys personalized welcome protocol instantly).
- Feature 4: Calendly Strategy Call CTA integration upon submission.
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

# PDF Generation Libraries
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

# Compressed key translation engine for strict Telegram payload constraints
ID_MAP = {
    "age": "a", "sex": "s", "name": "n", "height": "h", "weight": "w", "profession": "p",
    "diet_type": "dt", "dislikes": "dl", "cuisine": "cs", "tea_coffee": "tc",
    "wake_time": "wt", "bfast_time": "bt", "work_start": "ws", "work_end": "we", 
    "lunch_time": "lt", "dinner_time": "dn", "sleep_time": "st", "snacking": "sn", "water": "wa",
    "outside_food": "of", "alcohol": "al", "smoke": "sm",
    "injuries": "ij", "conditions": "cd", "medications": "md", "digestive": "dg", "allergies": "ag",
    "cravings": "cr", "energy_slumps": "es", "skin_hair": "sh", "immunity": "im",
    "supp_d3": "d3", "supp_b12": "b12", "supp_fishoil": "fo", "supp_multi": "mv",
    "hair_dye": "hd", "brain_fog": "bf", "mood_swings": "ms", "recovery": "rc", "stress": "str", "sleep_depth": "sdp",
    "snoring": "snr", "morning_fatigue": "mf", "dark_circles": "dc", "cramps": "cp", "activity": "act", "steps": "stp",
    "weight_shifts": "wsh", "retention": "rt", "cold_extremities": "ce", "joint_pains": "jp", "breathless": "bl", "sitting_hours": "shh",
    "family_history": "fh", "skin_look": "skl", "appetite": "ap",
    "caloric_tracking": "ct", "primary_objective": "po", "barrier": "br", "energy_consistency": "ec", "exercise_time": "et",
    "soda": "sda", "prescription": "rx", "timeline": "tl", "night_hunger": "nh", "caffeine_cups": "cc", "upcoming_event": "ue",
    "food_preference": "fp", "commitment": "cm", "photos": "ph"
}
REV_MAP = {v: k for k, v in ID_MAP.items()}

# Core 61-Question Layout Struct
SCREENS = [
    {"id": 1, "section": "👤 About You", "fields": [
        {"id": "name", "text": "What is your full name?", "type": "text", "required": True},
        {"id": "age", "text": "What is your current age?", "type": "text", "required": True},
        {"id": "height", "text": "Current height (in cm)?", "type": "text", "required": True},
        {"id": "weight", "text": "Current weight (in kg)?", "type": "text", "required": True}
    ]},
    {"id": 2, "section": "👤 About You", "fields": [
        {"id": "profession", "text": "What is your occupation/profession?", "type": "buttons", "required": True, "options": ["💻 Engineer", "👨‍⚕️ Doctor", "📚 Student", "👔 Business", "🤵 Consultant", "📊 Corporate"]},
        {"id": "sex", "text": "What is your biological sex?", "type": "buttons", "required": True, "options": ["👨 Male", "👩 Female"]}
    ]},
    {"id": 3, "section": "🍏 Diet & Food", "fields": [
        {"id": "diet_type", "text": "Select your core dietary preference (Type)?", "type": "buttons", "required": True, "options": ["🍗 Non-Veg", "🥕 Veg", "🥚 Eggitarian", "🌱 Vegan", "☪️ Jain Vegetarian"]},
        {"id": "dislikes", "text": "Foods you absolutely HATE or avoid? (Multi-select)", "type": "buttons_multi", "required": False, "options": ["🥒 Bitter Gourd", "🍆 Eggplant", "🍄 Mushroom", "🐟 Fish", "🥛 Dairy", "🧅 No Onion/Garlic"]}
    ]},
    {"id": 4, "section": "🍏 Diet & Food", "fields": [
        {"id": "cuisine", "text": "What are your structural Cuisine Preferences?", "type": "buttons", "required": True, "options": ["🍛 North Indian", "🫓 South Indian", "🥗 Continental", "🥢 Asian Mix"]},
        {"id": "tea_coffee", "text": "Do you consume tea or coffee regularly?", "type": "buttons", "required": True, "options": ["☕ Yes, regularly", "🍵 Occasionally", "🚫 Total Abstinence"]}
    ]},
    {"id": 5, "section": "🌅 Your Day", "fields": [
        {"id": "wake_time", "text": "What time do you wake up?", "type": "buttons", "required": True, "options": ["⏰ 5:00 AM", "⏰ 6:00 AM", "⏰ 7:00 AM", "⏰ 8:00 AM+"]},
        {"id": "bfast_time", "text": "What time do you eat breakfast?", "type": "buttons", "required": True, "options": ["🌅 8:00 AM", "🌅 9:00 AM", "🌅 10:00 AM", "⏭️ Skip Breakfast"]},
        {"id": "work_start", "text": "When do you start your work day?", "type": "buttons", "required": True, "options": ["💼 8:00 AM", "💼 9:00 AM", "💼 10:00 AM", "⌛ Shift Rotation"]}
    ]},
    {"id": 6, "section": "🌅 Your Day", "fields": [
        {"id": "work_end", "text": "What time do you finish work?", "type": "buttons", "required": True, "options": ["⏰ 5:00 PM", "⏰ 6:00 PM", "⏰ 7:00 PM", "🌙 9:00 PM+"]},
        {"id": "lunch_time", "text": "What time do you eat lunch?", "type": "buttons", "required": True, "options": ["🍱 12:30 PM", "🍱 1:30 PM", "🍱 2:30 PM", "⏳ Unfixed/Variable"]},
        {"id": "dinner_time", "text": "What time do you eat dinner?", "type": "buttons", "required": True, "options": ["🍽️ 7:00 PM", "🍽️ 8:00 PM", "🍽️ 9:00 PM", "🌙 10:00 PM+"]}
    ]},
    {"id": 7, "section": "🌅 Your Day", "fields": [
        {"id": "sleep_time", "text": "What time do you typically sleep?", "type": "buttons", "required": True, "options": ["🌙 10:00 PM", "🌙 11:00 PM", "🌙 12:00 AM", "🦉 1:00 AM+"]},
        {"id": "snacking", "text": "Frequency of mid-day snacking?", "type": "buttons", "required": True, "options": ["🍪 Constant", "🍏 Occasional", "🚫 No Snacking"]},
        {"id": "water", "text": "Daily water fluid volume tracking?", "type": "buttons", "required": True, "options": ["🥛 < 1 Litre", "💧 1-2 Litres", "🚰 2-3 Litres", "🌊 3+ Litres"]}
    ]},
    {"id": 8, "section": "🌅 Your Day", "fields": [
        {"id": "outside_food", "text": "How often do you consume outside/packaged food?", "type": "buttons", "required": True, "options": ["🍔 Daily", "🍕 2-3x / Week", "🥗 Rarely", "✅ Never"]},
        {"id": "alcohol", "text": "Weekly alcohol intake configurations?", "type": "buttons", "required": True, "options": ["🍺 High Volume", "🍷 Social/Weekend", "🚫 Completely Clean"]},
        {"id": "smoke", "text": "Do you smoke or consume tobacco items?", "type": "buttons", "required": True, "options": ["🚬 Yes, daily", "💨 Socially", "🚫 No"]}
    ]},
    {"id": 9, "section": "🏥 Health", "fields": [
        {"id": "conditions", "text": "Diagnosed clinical issues (Conditions)?", "type": "buttons_multi", "required": False, "options": ["🔬 Diabetes", "🧬 Thyroid", "🔴 PCOS/PCOD", "❤️ Hypertension", "🍗 Fatty Liver", "✅ None"]},
        {"id": "injuries", "text": "Any history of specific physical injuries?", "type": "text", "required": False},
        {"id": "allergies", "text": "Do you present with internal allergies detailed?", "type": "buttons", "required": True, "options": ["✅ None", "🍔 Food Specific", "💊 Pharmaceutical", "🌫️ Environmental"]}
    ]},
    {"id": 10, "section": "🏥 Health", "fields": [
        {"id": "medications", "text": "Are you currently taking any regular prescription medications?", "type": "text", "required": False},
        {"id": "digestive", "text": "Describe your digestion and bowel issues?", "type": "buttons", "required": True, "options": ["🟢 Smooth/Regular", "⚠️ Chronic Bloating", "🛑 Regular Constipation", "🔥 Acid Reflux"]}
    ]},
    {"id": 11, "section": "🏥 Health", "fields": [
        {"id": "cravings", "text": "Do you suffer from frequent sweet or sugar cravings?", "type": "buttons", "required": True, "options": ["🍩 Intense daily", "🍫 Post-meals only", "🚫 Seldom/Never"]},
        {"id": "energy_slumps", "text": "Do you experience regular energy slumps?", "type": "buttons", "required": True, "options": ["🥱 Severe 3 PM crash", "🥱 Constant fatigue", "⚡ Steady performance"]}
    ]},
    {"id": 12, "section": "🏥 Health", "fields": [
        {"id": "skin_hair", "text": "Current skin or hair health tracking status?", "type": "buttons", "required": True, "options": ["⚠️ High hair fall", "⚠️ Acne breaks", "✅ Stable/Optimal"]},
        {"id": "immunity", "text": "Describe your baseline immune defense system?", "type": "buttons", "required": True, "options": ["🤧 Catch colds easily", "💊 Depend on meds", "🛡️ High/Rarely sick"]}
    ]},
    {"id": 13, "section": "💊 Supplements & Habits", "fields": [
        {"id": "supp_d3", "text": "Vitamin D3 Supplementation status?", "type": "buttons", "required": True, "options": ["💊 Daily/Weekly", "🧪 Deficient (No Pill)", "❌ Not Tracking"]},
        {"id": "supp_b12", "text": "Vitamin B12 Supplementation status?", "type": "buttons", "required": True, "options": ["💊 Regular Intake", "🧪 Deficient", "❌ Not Tracking"]},
        {"id": "supp_fishoil", "text": "Omega-3 / Fish Oil Habits?", "type": "buttons", "required": True, "options": ["✅ Yes, daily", "❌ No Intake"]},
        {"id": "supp_multi", "text": "General Multivitamins usage?", "type": "buttons", "required": True, "options": ["✅ Consuming", "❌ No Intake"]}
    ]},
    {"id": 14, "section": "💊 Supplements & Habits", "fields": [
        {"id": "hair_dye", "text": "Do you use hair dye or chemicals often?", "type": "buttons", "required": True, "options": ["💇 Yes, frequently", "🚫 Minimal/Never"]},
        {"id": "brain_fog", "text": "Do you suffer from brain fog or lack of focus?", "type": "buttons", "required": True, "options": ["🧠 Yes, regularly", "😐 Mid-day fatigue", "✅ Clear/Sharp"]},
        {"id": "mood_swings", "text": "Are you prone to mood swings or anxiety?", "type": "buttons", "required": True, "options": ["⚡ Frequent shifts", "🌊 Under high stress", "😊 Balanced/Grounded"]}
    ]},
    {"id": 15, "section": "💊 Supplements & Habits", "fields": [
        {"id": "recovery", "text": "How do you rate your body recovery cycles?", "type": "buttons", "required": True, "options": ["🐌 Wake up tired", "⚡ Fast joint recovery", "🩹 Slow healing/Sore"]},
        {"id": "stress", "text": "Current mental stress levels?", "type": "buttons", "required": True, "options": ["😊 1-2 (Low)", "😐 3 (Manageable)", "😫 4-5 (High)"]},
        {"id": "sleep_depth", "text": "Sleep deepness quality profile?", "type": "buttons", "required": True, "options": [" Fragmented/Wakeful", " Average Depth", " Deep Nightly State"]}
    ]},
    {"id": 16, "section": "🏃 Physical Biomechanics", "fields": [
        {"id": "snoring", "text": "Rate of physical snoring occurrences?", "type": "buttons", "required": True, "options": ["🔊 Yes, heavy snoring", "🔉 Light/Occasional", "🚫 No Snoring"]},
        {"id": "morning_fatigue", "text": "Morning fatigue state status?", "type": "buttons", "required": True, "options": ["✅ Wake up fresh", "Usually groggy 🥱", "Tired/Exhausted 💤"]},
        {"id": "dark_circles", "text": "Do you have dark circles under your eyes?", "type": "buttons", "required": True, "options": ["👁️ Prominent/Dark", "👁️ Faint", "✅ None"]}
    ]},
    {"id": 17, "section": "🏃 Physical Biomechanics", "fields": [
        {"id": "cramps", "text": "Do you experience regular muscle twitching/cramps?", "type": "buttons", "required": True, "options": ["⚡ Frequent cramps", "⚡ Rarely", "🚫 Never"]},
        {"id": "activity", "text": "Current physical activity routine parameters?", "type": "buttons", "required": True, "options": ["🏋️ Heavy lifting 3-5x", "🏃 Cardio/Running", "🧘 Yoga/Walking", "🛋️ Sedentary/None"]},
        {"id": "steps", "text": "Average daily step count logs?", "type": "buttons", "required": True, "options": ["🐌 Under 3,000 steps", "🚶 3,000 - 5,000 steps", "🏃 5,000 - 8,000 steps", "⚡ 10,000+ steps!"]}
    ]},
    {"id": 18, "section": "🏃 Physical Biomechanics", "fields": [
        {"id": "weight_shifts", "text": "Any history of rapid, unexplained weight shifts?", "type": "buttons", "required": True, "options": ["📈 Gained fast lately", "📉 Dropped fast lately", "✅ Steady weight"]},
        {"id": "retention", "text": "Are you prone to continuous water retention/bloating?", "type": "buttons", "required": True, "options": ["💧 Heavy ankles/hands", "💧 Face puffiness", "🚫 No"]},
        {"id": "cold_extremities", "text": "Do you have chronic cold hands or cold feet?", "type": "buttons", "required": True, "options": ["🥶 Yes, constantly", "🥶 Only in winter", "🚫 No"]}
    ]},
    {"id": 19, "section": "🏃 Physical Biomechanics", "fields": [
        {"id": "joint_pains", "text": "Do you suffer from chronic joint or body pains?", "type": "buttons", "required": True, "options": ["💥 Lower back issue", "💥 Knee pain structural", "💥 Neck/Shoulders", "✅ Fully pain-free"]},
        {"id": "breathless", "text": "How quickly do you experience shortness of breath?", "type": "buttons", "required": True, "options": ["🫁 Walking up stairs", "🫁 Only during sprints", "⚡ Strong cardiorespiratory"]},
        {"id": "sitting_hours", "text": "Continuous hours spent sitting at a desk daily?", "type": "buttons", "required": True, "options": ["🚶 Below 4 Hours", "😐 4 - 7 Hours", "💀 8+ Hours"]}
    ]},
    {"id": 20, "section": "🏃 Physical Biomechanics", "fields": [
        {"id": "family_history", "text": "Any history of family lifestyle diseases?", "type": "buttons_multi", "required": False, "options": ["🩸 Diabetes trend", "❤️ Cardiovascular issues", "🧬 Obesity traits", "✅ Clear History"]},
        {"id": "skin_look", "text": "Rate your daily structural skin health look?", "type": "buttons", "required": True, "options": ["🍂 Very dry/flaky", "💧 Excess oily zone", "✨ Well-hydrated/Normal"]},
        {"id": "appetite", "text": "Describe your appetite stability profile?", "type": "buttons", "required": True, "options": ["🔥 Uncontrollable/Bingeing", "🧊 Low appetite/Forget to eat", "✅ Stable patterns"]}
    ]},
    {"id": 21, "section": "🎯 Targets & Objectives", "fields": [
        {"id": "caloric_tracking", "text": "Have you ever tried an official caloric tracking plan before?", "type": "buttons", "required": True, "options": ["📈 Yes, did macros", "📉 Tried and failed", "🚫 Never tracked"]},
        {"id": "primary_objective", "text": "What is your core primary health objective?", "type": "buttons", "required": True, "options": ["📉 Aggressive Fat Loss", "💪 Hypertrophy Lean Muscle", "⚡ Athletic Endurance", "❤️ Metabolic Correction"]},
        {"id": "barrier", "text": "What is your main structural barrier to consistency?", "type": "buttons", "required": True, "options": ["⏳ Extreme time deficit", "🍳 Cooking complexity", "🍿 Social/Travel habits", "🧠 Lack of internal drive"]}
    ]},
    {"id": 22, "section": "🎯 Targets & Objectives", "fields": [
        {"id": "energy_consistency", "text": "Rate your overall daily energy level consistency?", "type": "buttons", "required": True, "options": ["📈 Peak morning/low night", "📉 Flatline low energy", "⚡ High baseline all day"]},
        {"id": "exercise_time", "text": "How much time can you allocate to exercise weekly?", "type": "buttons", "required": True, "options": ["⏳ Under 2 Hours", "⏳ 2 to 4 Hours", "⚡ 5+ Hours fully ready!"]}
    ]},
    {"id": 23, "section": "🎯 Targets & Objectives", "fields": [
        {"id": "soda", "text": "Do you drink soda, carbonated beverages, or energy drinks?", "type": "buttons", "required": True, "options": ["🥤 Yes, almost daily", "🥤 Socially/Weekends", "🚫 Complete clean limit"]},
        {"id": "prescription", "text": "Are you currently taking any prescription medications?", "type": "buttons", "required": True, "options": ["💊 Chronic daily meds", "💊 Occasional use", "🚫 None"]},
        {"id": "timeline", "text": "What is your target timeline to reach this structural milestone?", "type": "buttons", "required": True, "options": ["🔥 4 to 8 Weeks", "⚡ 12 Weeks (Recommended)", "⏳ Long-term shift"]}
    ]},
    {"id": 24, "section": "🎯 Targets & Objectives", "fields": [
        {"id": "night_hunger", "text": "Do you experience regular night-time hunger pangs?", "type": "buttons", "required": True, "options": ["🌙 Heavy midnight raids", "🌙 Light cravings", "🚫 Sleep cleanly through"]},
        {"id": "caffeine_cups", "text": "How many coffee or caffeine cups do you consume daily?", "type": "buttons", "required": True, "options": ["☕ 1-2 Cups", "🚀 3-4 Cups extreme", "🚫 No caffeine logs"]},
        {"id": "upcoming_event", "text": "Are you preparing for an upcoming major event?", "type": "buttons", "required": True, "options": ["🤵 Wedding/Event soon", "🏖️ Vacation target", "🎯 General wellness optimization"]}
    ]},
    {"id": 25, "section": "🎯 Targets & Objectives", "fields": [
        {"id": "food_preference", "text": "Do you prefer home-cooked structures or restaurant prep?", "type": "buttons", "required": True, "options": ["🍳 100% Home Cooked", "🍱 Meal prep service", "🏢 Office cafeteria/Outside"]},
        {"id": "commitment", "text": "Are you mentally ready to commit to this roadmap layout?", "type": "buttons", "required": True, "options": ["🔥 READY RIGHT NOW. LET'S GO!", "⏳ Finalizing mental parameters"]}
    ]},
    {"id": 26, "section": "📸 Biometric Profiles", "fields": [
        {"id": "photos", "text": "Upload front, side, or back body profiles for direct visual composition metrics.", "type": "media", "required": False}
    ]}
]

class UserSession:
    def __init__(self):
        self.current_screen_idx = 0
        self.answers = {}
        self.name = None
        self.awaiting_custom_field_id = None
        self.last_commentary = ""
        self.nudge_job = None
        self.is_submitted = False
        
    def calculate_readiness_score(self):
        score = 80
        wa = str(self.answers.get("water", ""))
        str_val = str(self.answers.get("stress", ""))
        stp = str(self.answers.get("steps", ""))
        sdp = str(self.answers.get("sleep_depth", ""))
        
        if "< 1" in wa: score -= 15
        elif "3+" in wa: score += 10
        if "4-5" in str_val: score -= 15
        if "Under 3,000" in stp: score -= 15
        elif "10,000+" in stp: score += 15
        if "Fragmented" in sdp: score -= 10
        return max(10, min(100, score))

# =========================================================================
# FEATURE 2: LIVE METABOLIC RISK SUMMARIES ENGINE
# =========================================================================
def check_metabolic_indicators(session) -> str:
    indicators = []
    wa = str(session.answers.get("water", ""))
    sth = str(session.answers.get("sitting_hours", ""))
    es = str(session.answers.get("energy_slumps", ""))
    
    if "< 1" in wa:
        indicators.append("🚨 <b>CRITICAL HYDRATION ALERT</b>: Cellular fluid deficit detected.")
    if "8+" in sth:
        indicators.append("🛋️ <b>BIOMECHANICAL RISK</b>: High desk-sitting hours found.")
    if "3 PM crash" in es or "Constant" in es:
        indicators.append("🥱 <b>METABOLIC SLUMP DETECTED</b>: Insulin/glucose management requires focus.")
        
    if not indicators:
        return "✨ <b>Current Biomarkers:</b> Stable performance baselines logged."
    return "\n".join(indicators)

# =========================================================================
# FEATURE 3: REPORTLAB AUTOMATED ONBOARDING PDF GENERATOR
# =========================================================================
def generate_onboarding_pdf(session) -> BytesIO:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Heading1'], fontSize=24, leading=28, textColor=colors.HexColor("#1A365D"), spaceAfter=15
    )
    section_style = ParagraphStyle(
        'SecTitle', parent=styles['Heading2'], fontSize=14, leading=18, textColor=colors.HexColor("#2B6CB0"), spaceBefore=12, spaceAfter=6
    )
    body_style = ParagraphStyle(
        'BodyTextCustom', parent=styles['Normal'], fontSize=10, leading=14, textColor=colors.HexColor("#2D3748")
    )
    
    # PDF Header Elements
    story.append(Paragraph(f"COACH AVNI — OFFICIAL PROTOCOL BRIEF", title_style))
    story.append(Paragraph(f"<b>Client Profile Name:</b> {session.name or 'Valued Client'}", body_style))
    story.append(Paragraph(f"<b>Metabolic Evaluation Baseline Score:</b> {session.calculate_readiness_score()}/100", body_style))
    story.append(Spacer(1, 15))
    
    # Tabulating User Logs 
    data = [["Assessment Metric", "Logged Status Point"]]
    for screen in SCREENS:
        for field in screen['fields']:
            ans = session.answers.get(field['id'])
            if ans:
                val_str = ", ".join(ans) if isinstance(ans, list) else str(ans)
                clean_lbl = field['text'].split('?')[0]
                data.append([Paragraph(clean_lbl, body_style), Paragraph(val_str, body_style)])
                
    t = Table(data, colWidths=[240, 260])
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

# =========================================================================
# SYSTEM CORE RENDER AND BUTTON HANDLERS
# =========================================================================
async def render_screen(update: Update, context: ContextTypes.DEFAULT_TYPE, query=None, chat_id=None):
    user_id = update.effective_user.id
    if not chat_id: chat_id = update.effective_chat.id
    session = context.user_data[user_id]
    
    # PATH A: FINAL SUBMISSION REVIEW MATRIX
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
                review_text += f" • {field['text'].split('?')[0]}: <code>{val_str}</code>\n"
            review_text += "\n"
            
        keyboard = []
        row = []
        for sec in processed_sections:
            row.append(InlineKeyboardButton(f"✏️ {sec.split()[-1]}", callback_data=f"edit_sec_{sec}"))
            if len(row) == 3:
                keyboard.append(row)
                row = []
        if row: keyboard.append(row)
        keyboard.append([InlineKeyboardButton("🚀 LOCK PROFILE & SECURE WELCOME KIT", callback_data="final_submit")])
        
        if query: await query.edit_message_text(review_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")
        else: await context.bot.send_message(chat_id, text=review_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")
        return

    # PATH B: SUCCESS PLATFORM W/ CALENDLY CALL TO ACTION (FEATURE 4)
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

    # PATH C: SCREEN STEPPING CONTROLLER (FEATURE 2 INJECTED HERE)
    screen_data = SCREENS[session.current_screen_idx]
    progress = int((session.current_screen_idx / len(SCREENS)) * 100)
    
    # Calculate live indicators on the fly
    live_risk_bar = check_metabolic_indicators(session)
    
    text = (
        f"⚙️ <b>Evaluation Setup: {progress}% Done</b>\n"
        f"Module: <i>{screen_data['section']}</i>\n"
        f"-----------------------------------------\n"
        f"{live_risk_bar}\n"
        f"-----------------------------------------\n\n"
    )
    
    for field in screen_data['fields']:
        ans = session.answers.get(field['id'])
        if session.awaiting_custom_field_id == field['id']:
            text += f"❓ <b>{field['text']}</b>\n✍️ <code>[Waiting for input context via chat line...]</code>\n\n"
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
        if check_screen_satisfied(session, screen_data): nav_row.append(InlineKeyboardButton("CONTINUE ➡️", callback_data="next_screen"))
        else: nav_row.append(InlineKeyboardButton("🔒 Finish Selection Profile", callback_data="locked"))
    if nav_row: keyboard.append(nav_row)

    try:
        if query: await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")
        else: await context.bot.send_message(chat_id, text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")
    except Exception: pass

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    context.user_data[user_id] = UserSession()
    text = "🧠 <b>Welcome to Coach Avni's High-Feature Onboarding Node.</b>\nPress initialization below to safely map out your data markers."
    keyboard = [[InlineKeyboardButton("⚡ INITIATE ASSESSMENT INTERFACE", callback_data="start")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    session = context.user_data.get(user_id)
    if not session: return await query.answer("System update. Tap /start.", show_alert=True)
    
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
        
    # PROCESS SUBMISSION -> DISPATCH AUTOMATED PDF ATTACHMENT (FEATURE 3)
    if data == "final_submit":
        await query.answer("💾 Compiling Onboarding Document Bundle...", show_alert=True)
        session.is_submitted = True
        
        # Render the template out to chat window
        await render_screen(update, context, query)
        
        # Fire off document transmission asynchronously
        pdf_file = generate_onboarding_pdf(session)
        filename = f"Onboarding_Brief_{session.name or 'Client'}.pdf".replace(" ", "_")
        await context.bot.send_document(
            chat_id=query.message.chat_id,
            document=pdf_file,
            filename=filename,
            caption="📄 <b>Your Generated Onboarding Profile Brief</b>\nThis summary is synced to Coach Avni's management sheet master list.",
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
        session.answers["photos"] = "Ski
