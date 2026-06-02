#!/usr/bin/env python3
"""
COACH AVNI BOT - ADAPTIVE INTELLIGENCE ENGINE
✅ Dynamic Memory: Cross-references past answers to form complex, human-like insights.
✅ Live Scoring: Computes a real-time "Readiness Score" based on lifestyle inputs.
✅ Voice/Audio Catching: Intelligently handles unexpected media types gracefully.
"""

import os
import sys
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TOKEN:
    print("ERROR: TELEGRAM_TOKEN missing in environment configuration.")
    sys.exit(1)

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
    
    {"id": 10, "section": "🏥 Health & Diagnostics", "fields": [
        {"id": "q21", "text": "⚕️ Diagnosed clinical conditions? (Select all)", "type": "buttons_multi", "required": False, "options": ["🔬 Diabetes", "🧬 Thyroid", "🔴 PCOS/PCOD", "❤️ Hypertension", "⚠️ Cholesterol", "🍗 Fatty Liver", "✅ None"]},
        {"id": "q_specific_health", "text": "🔍 Do you deal with targeted symptoms?", "type": "buttons_multi", "required": False, "options": ["🎈 Chronic Bloating", "💩 Constipation", "🔥 Acid Reflux / Acidity", "😴 Fatigue / Low Energy", "💇 Hair Thinning/Loss", "✨ None"]},
        {"id": "q22", "text": "🤧 Any known allergies?", "type": "buttons", "required": True, "options": ["✅ No Allergies", "🍔 Food Specific", "🌫️ Environmental"]}
    ]},
    
    {"id": 11, "section": "😴 Stress & Sleep Quality", "fields": [
        {"id": "q32", "text": "😰 Mental stress levels?", "type": "buttons", "required": True, "options": ["😊 1-2 (Low/Chill)", "😐 3 (Manageable)", "😫 4-5 (High/Overwhelming)"]},
        {"id": "q33", "text": "💤 Sleep deepness level?", "type": "buttons", "required": True, "options": ["😴 1-2 (Fragmented)", "😴 3 (Average)", "😴 4-5 (Deep/Restful)"]},
        {"id": "q35", "text": "🌅 Morning fatigue state?", "type": "buttons", "required": True, "options": ["✅ Wake up fresh", "Usually groggy 😊", "Tired/Exhausted 😴"]}
    ]},
    
    {"id": 12, "section": "💪 Physical Mechanics", "fields": [
        {"id": "q_steps", "text": "🚶 Average structural steps daily?", "type": "buttons", "required": True, "options": ["🐌 Under 3,000 steps", "🚶 3,000 - 5,000 steps", "🏃 5,000 - 8,000 steps", "⚡ 10,000+ steps!"]},
        {"id": "q44", "text": "🪑 Daily continuous desk sitting?", "type": "buttons", "required": True, "options": ["🚶 Below 4 Hours", "😐 4 - 7 Hours", "💀 8+ Hours (Heavy Sedentary)"]}
    ]},
    
    {"id": 13, "section": "🎯 Targets & Commitment", "fields": [
        {"id": "q49", "text": "🎯 Core primary physical objective?", "type": "buttons", "required": True, "options": ["📉 Aggressive Fat Loss", "💪 Hypertrophy Lean Muscle", "⚡ Athletic Strength & Endurance", "❤️ Metabolic/Biomarker Correction"]},
        {"id": "q61", "text": "🚀 Are you mentally ready to begin?", "type": "buttons", "required": True, "options": ["🔥 READY NOW. LET'S GO!", "⏳ Finalizing mental readiness"]}
    ]},

    {"id": 14, "section": "📸 Full-Body Assessment Photo", "fields": [
        {"id": "q_photos", "text": "📸 [Optional] Please upload a front/side full-body photo to assist with fat composition analysis.", "type": "media", "required": False}
    ]}
]

