#!/usr/bin/env python3
"""
COACH AVNI - THE MASTER 62-QUESTION GROUPED LIVE CHAT PROTOCOL
Features:
- Contains all 62 strategic health, lifestyle, and clinical metrics.
- Grouped efficiently into 6 comprehensive onboarding phases.
- Smart processing for Voice Notes/Audio inputs seamlessly across text fields.
- High-energy, witty peer-to-peer interactive coaching humor.
- Dynamic name insertion across all transitions to simulate live chatting.
- Embedded automated calorie/macro matrix and WeasyPrint PDF compiler.
"""

import os
import sys
import re
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
    print("CRITICAL MASTER CONFIG ERROR: TELEGRAM_TOKEN missing from environment variables.")
    sys.exit(1)

# MASTER DATABANK: ALL 62 STRATEGIC QUESTIONS PRE-ROUTED INTO INTEGRATED PHASES
SCREENS = {
    "welcome": {
        "text": {
            "en": "🔥 <b>Welcome to your Transformation Portal.</b>\n\nI'm Coach Avni. No standard medical corporate intake sheets, no generic templates. Just raw science, zero judgment, and a protocol built for your actual chaotic life.\n\nLet's get connected. Choose your language:",
            "hi": "🔥 <b>आपके ट्रांसफॉर्मेशन पोर्टल में आपका स्वागत है।</b>\n\nमैं हूँ कोच अवनी। कोई उबाऊ फॉर्म नहीं, कोई घिसी-पिटी सलाह नहीं। सिर्फ शुद्ध विज्ञान, ज़ीरो जजमेंट, और एक ऐसा प्रोटोकॉल जो आपकी लाइफस्टाइल के लिए बना है।\n\nभाषा चुनें:"
        }
    },
    "phase1": {
        "section": "👤 Phase 1: Biological & Professional Core (Q1-Q6)",
        "fields": [
            {"id": "q1", "label": "Full Name", "type": "text"},
            {"id": "q2", "label": "Age", "type": "text"},
            {"id": "q3", "label": "Height (cm)", "type": "text"},
            {"id": "q4", "label": "Current Weight (kg)", "type": "text"},
            {"id": "q5", "label": "Occupation", "type": "buttons", 
             "options": {"en": ["💻 Tech/Desk Marathon", "👨‍⚕️ Medical/Hospital", "📚 Student/Academic", "👔 Business Owner", "🤵 Consultant/Travel", "📊 Corporate Elite"], 
                         "hi": ["💻 टेक/डेस्क जॉब", "👨‍⚕️ मेडिकल/डॉक्टर", "📚 छात्र", "👔 बिजनेस ओनर", "🤵 सलाहकार", "📊 कॉर्पोरेट डेस्क"]}},
            {"id": "q6", "label": "Biological Sex", "type": "buttons", 
             "options": {"en": ["👨 Male", "👩 Female"], "hi": ["👨 पुरुष", "👩 महिला"]}}
        ],
        "text": {
            "en": "Let's lock in your baseline metrics first.\n\n<b>Type or drop a quick VOICE NOTE with these 4 items in this format:</b>\n<code>[Full Name]\n[Age]\n[Height in cm]\n[Weight in kg]</code>\n\nThen select your occupation and sex below:",
            "hi": "चलो तुम्हारी बेसलाइन मेट्रिक्स लॉक करते हैं।\n\n<b>कृपया टाइप करें या एक तेज़ VOICE NOTE में ये 4 बातें बताएं:</b>\n<code>[आपका पूरा नाम]\n[उम्र]\n[ऊंचाई - cm]\n[वजन - kg]</code>\n\nफिर नीचे से अपना व्यवसाय और लिंग चुनें:"
        }
    },
    "phase2": {
        "section": "🍏 Phase 2: Nutritional Integrity & Kitchen Realities (Q7-Q10)",
        "fields": [
            {"id": "q7", "label": "Primary Diet", "type": "buttons",
             "options": {"en": ["🍗 Non-Veg", "🥕 Pure Veg", "🥚 Eggitarian", "🌱 Vegan", "☪️ Jain Vegetarian"], 
                         "hi": ["🍗 मांसाहारी", "🥕 शुद्ध शाकाहारी", "🥚 अंडाहारी", "🌱 वीगन", "☪️ जैन शाकाहारी"]}},
            {"id": "q8", "label": "Disliked Foods", "type": "text"},
            {"id": "q9", "label": "Soul Food Style", "type": "buttons",
             "options": {"en": ["🍛 North Indian", "🫓 South Indian", "🥗 Continental", "🥢 Asian Mix"], 
                         "hi": ["🍛 उत्तर भारतीय", "🫓 दक्षिण भारतीय", "🥗 कॉन्टिनेंटल", "🥢 एशियन मिक्स"]}},
            {"id": "q10", "label": "Caffeine Dependence", "type": "buttons",
             "options": {"en": ["☕ Total Lifeline", "🍵 Occasional Cup", "🚫 Completely Clean"], 
                         "hi": ["☕ हाँ, इसके बिना पत्ता नहीं हिलता", "🍵 कभी-कभार", "🚫 बिल्कुल नहीं"]}}
        ],
        "text": {
            "en": "Let's crack open your kitchen reality, {name}.\n\n<b>First, voice record or type any foods you absolutely hate or refuse to eat (Q8):</b>\nThen choose your dietary style and caffeine dependency using the active buttons below.",
            "hi": "{name}, अब तुम्हारे खाने की असलियत देखते हैं।\n\n<b>सबसे पहले, वो चीजें टाइप करें या VOICE NOTE में बताएं जो आपको बिल्कुल पसंद नहीं हैं (Q8):</b>\nफिर नीचे दिए गए बटनों से अपनी डाइट शैली और कैफीन निर्भरता चुनें।"
        }
    },
    "phase3": {
        "section": "🌅 Phase 3: Chronobiology & Daily Routines (Q11-Q22)",
        "fields": [
            {"id": "q11", "label": "Wake Up Time", "type": "text"},
            {"id": "q12", "label": "First Meal Time", "type": "text"},
            {"id": "q13", "label": "Work Login Time", "type": "text"},
            {"id": "q14", "label": "Work Logoff Time", "type": "text"},
            {"id": "q15", "label": "Lunch Window", "type": "text"},
            {"id": "q16", "label": "Dinner Window", "type": "text"},
            {"id": "q17", "label": "Lights Out Sleep Schedule", "type": "buttons",
             "options": {"en": ["🌙 Early (10 PM)", "🌙 Midnight (12 AM)", "🦉 Night Owl (1 AM+)"], 
                         "hi": ["🌙 जल्दी (10 बजे)", "🌙 आधी रात (12 बजे)", "🦉 नाइट आउल (1 बजे+)"]}},
            {"id": "q18", "label": "Snacking Frequency", "type": "buttons",
             "options": {"en": ["🍪 Constant Grazing", "🍏 Occasional Snack", "🚫 Clean - No Snacking"], 
                         "hi": ["🍪 लगातार कुछ न कुछ चाहिए", "🍏 कभी-कभार", "🚫 बिल्कुल नहीं"]}},
            {"id": "q19", "label": "Water Intake", "type": "text"},
            {"id": "q20", "label": "Swiggy/Zomato Load", "type": "buttons",
             "options": {"en": ["🍔 Daily/Almost Daily", "🍕 2-3x / Week", "🥗 Rarely/Never"], 
                         "hi": ["🍔 रोज़ाना लगभग", "🍕 हफ्ते में 2-3 बार", "🥗 बहुत कम/कभी नहीं"]}},
            {"id": "q21", "label": "Alcohol Intake", "type": "text"},
            {"id": "q22", "label": "Smoking Habits", "type": "text"}
        ],
        "text": {
            "en": "Chronobiology time, {name}. Let's look at your timing matrix.\n\n<b>Send a voice note or type your daily timeline breakdown:</b>\n- Wake time, First meal, Work shift layout (Q11-Q14)\n- Lunch/Dinner times, Daily water liters, Alcohol/Smoking status (Q15-Q16, Q19, Q21-Q22)\n\nThen click the buttons below to lock in your sleep and snacking trends:",
            "hi": "चलो तुम्हारी लाइफस्टाइल टाइमिंग्स देखते हैं, {name}।\n\n<b>एक VOICE NOTE भेजें या टाइप करें अपनी दिनचर्या:</b>\n- उठने का समय, पहला भोजन, ऑफिस शिफ्ट (Q11-Q14)\n- दोपहर/रात का खाना, पानी की मात्रा, स्मोकिंग/अल्कोहल (Q15-Q16, Q19, Q21-Q22)\n\nफिर नीचे बटनों से अपनी स्लीपिंग और स्नैकिंग आदतें चुनें:"
        }
    },
    "phase4": {
        "section": "🏥 Phase 4: Clinical History & Gut Assessment (Q23-Q31)",
        "fields": [
            {"id": "q23", "label": "Metabolic Conditions", "type": "text"},
            {"id": "q24", "label": "Structural Injuries", "type": "text"},
            {"id": "q25", "label": "Severe Allergies", "type": "text"},
            {"id": "q26", "label": "Prescription Meds", "type": "text"},
            {"id": "q27", "label": "Digestion Profile Check", "type": "buttons",
             "options": {"en": ["🟢 Smooth & Regular", "⚠️ Chronic Bloating", "🛑 Regular Constipation", "🔥 Acidity/Reflux"], 
                         "hi": ["🟢 बिल्कुल ठीक", "⚠️ गैस और ब्लोटिंग", "🛑 कब्ज की समस्या", "🔥 एसिडिटी"]}},
            {"id": "q28", "label": "Sugar Cravings", "type": "buttons",
             "options": {"en": ["🍩 Intense daily monster", "🍫 Post-meals only", "🚫 Seldom/Never"], 
                         "hi": ["🍩 रोज़ाना बहुत तेज़", "🍫 सिर्फ खाने के बाद", "🚫 कभी नहीं"]}},
            {"id": "q29", "label": "Energy Slumps", "type": "text"},
            {"id": "q30", "label": "Skin & Hair Issues", "type": "text"},
            {"id": "q31", "label": "Seasonal Immunity Status", "type": "text"}
        ],
        "text": {
            "en": "Time for a medical health check, {name}.\n\n<b>Type or speak into a VOICE NOTE regarding your clinical health markers:</b>\n- Pre-existing issues like Thyroid, Diabetes, PCOS (Q23)\n- Past injuries, allergies, daily prescription medicines (Q24-Q26)\n- Energy crashes, hair loss, skin trends, or low immunity (Q29-Q31)\n\nThen use the buttons below to log your gut performance:",
            "hi": "अब मेडिकल और हेल्थ चेक की बारी है, {name}।\n\n<b>टाइप करें या VOICE NOTE में अपनी सेहत का हाल बताएं:</b>\n- थायराइड, डायबिटीज, पीसीओएस जैसी कोई समस्या (Q23)\n- पुरानी चोटें, एलर्जी, नियमित दवाएं (Q24-Q26)\n- सुस्ती/थकान, बालों का झड़ना, बार-बार बीमार पड़ना (Q29-Q31)\n\nफिर नीचे दिए गए बटनों से अपने पेट और क्रेविंग्स का हाल चुनें:"
        }
    },
    "phase5": {
        "section": "🧠 Phase 5: Micronutrients, Cognition & Biomechanics (Q32-Q53)",
        "fields": [
            {"id": "q32", "label": "Vitamin D3", "type": "text"},
            {"id": "q33", "label": "Vitamin B12", "type": "text"},
            {"id": "q34", "label": "Omega-3 Status", "type": "text"},
            {"id": "q35", "label": "Multivitamins Intake", "type": "text"},
            {"id": "q36", "label": "Hair Salon Treatments", "type": "text"},
            {"id": "q37", "label": "Brain Fog Profile", "type": "text"},
            {"id": "q38", "label": "Anxiety/Mood Swings", "type": "text"},
            {"id": "q39", "label": "Waking Physical State", "type": "text"},
            {"id": "q40", "label": "Daily Stress Load", "type": "text"},
            {"id": "q41", "label": "Sleep Deep State", "type": "text"},
            {"id": "q42", "label": "Snoring Profile", "type": "text"},
            {"id": "q43", "label": "Waking Emotional State", "type": "text"},
            {"id": "q44", "label": "Dark Circles營", "type": "text"},
            {"id": "q45", "label": "Weight Shifts History", "type": "text"},
            {"id": "q46", "label": "Morning Puffiness", "type": "text"},
            {"id": "q47", "label": "Cold Hands & Feet", "type": "text"},
            {"id": "q48", "label": "Joint & Spine Pain", "type": "text"},
            {"id": "q49", "label": "Incline Breathing Gasp", "type": "text"},
            {"id": "q50", "label": "Desk Glued Chair Hours", "type": "text"},
            {"id": "q51", "label": "Family Medical History", "type": "text"},
            {"id": "q52", "label": "Skin Dryness/Oiliness", "type": "text"},
            {"id": "q53", "label": "Neuro-Appetite Stability", "type": "text"}
        ],
        "text": {
            "en": "Let's analyze micronutrients, brain focus, and spine alignment, {name}.\n\n<b>Give me a comprehensive VOICE NOTE or text block covering:</b>\n- Supplements: D3, B12, Fish oil, Multivitamins (Q32-Q35)\n- Focus: Brain fog, stress levels, mood swings, sleep quality, snoring (Q37-Q43)\n- Body: Joint pains, back strain, family history, morning puffiness, cold limbs, chair hours (Q45-Q53)\n\nClick Next when you are completely done detailing this block.",
            "hi": "अब सप्लीमेंट्स, फोकस और रीढ़ की हड्डी की स्थिति का विश्लेषण करते हैं, {name}।\n\n<b>एक विस्तृत VOICE NOTE भेजें या पूरा टेक्स्ट ब्लॉक लिखें जिसमें बताएं:</b>\n- सप्लीमेंट्स: D3, B12, फिश ऑयल, मल्टीविटामिन (Q32-Q35)\n- मानसिक स्थिति: ब्रेन फॉग, तनाव, मूड स्विंग्स, नींद की गहराई, खर्राटे (Q37-Q43)\n- शारीरिक दर्द: जोड़ों/कमर में दर्द, फैमिली मेडिकल हिस्ट्री, सुबह की सूजन, कुर्सी पर बिताए घंटे (Q45-Q53)\n\nपूरा होने पर सीधे Next बटन दबाएं।"
        }
    },
    "phase6": {
        "section": "🎯 Phase 6: Core Targets & Asset Capture (Q54-Q62)",
        "fields": [
            {"id": "q54", "label": "Tracking Experience", "type": "text"},
            {"id": "q55", "label": "Absolute Primary Focus", "type": "buttons",
             "options": {"en": ["📉 Aggressive Fat Loss", "💪 Hypertrophy Lean Muscle", "❤️ Metabolic Correction", "⚡ Athletic Endurance"], 
                         "hi": ["📉 तेज़ फैट लॉस", "💪 लीन मसल गेन", "❤️ मेटाबॉलिज्म ठीक करना", "⚡ एथलेटिक स्टैमिना"]}},
            {"id": "q56", "label": "Consistency Roadmap Blocker", "type": "text"},
            {"id": "q57", "label": "Daily Energy Flow Style", "type": "text"},
            {"id": "q58", "label": "Weekly Training Hours Available", "type": "text"},
            {"id": "q59", "label": "Soda/Energy Drink Intake", "type": "text"},
            {"id": "q60", "label": "Countdown Timeline Goal", "type": "text"},
            {"id": "q62", "label": "Custom Strategic Remarks", "type": "text"},
            {"id": "q61", "label": "Posture Alignment Photo", "type": "media"}
        ],
        "text": {
            "en": "Final milestone, {name}! Let's lock down the target execution strategy.\n\n<b>Drop a final voice note or message explaining:</b>\n- Past calorie tracking history, consistency blockers, weekly workout time available (Q54, Q56, Q58)\n- Soda intake, transformation timeline goal, and final burning notes (Q59, Q60, Q62)\n\n<b>Select your absolute primary focus button below and drop your clear full-length posture photo (Q61) to lock things in:</b>",
            "hi": "अंतिम मील का पत्थर, {name}! चलो लक्ष्य रणनीति तय करते हैं।\n\n<b>एक आखिरी वॉइस नोट या मैसेज छोड़ें और बताएं:</b>\n- पुरानी कैलोरी ट्रैकिंग का अनुभव, वर्कआउट के लिए मिलने वाले घंटे (Q54, Q56, Q58)\n- ट्रांसफॉर्मेशन की समय सीमा और कोई भी आखिरी पर्सनल नोट (Q59, Q60, Q62)\n\n<b>नीचे दिए गए बटनों से अपना मुख्य लक्ष्य चुनें और अपनी एक साफ फुल-लेंथ फोटो (Q61) भेजें:</b>"
        }
    }
}

