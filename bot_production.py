#!/usr/bin/env python3
"""
COACH AVNI - LOCALIZED PRODUCTION ENGINE
Features:
- Feature 3 Integrated: Dynamic multi-language localized gatekeeper (English & Hindi)
- Automated runtime question translation matching session state profiles
- Review Board step before final lockdown with contextual edit capabilities
- Compressed callback keys avoiding Telegram's 64-byte payload limit
- Fully unified background drop-off safety trackers & ReportLab PDF compiler
"""

import os
import sys
from io import BytesIO
from datetime import datetime
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
    print("CRITICAL: TELEGRAM_TOKEN missing from environment configurations.")
    sys.exit(1)

# Compressed state mapping to guarantee payloads fit into Telegram's 64-byte callbacks safely
ID_MAP = {f"q{i}": f"v{i}" for i in range(1, 62)}
REV_MAP = {v: k for k, v in ID_MAP.items()}

# LOCALIZATION MATRIX (ENGLISH & HINDI)
LOCALIZATION = {
    "en": {
        "welcome": "🔥 <b>Welcome to Coach Avni's Strategic Onboarding Funnel.</b>\n\nPlease choose your preferred language to begin:",
        "phase": "Phase",
        "progress": "Progress",
        "speak_type": "🎙️ Speak / Type Custom Answer",
        "skip_media": "⏭️ Skip Upload (Can do this later)",
        "back": "⬅️ BACK",
        "continue": "CONTINUE ➡️",
        "locked": "🔒 Finish answers to un-lock",
        "review_title": "📋 <b>Review Your Assessment Profile ({name})</b>",
        "review_subtitle": "Please verify your logs before submitting to Coach Avni's analyzer.",
        "edit_btn": "✏️ EDIT / CHANGE ANSWERS",
        "submit_btn": "🚀 FINAL SUBMIT PROFILE",
        "fallback_name": "there",
        "down_hdr": "⬇️ Answer Options ⬇️",
        "coach_reply": "🎙️ <b>Coach Avni:</b> "
    },
    "hi": {
        "welcome": "🔥 <b>कोच अवनी के स्ट्रेटेजिक ऑनबोर्डिंग फनल में आपका स्वागत है।</b>\n\nशुरू करने के लिए कृपया अपनी पसंदीदा भाषा चुनें:",
        "phase": "चरण",
        "progress": "प्रगति",
        "speak_type": "🎙️ बोलें / कस्टम उत्तर टाइप करें",
        "skip_media": "⏭️ अपलोड छोड़ें (बाद में कर सकते हैं)",
        "back": "⬅️ पीछे",
        "continue": "आगे बढ़ें ➡️",
        "locked": "🔒 अनलॉक करने के लिए उत्तर पूरे करें",
        "review_title": "📋 <b>आपके असेसमेंट प्रोफ़ाइल की समीक्षा ({name})</b>",
        "review_subtitle": "कोच अवनी के एनालाइज़र को सबमिट करने से पहले कृपया अपने उत्तरों की जांच करें।",
        "edit_btn": "✏️ उत्तर बदलें / एडिट करें",
        "submit_btn": "🚀 फाइनल सबमिट प्रोफ़ाइल",
        "fallback_name": "दोस्त",
        "down_hdr": "⬇️ उत्तर के विकल्प ⬇️",
        "coach_reply": "🎙️ <b>कोच अवनी:</b> "
    }
}

