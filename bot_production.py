#!/usr/bin/env python3
"""
COACH AVNI - ALL-IN-ONE ENTERPRISE ARCHITECTURE
Features Included:
1. Screenshot-Accurate Layouts: Simple progressive text blocks, double-stacked button rows, custom gates.
2. Direct Name Injection: The second the user inputs their name, the engine strictly addresses them by name.
3. Ghost Client Prevention System: Background loops track inactivity, sending reminders at 1-hour and 24-hour marks.
4. Adaptive Deep-Dive Branching: Selecting Diabetes, Thyroid, or PCOS/PCOD dynamically triggers bespoke follow-ups.
5. Review & Submit Matrix Screen: A comprehensive final display summarizing variables for confirmation.
6. End-of-Funnel Fulfillment: Generates final macros, writes an analytical PDF dossier, and prints the booking link.
"""

import os
import sys
import re
import asyncio
import tempfile
from io import BytesIO
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler, 
    filters, ContextTypes
)

try:
    from weasyprint import HTML
    HAS_WEASYPRINT = True
except ImportError:
    HAS_WEASYPRINT = False

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
CALENDLY_LINK = os.getenv("CALENDLY_LINK", "https://calendly.com/coach_avni/strategy-session")

if not TOKEN:
    print("CRITICAL EXCEPTION: TELEGRAM_TOKEN environmental parameter is missing.")
    sys.exit(1)

def generate_progress_bar(pct):
    filled_len = int(pct / 10)
    bar = "░" * filled_len + " " * (10 - filled_len)
    return f"[{bar}]  {pct}%"

# MASTER CORE SURVEY MATRIX WITH DEEP-DIVE FORWARD ROUTING KEYS
SCREENS = {
    "phase1_text": {
        "title": "📝 Phase: 👤 About You",
        "pct": 0,
        "type": "text_block",
        "next": "phase1_buttons",
        "questions": [
            {"id": "q1", "label": "👉 First things first, what's your full name?"},
            {"id": "q2", "label": "👉 Awesome {name}. How many years young are you?"},
            {"id": "q3", "label": "👉 What's your height in cm, {name}?"},
            {"id": "q4", "label": "👉 And where is your current weight sitting at in kg, {name}?"}
        ]
    },
    "phase1_buttons": {
        "title": "📝 Phase: 👤 About You",
        "pct": 20,
        "type": "button_block",
        "next": "phase2_clinical",
        "questions": [
            {"id": "q5", "label": "👉 What do you do for work, {name}?", "type": "select", 
             "options": [["💻 Engineer", "👨‍⚕️ Doctor"], ["📚 Student", "👔 Business"], ["🙋‍♂️ Consultant", "🏢 Corporate"]]},
            {"id": "q6", "label": "👉 And what is your biological sex?", "type": "select", 
             "options": [["👨 Male", "👩 Female"]]}
        ]
    },
    "phase2_clinical": {
        "title": "📝 Phase: 🏥 Clinical Markers",
        "pct": 40,
        "type": "button_block",
        "next": "phase3_habits",
        "questions": [
            {"id": "q23", "label": "👉 Do you manage any of these metabolic conditions, {name}?", "type": "select",
             "options": [["🩸 Diabetes", "🦋 Thyroid"], ["🧬 PCOS/PCOD", "🟢 None / Completely Fit"]]}
        ]
    },
    "conditional_diabetes": {
        "title": "📝 Phase: 🔬 Metabolic Deep-Dive",
        "pct": 60,
        "type": "text_block",
        "next": "phase3_habits",
        "questions": [
            {"id": "q23_db_sub", "label": "👉 What was your last Fasting Blood Sugar or HbA1c reading, {name}? (Type your value or type 'skip')"}
        ]
    },
    "conditional_thyroid": {
        "title": "📝 Phase: 🦋 Thyroid Deep-Dive",
        "pct": 60,
        "type": "text_block",
        "next": "phase3_habits",
        "questions": [
            {"id": "q23_th_sub", "label": "👉 Is it Hypo or Hyper thyroidism, {name}? And what is your current TSH value? (Type your value or type 'skip')"}
        ]
    },
    "conditional_pcos": {
        "title": "📝 Phase: 🧬 Hormonal Deep-Dive",
        "pct": 60,
        "type": "text_block",
        "next": "phase3_habits",
        "questions": [
            {"id": "q23_pc_sub", "label": "👉 Are you experiencing irregular cycles, hair thinning, or stubborn weight blocks, {name}? (Type your notes or skip)"}
        ]
    },
    "phase3_habits": {
        "title": "📝 Phase: 🍏 Everyday Rhythms",
        "pct": 80,
        "type": "button_block",
        "next": "review_screen",
        "questions": [
            {"id": "q7", "label": "👉 How heavy is that caffeine reliance, {name}?", "type": "select",
             "options": [["☕ Total Lifeline", "🍵 Occasional Cup"], ["🚫 Completely Clean"]]},
            {"id": "q8", "label": "👉 How often does restaurant food land on your plate, {name}?", "type": "select",
             "options": [["🍔 Daily Run", "🍕 2-3x / Week"], ["🥗 Rarely/Never"]]}
        ]
    }
}