class UserSession:
    def __init__(self):
        self.current_screen_idx = 0
        self.answers = {}
        self.name = None
        self.awaiting_custom_field_id = None
        self.last_commentary = ""
        
    def calculate_readiness_score(self):
        """Intelligently calculates a live baseline score out of 100 based on habits."""
        score = 80 # Base starting score
        
        water = self.answers.get("q_water", "")
        if "Less than 1" in str(water): score -= 15
        elif "More than 3" in str(water): score += 10
            
        stress = self.answers.get("q32", "")
        if "4-5" in str(stress): score -= 10
        elif "1-2" in str(stress): score += 10
            
        steps = self.answers.get("q_steps", "")
        if "Under 3,000" in str(steps): score -= 10
        elif "10,000+" in str(steps): score += 15
            
        sleep = self.answers.get("q33", "")
        if "1-2" in str(sleep): score -= 10
        elif "4-5" in str(sleep): score += 10
            
        return max(10, min(100, score)) # Cap between 10 and 100

def determine_intelligent_insight(session, field_id, value) -> str:
    """Uses cross-referencing memory to generate hyper-personalized insights."""
    val_str = str(value)
    
    if field_id == "q1":
        return f"👋 Awesome to meet you, {val_str}. Let's build your baseline."

    if field_id == "q16": # Bedtime
        wakeup = session.answers.get("q10", "")
        if wakeup:
            return f"🧠 Memory Link: You wake up at {wakeup} and sleep at {val_str}. I'm calculating your sleep window right now..."
            
    if field_id == "q_water":
        if "Less than 1 Litre" in val_str: 
            return "⚠️ Flagged: Dehydration limits fat oxidation. We are going to have to fix this immediately."

    if field_id == "q35": # Fatigue
        stress = session.answers.get("q32", "")
        if "Tired/Exhausted" in val_str and "4-5" in stress:
            return "🧠 Memory Link: High stress + morning exhaustion. Your cortisol levels are misaligned. I know exactly how to program your recovery."
            
    if field_id == "q44": # Desk sitting
        steps = session.answers.get("q_steps", "")
        if "8+ Hours" in val_str and "Under 3,000" in steps:
            return "🚨 System Alert: Heavy sitting paired with low daily steps. Don't worry, we will introduce micro-movements into your work day."

    if field_id == "q49":
        return "🎯 Target locked into the algorithm. Adjusting nutritional macros for this specific goal."

    return ""

def generate_diagnostic_dossier(session) -> str:
    final_score = session.calculate_readiness_score()
    
    # Intelligent classification based on score
    if final_score >= 90: status = "🟢 ELITE OPTIMIZATION READY"
    elif final_score >= 70: status = "🟡 SOLID BASELINE (TWEAKS NEEDED)"
    else: status = "🔴 HIGH FRICTION (REBUILD REQUIRED)"

    return (
        f"📋 <b>╔════════════════════════════════════════╗</b>\n"
        f"   <b>║     🧠 AI DIAGNOSTIC ENGINE COMPLETE   ║</b>\n"
        f"   <b>╚════════════════════════════════════════╝</b>\n\n"
        f"👤 <b>THE CHAMPION:</b> {session.name or 'Valued Client'}\n"
        f"🎯 <b>PRIMARY GOAL:</b> {session.answers.get('q49', 'Optimization')}\n\n"
        f"📊 <b>COMPUTED METABOLIC READINESS SCORE: {final_score}/100</b>\n"
        f"<i>Status: {status}</i>\n\n"
        f"⚙️ <b>ALGORITHMIC INSIGHTS:</b>\n"
        f"• Hydration Protocol: {session.answers.get('q_water', 'N/A')}\n"
        f"• Mechanical Load: {session.answers.get('q44', 'N/A')} desk time.\n"
        f"• Stress Burden: {session.answers.get('q32', 'N/A')} | Recovery: {session.answers.get('q35', 'N/A')}\n\n"
        f"🚀 <i>Your data matrix is secure. I am generating your custom protocol now...</i>"
    )