SCREENS = [
    {"id": 1, "section": {"en": "👤 About You", "hi": "👤 आपके बारे में"}, "fields": [
        {"id": "q1", 
         "text": {"en": "First things first, what's your full name?", "hi": "सबसे पहले, आपका पूरा नाम क्या है?"}, "type": "text", "required": True},
        {"id": "q2", 
         "text": {"en": "Awesome {name}. How many years young are you?", "hi": "बहुत बढ़िया {name}। आपकी उम्र कितने साल है?"}, "type": "text", "required": True},
        {"id": "q3", 
         "text": {"en": "What's your height in cm, {name}? (No stretching the truth here!)", "hi": "{name}, सेंटीमीटर (cm) में आपकी ऊंचाई कितनी है?"}, "type": "text", "required": True},
        {"id": "q4", 
         "text": {"en": "And where is your current weight sitting at in kg?", "hi": "और आपका वर्तमान वजन कितने किलोग्राम (kg) है?"}, "type": "text", "required": True}
    ]},
    {"id": 2, "section": {"en": "👤 About You", "hi": "👤 आपके बारे में"}, "fields": [
        {"id": "q5", 
         "text": {"en": "What do you do for work, {name}? Let's see your daytime battlefield:", "hi": "{name}, आप काम क्या करते हैं? अपना कार्यक्षेत्र चुनें:"}, 
         "type": "buttons", "required": True, 
         "options": {
             "en": ["💻 Engineer", "👨‍⚕️ Doctor", "📚 Student", "👔 Business", "🤵 Consultant", "📊 Corporate"],
             "hi": ["💻 इंजीनियर", "👨‍⚕️ डॉक्टर", "📚 छात्र", "👔 व्यापार", "🤵 सलाहकार", "📊 कॉर्पोरेट"]
         }},
        {"id": "q6", 
         "text": {"en": "And what is your biological sex?", "hi": "और आपका जैविक लिंग (Sex) क्या है?"}, 
         "type": "buttons", "required": True, 
         "options": {
             "en": ["👨 Male", "👩 Female"],
             "hi": ["👨 पुरुष", "👩 महिला"]
         }}
    ]},
    {"id": 3, "section": {"en": "🍏 Diet & Food", "hi": "🍏 आहार और भोजन"}, "fields": [
        {"id": "q7", 
         "text": {"en": "Let's talk kitchen rules, {name}. What's your primary dietary style?", "hi": "भोजन की बात करते हैं, {name}। आपकी मुख्य आहार शैली क्या है?"}, 
         "type": "buttons", "required": True, 
         "options": {
             "en": ["🍗 Non-Veg", "🥕 Veg", "🥚 Eggitarian", "🌱 Vegan", "☪️ Jain Vegetarian"],
             "hi": ["🍗 मांसाहारी", "🥕 शाकाहारी", "🥚 अंडा खाने वाले", "🌱 वीगन", "☪️ जैन शाकाहारी"]
         }},
        {"id": "q8", 
         "text": {"en": "Any foods you absolutely can't stand or refuse to eat? (Pick all that apply)", "hi": "कोई ऐसा भोजन जो आपको बिल्कुल पसंद नहीं है? (जो भी लागू हो चुनें)"}, 
         "type": "buttons_multi", "required": False, 
         "options": {
             "en": ["🥒 Bitter Gourd", "🍆 Eggplant", "🍄 Mushroom", "🐟 Fish", "🥛 Dairy", "🧅 No Onion/Garlic"],
             "hi": ["🥒 करेला", "🍆 बैंगन", "🍄 मशरूम", "🐟 मछली", "🥛 डेयरी उत्पाद", "🧅 बिना प्याज/लहसुन"]
         }}
    ]},
    {"id": 4, "section": {"en": "🍏 Diet & Food", "hi": "🍏 आहार और भोजन"}, "fields": [
        {"id": "q9", 
         "text": {"en": "Which cuisine makes your soul happy, {name}?", "hi": "{name}, आपको कौन सा खाना सबसे ज्यादा पसंद है?"}, 
         "type": "buttons", "required": True, 
         "options": {
             "en": ["🍛 North Indian", "🫓 South Indian", "🥗 Continental", "🥢 Asian Mix"],
             "hi": ["🍛 उत्तर भारतीय", "🫓 दक्षिण भारतीय", "🥗 कॉन्टिनेंटल", "🥢 एशियन मिक्स"]
         }},
        {"id": "q10", 
         "text": {"en": "Be honest: how dependent are you on tea or coffee?", "hi": "सच बताइएगा: आप चाय या कॉफी पर कितने निर्भर हैं?"}, 
         "type": "buttons", "required": True, 
         "options": {
             "en": ["☕ Yes, regularly", "🍵 Occasionally", "🚫 Total Abstinence"],
             "hi": ["☕ हाँ, नियमित रूप से", "🍵 कभी-कभी", "🚫 बिल्कुल नहीं"]
         }}
    ]},
    {"id": 5, "section": {"en": "🌅 Your Day", "hi": "🌅 आपका दिन"}, "fields": [
        {"id": "q11", "text": {"en": "What time does your alarm usually go off, {name}?", "hi": "{name}, आपका अलार्म आमतौर पर कितने बजे बजता है?"}, "type": "buttons", "required": True, "options": {"en": ["⏰ 5:00 AM", "⏰ 6:00 AM", "⏰ 7:00 AM", "⏰ 8:00 AM+"], "hi": ["⏰ सुबह 5:00 बजे", "⏰ सुबह 6:00 बजे", "⏰ सुबह 7:00 बजे", "⏰ सुबह 8:00+ बाद"]}},
        {"id": "q12", "text": {"en": "When do you typically fuel up with breakfast?", "hi": "आप आमतौर पर नाश्ता किस समय करते हैं?"}, "type": "buttons", "required": True, "options": {"en": ["🌅 8:00 AM", "🌅 9:00 AM", "🌅 10:00 AM", "⏭️ Skip Breakfast"], "hi": ["🌅 सुबह 8:00 बजे", "🌅 सुबह 9:00 बजे", "🌅 सुबह 10:00 बजे", "⏭️ नाश्ता नहीं करते"]}},
        {"id": "q13", "text": {"en": "When do you step into the work mindset?", "hi": "आप अपने काम की शुरुआत किस समय करते हैं?"}, "type": "buttons", "required": True, "options": {"en": ["💼 8:00 AM", "💼 9:00 AM", "💼 10:00 AM", "⌛ Shift Rotation"], "hi": ["💼 सुबह 8:00 बजे", "💼 सुबह 9:00 बजे", "💼 सुबह 10:00 बजे", "⌛ शिफ्ट बदलती रहती है"]}}
    ]},
    {"id": 6, "section": {"en": "🌅 Your Day", "hi": "🌅 आपका दिन"}, "fields": [
        {"id": "q14", "text": {"en": "What time do you usually close your laptop or finish work?", "hi": "आप आमतौर पर अपना काम कितने बजे खत्म करते हैं?"}, "type": "buttons", "required": True, "options": {"en": ["⏰ 5:00 PM", "⏰ 6:00 PM", "⏰ 7:00 PM", "🌙 9:00 PM+"], "hi": ["⏰ शाम 5:00 बजे", "⏰ शाम 6:00 बजे", "⏰ शाम 7:00 बजे", "🌙 रात 9:00+ बाद"]}},
        {"id": "q15", "text": {"en": "What's the standard window for your lunch, {name}?", "hi": "{name}, आपके दोपहर के भोजन (Lunch) का समय क्या है?"}, "type": "buttons", "required": True, "options": {"en": ["🍱 12:30 PM", "🍱 1:30 PM", "🍱 2:30 PM", "⏳ Unfixed/Variable"], "hi": ["🍱 दोपहर 12:30 बजे", "🍱 दोपहर 1:30 बजे", "🍱 दोपहर 2:30 बजे", "⏳ कोई तय समय नहीं"]}},
        {"id": "q16", "text": {"en": "When are you having your last solid meal of the day (Dinner)?", "hi": "आप रात का खाना (Dinner) आमतौर पर किस समय खाते हैं?"}, "type": "buttons", "required": True, "options": {"en": ["🍽️ 7:00 PM", "🍽️ 8:00 PM", "🍽️ 9:00 PM", "🌙 10:00 PM+"], "hi": ["🍽️ शाम 7:00 बजे", "🍽️ रात 8:00 बजे", "🍽️ रात 9:00 बजे", "🌙 रात 10:00+ बाद"]}}
    ]},
    {"id": 7, "section": {"en": "🌅 Your Day", "hi": "🌅 आपका दिन"}, "fields": [
        {"id": "q17", "text": {"en": "What time are your lights completely out, {name}?", "hi": "{name}, आप रात को कितने बजे सोते हैं?"}, "type": "buttons", "required": True, "options": {"en": ["🌙 10:00 PM", "🌙 11:00 PM", "🌙 12:00 AM", "🦉 1:00 AM+"], "hi": ["🌙 रात 10:00 बजे", "🌙 रात 11:00 बजे", "🌙 रात 12:00 बजे", "🦉 रात 1:00+ बाद"]}},
        {"id": "q18", "text": {"en": "How often are you visiting the snack cabinet between meals?", "hi": "आप भोजन के बीच में कितनी बार स्नैक्स या स्नैक कैबिनेट का चक्कर लगाते हैं?"}, "type": "buttons", "required": True, "options": {"en": ["🍪 Constant", "🍏 Occasional", "🚫 No Snacking"], "hi": ["🍪 लगातार/बहुत बार", "🍏 कभी-कभी", "🚫 बिल्कुल नहीं"]}},
        {"id": "q19", "text": {"en": "How much water are you actually drinking every day?", "hi": "आप रोजाना असल में कितना पानी पीते हैं?"}, "type": "buttons", "required": True, "options": {"en": ["🥛 < 1 Litre", "💧 1-2 Litres", "🚰 2-3 Litres", "🌊 3+ Litres"], "hi": ["🥛 1 लीटर से कम", "💧 1-2 लीटर", "🚰 2-3割 लीटर", "🌊 3 लीटर से ज्यादा"]}}
    ]},
    {"id": 8, "section": {"en": "🌅 Your Day", "hi": "🌅 आपका दिन"}, "fields": [
        {"id": "q20", "text": {"en": "How often is takeout or restaurant food landing on your plate, {name}?", "hi": "{name}, आप बाहर का या रेस्टोरेंट का खाना कितनी बार खाते हैं?"}, "type": "buttons", "required": True, "options": {"en": ["🍔 Daily", "🍕 2-3x / Week", "🥗 Rarely", "✅ Never"], "hi": ["🍔 रोज़ाना", "🍕 हफ्ते में 2-3 बार", "🥗 बहुत कम", "✅ कभी नहीं"]}},
        {"id": "q21", "text": {"en": "Let's talk social hours—what's your weekly relationship with alcohol?", "hi": "क्या आप अल्कोहल (शराब) का सेवन करते हैं?"}, "type": "buttons", "required": True, "options": {"en": ["🍺 High Volume", "🍷 Social/Weekend", "🚫 Completely Clean"], "hi": ["🍺 काफी ज्यादा", "🍷 केवल वीकेंड/सोशल", "🚫 बिल्कुल नहीं"]}},
        {"id": "q22", "text": {"en": "Do you smoke or consume tobacco items?", "hi": "क्या आप धूम्रपान (Smoke) या तंबाकू का सेवन करते हैं?"}, "type": "buttons", "required": True, "options": {"en": ["🚬 Yes, daily", "💨 Socially", "🚫 No"], "hi": ["🚬 हाँ, रोज़ाना", "💨 कभी-कभी दोस्तों के साथ", "🚫 नहीं"]}}
    ]},
    {"id": 9, "section": {"en": "🏥 Health", "hi": "🏥 स्वास्थ्य"}, "fields": [
        {"id": "q23", "text": {"en": "Have you been diagnosed with any of these metabolic conditions, {name}?", "hi": "{name}, क्या आपको इनमें से कोई स्वास्थ्य समस्या है?"}, "type": "buttons_multi", "required": False, "options": {"en": ["🔬 Diabetes", "🧬 Thyroid", "🔴 PCOS/PCOD", "❤️ Hypertension", "🍗 Fatty Liver", "✅ None"], "hi": ["🔬 डायबिटीज", "🧬 थायराइड", "🔴 पीसीओएस/पीसीओडी", "❤️ हाई बीपी", "🍗 फैटी लिवर", "✅ कोई नहीं"]}},
        {"id": "q24", "text": {"en": "Any old or current injuries I need to protect while building your workouts?", "hi": "कोई पुरानी या वर्तमान चोट जिसके बारे में मुझे वर्कआउट बनाते समय ध्यान रखना चाहिए?"}, "type": "text", "required": False},
        {"id": "q25", "text": {"en": "Do you fight any nasty allergies?", "hi": "क्या आपको किसी प्रकार की एलर्जी है?"}, "type": "buttons", "required": True, "options": {"en": ["✅ None", "🍔 Food Specific", "💊 Pharmaceutical", "🌫️ Environmental"], "hi": ["✅ कोई नहीं", "🍔 भोजन से एलर्जी", "💊 दवाओं से एलर्जी", "🌫️ धूल/मौसम से एलर्जी"]}}
    ]},
    {"id": 10, "section": {"en": "🏥 Health", "hi": "🏥 स्वास्थ्य"}, "fields": [
        {"id": "q26", "text": {"en": "Any specific prescription meds you're currently taking, {name}?", "hi": "{name}, क्या आप इस समय कोई डॉक्टर की बताई दवाएं ले रहे हैं?"}, "type": "text", "required": False},
        {"id": "q27", "text": {"en": "Time for gut check—how is your digestion behaving?", "hi": "पेट की बात करते हैं—आपका पाचन (Digestion) कैसा रहता है?"}, "type": "buttons", "required": True, "options": {"en": ["🟢 Smooth/Regular", "⚠️ Chronic Bloating", "🛑 Regular Constipation", "🔥 Acid Reflux"], "hi": ["🟢 बिल्कुल ठीक/नियमित", "⚠️ गैस/ब्लोटिंग", "🛑 कब्ज की समस्या", "🔥 एसिडिटी/एसिड रिफ्लक्स"]}}
    ]},
    {"id": 11, "section": {"en": "🏥 Health", "hi": "🏥 स्वास्थ्य"}, "fields": [
        {"id": "q28", "text": {"en": "How intense are your sugar cravings, {name}?", "hi": "{name}, आपको मीठा खाने की इच्छा (Sugar Cravings) कितनी होती है?"}, "type": "buttons", "required": True, "options": {"en": ["🍩 Intense daily", "🍫 Post-meals only", "🚫 Seldom/Never"], "hi": ["🍩 रोज़ाना बहुत तेज़", "🍫 सिर्फ खाने के बाद", "🚫 कभी-कभार/कभी नहीं"]}},
        {"id": "q29", "text": {"en": "Do you hit a wall and get hit by random energy slumps?", "hi": "क्या आपको दिन में अचानक थकान या सुस्ती महसूस होती है?"}, "type": "buttons", "required": True, "options": {"en": ["🥱 Severe 3 PM crash", "🥱 Constant fatigue", "⚡ Steady performance"], "hi": ["🥱 दोपहर 3 बजे भारी सुस्ती", "🥱 हमेशा थकान महसूस होना", "⚡ एनर्जी हमेशा बनी रहती है"]}}
    ]},
    {"id": 12, "section": {"en": "🏥 Health", "hi": "🏥 स्वास्थ्य"}, "fields": [
        {"id": "q30", "text": {"en": "Notice anything happening with your skin or hair lately?", "hi": "क्या आपको हाल ही में त्वचा (Skin) या बालों में कोई बदलाव दिखा है?"}, "type": "buttons", "required": True, "options": {"en": ["⚠️ High hair fall", "⚠️ Acne breaks", "✅ Stable/Optimal"], "hi": ["⚠️ बालों का बहुत झड़ना", "⚠️ मुंहासे/एक्ने", "✅ सब सामान्य है"]}},
        {"id": "q31", "text": {"en": "How often do you catch yourself getting sick or feeling run down, {name}?", "hi": "{name}, आप कितनी जल्दी बीमार पड़ते हैं या कमजोरी महसूस करते हैं?"}, "type": "buttons", "required": True, "options": {"en": ["🤧 Catch colds easily", "💊 Depend on meds", "🛡️ High/Rarely sick"], "hi": ["🤧 सर्दी-खांसी जल्दी होना", "💊 दवाओं पर निर्भर", "🛡️ इम्यूनिटी अच्छी है/शायद ही कभी"]}}
    ]},
    {"id": 13, "section": {"en": "💊 Supplements & Habits", "hi": "💊 सप्लीमेंट्स और आदतें"}, "fields": [
        {"id": "q32", "text": {"en": "Are you supplementing your Vitamin D3, {name}?", "hi": "{name}, क्या आप विटामिन D3 का सप्लीमेंट ले रहे हैं?"}, "type": "buttons", "required": True, "options": {"en": ["💊 Daily/Weekly", "🧪 Deficient (No Pill)", "❌ Not Tracking"], "hi": ["💊 हाँ, नियमित रूप से", "🧪 कमी है पर दवा नहीं ले रहे", "❌ कोई जानकारी नहीं"]}},
        {"id": "q33", "text": {"en": "What about your Vitamin B12 levels?", "hi": "आपके विटामिन B12 का क्या स्तर है?"}, "type": "buttons", "required": True, "options": {"en": ["💊 Regular Intake", "🧪 Deficient", "❌ Not Tracking"], "hi": ["💊 नियमित सेवन", "🧪 शरीर में कमी है", "❌ कोई जानकारी नहीं"]}},
        {"id": "q34", "text": {"en": "Are you taking Omega-3 or Fish Oil supplements?", "hi": "क्या आप ओमेगा-3 या फिश ऑयल सप्लीमेंट लेते हैं?"}, "type": "buttons", "required": True, "options": {"en": ["✅ Yes, daily", "❌ No Intake"], "hi": ["✅ हाँ, रोज़ाना", "❌ नहीं लेते"]}},
        {"id": "q35", "text": {"en": "Do you take a regular multivitamin?", "hi": "क्या आप कोई मल्टीविटामिन लेते हैं?"}, "type": "buttons", "required": True, "options": {"en": ["✅ Consuming", "❌ No Intake"], "hi": ["✅ हाँ, ले रहे हैं", "❌ नहीं लेते"]}}
    ]},
    {"id": 14, "section": {"en": "💊 Supplements & Habits", "hi": "💊 सप्लीमेंट्स और आदतें"}, "fields": [
        {"id": "q36", "text": {"en": "Do you apply heavy hair dye or artificial treatments frequently, {name}?", "hi": "{name}, क्या आप अक्सर बालों में केमिकल डाई या कोई आर्टिफिशियल ट्रीटमेंट करवाते हैं?"}, "type": "buttons", "required": True, "options": {"en": ["💇 Yes, frequently", "🚫 Minimal/Never"], "hi": ["💇 हाँ, अक्सर", "🚫 बहुत कम/कभी नहीं"]}},
        {"id": "q37", "text": {"en": "Do you catch yourself suffering from brain fog or scattered focus?", "hi": "क्या आपको ध्यान लगाने में कमी या मानसिक धुंधलापन (Brain Fog) महसूस होता है?"}, "type": "buttons", "required": True, "options": {"en": ["🧠 Yes, regularly", "😐 Mid-day fatigue", "✅ Clear/Sharp"], "hi": ["🧠 हाँ, नियमित रूप से", "😐 दोपहर में फोकस कम होना", "✅ बिल्कुल स्पष्ट/तेज़ फोकस"]}},
        {"id": "q38", "text": {"en": "How often do uninvited mood swings or anxiety creep up?", "hi": "आपको मूड स्विंग्स (मूड बदलना) या एंग्जायटी कितनी बार महसूस होती है?"}, "type": "buttons", "required": True, "options": {"en": ["⚡ Frequent shifts", "🌊 Under high stress", "😊 Balanced/Grounded"], "hi": ["⚡ अक्सर बदलाव", "🌊 सिर्फ अत्यधिक तनाव में", "😊 संतुलित/शांत रहता हूँ"]}}
    ]},
    {"id": 15, "section": {"en": "💊 Supplements & Habits", "hi": "💊 सप्लीमेंट्स और आदतें"}, "fields": [
        {"id": "q39", "text": {"en": "How do you feel when you wake up in the morning, {name}?", "hi": "{name}, सुबह उठने पर आपको कैसा महसूस होता है?"}, "type": "buttons", "required": True, "options": {"en": ["🐌 Wake up tired", "⚡ Fast joint recovery", "🩹 Slow healing/Sore"], "hi": ["🐌 उठने पर थकान होना", "⚡ शरीर फ्रेश महसूस होता है", "🩹 शरीर में जकड़न/दर्द रहता है"]}},
        {"id": "q40", "text": {"en": "Rate your overall mental stress load on a daily basis:", "hi": "रोजाना के आधार पर अपने मानसिक तनाव (Stress) को रेट करें:"}, "type": "buttons", "required": True, "options": {"en": ["😊 1-2 (Low)", "😐 3 (Manageable)", "😫 4-5 (High)"], "hi": ["😊 1-2 (बहुत कम)", "😐 3 (सामान्य)", "😫 4-5 (अत्यधिक तनाव)"]}},
        {"id": "q41", "text": {"en": "When you sleep, are you actually out cold or tossing and turning?", "hi": "जब आप सोते हैं, तो आपकी नींद कैसी होती है?"}, "type": "buttons", "required": True, "options": {"en": ["🥱 Fragmented/Wakeful", "😐 Average Depth", "😴 Deep Nightly State"], "hi": ["🥱 बार-बार नींद टूटना", "😐 सामान्य नींद", "😴 गहरी और अच्छी नींद"]}}
    ]},
    {"id": 16, "section": {"en": "🏃 Physical Biomechanics", "hi": "🏃 शारीरिक बायोमैकेनिक्स"}, "fields": [
        {"id": "q42", "text": {"en": "Has anyone ever told you that you snore pretty heavily, {name}?", "hi": "क्या किसी ने आपसे कहा है कि आप सोते समय काफी खर्राटे (Snore) लेते हैं, {name}?"}, "type": "buttons", "required": True, "options": {"en": ["🔊 Yes, heavy snoring", "🔉 Light/Occasional", "🚫 No Snoring"], "hi": ["🔊 हाँ, भारी खर्राटे", "🔉 हल्के/कभी-कभार", "🚫 बिल्कुल नहीं"]}},
        {"id": "q43", "text": {"en": "What is your baseline state right after your feet hit the floor?", "hi": "सुबह बिस्तर से पैर नीचे रखते ही आपकी शारीरिक स्थिति कैसी होती है?"}, "type": "buttons", "required": True, "options": {"en": ["✅ Wake up fresh", "Usually groggy 🥱", "Tired/Exhausted 💤"], "hi": ["✅ एकदम तरोताज़ा", "आमतौर पर सुस्ती 🥱", "थका हुआ/कमज़ोर 💤"]}},
        {"id": "q44", "text": {"en": "Are dark circles making a permanent home under your eyes?", "hi": "क्या आपकी आंखों के नीचे स्थायी डार्क सर्कल्स (काले घेरे) बन गए हैं?"}, "type": "buttons", "required": True, "options": {"en": ["👁️ Prominent/Dark", "👁️ Faint", "✅ None"], "hi": ["👁️ बहुत गहरे/साफ दिखने वाले", "👁️ हल्के", "✅ एक भी नहीं"]}}
    ]},
    {"id": 17, "section": {"en": "🏃 Physical Biomechanics", "hi": "🏃 शारीरिक बायोमैकेनिक्स"}, "fields": [
        {"id": "q45", "text": {"en": "Any history of weird, rapid, unexplained shifts in your weight, {name}?", "hi": "{name}, क्या आपके वजन में कभी अचानक या बिना कारण बड़ा बदलाव हुआ है?"}, "type": "buttons", "required": True, "options": {"en": ["📈 Gained fast lately", "📉 Dropped fast lately", "✅ Steady weight"], "hi": ["📈 हाल ही में तेजी से बढ़ा", "📉 हाल ही में तेजी से घटा", "✅ वजन स्थिर रहा है"]}},
        {"id": "q46", "text": {"en": "Do your hands, feet, or face feel swollen and puffy often?", "hi": "क्या आपके हाथ, पैर या चेहरे पर अक्सर सूजन या भारीपन (Puffy) महसूस होता है?"}, "type": "buttons", "required": True, "options": {"en": ["💧 Heavy ankles/hands", "💧 Face puffiness", "🚫 No"], "hi": ["💧 टखनों/हाथों में सूजन", "💧 चेहरे पर भारीपन", "🚫 नहीं"]}},
        {"id": "q47", "text": {"en": "Do you get freezing cold hands or cold feet, even when it's warm?", "hi": "क्या आपके हाथ या पैर सामान्य मौसम में भी बहुत ठंडे रहते हैं?"}, "type": "buttons", "required": True, "options": {"en": ["🥶 Yes, constantly", "🥶 Only in winter", "🚫 No"], "hi": ["🥶 हाँ, हमेशा", "🥶 सिर्फ सर्दियों में", "🚫 नहीं"]}}
    ]},
    {"id": 18, "section": {"en": "🏃 Physical Biomechanics", "hi": "🏃 शारीरिक बायोमैकेनिक्स"}, "fields": [
        {"id": "q48", "text": {"en": "Are you dealing with any nagging joint or body pain, {name}?", "hi": "{name}, क्या आप जोड़ों या शरीर के किसी लगातार दर्द से परेशान हैं?"}, "type": "buttons", "required": True, "options": {"en": ["💥 Lower back issue", "💥 Knee pain structural", "💥 Neck/Shoulders", "✅ Fully pain-free"], "hi": ["💥 पीठ के निचले हिस्से में", "💥 घुटनों का दर्द", "💥 गर्दन/कंधे में दर्द", "✅ कोई दर्द नहीं है"]}},
        {"id": "q49", "text": {"en": "How quickly do you start gasping for air when moving around?", "hi": "चलने-फिरने या काम करते समय आपकी सांस कितनी जल्दी फूलने लगती है?"}, "type": "buttons", "required": True, "options": {"en": ["🫁 Walking up stairs", "🫁 Only during sprints", "⚡ Strong cardiorespiratory"], "hi": ["🫁 सीढ़ियां चढ़ते ही", "🫁 केवल तेज़ दौड़ने पर", "⚡ स्टैमिना अच्छा है"]}},
        {"id": "q50", "text": {"en": "How many hours is your back glued to a desk chair every day?", "hi": "आप रोजाना कितने घंटे कुर्सी पर बैठकर बिताते हैं?"}, "type": "buttons", "required": True, "options": {"en": ["🚶 Below 4 Hours", "😐 4 - 7 Hours", "💀 8+ Hours"], "hi": ["🚶 4 घंटे से कम", "😐 4 से 7 घंटे", "💀 8 घंटे से ज्यादा"]}}
    ]},
    {"id": 19, "section": {"en": "🏃 Physical Biomechanics", "hi": "🏃 शारीरिक बायोमैकेनिक्स"}, "fields": [
        {"id": "q51", "text": {"en": "Any health issues running rampant in your immediate family tree, {name}?", "hi": "{name}, क्या आपके परिवार में इनमें से कोई बीमारी रही है?"}, "type": "buttons_multi", "required": False, "options": {"en": ["🩸 Diabetes trend", "❤️ Cardiovascular issues", "🧬 Obesity traits", "✅ Clear History"], "hi": ["🩸 डायबिटीज का इतिहास", "❤️ दिल की बीमारी", "🧬 मोटापे की समस्या", "✅ कोई बीमारी नहीं रही"]}},
        {"id": "q52", "text": {"en": "How would you describe your natural skin condition?", "hi": "आप अपनी त्वचा (Skin) की प्राकृतिक स्थिति को कैसे दर्शाएंगे?"}, "type": "buttons", "required": True, "options": {"en": ["🍂 Very dry/flaky", "💧 Excess oily zone", "✨ Well-hydrated/Normal"], "hi": ["🍂 बहुत रूखी/ड्राई", "💧 बहुत ऑइली (तेलीय)", "✨ बिल्कुल सामान्य/स्वस्थ"]}},
        {"id": "q53", "text": {"en": "How stable is your daily appetite?", "hi": "आपकी दैनिक भूख कैसी रहती है?"}, "type": "buttons", "required": True, "options": {"en": ["🔥 Uncontrollable/Bingeing", "🧊 Low appetite/Forget to eat", "✅ Stable patterns"], "hi": ["🔥 बहुत ज्यादा/बिंज ईटिंग", "🧊 बहुत कम भूख/खाना भूल जाना", "✅ बिल्कुल स्थिर और सामान्य"]}}
    ]},
    {"id": 20, "section": {"en": "🎯 Targets & Objectives", "hi": "🎯 लक्ष्य और उद्देश्य"}, "fields": [
        {"id": "q54", "text": {"en": "Have you ever tried tracking calories or macros before, {name}?", "hi": "{name}, क्या आपने पहले कभी कैलोरी या मैक्रोज़ ट्रैक करने की कोशिश की है?"}, "type": "buttons", "required": True, "options": {"en": ["📈 Yes, did macros", "📉 Tried and failed", "🚫 Never tracked"], "hi": ["📈 हाँ, ट्रैक किया है", "📉 कोशिश की पर नहीं हो पाया", "🚫 कभी ट्रैक नहीं किया"]}},
        {"id": "q55", "text": {"en": "If we could wave a magic wand, what's our absolute primary focus?", "hi": "अगर हमारे पास कोई जादुई छड़ी हो, तो आपका सबसे मुख्य लक्ष्य क्या होगा?"}, "type": "buttons", "required": True, "options": {"en": ["📉 Aggressive Fat Loss", "💪 Hypertrophy Lean Muscle", "⚡ Athletic Endurance", "❤️ Metabolic Correction"], "hi": ["📉 तेज़ फैट लॉस", "💪 लीन मसल गेन", "⚡ एथलेटिक स्टैमिना", "❤️ मेटाबॉलिज्म ठीक करना"]}},
        {"id": "q56", "text": {"en": "What has been your main roadblock to consistency in the past?", "hi": "अतीत में आपके नियमित न रह पाने की सबसे बड़ी बाधा क्या रही है?"}, "type": "buttons", "required": True, "options": {"en": ["⏳ Extreme time deficit", "🍳 Cooking complexity", "🍿 Social/Travel habits", "🧠 Lack of internal drive"], "hi": ["⏳ समय की भारी कमी", "🍳 खाना बनाने की झंझट", "🍿 सोशल लाइफ/ट्रैवल आदतें", "🧠 अंदरूनी मोटिवेशन की कमी"]}}
    ]},
    {"id": 21, "section": {"en": "🎯 Targets & Objectives", "hi": "🎯 लक्ष्य और उद्देश्य"}, "fields": [
        {"id": "q57", "text": {"en": "Rate your overall daily energy flow, {name}—are you a firecracker or a slow burn?", "hi": "{name}, आपकी पूरे दिन की एनर्जी कैसी रहती है?"}, "type": "buttons", "required": True, "options": {"en": ["📈 Peak morning/low night", "📉 Flatline low energy", "⚡ High baseline all day"], "hi": ["📈 सुबह बहुत तेज़/रात को कम", "📉 हमेशा लो एनर्जी महसूस होना", "⚡ पूरे दिन शानदार एनर्जी रहता हूँ"]}},
        {"id": "q58", "text": {"en": "Realistically, how much time can you clip out for your workouts weekly?", "hi": "वास्तविक रूप से, आप वर्कआउट के लिए हर हफ्ते कितना समय निकाल सकते हैं?"}, "type": "buttons", "required": True, "options": {"en": ["⏳ Under 2 Hours", "⏳ 2 to 4 Hours", "⚡ 5+ Hours fully ready!"], "hi": ["⏳ हर हफ्ते 2 घंटे से कम", "⏳ हर हफ्ते 2 से 4 घंटे", "⚡ हर हफ्ते 5+ घंटे से ज्यादा"]}}
    ]},
    {"id": 22, "section": {"en": "🎯 Targets & Objectives", "hi": "🎯 लक्ष्य और उद्देश्य"}, "fields": [
        {"id": "q59", "text": {"en": "How often are soda, energy drinks, or sweet commercial beverages making an appearance, {name}?", "hi": "{name}, आप कोल्ड ड्रिंक्स, एनर्जी ड्रिंक्स या मीठे पेय पदार्थों का कितना सेवन करते हैं?"}, "type": "buttons", "required": True, "options": {"en": ["🥤 Yes, almost daily", "🥤 Socially/Weekends", "🚫 Complete clean limit"], "hi": ["🥤 हाँ, लगभग रोज़ाना", "🥤 कभी-कभी/वीकेंड पर", "🚫 बिल्कुल बंद"]}},
        {"id": "q60", "text": {"en": "What's our targeted countdown timeline to make this transformation real?", "hi": "इस ट्रांसफॉर्मेशन को सच करने के लिए आपका समय सीमा लक्ष्य क्या है?"}, "type": "buttons", "required": True, "options": {"en": ["🔥 4 to 8 Weeks", "⚡ 12 Weeks (Recommended)", "⏳ Long-term shift"], "hi": ["🔥 4 से 8 हफ्ते", "⚡ 12 हफ्ते (सुझाया गया)", "⏳ लंबे समय का लाइफस्टाइल बदलाव"]}}
    ]},
    {"id": 23, "section": {"en": "📸 Biometric Profiles", "hi": "📸 बायोमेट्रिक प्रोफाइल"}, "fields": [
        {"id": "q61", "text": {"en": "Drop a clear front, side, or back body photo here so I can evaluate your real posture and muscle structure, {name}.", "hi": "{name}, अपनी सामने, साइड या पीछे की एक साफ बॉडी फोटो भेजें ताकि मैं आपके पोस्चर का मूल्यांकन कर सकूँ।"}, "type": "media", "required": False}
    ]}
]