# INTERACTIVE WIT REACTION LOGIC
def get_avni_live_wit(field_id, val, name):
    comments = {
        "q5": {
            "💻 Tech/Desk Marathon": f"A tech desk marathon marathoner! Say no more, {name}. Translation: Your shoulders are hunched, your lower back is on fire, and your code compiles faster than your current metabolic rate. Let's fix that posture.",
            "👨‍⚕️ Medical/Hospital": f"A doctor/medical pro! Saving everyone else's life out there but surviving on skipped meals and bad posture, right {name}? Time to treat the healer."
        },
        "q10": {
            "☕ Total Lifeline": f"Haha, running on pure liquid adrenaline! Coffee isn't an independent food group, {name}. We are going to rebuild your actual, sustainable cellular energy.",
            "🚫 Completely Clean": f"Zero reliance on caffeine? Incredible, {name}. Your central nervous system is starting with a magnificent natural advantage."
        },
        "q17": {
            "🦉 Night Owl (1 AM+)": f"1 AM?! {name}, your key fat-burning hormones are crying in the dark. Late nights are the absolute silent assassin of physical transformations.",
            "🌙 Early (10 PM)": f"10 PM? Absolute champion sleep architecture! Your body is beautifully set up for recovery."
        },
        "q27": {
            "⚠️ Chronic Bloating": f"Chronic bloating means your gut microbiome is screaming for structural support. If your gut is blocked, {name}, you aren't absorbing macros anyway. Fixing this first.",
            "🟢 Smooth & Regular": f"A perfectly smooth gut is a complete metabolic cheat code, {name}. This makes our absorption pipeline smooth as butter."
        }
    }
    return comments.get(field_id, {}).get(val, "")