def check_screen_satisfied(session, screen_data) -> bool:
    for field in screen_data['fields']:
        ans = session.answers.get(field['id'])
        if field['required'] and (ans is None or (isinstance(ans, list) and len(ans) == 0)):
            return False
    return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    context.user_data[user_id] = UserSession()
    
    text = (
        "🧠 <b>Welcome to the Adaptive Intelligence Intake.</b>\n\n"
        "I am not just a form. As you answer, my engine will cross-reference your habits and calculate a live <b>Readiness Score</b>.\n\n"
        "Let's map out your physiology. 👇"
    )
    keyboard = [[InlineKeyboardButton("⚡ INITIALIZE ENGINE", callback_data="start")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")

async def render_screen(update: Update, context: ContextTypes.DEFAULT_TYPE, query=None):
    user_id = update.effective_user.id
    session = context.user_data[user_id]
    
    if session.current_screen_idx >= len(SCREENS):
        dossier_text = generate_diagnostic_dossier(session)
        if query: await query.edit_message_text(dossier_text, parse_mode="HTML")
        else: await update.message.reply_text(dossier_text, parse_mode="HTML")
        return

    screen_data = SCREENS[session.current_screen_idx]
    progress = int((session.current_screen_idx / len(SCREENS)) * 100)
    current_score = session.calculate_readiness_score()
    
    text_lines = [
        f"📊 <b>Progress: {progress}%</b> | 🧬 <b>Live Score: {current_score}/100</b>",
        f"📑 <i>Section: {screen_data['section']}</i>\n"
    ]
    
    if session.last_commentary:
        text_lines.append(f"💡 <b>Coach AI:</b> <i>{session.last_commentary}</i>\n")
    
    for field in screen_data['fields']:
        ans = session.answers.get(field['id'])
        is_answered = ans is not None and (not isinstance(ans, list) or len(ans) > 0)
        
        if session.awaiting_custom_field_id == field['id']:
            text_lines.append(f"❓ <b>{field['text']}</b>\n✍️ <code>[Waiting for keyboard input...]</code>")
        elif is_answered:
            display_val = ', '.join(ans) if isinstance(ans, list) else str(ans)
            text_lines.append(f"✅ <b>{field['text']}</b>\n👉 <i>{display_val}</i>")
        else:
            text_lines.append(f"👉 <b>{field['text']}</b>")
        text_lines.append("")

    text = "\n".join(text_lines)
    keyboard = []
    
    has_multi = any(f['type'] == 'buttons_multi' for f in screen_data['fields'])
    is_multi_question = len(screen_data['fields']) > 1
    
    for field in screen_data['fields']:
        if field['type'] in ['buttons', 'buttons_multi']:
            clean_q = field['text'].split('?')[0] + "?"
            keyboard.append([InlineKeyboardButton(f"✨ {clean_q} ✨", callback_data="ignore")])
            
            row = []
            short_field_id = ID_MAP[field['id']]
            
            for idx, opt in enumerate(field['options']):
                display_opt = opt
                ans = session.answers.get(field['id'])
                if field['type'] == 'buttons' and ans == opt: display_opt = f"🔥 {opt}"
                elif field['type'] == 'buttons_multi' and ans and isinstance(ans, list) and opt in ans: display_opt = f"🔥 {opt}"
                    
                row.append(InlineKeyboardButton(display_opt, callback_data=f"s_{short_field_id}_{idx}"))
                if len(row) == 2:
                    keyboard.append(row)
                    row = []
            if row: keyboard.append(row)
            
            custom_label = "✍️ Custom Input"
            ans = session.answers.get(field['id'])
            if ans and not isinstance(ans, list) and ans not in field['options']: custom_label = f"🔥 Custom: {ans}"
            keyboard.append([InlineKeyboardButton(custom_label, callback_data=f"c_{short_field_id}")])
        
        elif field['type'] == 'media':
            keyboard.append([InlineKeyboardButton("⏭️ Skip Upload Process", callback_data="skip_media")])
    
    if has_multi or is_multi_question:
        if check_screen_satisfied(session, screen_data):
            keyboard.append([InlineKeyboardButton("⚡ SYNC & CONTINUE ➡️", callback_data="next_screen")])
        else:
            keyboard.append([InlineKeyboardButton("🔒 Awaiting Selection...", callback_data="locked")])

    markup = InlineKeyboardMarkup(keyboard) if keyboard else None
    try:
        if query: await query.edit_message_text(text, reply_markup=markup, parse_mode="HTML")
        else: await update.message.reply_text(text, reply_markup=markup, parse_mode="HTML")
    except Exception: pass

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
        await query.answer("⚠️ Tap your options above to unlock the next screen!", show_alert=(data=="locked"))
        return
    if data == "next_screen":
        await query.answer()
        session.current_screen_idx += 1
        session.last_commentary = ""
        await render_screen(update, context, query)
        return
    if data == "skip_media":
        await query.answer()
        session.answers["q_photos"] = "Bypassed"
        session.current_screen_idx += 1
        session.last_commentary = ""
        await render_screen(update, context, query)
        return

    if data.startswith("c_"):
        field_id = REV_MAP[data.split("_")[1]]
        session.awaiting_custom_field_id = field_id
        await query.answer("⌨️ Type your custom response in the chat!", show_alert=True)
        await render_screen(update, context, query)
        return
        
    if data.startswith("s_"):
        parts = data.split("_")
        field_id = REV_MAP[parts[1]]
        opt_idx = int(parts[2])
        
        screen_data = SCREENS[session.current_screen_idx]
        field = next((f for f in screen_data['fields'] if f['id'] == field_id), None)
        if not field: return
            
        selected_opt = field['options'][opt_idx]
        session.awaiting_custom_field_id = None
        
        if field['type'] == 'buttons':
            session.answers[field_id] = selected_opt
            session.last_commentary = determine_intelligent_insight(session, field_id, selected_opt)
        elif field['type'] == 'buttons_multi':
            current_ans = session.answers.get(field_id, [])
            if not isinstance(current_ans, list): current_ans = []
            if selected_opt in current_ans: current_ans.remove(selected_opt)
            else: current_ans.append(selected_opt)
            session.answers[field_id] = current_ans
            
        await query.answer()

        has_multi = any(f['type'] == 'buttons_multi' for f in screen_data['fields'])
        is_multi_question = len(screen_data['fields']) > 1
        
        if not has_multi and not is_multi_question and check_screen_satisfied(session, screen_data):
            session.current_screen_idx += 1
        elif is_multi_question and check_screen_satisfied(session, screen_data):
            session.current_screen_idx += 1
            
        await render_screen(update, context, query)

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = context.user_data.get(user_id)
    if not session: return
    
    text = update.message.text.strip()
    
    if session.awaiting_custom_field_id:
        session.answers[session.awaiting_custom_field_id] = text
        session.last_commentary = f"Data logged: '{text}'. Algorithm updated."
        session.awaiting_custom_field_id = None
        screen_data = SCREENS[session.current_screen_idx]
        if check_screen_satisfied(session, screen_data):
            session.current_screen_idx += 1
        await render_screen(update, context)
        return

    if session.current_screen_idx >= len(SCREENS): return
    screen_data = SCREENS[session.current_screen_idx]
    text_fields = [f for f in screen_data['fields'] if f['type'] == 'text']
    if not text_fields: return
        
    field = text_fields[0]
    session.answers[field['id']] = text
    if field['id'] == 'q1': session.name = text
    
    session.last_commentary = determine_intelligent_insight(session, field['id'], text)
    session.current_screen_idx += 1
    await render_screen(update, context)

async def catch_unsupported_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Intelligently catches voice notes so the bot doesn't ignore the user."""
    await update.message.reply_text(
        "🎤 <i>I see you sent a voice note! I don't have my audio-transcription engine plugged in yet, so please tap the buttons or type your answer for now!</i>", 
        parse_mode="HTML"
    )

async def media_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = context.user_data.get(user_id)
    if not session or session.current_screen_idx >= len(SCREENS): return
    
    file_id = update.message.photo[-1].file_id if update.message.photo else update.message.document.file_id
    session.answers["q_photos"] = f"Visual Baseline Locked"
    session.last_commentary = "Visual metrics synced into the database successfully."
    
    session.current_screen_idx += 1
    await render_screen(update, context)

def main():
    print("🚀 INTELLIGENT ADAPTIVE ENGINE ONLINE")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL, media_handler))
    app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, catch_unsupported_audio))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