class UserSession:
    def __init__(self):
        self.lang = "en"  # Safe internal default
        self.current_screen_idx = 0
        self.answers = {}
        self.name = ""  
        self.awaiting_custom_field_id = None
        self.is_submitted = False
        self.last_activity = datetime.now()
        
    def calculate_readiness_score(self):
        score = 85
        water = str(self.answers.get("q19", ""))
        stress = str(self.answers.get("q40", ""))
        sleep = str(self.answers.get("q41", ""))
        if "< 1" in water or "कम" in water: score -= 15
        if "4-5" in stress: score -= 15
        if "Fragmented" in sleep or "टूटना" in sleep: score -= 10
        return max(10, min(100, score))

def generate_progress_bar(pct: int) -> str:
    total_blocks = 10
    filled_blocks = int(pct / 10)
    empty_blocks = total_blocks - filled_blocks
    bar_str = "█" * filled_blocks + "░" * empty_blocks
    return f"<code>[{bar_str}] {pct}%</code>"

def get_funny_instant_reaction(field_id: str, value: str, lang: str) -> str:
    v = str(value)
    if lang == "hi":
        reactions = {
            "q2": "उम्र सिर्फ एक नंबर है। हम वैसे भी आपकी सेलुलर बायोलॉजी को ऑप्टिमाइज़ करने वाले हैं! 🧬",
            "q19": {"कम": "रुको... 1 लीटर से कम पानी?! आपका शरीर इस समय पानी की भारी कमी से जूझ रहा है। फोन छोड़ो और तुरंत एक गिलास पानी पियो! 🚰"},
            "q40": {"4-5": "अत्यधिक तनाव। बढ़ा हुआ कोर्टिसोल फैट लॉस में बड़ी बाधा है। हम आपके प्लान में रिकवरी को बहुत महत्व देंगे। 🧘‍♂️"}
        }
    else:
        reactions = {
            "q2": "Age is just a software parameter. We are about to optimize your cellular biology split anyway! 🧬",
            "q19": {"< 1": "Wait... less than 1L of water?! Your cellular matrix is practically wading through thick sludge right now. Drop the phone and drink a glass immediately! 🚰"},
            "q40": {"4-5": "High stress limits. Chronic cortisol is a major roadblock to lean body targets. We are placing heavy emphasis on recovery protocols for you. 🧘‍♂️"}
        }
        
    if field_id in reactions:
        if isinstance(reactions[field_id], dict):
            for key, msg in reactions[field_id].items():
                if key in v: return f"{LOCALIZATION[lang]['coach_reply']}{msg}"
        else:
            return f"{LOCALIZATION[lang]['coach_reply']}{reactions[field_id]}"
    return None