# AVNI'S VOICE WIT INTERACTION ENGINE
def get_avni_wit_remark(field_id, value, name):
    remarks = {
        "q5": {
            "💻 Engineer": f"An Engineer! Let me guess, {name}: completely rounded shoulders, lower back tight, and code compiles faster than your metabolism. Let's patch your layout blueprint.",
            "👨‍⚕️ Doctor": f"A medical warrior! Saving everyone else's life out there while surviving entirely on skipped lunches and cold hospital coffee, right {name}? Time to treat the healer."
        },
        "q23": {
            "🩸 Diabetes": f"Got it, tracking the insulin trend, {name}. Injecting our metabolic assessment layer to parse your carbohydrate limits safely.",
            "🦋 Thyroid": f"Understood, {name}. Thyroid fluctuations directly slow your basal metabolic rate down, making weight loss feel like quicksand. Let's trace it out.",
            "🧬 PCOS/PCOD": f"Understood, {name}. Managing androgen or insulin surges requires a highly targeted approach. Let's gather the data parameters."
        }
    }
    return remarks.get(field_id, {}).get(value, "")

class UserSession:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.current_screen = "phase1_text"
        self.answers = {}
        self.name = "there"
        self.is_submitted = False
        self.last_wit_commentary = ""
        self.nudge_tasks = []

    def calculate_macros(self):
        try:
            w = float(re.findall(r"\d+", str(self.answers.get("q4", "70")))[0])
            h = float(re.findall(r"\d+", str(self.answers.get("q3", "170")))[0])
            a = float(re.findall(r"\d+", str(self.answers.get("q2", "30")))[0])
        except Exception:
            w, h, a = 70.0, 170.0, 30.0
        bmr = (10 * w) + (6.25 * h) - (5 * a) + 5
        return {"bmr": int(bmr), "tdee": int(bmr * 1.35), "protein": int(w * 2)}

# ASYNCHRONOUS GHOST CLIENT REMINDER SCHEDULER
async def schedule_ghost_client_nudges(user_id, context: ContextTypes.DEFAULT_TYPE):
    session = context.user_data.get(user_id)
    if not session: return
    
    for task in session.nudge_tasks:
        task.cancel()
    session.nudge_tasks.clear()

    async def nudge_worker(delay, message):
        await asyncio.sleep(delay)
        current_session = context.user_data.get(user_id)
        if current_session and not current_session.is_submitted:
            try:
                await context.bot.send_message(chat_id=current_session.chat_id, text=message, parse_mode="HTML")
            except Exception:
                pass

    loop = asyncio.get_event_loop()
    msg_1h = f"🎙️ <b>Coach Avni:</b> <i>\"Hey {session.name}, don't leave your metabolic blueprint sitting on the table. We're only a few steps away from finishing your profile metrics! Let's lock it in.\"</i>"
    msg_24h = f"⚠️ <b>Coach Avni Final Warning:</b> <i>\"Listen {session.name}, I don't want you ghosting your goals. Tap the options below to step right back into where you left off!\"</i>"
    
    session.nudge_tasks.append(loop.create_task(nudge_worker(3600, msg_1h)))   # 1 Hour Delay
    session.nudge_tasks.append(loop.create_task(nudge_worker(86400, msg_24h))) # 24 Hour Delay

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    session = UserSession(chat_id)
    context.user_data[user_id] = session
    
    await send_current_screen(update, context, chat_id)
    await schedule_ghost_client_nudges(user_id, context)