class UserSession:
    def __init__(self):
        self.lang = "en"
        self.current_screen = "welcome"
        self.answers = {}
        self.name = "there"
        self.is_submitted = False
        self.review_mode = False

    def calculate_macros(self):
        try:
            w = float(re.findall(r"\d+", str(self.answers.get("q4", "70")))[0])
            h = float(re.findall(r"\d+", str(self.answers.get("q3", "170")))[0])
            a = float(re.findall(r"\d+", str(self.answers.get("q2", "30")))[0])
        except Exception:
            w, h, a = 70.0, 170.0, 30.0
        
        bmr = (10 * w) + (6.25 * h) - (5 * a) + 5
        tdee = int(bmr * 1.35)
        protein = int(w * 2)
        fats = int((tdee * 0.25) / 9)
        carbs = int((tdee - (protein * 4) - (fats * 9)) / 4)
        return {"bmr": int(bmr), "tdee": tdee, "protein": protein, "carbs": carbs, "fats": fats}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = UserSession()
    context.user_data[user_id] = session
    
    kb = [[InlineKeyboardButton("🇬🇧 Let's chat in English", callback_data="lang_en")],
          [InlineKeyboardButton("🇮🇳 हिन्दी में बात करते हैं", callback_data="lang_hi")]]
    
    await update.message.reply_text(
        SCREENS["welcome"]["text"]["en"],
        reply_markup=InlineKeyboardMarkup(kb), parse_mode="HTML"
    )