def check_screen_satisfied(session, screen_data) -> bool:
    for field in screen_data['fields']:
        ans = session.answers.get(field['id'])
        if field['required'] and (ans is None or (isinstance(ans, list) and len(ans) == 0)):
            return False
    return True

def reset_dropoff_tracker(context: ContextTypes.DEFAULT_TYPE, user_id: int, chat_id: int):
    if not context.job_queue:
        return
    current_jobs = context.job_queue.get_jobs_by_name(f"dropoff_{user_id}")
    for job in current_jobs:
        job.schedule_removal()
        
    context.job_queue.run_once(callback=ghost_client_nudge_callback, when=3600, name=f"dropoff_{user_id}", user_id=user_id, chat_id=chat_id)

async def ghost_client_nudge_callback(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    session = context.application.user_data.get(job.user_id)
    if not session or session.is_submitted: return
    ln = session.lang
    display_name = session.name if session.name else LOCALIZATION[ln]["fallback_name"]
    text = f"🎙️ <b>Coach Avni:</b> Hey {display_name}, don't leave your profile incomplete. Tap below to continue!"
    keyboard = [[InlineKeyboardButton("⚡ CONTINUE", callback_data="resume_onboarding")]]
    await context.bot.send_message(chat_id=job.chat_id, text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")

async def render_review_screen(update: Update, context: ContextTypes.DEFAULT_TYPE, target_message_id=None, target_chat_id=None):
    user_id = update.effective_user.id
    if not target_chat_id: target_chat_id = update.effective_chat.id
    session = context.user_data[user_id]
    ln = session.lang
    
    display_name = session.name if session.name else "Harsh"
    text = LOCALIZATION[ln]["review_title"].format(name=display_name) + f"\n{LOCALIZATION[ln]['review_subtitle']}\n━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    for screen in SCREENS:
        for field in screen['fields']:
            ans = session.answers.get(field['id'])
            if ans:
                clean_q = field['text'][ln].replace("{name}", display_name)
                val_display = ", ".join(ans) if isinstance(ans, list) else str(ans)
                text += f"🔹 <b>{clean_q}</b>\n👉 <code>{val_display}</code>\n\n"

    keyboard = [
        [InlineKeyboardButton(LOCALIZATION[ln]["edit_btn"], callback_data="back_from_review")],
        [InlineKeyboardButton(LOCALIZATION[ln]["submit_btn"], callback_data="final_commit_submit")]
    ]
    
    if target_message_id:
        try:
            await context.bot.edit_message_text(text, chat_id=target_chat_id, message_id=target_message_id, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")
            return
        except Exception: pass
    await context.bot.send_message(chat_id=target_chat_id, text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")

async def deliver_final_success_ui(update: Update, context: ContextTypes.DEFAULT_TYPE, target_chat_id):
    user_id = update.effective_user.id
    session = context.user_data[user_id]
    session.is_submitted = True
    ln = session.lang
    
    score = session.calculate_readiness_score()
    display_name = session.name if session.name else "Client"
    
    success_text = (
        f"🧠 <b>BIOMETRIC RECORD SUBMITTED</b>\n\n"
        f"👤 <b>Client:</b> {display_name}\n"
        f"📊 <b>Score Metric:</b> {score}/100\n"
        f"🌍 <b>Language Stack:</b> {ln.upper()}\n\n"
        f"Onboarding protocol generated successfully. Use Calendly to lock your kickoff slot."
    )
    keyboard = [[InlineKeyboardButton("📅 CALENDLY LINK", url=CALENDLY_LINK)]]
    await context.bot.send_message(chat_id=target_chat_id, text=success_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")

async def render_screen(update: Update, context: ContextTypes.DEFAULT_TYPE, target_message_id=None, target_chat_id=None):
    user_id = update.effective_user.id
    if not target_chat_id: target_chat_id = update.effective_chat.id
    session = context.user_data[user_id]
    ln = session.lang
    reset_dropoff_tracker(context, user_id, target_chat_id)
    
    if session.current_screen_idx >= len(SCREENS):
        await render_review_screen(update, context, target_message_id=target_message_id, target_chat_id=target_chat_id)
        return

    screen_data = SCREENS[session.current_screen_idx]
    progress = int((session.current_screen_idx / len(SCREENS)) * 100)
    progress_bar = generate_progress_bar(progress)
    
    section_title = screen_data['section'][ln]
    text = f"📝 <b>{LOCALIZATION[ln]['phase']}: {section_title}</b>\n{LOCALIZATION[ln]['progress']}: {progress_bar}\n━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    current_display_name = str(session.answers.get("q1")) if session.answers.get("q1") else LOCALIZATION[ln]["fallback_name"]

    for field in screen_data['fields']:
        ans = session.answers.get(field['id'])
        orig_text = field['text'][ln].replace("{name}", current_display_name)
        
        if session.awaiting_custom_field_id == field['id']:
            text += f"❓ <b>{orig_text}</b>\n✍️ <i>[...]</i>\n\n"
        elif ans:
            display = ", ".join(ans) if isinstance(ans, list) else str(ans)
            text += f"✅ <b>{orig_text}</b>\n👉 <code>{display}</code>\n\n"
        else:
            text += f"👉 <b>{orig_text}</b>\n\n"

    keyboard = []
    has_multi = any(f['type'] == 'buttons_multi' for f in screen_data['fields'])
    
    for field in screen_data['fields']:
        if field['type'] in ['buttons', 'buttons_multi']:
            keyboard.append([InlineKeyboardButton(LOCALIZATION[ln]["down_hdr"], callback_data="ignore")])
            row, short_id = [], ID_MAP[field['id']]
            options_list = field['options'][ln]
            for idx, opt in enumerate(options_list):
                lbl = opt
                ans = session.answers.get(field['id'])
                if field['type'] == 'buttons' and ans == opt: lbl = f"🔥 {opt} ✓"
                elif field['type'] == 'buttons_multi' and ans and opt in ans: lbl = f"🔥 {opt} ✓"
                row.append(InlineKeyboardButton(lbl, callback_data=f"s_{short_id}_{idx}"))
                if len(row) == 2:
                    keyboard.append(row)
                    row = []
            if row: keyboard.append(row)
            keyboard.append([InlineKeyboardButton(LOCALIZATION[ln]["speak_type"], callback_data=f"c_{short_id}")])
        elif field['type'] == 'media':
            keyboard.append([InlineKeyboardButton(LOCALIZATION[ln]["skip_media"], callback_data="skip_media")])

    nav_row = []
    if session.current_screen_idx > 0:
        nav_row.append(InlineKeyboardButton(LOCALIZATION[ln]["back"], callback_data="back_screen"))
    if has_multi or len(screen_data['fields']) > 1:
        if check_screen_satisfied(session, screen_data): 
            nav_row.append(InlineKeyboardButton(LOCALIZATION[ln]["continue"], callback_data="next_screen"))
        else: 
            nav_row.append(InlineKeyboardButton(LOCALIZATION[ln]["locked"], callback_data="locked"))
    if nav_row: keyboard.append(nav_row)

    if target_message_id:
        try:
            await context.bot.edit_message_text(text, chat_id=target_chat_id, message_id=target_message_id, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")
            return
        except Exception: pass
    await context.bot.send_message(chat_id=target_chat_id, text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    context.user_data[user_id] = UserSession()
    
    keyboard = [
        [InlineKeyboardButton("🇬🇧 English", callback_data="setlang_en"),
         InlineKeyboardButton("🇮🇳 हिन्दी", callback_data="setlang_hi")]
    ]
    await update.message.reply_text(LOCALIZATION["en"]["welcome"], reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    session = context.user_data.get(user_id)
    if not session: return await query.answer("Session timeout! Type /start", show_alert=True)
    
    data = query.data
    if data in ["ignore", "locked"]: return await query.answer()
    
    if data.startswith("setlang_"):
        await query.answer()
        session.lang = data.split("_")[1]
        try: await query.message.delete()
        except Exception: pass
        await render_screen(update, context, target_chat_id=query.message.chat_id)
        return

    if data == "back_from_review":
        await query.answer()
        session.current_screen_idx = len(SCREENS) - 1
        await render_screen(update, context, target_message_id=query.message.message_id, target_chat_id=query.message.chat_id)
        return

    if data == "final_commit_submit":
        await query.answer()
        try: await query.message.delete()
        except Exception: pass
        await deliver_final_success_ui(update, context, query.message.chat_id)
        return

    if data == "back_screen":
        await query.answer()
        if session.current_screen_idx > 0: session.current_screen_idx -= 1
        await render_screen(update, context, target_message_id=query.message.message_id, target_chat_id=query.message.chat_id)
        return

    if data == "next_screen":
        await query.answer()
        session.current_screen_idx += 1
        await render_screen(update, context, target_message_id=query.message.message_id, target_chat_id=query.message.chat_id)
        return

    if data == "skip_media":
        await query.answer()
        session.answers["q61"] = "Skipped"
        session.current_screen_idx += 1
        await render_screen(update, context, target_message_id=query.message.message_id, target_chat_id=query.message.chat_id)
        return

    parts = data.split("_")
    action = parts[0]
    
    if action in ["s", "c"] and len(parts) >= 2:
        short_id = parts[1]
        field_id = REV_MAP.get(short_id)
        screen_data = SCREENS[session.current_screen_idx]
        target_field = next((f for f in screen_data['fields'] if f['id'] == field_id), None)
        if not target_field: return await query.answer()

        if action == "c":
            await query.answer()
            session.awaiting_custom_field_id = field_id
            await render_screen(update, context, target_message_id=query.message.message_id, target_chat_id=query.message.chat_id)
            return

        if action == "s":
            opt_idx = int(parts[2])
            chosen_option = target_field['options'][session.lang][opt_idx]
            
            if target_field['type'] == 'buttons_multi':
                current_ans = session.answers.get(field_id, [])
                if chosen_option in current_ans: current_ans.remove(chosen_option)
                else: current_ans.append(chosen_option)
                session.answers[field_id] = current_ans
                await query.answer()
            else:
                session.answers[field_id] = chosen_option
                reaction = get_funny_instant_reaction(field_id, chosen_option, session.lang)
                if reaction: await query.answer(text=reaction.replace("🎙️ <b>Coach Avni:</b> ", ""), show_alert=True)
                else: await query.answer()
                
                if len(screen_data['fields']) == 1: session.current_screen_idx += 1

            await render_screen(update, context, target_message_id=query.message.message_id, target_chat_id=query.message.chat_id)

async def inbound_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = context.user_data.get(user_id)
    if not session or session.is_submitted or session.current_screen_idx >= len(SCREENS): return

    screen_data = SCREENS[session.current_screen_idx]
    target_field_id = session.awaiting_custom_field_id or next((f['id'] for f in screen_data['fields'] if f['type'] in ['text', 'media'] and not session.answers.get(f['id'])), None)
    if not target_field_id: return

    val = update.message.text.strip() if update.message.text else "[File]"
    session.answers[target_field_id] = val
    if target_field_id == "q1": session.name = val
    session.awaiting_custom_field_id = None

    if check_screen_satisfied(session, screen_data): session.current_screen_idx += 1
    await render_screen(update, context, target_chat_id=update.effective_chat.id)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT | filters.VOICE | filters.PHOTO, inbound_message_handler))
    print("🚀 Localized Production Core Engine Online.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