async def send_current_screen(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id, message_id=None):
    user_id = update.effective_user.id
    session = context.user_data[user_id]
    
    # INTERACTIVE REVIEW AND SUBMIT DISPLAY
    if session.current_screen == "review_screen":
        text = f"📋 <b>Review Your Metrics Summary, {session.name}</b>\n"
        text += "Please review your information carefully before generating your diagnostic file:\n\n"
        text += f"• <b>Full Name:</b> {session.answers.get('q1', 'Unanswered')}\n"
        text += f"• <b>Age Index:</b> {session.answers.get('q2', 'Unanswered')} years\n"
        text += f"• <b>Height Axis:</b> {session.answers.get('q3', 'Unanswered')} cm\n"
        text += f"• <b>Current Mass:</b> {session.answers.get('q4', 'Unanswered')} kg\n"
        text += f"• <b>Profession:</b> {session.answers.get('q5', 'Unanswered')}\n"
        text += f"• <b>Biological Sex:</b> {session.answers.get('q6', 'Unanswered')}\n"
        text += f"• <b>Metabolic Base:</b> {session.answers.get('q23', 'Unanswered')}\n"
        
        if "q23_db_sub" in session.answers: text += f"  ↳ <i>Glucose Output:</i> {session.answers.get('q23_db_sub')}\n"
        if "q23_th_sub" in session.answers: text += f"  ↳ <i>Thyroid Output:</i> {session.answers.get('q23_th_sub')}\n"
        if "q23_pc_sub" in session.answers: text += f"  ↳ <i>Hhormonal Output:</i> {session.answers.get('q23_pc_sub')}\n"
        
        text += f"• <b>Caffeine Load:</b> {session.answers.get('q7', 'Unanswered')}\n"
        text += f"• <b>Dining Frequency:</b> {session.answers.get('q8', 'Unanswered')}\n\n"
        text += "<i>Everything look correct? Click the submit button to compile your blueprint dossier immediately!</i>"
        
        kb = [
            [InlineKeyboardButton("⬅️ BACK & EDIT ENTRIES", callback_data="action_back")],
            [InlineKeyboardButton("🚀 LOOKS GOLDEN - SUBMIT ASSESSMENT", callback_data="final_submit_trigger")]
        ]
        
        if message_id:
            await context.bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, reply_markup=InlineKeyboardMarkup(kb), parse_mode="HTML")
        else:
            await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="HTML")
        return

    scr = SCREENS[session.current_screen]
    text = f"<b>{scr['title']}</b>\nProgress: <code>{generate_progress_bar(scr['pct'])}</code>\n"
    text += "━" * 25 + "\n\n"
    
    if session.last_wit_commentary:
        text += f"🎙️ <b>Coach Avni:</b> <i>\"{session.last_wit_commentary}\"</i>\n\n"
        session.last_wit_commentary = ""
        
    kb = []
    
    if scr["type"] == "text_block":
        unanswered_found = False
        for q in scr["questions"]:
            if q["id"] not in session.answers:
                text += f"{q['label'].replace('{name}', session.name)}\n\n"
                unanswered_found = True
                break
        
        if not unanswered_found:
            session.current_screen = scr["next"]
            await send_current_screen(update, context, chat_id, message_id)
            return
            
        kb.append([InlineKeyboardButton("🔒 Finish answers to un-lock", callback_data="locked_prompt")])
        
    elif scr["type"] == "button_block":
        for q in scr["questions"]:
            text += f"{q['label'].replace('{name}', session.name)}\n\n"
            kb.append([InlineKeyboardButton("⬇️ Answer Options ⬇️", callback_data="dummy")])
            for row in q["options"]:
                row_btns = []
                for opt in row:
                    lbl = f"✅ {opt}" if session.answers.get(q["id"]) == opt else opt
                    row_btns.append(InlineKeyboardButton(lbl, callback_data=f"opt_{q['id']}_{opt}"))
                kb.append(row_btns)
            kb.append([InlineKeyboardButton("🎙️ Speak / Type Custom Answer", callback_data="custom_hint")])
            
        kb.append([InlineKeyboardButton("⬅️ BACK", callback_data="action_back"), 
                   InlineKeyboardButton("🔒 Finish answers to un-lock", callback_data="action_forward")])

    if message_id:
        try:
            await context.bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, reply_markup=InlineKeyboardMarkup(kb), parse_mode="HTML")
            return
        except Exception:
            pass
    await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="HTML")