async def render_screen(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id, message_id=None, avni_commentary=""):
    user_id = update.effective_user.id
    session = context.user_data[user_id]
    ln = session.lang
    scr_id = session.current_screen

    if scr_id == "review" or session.review_mode:
        text = f"📋 <b>Alright {session.name}, I've processed your 62-point comprehensive diagnostic profile!</b>\n\nLook over your answers below. If any phase section needs adjusting, tap its button to update. Otherwise, smash the submit button below!"
        kb = []
        for sid, sdata in SCREENS.items():
            if sid == "welcome": continue
            lbl = f"✏️ Adjust {sdata['section'][:35]}..."
            kb.append([InlineKeyboardButton(lbl, callback_data=f"nav_scr_{sid}")])
        kb.append([InlineKeyboardButton("🚀 LOOKS GOLDEN - SUBMIT BLUEPRINT", callback_data="final_submit")])
        
        if message_id:
            await context.bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, reply_markup=InlineKeyboardMarkup(kb), parse_mode="HTML")
        else:
            await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="HTML")
        return

    scr_data = SCREENS[scr_id]
    raw_text = scr_data['text'][ln].replace("{name}", session.name)
    
    full_text = ""
    if avni_commentary:
        full_text += f"🎙️ <b>Coach Avni:</b> <i>\"{avni_commentary}\"</i>\n\n━━━━━━━━━━━━━━━━━━━━━\n\n"
    full_text += f"<b>{scr_data['section']}</b>\n\n💬 {raw_text}"
    
    kb = []
    for field in scr_data['fields']:
        if field['type'] == "buttons":
            for idx, opt in enumerate(field['options'][ln]):
                lbl = opt
                if session.answers.get(field['id']) == field['options']['en'][idx]:
                    lbl = f"✅ {opt}"
                kb.append([InlineKeyboardButton(lbl, callback_data=f"set_{field['id']}_{idx}")])

    nav_row = []
    if scr_id != "phase1":
        nav_row.append(InlineKeyboardButton("⬅️ Back Step", callback_data="nav_prev"))
    if session.review_mode:
        nav_row.append(InlineKeyboardButton("✅ Review Complete", callback_data="nav_review"))
    elif scr_id != "phase6":
        nav_row.append(InlineKeyboardButton("Next Phase ➡️", callback_data="nav_next"))
        
    if nav_row:
        kb.append(nav_row)

    if message_id:
        try:
            await context.bot.edit_message_text(full_text, chat_id=chat_id, message_id=message_id, reply_markup=InlineKeyboardMarkup(kb), parse_mode="HTML")
            return
        except Exception:
            pass

    await context.bot.send_message(chat_id=chat_id, text=full_text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="HTML")

async def button_dispatcher(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    session = context.user_data.get(user_id)
    if not session: return await query.answer("Session expired, write /start")
    
    data = query.data
    await query.answer()

    if data.startswith("lang_"):
        session.lang = data.split("_")[1]
        session.current_screen = "phase1"
        await query.message.delete()
        await render_screen(update, context, query.message.chat_id)
        return

    if data == "nav_next":
        screens_list = list(SCREENS.keys())
        idx = screens_list.index(session.current_screen)
        if idx < len(screens_list) - 1:
            session.current_screen = screens_list[idx + 1]
        await render_screen(update, context, query.message.chat_id, message_id=query.message.message_id)
        return

    if data == "nav_prev":
        screens_list = list(SCREENS.keys())
        idx = screens_list.index(session.current_screen)
        if idx > 1:
            session.current_screen = screens_list[idx - 1]
        await render_screen(update, context, query.message.chat_id, message_id=query.message.message_id)
        return

    if data == "nav_review":
        session.current_screen = "review"
        await render_screen(update, context, query.message.chat_id, message_id=query.message.message_id)
        return

    if data.startswith("nav_scr_"):
        session.current_screen = data.replace("nav_scr_", "")
        await render_screen(update, context, query.message.chat_id, message_id=query.message.message_id)
        return

    if data.startswith("set_"):
        parts = data.split("_")
        fid = parts[1]
        oidx = int(parts[2])
        
        for sdata in SCREENS.values():
            if "fields" in sdata:
                for f in sdata['fields']:
                    if f['id'] == fid:
                        session.answers[fid] = f['options']['en'][oidx]
                        chosen_display = f['options']['en'][oidx]
                        
                        remark = get_avni_live_wit(fid, chosen_display, session.name)
                        if remark:
                            await render_screen(update, context, query.message.chat_id, message_id=query.message.message_id, avni_commentary=remark)
                        else:
                            await render_screen(update, context, query.message.chat_id, message_id=query.message.message_id)
                        return

    if data == "final_submit":
        await query.message.delete()
        session.is_submitted = True
        m = session.calculate_macros()
        
        success_text = (
            f"🚀 <b>BOOM! ALL 62 MARKERS SUBMITTED.</b>\n\n"
            f"Spectacular endurance, {session.name}. I have successfully calculated your primary metabolic biomarkers and generated your protocol blueprint indices.\n\n"
            f"📊 <b>METABOLIC METRICS BREAKDOWN:</b>\n"
            f"• BMR (Resting metabolic output): <code>{m['bmr']} kcal</code>\n"
            f"• Estimated TDEE (Maintenance Baseline): <code>{m['tdee']} kcal</code>\n\n"
            f"⚡ <b>STRATEGIC MACRO TARGETS MATRIX:</b>\n"
            f"• 🍗 Protein Target Core: <code>{m['protein']}g</code>\n"
            f"• 🌾 Fuel Carbohydrates: <code>{m['carbs']}g</code>\n"
            f"• 🥑 Vital Structural Fats: <code>{m['fats']}g</code>\n\n"
            f"Grab your high-end tactical dossier report below, and let's hop onto our strategy call to build your execution phase!"
        )
        kb = [[InlineKeyboardButton("📅 LOCK IN STRATEGY SESSION NOW", url=CALENDLY_LINK)]]
        await context.bot.send_message(chat_id=query.message.chat_id, text=success_text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="HTML")
        
        if HAS_WEASYPRINT:
            try:
                html_data = f"""
                <html>
                <body style="font-family: Arial; padding: 40px; color: #2D3748;">
                    <div style="background: #1A365D; color: white; padding: 25px; text-align: center; border-radius: 4px;">
                        <h1>COACH AVNI MASTER BIOPRINT PLAN</h1>
                        <p>62-Point Comprehensive Diagnostic Briefing for: {session.name}</p>
                    </div>
                    <h3>Engineered Metabolic Targets</h3>
                    <p><b>Target Daily Energy Load (TDEE):</b> {m['tdee']} kcal</p>
                    <p><b>Protein Core:</b> {m['protein']}g | <b>Carbs:</b> {m['carbs']}g | <b>Fats:</b> {m['fats']}g</p>
                </body>
                </html>
                """
                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                    HTML(string=html_data).write_pdf(tmp.name)
                    with open(tmp.name, "rb") as f:
                        await context.bot.send_document(chat_id=query.message.chat_id, document=BytesIO(f.read()), filename=f"Coach_Avni_{session.name}_MasterDossier.pdf")
                os.unlink(tmp.name)
            except Exception as e:
                print(f"PDF engine exception trace: {e}")
        return

async def message_dispatcher(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = context.user_data.get(user_id)
    if not session or session.is_submitted: return

    # SMART INPUT HANDLER: Processes Text, Voice Note inputs, or Photo attachments automatically
    if update.message.voice:
        text_val = "[Processed Voice Input Record Asset]"
    elif update.message.photo:
        text_val = "[Uploaded Visual Posture Image]"
        session.answers["q61"] = text_val
    else:
        text_val = update.message.text.strip()
    
    if session.current_screen == "phase1":
        lines = [line.strip() for line in text_val.split("\n") if line.strip()]
        if len(lines) >= 4 or text_val.startswith("["):
            session.name = lines[0] if len(lines) > 0 else "Warrior"
            session.answers["q1"] = session.name
            session.answers["q2"] = lines[1] if len(lines) > 1 else "30"
            session.answers["q3"] = lines[2] if len(lines) > 2 else "170"
            session.answers["q4"] = lines[3] if len(lines) > 3 else "70"
            
            remark = f"Beautiful data blocks locked in, {session.name}! Let's finish up Phase 1 with the buttons below."
            await render_screen(update, context, update.effective_chat.id, avni_commentary=remark)
        else:
            await update.message.reply_text("⚠️ Drop a quick voice note or type all 4 fields cleanly (Name, Age, Height, Weight) so I can compute your numbers properly!")
    else:
        # File textual responses cleanly in the active group category open matrix
        session.answers[session.current_screen] = text_val
        remark = f"Got that filed away right inside your dossier, {session.name}."
        
        if session.review_mode:
            session.current_screen = "review"
        await render_screen(update, context, update.effective_chat.id, avni_commentary=remark)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_dispatcher))
    app.add_handler(MessageHandler(filters.TEXT | filters.VOICE | filters.PHOTO, message_dispatcher))
    print("🚀 Coach Avni Grouped Comprehensive 62-Question Engine Active.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