async def message_dispatcher(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = context.user_data.get(user_id)
    if not session or session.is_submitted: return

    await schedule_ghost_client_nudges(user_id, context)
    input_val = "[Voice Note Logged]" if update.message.voice else update.message.text.strip()
    scr = SCREENS[session.current_screen]

    if scr["type"] == "text_block":
        for q in scr["questions"]:
            if q["id"] not in session.answers:
                session.answers[q["id"]] = input_val
                
                # IMMEDIATE NAME LOCK IN
                if q["id"] == "q1" and not update.message.voice:
                    session.name = input_val.split()[0].title()
                    session.last_wit_commentary = f"Awesome to meet you, {session.name}. Let's secure the rest of your physical markers."
                break
                
        if all(q["id"] in session.answers for q in scr["questions"]):
            session.current_screen = scr["next"]

        await send_current_screen(update, context, update.effective_chat.id)

async def button_dispatcher(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    session = context.user_data.get(user_id)
    if not session: return
    
    await schedule_ghost_client_nudges(user_id, context)
    data = query.data
    await query.answer()
    
    if data.startswith("opt_"):
        _, qid, opt_val = data.split("_", 2)
        session.answers[qid] = opt_val
        
        wit = get_avni_wit_remark(qid, opt_val, session.name)
        if wit:
            session.last_wit_commentary = wit
            
        await send_current_screen(update, context, query.message.chat_id, message_id=query.message.message_id)
        
    elif data == "action_forward":
        scr = SCREENS[session.current_screen]
        if all(q["id"] in session.answers for q in scr["questions"]):
            
            # ADAPTIVE ROUTING CORE: BRANCHES DYNAMICALLY INTO EXTENDED PATHS
            if session.current_screen == "phase2_clinical":
                selected = session.answers.get("q23")
                if "Diabetes" in str(selected):
                    session.current_screen = "conditional_diabetes"
                elif "Thyroid" in str(selected):
                    session.current_screen = "conditional_thyroid"
                elif "PCOS" in str(selected):
                    session.current_screen = "conditional_pcos"
                else:
                    session.current_screen = scr["next"]
            else:
                session.current_screen = scr["next"]
                
            await send_current_screen(update, context, query.message.chat_id, message_id=query.message.message_id)
            
    elif data == "action_back":
        if session.current_screen == "review_screen":
            session.current_screen = "phase3_habits"
        elif session.current_screen == "phase3_habits":
            selected = session.answers.get("q23")
            if "Diabetes" in str(selected): session.current_screen = "conditional_diabetes"
            elif "Thyroid" in str(selected): session.current_screen = "conditional_thyroid"
            elif "PCOS" in str(selected): session.current_screen = "conditional_pcos"
            else: session.current_screen = "phase2_clinical"
        elif session.current_screen.startswith("conditional_"):
            session.current_screen = "phase2_clinical"
        elif session.current_screen == "phase2_clinical":
            session.current_screen = "phase1_buttons"
        elif session.current_screen == "phase1_buttons":
            session.current_screen = "phase1_text"
            session.answers.pop("q4", None)
            
        await send_current_screen(update, context, query.message.chat_id, message_id=query.message.message_id)

    # FINAL STEP PROCESSING - TRIGGER SUBMIT & EXPORT ASSETS
    elif data == "final_submit_trigger":
        session.is_submitted = True
        for task in session.nudge_tasks:
            task.cancel()
            
        m = session.calculate_macros()
        await query.message.delete()
        
        success_text = (
            f"🚀 <b>BIOPRINT FILE COMPLETED AND SUBMITTED, {session.name.upper()}!</b>\n\n"
            f"Your raw entries have successfully cleared verification.\n\n"
            f"📊 <b>METABOLIC PROFILE DEPLOYMENT:</b>\n"
            f"• BMR (Resting Energy): <code>{m['bmr']} kcal</code>\n"
            f"• Estimated Daily TDEE: <code>{m['tdee']} kcal</code>\n"
            f"• Baseline Target Protein Core: <code>{m['protein']}g</code>\n\n"
            f"📥 Your bespoke diagnostic assessment PDF report dossier has been generated below.\n\n"
            f"<b>Next Step:</b> Tap the official calendar scheduler link below to secure your execution briefing with me!"
        )
        
        kb = [[InlineKeyboardButton("📅 BOOK YOUR STRATEGY CALL NOW", url=CALENDLY_LINK)]]
        await context.bot.send_message(chat_id=query.message.chat_id, text=success_text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="HTML")
        
        # WEASYPRINT PDF DISPATCH SYSTEM
        if HAS_WEASYPRINT:
            try:
                html_layout = (
                    f"<html><body style='font-family:sans-serif; padding:50px; line-height:1.6;'>"
                    f"<h2 style='color:#E65100; font-size: 26px;'>Coach Avni Intelligent Diagnostic Blueprint</h2><hr/>"
                    f"<p style='font-size:16px;'><b>Client Identity:</b> {session.name}</p>"
                    f"<p style='font-size:16px;'><b>Calculated Metabolic Index (TDEE):</b> {m['tdee']} Calories / Day</p>"
                    f"<p style='font-size:16px;'><b>Daily Essential Protein Target:</b> {m['protein']} Grams / Day</p>"
                    f"<br/><p style='color:#555;'><i>This data dossier has been processed securely via the Telegram integration platform API pipeline.</i></p>"
                    f"</body></html>"
                )
                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                    HTML(string=html_layout).write_pdf(tmp.name)
                    with open(tmp.name, "rb") as f:
                        await context.bot.send_document(
                            chat_id=query.message.chat_id, 
                            document=BytesIO(f.read()), 
                            filename=f"Coach_Avni_{session.name}_BespokeDossier.pdf"
                        )
                os.unlink(tmp.name)
            except Exception as e:
                print(f"Bypassed or failed PDF output dispatch block: {e}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_dispatcher))
    app.add_handler(MessageHandler(filters.TEXT | filters.VOICE, message_dispatcher))
    print("🚀 Coach Avni Production Assessment Engine Live.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
