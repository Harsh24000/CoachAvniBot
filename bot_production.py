#!/usr/bin/env python3
"""
COACH AVNI - LOCALIZED 62-QUESTION CORE WITH HIGH ENERGY & REACTIVE WIT
Features:
- Infused with Avni's authentic personality, empathy, and direct humor.
- Dynamic commentary responses based on client inputs.
- Modern HTML-to-PDF Engine using WeasyPrint.
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
    print("CRITICAL: TELEGRAM_TOKEN missing from environment configurations.")
    sys.exit(1)

ID_MAP = {f"q{i}": f"v{i}" for i in range(1, 63)}
REV_MAP = {v: k for k, v in ID_MAP.items()}

LOCALIZATION = {
    "en": {
        "welcome": "🔥 <b>Welcome to Coach Avni's Strategic Onboarding Funnel.</b>\n\nNo BS. No cookie-cutter generic protocols. Just raw science, zero judgment, and a plan built for your actual life. Let's start by picking your language:",
        "phase": "Phase",
        "progress": "Progress",
        "speak_type": "🎙️ Speak / Type Custom Answer",
        "skip_media": "⏭️ Skip Upload (Can do this later)",
        "back": "⬅️ BACK",
        "continue": "CONTINUE ➡️",
        "locked": "🔒 Finish answers to un-lock",
        "review_title": "📋 <b>Review Your Assessment Profile ({name})</b>",
        "review_subtitle": "Click any ✏️ item below to jump directly back to that question and update it.",
        "submit_btn": "🚀 FINAL SUBMIT PROFILE",
        "fallback_name": "there",
        "down_hdr": "⬇️ Answer Options ⬇️",
        "coach_reply": "🎙️ <b>Coach Avni:</b> ",
        "pdf_title": "Strategic Biometric Brief",
        "pdf_subtitle": "Metabolic Blueprint & Macro Allocation Report",
        "pdf_summary_hdr": "Biological Core Analysis",
        "pdf_log_hdr": "Complete Assessment Log"
    },
    "hi": {
        "welcome": "🔥 <b>कोच अवनी के स्ट्रेटेजिक ऑनबोर्डिंग फनल में आपका स्वागत है।</b>\n\nकोई बकवास नहीं, कोई दिखावा नहीं। सिर्फ शुद्ध विज्ञान और एक ऐसा प्लान जो आपकी असली लाइफस्टाइल के लिए बना है। शुरू करने के लिए भाषा चुनें:",
        "phase": "चरण",
        "progress": "प्रगति",
        "speak_type": "🎙️ बोलें / कस्टम उत्तर टाइप करें",
        "skip_media": "⏭️ अपलोड छोड़ें (बाद में कर सकते हैं)",
        "back": "⬅️ पीछे",
        "continue": "आगे बढ़ें ➡️",
        "locked": "🔒 अनलॉक करने के लिए उत्तर पूरे करें",
        "review_title": "📋 <b>आपके असेसमेंट प्रोफ़ाइल की समीक्षा ({name})</b>",
        "review_subtitle": "किसी भी ✏️ आइटम पर क्लिक करके सीधे उस प्रश्न पर जाएं और उसे बदलें।",
        "submit_btn": "🚀 फाइनल सबमिट प्रोफ़ाइल",
        "fallback_name": "दोस्त",
        "down_hdr": "⬇️ उत्तर के विकल्प ⬇️",
        "coach_reply": "🎙️ <b>कोच अवनी:</b> ",
        "pdf_title": "रणनीतिक बायोमेट्रिक ब्रीफ",
        "pdf_subtitle": "मेटाबॉलिक ब्लूप्रिंट और मैक्रो आवंटन रिपोर्ट",
        "pdf_summary_hdr": "जैविक कोर विश्लेषण",
        "pdf_log_hdr": "पूर्ण मूल्यांकन लॉग"
    }
}

SCREENS = [
    # PHASE 1: ABOUT YOU
    {"id": 1, "section": {"en": "👤 About You", "hi": "👤 आपके बारे में"}, "fields": [
        {"id": "q1", "text": {"en": "First things first, what's your full name?", "hi": "सबसे पहले, आपका पूरा नाम क्या है?"}, "type": "text", "required": True},
        {"id": "q2", "text": {"en": "Awesome {name}. How many years young are you? (Be honest!)", "hi": "बहुत बढ़िया {name}। आपकी उम्र कितने साल है? (सच बताना!)"}, "type": "text", "required": True},
        {"id": "q3", "text": {"en": "What's your height in cm, {name}?", "hi": "{name}, सेंटीमीटर (cm) में आपकी ऊंचाई कितनी है?"}, "type": "text", "required": True},
        {"id": "q4", "text": {"en": "And where is your current weight sitting at in kg?", "hi": "और आपका वर्तमान वजन कितने किलोग्राम (kg) है?"}, "type": "text", "required": True}
    ]},
    {"id": 2, "section": {"en": "👤 About You", "hi": "👤 आपके बारे में"}, "fields": [
        {"id": "q5", "text": {"en": "What do you do for work? Let me see how much sitting you do:", "hi": "आप काम क्या करते हैं? जरा देखें कितनी देर बैठे रहते हो:"}, "type": "buttons", "required": True, "options": {"en": ["💻 Engineer", "👨‍⚕️ Doctor", "📚 Student", "👔 Business", "🤵 Consultant", "📊 Corporate"], "hi": ["💻 इंजीनियर", "👨‍⚕️ डॉक्टर", "📚 छात्र", "👔 व्यापार", "🤵 सलाहकार", "📊 कॉर्पोरेट"]}},
        {"id": "q6", "text": {"en": "And what is your biological sex?", "hi": "और आपका जैविक लिंग (Sex) क्या है?"}, "type": "buttons", "required": True, "options": {"en": ["👨 Male", "👩 Female"], "hi": ["👨 पुरुष", "👩 महिला"]}}
    ]},

    # PHASE 2: DIET & KITCHEN PROTOCOLS
    {"id": 3, "section": {"en": "🍏 Diet & Food", "hi": "🍏 आहार और भोजन"}, "fields": [
        {"id": "q7", "text": {"en": "What's your primary dietary style, {name}?", "hi": "आपकी मुख्य आहार शैली क्या है, {name}?"}, "type": "buttons", "required": True, "options": {"en": ["🍗 Non-Veg", "🥕 Veg", "🥚 Eggitarian", "🌱 Vegan", "☪️ Jain Vegetarian"], "hi": ["🍗 मांसाहारी", "🥕 शाकाहारी", "🥚 अंडाहारी", "🌱 वीगन", "☪️ जैन शाकाहारी"]}},
        {"id": "q8", "text": {"en": "Any foods you absolutely can't stand or refuse to eat? (No judgment, pick your enemies)", "hi": "कोई ऐसा भोजन जो आपको बिल्कुल पसंद नहीं है? (बिना शर्माए अपनी नापसंद चुनें)"}, "type": "buttons_multi", "required": False, "options": {"en": ["🥒 Bitter Gourd", "🍆 Eggplant", "🍄 Mushroom", "🐟 Fish", "🥛 Dairy", "🧅 No Onion/Garlic"], "hi": ["🥒 करेला", "🍆 बैंगन", "🍄 मशरूम", "🐟 मछली", "🥛 डेयरी", "🧅 बिना प्याज/लहसुन"]}}
    ]},
    {"id": 4, "section": {"en": "🍏 Diet & Food", "hi": "🍏 आहार और भोजन"}, "fields": [
        {"id": "q9", "text": {"en": "Which cuisine makes your soul happy, {name}?", "hi": "{name}, आपको कौन सा खाना सबसे ज्यादा खुश करता है?"}, "type": "buttons", "required": True, "options": {"en": ["🍛 North Indian", "🫓 South Indian", "🥗 Continental", "🥢 Asian Mix"], "hi": ["🍛 उत्तर भारतीय", "🫓 दक्षिण भारतीय", "🥗 कॉन्टिनेंटल", "🥢 एशियन मिक्स"]}},
        {"id": "q10", "text": {"en": "Be honest: how dependent are you on tea or coffee to function like a human?", "hi": "सच बताइएगा: एक सामान्य इंसान की तरह काम करने के लिए चाय या कॉफी पर कितने निर्भर हैं?"}, "type": "buttons", "required": True, "options": {"en": ["☕ Yes, regularly", "🍵 Occasionally", "🚫 Total Abstinence"], "hi": ["☕ हाँ, नियमित रूप से", "🍵 कभी-कभी", "🚫 बिल्कुल नहीं"]}}
    ]},

    # PHASE 3: LIFESTYLE TIMINGS & CHRONOBIOLOGY
    {"id": 5, "section": {"en": "🌅 Your Day", "hi": "🌅 आपका दिन"}, "fields": [
        {"id": "q11", "text": {"en": "What time does your alarm usually go off, {name}?", "hi": "{name}, आपका अलार्म आमतौर पर कितने बजे बजता है?"}, "type": "buttons", "required": True, "options": {"en": ["⏰ 5:00 AM", "⏰ 6:00 AM", "⏰ 7:00 AM", "⏰ 8:00 AM+"], "hi": ["⏰ सुबह 5:00 बजे", "⏰ सुबह 6:00 बजे", "⏰ सुबह 7:00 बजे", "⏰ सुबह 8:00+ बाद"]}},
        {"id": "q12", "text": {"en": "When do you typically fuel up with breakfast?", "hi": "आप आमतौर पर नाश्ता किस समय करते हैं?"}, "type": "buttons", "required": True, "options": {"en": ["🌅 8:00 AM", "🌅 9:00 AM", "🌅 10:00 AM", "⏭️ Skip Breakfast"], "hi": ["🌅 सुबह 8:00 बजे", "🌅 सुबह 9:00 बजे", "🌅 सुबह 10:00 बजे", "⏭️ नाश्ता नहीं"]}},
        {"id": "q13", "text": {"en": "When do you step into the work mindset?", "hi": "आप अपने काम की शुरुआत किस समय करते हैं?"}, "type": "buttons", "required": True, "options": {"en": ["💼 8:00 AM", "💼 9:00 AM", "💼 10:00 AM", "⌛ Shift Rotation"], "hi": ["💼 सुबह 8:00 बजे", "💼 सुबह 9:00 बजे", "💼 सुबह 10:00 बजे", "⌛ शिफ्ट बदलती है"]}}
    ]},
    {"id": 6, "section": {"en": "🌅 Your Day", "hi": "🌅 आपका दिन"}, "fields": [
        {"id": "q14", "text": {"en": "What time do you log off and escape from work?", "hi": "आप आमतौर पर अपने काम से कब आज़ाद होते हैं?"}, "type": "buttons", "required": True, "options": {"en": ["⏰ 5:00 PM", "⏰ 6:00 PM", "⏰ 7:00 PM", "🌙 9:00 PM+"], "hi": ["⏰ शाम 5:00 बजे", "⏰ शाम 6:00 बजे", "⏰ शाम 7:00 बजे", "🌙 रात 9:00+ बाद"]}},
        {"id": "q15", "text": {"en": "What's the standard window for your lunch, {name}?", "hi": "{name}, आपके दोपहर के भोजन का समय क्या है?"}, "type": "buttons", "required": True, "options": {"en": ["🍱 12:30 PM", "🍱 1:30 PM", "🍱 2:30 PM", "⏳ Unfixed/Variable"], "hi": ["🍱 दोपहर 12:30 बजे", "🍱 दोपहर 1:30 बजे", "🍱 दोपहर 2:30 बजे", "⏳ कोई तय समय नहीं"]}},
        {"id": "q16", "text": {"en": "When are you having your Dinner?", "hi": "आप रात का खाना आमतौर पर किस समय खाते हैं?"}, "type": "buttons", "required": True, "options": {"en": ["🍽️ 7:00 PM", "🍽️ 8:00 PM", "🍽️ 9:00 PM", "🌙 10:00 PM+"], "hi": ["🍽️ शाम 7:00 बजे", "🍽️ रात 8:00 बजे", "🍽️ रात 9:00 बजे", "🌙 रात 10:00+ बाद"]}}
    ]},
    {"id": 7, "section": {"en": "🌅 Your Day", "hi": "🌅 आपका दिन"}, "fields": [
        {"id": "q17", "text": {"en": "What time are your lights completely out, {name}? (Be honest, scrolling reels counts as awake!)", "hi": "{name}, आप रात को कितने बजे सोते हैं? (रील्स देखना भी जागने में आता है!)"}, "type": "buttons", "required": True, "options": {"en": ["🌙 10:00 PM", "🌙 11:00 PM", "🌙 12:00 AM", "🦉 1:00 AM+"], "hi": ["🌙 रात 10:00 बजे", "🌙 रात 11:00 बजे", "🌙 रात 12:00 बजे", "🦉 रात 1:00+ बाद"]}},
        {"id": "q18", "text": {"en": "How often are you visiting the snack cabinet between meals?", "hi": "आप भोजन के बीच में कितनी बार स्नैक्स का चक्कर लगाते हैं?"}, "type": "buttons", "required": True, "options": {"en": ["🍪 Constant", "🍏 Occasional", "🚫 No Snacking"], "hi": ["🍪 लगातार/बहुत बार", "🍏 कभी-कभी", "🚫 बिल्कुल नहीं"]}},
        {"id": "q19", "text": {"en": "How much water are you actually drinking every day?", "hi": "आप रोजाना असल में कितना पानी पीते हैं?"}, "type": "buttons", "required": True, "options": {"en": ["🥛 < 1 Litre", "💧 1-2 Litres", "🚰 2-3 Litres", "🌊 3+ Litres"], "hi": ["🥛 1 लीटर से कम", "💧 1-2 या 2-3 लीटर", "🚰 2-3延ीट", "🌊 3 लीटर से ज्यादा"]}}
    ]},
    {"id": 8, "section": {"en": "🌅 Your Day", "hi": "🌅 आपका दिन"}, "fields": [
        {"id": "q20", "text": {"en": "How often is restaurant food landing on your plate, {name}?", "hi": "{name}, आप बाहर का खाना कितनी बार खाते हैं?"}, "type": "buttons", "required": True, "options": {"en": ["🍔 Daily", "🍕 2-3x / Week", "🥗 Rarely", "✅ Never"], "hi": ["🍔 रोज़ाना", "🍕 हफ्ते में 2-3 बार", "🥗 बहुत कम", "✅ कभी नहीं"]}},
        {"id": "q21", "text": {"en": "What's your weekly relationship with alcohol?", "hi": "क्या आप अल्कोहल (शराब) का सेवन करते हैं?"}, "type": "buttons", "required": True, "options": {"en": ["🍺 High Volume", "🍷 Social/Weekend", "🚫 Completely Clean"], "hi": ["🍺 काफी ज्यादा", "🍷 केवल वीकेंड", "🚫 बिल्कुल नहीं"]}},
        {"id": "q22", "text": {"en": "Do you smoke or consume tobacco items?", "hi": "क्या आप धूम्रपान (Smoke) या तंबाकू का सेवन करते हैं?"}, "type": "buttons", "required": True, "options": {"en": ["🚬 Yes, daily", "💨 Socially", "🚫 No"], "hi": ["🚬 हाँ, रोज़ाना", "💨 कभी-कभी", "🚫 नहीं"]}}
    ]},

    # PHASE 4: CLINICAL HEALTH & MEDICAL SYMPTOMS
    {"id": 9, "section": {"en": "🏥 Health & Vitals", "hi": "🏥 स्वास्थ्य और वाइटल्स"}, "fields": [
        {"id": "q23", "text": {"en": "Have you been diagnosed with any metabolic conditions, {name}?", "hi": "{name}, क्या आपको इनमें से कोई स्वास्थ्य समस्या है?"}, "type": "buttons_multi", "required": False, "options": {"en": ["🔬 Diabetes", "🧬 Thyroid", "🔴 PCOS/PCOD", "❤️ Hypertension", "🍗 Fatty Liver", "✅ None"], "hi": ["🔬 डायबिटीज", "🧬 थायराइड", "🔴 पीसीओएस", "❤️ हाई बीपी", "🍗 फैटी लिवर", "✅ कोई नहीं"]}},
        {"id": "q24", "text": {"en": "Any old or current injuries I need to protect while building your workout?", "hi": "कोई पुरानी या वर्तमान चोट जिसके बारे में मुझे पता होना चाहिए?"}, "type": "text", "required": False},
        {"id": "q25", "text": {"en": "Do you fight any nasty allergies?", "hi": "क्या आपको किसी प्रकार की एलर्जी है?"}, "type": "buttons", "required": True, "options": {"en": ["✅ None", "🍔 Food Specific", "💊 Pharmaceutical", "🌫️ Environmental"], "hi": ["✅ कोई नहीं", "🍔 भोजन से", "💊 दवाओं से", "🌫️ धूल/मौसम से"]}}
    ]},
    {"id": 10, "section": {"en": "🏥 Health & Vitals", "hi": "🏥 स्वास्थ्य और वाइटल्स"}, "fields": [
        {"id": "q26", "text": {"en": "Any specific prescription meds you're currently taking, {name}?", "hi": "{name}, क्या आप कोई डॉक्टर की बताई दवाएं ले रहे हैं?"}, "type": "text", "required": False},
        {"id": "q27", "text": {"en": "Time for a gut check—how is your digestion behaving?", "hi": "आपका पाचन (Digestion) कैसा रहता है?"}, "type": "buttons", "required": True, "options": {"en": ["🟢 Smooth/Regular", "⚠️ Chronic Bloating", "🛑 Regular Constipation", "🔥 Acid Reflux"], "hi": ["🟢 बिल्कुल ठीक", "⚠️ गैस/ब्लोटिंग", "🛑 कब्ज की समस्या", "🔥 एसिडिटी"]}}
    ]},
    {"id": 11, "section": {"en": "🏥 Health & Vitals", "hi": "🏥 स्वास्थ्य और वाइटल्स"}, "fields": [
        {"id": "q28", "text": {"en": "How intense are your sugar cravings, {name}?", "hi": "{name}, आपको मीठा खाने की इच्छा कितनी होती है?"}, "type": "buttons", "required": True, "options": {"en": ["🍩 Intense daily", "🍫 Post-meals only", "🚫 Seldom/Never"], "hi": ["🍩 रोज़ाना बहुत तेज़", "🍫 सिर्फ खाने के बाद", "🚫 कभी नहीं"]}},
        {"id": "q29", "text": {"en": "Do you hit a wall and get hit by random energy slumps?", "hi": "क्या आपको दिन में अचानक थकान या सुस्ती महसूस होती है?"}, "type": "buttons", "required": True, "options": {"en": ["🥱 Severe 3 PM crash", "🥱 Constant fatigue", "⚡ Steady performance"], "hi": ["🥱 दोपहर में भारी सुस्ती", "🥱 हमेशा थकान होना", "⚡ एनर्जी बनी रहती है"]}}
    ]},
    {"id": 12, "section": {"en": "🏥 Health & Vitals", "hi": "🏥 स्वास्थ्य और वाइटल्स"}, "fields": [
        {"id": "q30", "text": {"en": "Notice anything happening with your skin or hair lately?", "hi": "क्या आपको हाल ही में त्वचा या बालों में कोई बदलाव दिख रहा है?"}, "type": "buttons", "required": True, "options": {"en": ["⚠️ High hair fall", "⚠️ Acne breaks", "✅ Stable/Optimal"], "hi": ["⚠️ बालों का झड़ना", "⚠️ मुंहासे/एक्ने", "✅ सब सामान्य है"]}},
        {"id": "q31", "text": {"en": "How often do you catch yourself getting sick, {name}?", "hi": "{name}, आप कितनी जल्दी बीमार पड़ते हैं?"}, "type": "buttons", "required": True, "options": {"en": ["🤧 Catch colds easily", "💊 Depend on meds", "🛡️ High/Rarely sick"], "hi": ["🤧 सर्दी-खांसी जल्दी होना", "💊 दवाओं पर निर्भर", "🛡️ बहुत ही कम"]}}
    ]},

    # PHASE 5: SUPPLEMENTS, COGNITION & HABITS
    {"id": 13, "section": {"en": "💊 Supplements & Habits", "hi": "💊 सप्लीमेंट्स और आदतें"}, "fields": [
        {"id": "q32", "text": {"en": "Are you supplementing your Vitamin D3, {name}?", "hi": "{name}, क्या आप विटामिन D3 ले रहे हैं?"}, "type": "buttons", "required": True, "options": {"en": ["💊 Daily/Weekly", "🧪 Deficient (No Pill)", "❌ Not Tracking"], "hi": ["💊 हाँ, नियमित रूप से", "🧪 कमी है पर नहीं ले रहे", "❌ कोई जानकारी नहीं"]}},
        {"id": "q33", "text": {"en": "What about your Vitamin B12 levels?", "hi": "आपके विटामिन B12 का क्या स्तर है?"}, "type": "buttons", "required": True, "options": {"en": ["💊 Regular Intake", "🧪 Deficient", "❌ Not Tracking"], "hi": ["💊 नियमित सेवन", "🧪 शरीर में कमी है", "❌ कोई जानकारी नहीं"]}},
        {"id": "q34", "text": {"en": "Are you taking Omega-3 or Fish Oil supplements?", "hi": "क्या आप ओमेगा-3 या फिश ऑयल सप्लीमेंट लेते हैं?"}, "type": "buttons", "required": True, "options": {"en": ["✅ Yes, daily", "❌ No Intake"], "hi": ["✅ हाँ, रोज़ाना", "❌ नहीं लेते"]}},
        {"id": "q35", "text": {"en": "Do you take a regular multivitamin?", "hi": "क्या आप कोई मल्टीविटामिन लेते हैं?"}, "type": "buttons", "required": True, "options": {"en": ["✅ Consuming", "❌ No Intake"], "hi": ["✅ हाँ, ले रहे हैं", "❌ नहीं लेते"]}}
    ]},
    {"id": 14, "section": {"en": "💊 Supplements & Habits", "hi": "💊 सप्लीमेंट्स और आदतें"}, "fields": [
        {"id": "q36", "text": {"en": "Do you apply heavy hair dye or artificial treatments frequently, {name}?", "hi": "{name}, क्या आप अक्सर बालों में केमिकल डाई का प्रयोग करते हैं?"}, "type": "buttons", "required": True, "options": {"en": ["💇 Yes, frequently", "🚫 Minimal/Never"], "hi": ["💇 हाँ, अक्सर", "🚫 बहुत कम/कभी नहीं"]}},
        {"id": "q37", "text": {"en": "Do you catch yourself suffering from brain fog or scattered focus?", "hi": "क्या आपको ध्यान लगाने में कमी या मानसिक धुंधलापन महसूस होता है?"}, "type": "buttons", "required": True, "options": {"en": ["🧠 Yes, regularly", "😐 Mid-day fatigue", "✅ Clear/Sharp"], "hi": ["🧠 हाँ, नियमित रूप से", "😐 दोपहर में फोकस कम", "✅ बिल्कुल साफ फोकस"]}},
        {"id": "q38", "text": {"en": "How often do uninvited mood swings or anxiety creep up?", "hi": "आपको मूड स्विंग्स या एंग्जायटी कितनी बार महसूस होती है?"}, "type": "buttons", "required": True, "options": {"en": ["⚡ Frequent shifts", "🌊 Under high stress", "😊 Balanced/Grounded"], "hi": ["⚡ अक्सर बदलाव", "🌊 सिर्फ अत्यधिक तनाव में", "😊 शांत रहता हूँ"]}}
    ]},
    {"id": 15, "section": {"en": "💊 Supplements & Habits", "hi": "💊 सप्लीमेंट्स और आदतें"}, "fields": [
        {"id": "q39", "text": {"en": "How do you feel when you wake up in the morning, {name}?", "hi": "{name}, सुबह उठने पर आपको शारीरिक रूप से कैसा महसूस होता है?"}, "type": "buttons", "required": True, "options": {"en": ["🐌 Wake up tired", "⚡ Fast joint recovery", "🩹 Slow healing/Sore"], "hi": ["🐌 उठने पर थकान होना", "⚡ शरीर फ्रेश होता है", "🩹 शरीर में जकड़न/दर्द"]}},
        {"id": "q40", "text": {"en": "Rate your overall mental stress load on a daily basis:", "hi": "रोजाना के आधार पर अपने मानसिक तनाव को रेट करें:"}, "type": "buttons", "required": True, "options": {"en": ["😊 1-2 (Low)", "😐 3 (Manageable)", "😫 4-5 (High)"], "hi": ["😊 1-2 (बहुत कम)", "😐 3 (सामान्य)", "😫 4-5 (अत्यधिक तनाव)"]}},
        {"id": "q41", "text": {"en": "When you sleep, are you actually out cold or tossing and turning?", "hi": "जब आप सोते हैं, तो आपकी नींद की गहराई कैसी होती है?"}, "type": "buttons", "required": True, "options": {"en": ["🥱 Fragmented/Wakeful", "😐 Average Depth", "😴 Deep Nightly State"], "hi": ["🥱 बार-बार नींद टूटना", "😐 सामान्य नींद", "😴 गहरी और अच्छी नींद"]}}
    ]},

    # PHASE 6: BIOMECHANICS & STRUCTURAL FUNCTION
    {"id": 16, "section": {"en": "🏃 Biomechanics & Structure", "hi": "🏃 बायोमैकेनिक्स और ढांचा"}, "fields": [
        {"id": "q42", "text": {"en": "Has anyone ever told you that you snore pretty heavily, {name}?", "hi": "क्या आप सोते समय काफी खर्राटे लेते हैं, {name}?"}, "type": "buttons", "required": True, "options": {"en": ["🔊 Yes, heavy snoring", "🔉 Light/Occasional", "🚫 No Snoring"], "hi": ["🔊 हाँ, भारी खर्राटे", "🔉 हल्के/कभी-कभार", "🚫 बिल्कुल नहीं"]}},
        {"id": "q43", "text": {"en": "What is your baseline state right after your feet hit the floor?", "hi": "सुबह बिस्तर से उठते ही आपकी मानसिक स्थिति कैसी होती है?"}, "type": "buttons", "required": True, "options": {"en": ["✅ Wake up fresh", "Usually groggy 🥱", "Tired/Exhausted 💤"], "hi": ["✅ एकदम तरोताज़ा", "आमतौर पर सुस्ती 🥱", "थका हुआ/कमज़ोर 💤"]}},
        {"id": "q44", "text": {"en": "Are dark circles making a permanent home under your eyes?", "hi": "क्या आपकी आंखों के नीचे डार्क सर्कल्स बन गए हैं?"}, "type": "buttons", "required": True, "options": {"en": ["👁️ Prominent/Dark", "👁️ Faint", "✅ None"], "hi": ["👁️ बहुत गहरे", "👁️ हल्के", "✅ एक भी नहीं"]}}
    ]},
    {"id": 17, "section": {"en": "🏃 Biomechanics & Structure", "hi": "🏃 बायोमैकेनिक्स और ढांचा"}, "fields": [
        {"id": "q45", "text": {"en": "Any history of rapid, unexplained shifts in your weight, {name}?", "hi": "{name}, क्या आपके वजन में कभी अचानक बड़ा बदलाव हुआ है?"}, "type": "buttons", "required": True, "options": {"en": ["📈 Gained fast lately", "📉 Dropped fast lately", "✅ Steady weight"], "hi": ["📈 हाल ही में तेजी से बढ़ा", "📉 हाल ही में तेजी से घटा", "✅ वजन स्थिर रहा है"]}},
        {"id": "q46", "text": {"en": "Do your hands, feet, or face feel swollen and puffy often?", "hi": "क्या आपके हाथ, पैर या चेहरे पर अक्सर सूजन महसूस होती है?"}, "type": "buttons", "required": True, "options": {"en": ["💧 Heavy ankles/hands", "💧 Face puffiness", "🚫 No"], "hi": ["💧 टखनों/हाथों में सूजन", "💧 चेहरे पर भारीपन", "🚫 नहीं"]}},
        {"id": "q47", "text": {"en": "Do you get freezing cold hands or cold feet, even when it's warm?", "hi": "क्या आपके हाथ या पैर सामान्य मौसम में भी बहुत ठंडे रहते हैं?"}, "type": "buttons", "required": True, "options": {"en": ["🥶 Yes, constantly", "🥶 Only in winter", "🚫 No"], "hi": ["🥶 हाँ, हमेशा", "🥶 सिर्फ सर्दियों में", "🚫 नहीं"]}}
    ]},
    {"id": 18, "section": {"en": "🏃 Biomechanics & Structure", "hi": "🏃 बायोमैकेनिक्स और ढांचा"}, "fields": [
        {"id": "q48", "text": {"en": "Are you dealing with any nagging joint or body pain, {name}?", "hi": "{name}, क्या आप जोड़ों या शरीर के किसी दर्द से परेशान हैं?"}, "type": "buttons", "required": True, "options": {"en": ["💥 Lower back issue", "💥 Knee pain structural", "💥 Neck/Shoulders", "✅ Fully pain-free"], "hi": ["💥 पीठ के निचले हिस्से में", "💥 घुटनों का दर्द", "💥 गर्दन/कंधे में दर्द", "✅ कोई दर्द नहीं है"]}},
        {"id": "q49", "text": {"en": "How quickly do you start gasping for air when moving around?", "hi": "चलने-फिरने या सीढ़ियां चढ़ते समय आपकी सांस कितनी जल्दी फूलती है?"}, "type": "buttons", "required": True, "options": {"en": ["🫁 Walking up stairs", "🫁 Only during sprints", "⚡ Strong cardiorespiratory"], "hi": ["🫁 सीढ़ियां चढ़ते ही", "🫁 केवल तेज़ दौड़ने पर", "⚡ स्टैमिना अच्छा है"]}},
        {"id": "q50", "text": {"en": "How many hours is your back glued to a desk chair every day?", "hi": "आप रोजाना कितने घंटे कुर्सी पर बैठकर बिताते हैं?"}, "type": "buttons", "required": True, "options": {"en": ["🚶 Below 4 Hours", "😐 4 - 7 Hours", "💀 8+ Hours"], "hi": ["🚶 4 घंटे से कम", "😐 4 से 7 घंटे", "💀 8 घंटे से ज्यादा"]}}
    ]},
    {"id": 19, "section": {"en": "🏃 Biomechanics & Structure", "hi": "🏃 बायोमैकेनिक्स और ढांचा"}, "fields": [
        {"id": "q51", "text": {"en": "Any health issues running rampant in your family tree, {name}?", "hi": "{name}, क्या आपके परिवार में इनमें से कोई बीमारी रही है?"}, "type": "buttons_multi", "required": False, "options": {"en": ["🩸 Diabetes trend", "❤️ Cardiovascular issues", "🧬 Obesity traits", "✅ Clear History"], "hi": ["🩸 डायबिटीज का इतिहास", "❤️ दिल की बीमारी", "🧬 मोटापे की समस्या", "✅ कोई बीमारी नहीं रही"]}},
        {"id": "q52", "text": {"en": "How would you describe your natural skin condition?", "hi": "आप अपनी त्वचा की प्राकृतिक स्थिति को कैसे दर्शाएंगे?"}, "type": "buttons", "required": True, "options": {"en": ["🍂 Very dry/flaky", "💧 Excess oily zone", "✨ Well-hydrated/Normal"], "hi": ["🍂 बहुत रूखी/ड्राई", "💧 बहुत ऑइली", "✨ बिल्कुल सामान्य/स्वस्थ"]}},
        {"id": "q53", "text": {"en": "How stable is your daily appetite?", "hi": "आपकी दैनिक भूख कैसी रहती है?"}, "type": "buttons", "required": True, "options": {"en": ["🔥 Uncontrollable/Bingeing", "🧊 Low appetite/Forget to eat", "✅ Stable patterns"], "hi": ["🔥 बहुत ज्यादा भूख", "🧊 बहुत कम भूख लगना", "✅ बिल्कुल स्थिर और सामान्य"]}}
    ]},

    # PHASE 7: TARGETS & OBJECTIVES
    {"id": 20, "section": {"en": "🎯 Targets & Objectives", "hi": "🎯 लक्ष्य और उद्देश्य"}, "fields": [
        {"id": "q54", "text": {"en": "Have you ever tried tracking calories or macros before, {name}?", "hi": "{name}, क्या आपने पहले कभी कैलोरी या मैक्रोज़ ट्रैक करने की कोशिश की है?"}, "type": "buttons", "required": True, "options": {"en": ["📈 Yes, did macros", "📉 Tried and failed", "🚫 Never tracked"], "hi": ["📈 हाँ, ट्रैक किया है", "📉 कोशिश की पर नहीं हुआ", "🚫 कभी ट्रैक नहीं किया"]}},
        {"id": "q55", "text": {"en": "If we could wave a magic wand, what's our absolute primary focus?", "hi": "आपका सबसे मुख्य लक्ष्य क्या होगा?"}, "type": "buttons", "required": True, "options": {"en": ["📉 Aggressive Fat Loss", "💪 Hypertrophy Lean Muscle", "⚡ Athletic Endurance", "❤️ Metabolic Correction"], "hi": ["📉 तेज़ फैट लॉस", "💪 लीन मसल गेन", "⚡ एथलिक स्टैमिना", "❤️ मेटाबॉलिज्म ठीक करना"]}},
        {"id": "q56", "text": {"en": "What has been your main roadblock to consistency in the past?", "hi": "अतीत में आपके नियमित न रह पाने की सबसे बड़ी बाधा क्या रही है?"}, "type": "buttons", "required": True, "options": {"en": ["⏳ Extreme time deficit", "🍳 Cooking complexity", "🍿 Social/Travel habits", "🧠 Lack of internal drive"], "hi": ["⏳ समय की भारी कमी", "🍳 खाना बनाने की झंझट", "🍿 सोशल लाइफ/ट्रैवल", "🧠 मोटिवेशन की कमी"]}}
    ]},
    {"id": 21, "section": {"en": "🎯 Targets & Objectives", "hi": "🎯 लक्ष्य और उद्देश्य"}, "fields": [
        {"id": "q57", "text": {"en": "Rate your overall daily energy flow, {name}—firecracker or slow burn?", "hi": "{name}, आपकी पूरे दिन की एनर्जी कैसी रहती है?"}, "type": "buttons", "required": True, "options": {"en": ["📈 Peak morning/low night", "📉 Flatline low energy", "⚡ High baseline all day"], "hi": ["📈 सुबह तेज़/रात को कम", "📉 हमेशा लो एनर्जी होना", "⚡ पूरे दिन शानदार एनर्जी"]}},
        {"id": "q58", "text": {"en": "Realistically, how much time can you clip out for your workouts weekly?", "hi": "आप वर्कआउट के लिए हर हफ्ते कितना समय निकाल सकते हैं?"}, "type": "buttons", "required": True, "options": {"en": ["⏳ Under 2 Hours", "⏳ 2 to 4 Hours", "⚡ 5+ Hours fully ready!"], "hi": ["⏳ हर हफ्ते 2 घंटे से कम", "⏳ हर हफ्ते 2 से 4 घंटे", "⚡ हर हफ्ते 5+ घंटे से ज्यादा"]}}
    ]},
    {"id": 22, "section": {"en": "🎯 Targets & Objectives", "hi": "🎯 लक्ष्य और उद्देश्य"}, "fields": [
        {"id": "q59", "text": {"en": "How often are soda or energy drinks making an appearance, {name}?", "hi": "{name}, आप कोल्ड ड्रिंक्स या मीठे पेय पदार्थों का कितना सेवन करते हैं?"}, "type": "buttons", "required": True, "options": {"en": ["🥤 Yes, almost daily", "🥤 Socially/Weekends", "🚫 Complete clean limit"], "hi": ["🥤 हाँ, लगभग रोज़ाना", "🥤 कभी-कभी/वीकेंड पर", "🚫 बिल्कुल बंद"]}},
        {"id": "q60", "text": {"en": "What's our targeted countdown timeline to make this transformation real?", "hi": "इस ट्रांसफॉर्मेशन को सच करने के लिए आपका समय सीमा लक्ष्य क्या है?"}, "type": "buttons", "required": True, "options": {"en": ["🔥 4 to 8 Weeks", "⚡ 12 Weeks (Recommended)", "⏳ Long-term shift"], "hi": ["🔥 4 से 8 हफ्ते", "⚡ 12 हफ्ते (सुझाया गया)", "⏳ लंबे समय का लाइफस्टाइल बदलाव"]}},
        {"id": "q62", "text": {"en": "Any final remarks or notes you want to pass to Coach Avni directly?", "hi": "कोई अंतिम टिप्पणी या बात जो आप सीधे कोच अवनी तक पहुंचाना चाहते हैं?"}, "type": "text", "required": False}
    ]},

    # PHASE 8: BIOMETRICS ASSETS CAPTURE
    {"id": 23, "section": {"en": "📸 Biometric Profiles", "hi": "📸 बायोमेट्रिक प्रोफाइल"}, "fields": [
        {"id": "q61", "text": {"en": "Drop a clear posture body photo here so I can evaluate structural frames, {name}.", "hi": "{name}, अपनी सामने की एक साफ बॉडी फोटो भेजें ताकि मैं आपके पोस्चर का मूल्यांकन कर सकूँ।"}, "type": "media", "required": False}
    ]}
]

# AVNI'S INTUITION & WITTY REACTION ENGINE
def get_avni_commentary(field_id, val, lang):
    comments = {
        "q5": {
            "💻 Engineer": {"en": "An Engineer! Translation: A lot of desk sitting and posture-ruining code marathons. Let's fix that stance.", "hi": "इंजीनियर! यानी कुर्सी से चिपके रहना और कोडिंग मैराथन। तुम्हारी रीढ़ की हड्डी को वापस सीधा करना पड़ेगा।"},
            "👨‍⚕️ Doctor": {"en": "A Doctor! Saving lives but skipping meals, huh? Time to write you a metabolic prescription.", "hi": "डॉक्टर साहब! दुनिया की जान बचा रहे हो और खुद के खाने का ठिकाना नहीं है? अब तुम्हारा खुद का इलाज करना पड़ेगा।"}
        },
        "q10": {
            "☕ Yes, regularly": {"en": "Ah, running on liquid adrenaline. We'll need to sort your deep baseline sleep energy out.", "hi": "यानी लिक्विड एड्रेनालाईन पर चल रहे हो। तुम्हारी गहरी नींद और असली एनर्जी को वापस लाना होगा।"}
        },
        "q17": {
            "🦉 1:00 AM+": {"en": "1 AM?! Your cortisol levels must be having a party. Late nights are the silent killer of body fat loss goals.", "hi": "रात के 1 बजे?! तुम्हारा कोर्टिसोल लेवल तो रॉकेट हो रखा होगा। देर रात तक जागना फैट लॉस का सबसे बड़ा दुश्मन है।"}
        },
        "q18": {
            "🍪 Constant": {"en": "Constant snacking? Your insulin levels are on a rollercoaster ride. Let's steady that down.", "hi": "लगातार स्नैकिंग? तुम्हारा इंसुलिन लेवल झूला झूल रहा है। इसे शांत करना बेहद ज़रूरी है।"}
        },
        "q20": {
            "🍔 Daily": {"en": "Daily restaurant food? Oof, your sodium intake is screaming for help. Let's fix the kitchen game.", "hi": "रोज़ बाहर का खाना? भाई, तुम्हारी बॉडी का सोडियम लेवल मदद की भीख मांग रहा है। घर का खाना ज़िंदाबाद करना पड़ेगा।"}
        }
    }
    return comments.get(field_id, {}).get(val, {}).get(lang, "")

class UserSession:
    def __init__(self):
        self.lang = "en"
        self.current_screen_idx = 0
        self.answers = {}
        self.name = ""  
        self.awaiting_custom_field_id = None
        self.is_submitted = False
        self.review_editing_mode = False  
        self.last_activity = datetime.now()
        
    def calculate_macros(self):
        try:
            weight = float(re.findall(r"[-+]?\d*\.\d+|\d+", str(self.answers.get("q4", "70")))[0])
            height = float(re.findall(r"[-+]?\d*\.\d+|\d+", str(self.answers.get("q3", "170")))[0])
            age = float(re.findall(r"[-+]?\d*\.\d+|\d+", str(self.answers.get("q2", "30")))[0])
        except Exception:
            weight, height, age = 70.0, 170.0, 30.0
            
        sex = str(self.answers.get("q6", "Male"))
        if "Female" in sex or "महिला" in sex:
            bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
        else:
            bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
            
        job = str(self.answers.get("q5", ""))
        multiplier = 1.2
        if "Engineer" in job or "इंजीनियर" in job or "Corporate" in job: multiplier = 1.35
        elif "Doctor" in job or "डॉक्टर" in job: multiplier = 1.45
        
        tdee = int(bmr * multiplier)
        protein = int(weight * 2.0)  
        fats = int((tdee * 0.25) / 9)
        carbs = int((tdee - (protein * 4) - (fats * 9)) / 4)
        return {"bmr": int(bmr), "tdee": tdee, "protein": protein, "carbs": carbs, "fats": fats}

def generate_progress_bar(pct: int) -> str:
    total_blocks = 10
    filled_blocks = int(pct / 10)
    empty_blocks = total_blocks - filled_blocks
    return f"<code>[{'█' * filled_blocks}{'░' * empty_blocks}] {pct}%</code>"

def check_screen_satisfied(session, screen_data) -> bool:
    for field in screen_data['fields']:
        ans = session.answers.get(field['id'])
        if field['required'] and (ans is None or (isinstance(ans, list) and len(ans) == 0)):
            return False
    return True

async def render_review_screen(update: Update, context: ContextTypes.DEFAULT_TYPE, target_message_id=None, target_chat_id=None):
    user_id = update.effective_user.id
    if not target_chat_id: target_chat_id = update.effective_chat.id
    session = context.user_data[user_id]
    ln = session.lang
    session.review_editing_mode = False 
    
    display_name = session.name if session.name else "Client"
    text = LOCALIZATION[ln]["review_title"].format(name=display_name) + f"\n{LOCALIZATION[ln]['review_subtitle']}\n━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    keyboard = []
    for s_idx, screen in enumerate(SCREENS):
        for field in screen['fields']:
            ans = session.answers.get(field['id'])
            if ans:
                clean_q = field['text'][ln].replace("{name}", display_name)
                val_display = ", ".join(ans) if isinstance(ans, list) else str(ans)
                if len(clean_q) > 28: clean_q = clean_q[:25] + "..."
                keyboard.append([InlineKeyboardButton(f"✏️ {clean_q}: {val_display}", callback_data=f"editf_{s_idx}")])

    keyboard.append([InlineKeyboardButton(LOCALIZATION[ln]["submit_btn"], callback_data="final_commit_submit")])
    
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
    
    macros = session.calculate_macros()
    display_name = session.name if session.name else "Client"
    
    success_text = (
        f"🚀 <b>ASSESSMENT MATRIX LOCKED SUCCESSFULLY</b>\n\n"
        f"👤 <b>Client Profile:</b> {display_name}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 <b>AUTOMATED METABOLIC FORECAST:</b>\n"
        f"• Base BMR: <code>{macros['bmr']} kcal</code>\n"
        f"• Est. Daily TDEE: <code>{macros['tdee']} kcal</code>\n\n"
        f"💡 <b>TARGET METABOLIC MACRO SPLIT:</b>\n"
        f"• 🍗 Protein: <code>{macros['protein']}g</code>\n"
        f"• 🌾 Carbs: <code>{macros['carbs']}g</code>\n"
        f"• 🥑 Fats: <code>{macros['fats']}g</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Coach Avni is running numbers on your files. Book your strategy session down below!"
    )
    keyboard = [[InlineKeyboardButton("📅 BOOK CALL VIA CALENDLY", url=CALENDLY_LINK)]]
    await context.bot.send_message(chat_id=target_chat_id, text=success_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")
    
    if HAS_WEASYPRINT:
        try:
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    @page {{ size: A4; margin: 20mm 15mm; }}
                    body {{ font-family: Arial, sans-serif; color: #2D3748; line-height: 1.5; }}
                    .header {{ background-color: #1A365D; color: white; padding: 25px; text-align: center; margin-bottom: 20px; }}
                    .metric-box {{ background-color: #F7FAFC; border: 1px solid #E2E8F0; padding: 15px; border-radius: 6px; }}
                    table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
                    th {{ background-color: #2B6CB0; color: white; padding: 10px; text-align: left; }}
                    td {{ padding: 10px; border-bottom: 1px solid #E2E8F0; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>COACH AVNI STRATEGIC PROFILE</h1>
                    <p>Client: {display_name}</p>
                </div>
                <h2>Metabolic Analysis</h2>
                <div class="metric-box">
                    <p><b>BMR:</b> {macros['bmr']} kcal | <b>TDEE:</b> {macros['tdee']} kcal</p>
                    <p><b>Macros:</b> Protein: {macros['protein']}g | Carbs: {macros['carbs']}g | Fats: {macros['fats']}g</p>
                </div>
                <h2>Full Question Log</h2>
                <table>
                    <thead><tr><th>Question</th><th>Response</th></tr></thead>
                    <tbody>
            """
            for screen in SCREENS:
                for field in screen['fields']:
                    ans = session.answers.get(field['id'])
                    if ans:
                        clean_q = field['text'][ln].replace("{name}", display_name)
                        val_str = ", ".join(ans) if isinstance(ans, list) else str(ans)
                        html_content += f"<tr><td><b>{clean_q}</b></td><td>{val_str}</td></tr>"
            html_content += "</tbody></table></body></html>"
            
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_pdf:
                HTML(string=html_content).write_pdf(tmp_pdf.name)
                tmp_pdf.seek(0)
                with open(tmp_pdf.name, "rb") as f:
                    await context.bot.send_document(chat_id=target_chat_id, document=BytesIO(f.read()), filename=f"Coach_Avni_{display_name}_Dossier.pdf")
            os.unlink(tmp_pdf.name)
        except Exception as e:
            print(f"PDF Error: {e}")

async def render_screen(update: Update, context: ContextTypes.DEFAULT_TYPE, target_message_id=None, target_chat_id=None, avni_push=""):
    user_id = update.effective_user.id
    if not target_chat_id: target_chat_id = update.effective_chat.id
    session = context.user_data[user_id]
    ln = session.lang
    
    if session.current_screen_idx >= len(SCREENS):
        await render_review_screen(update, context, target_message_id=target_message_id, target_chat_id=target_chat_id)
        return

    screen_data = SCREENS[session.current_screen_idx]
    progress = int((session.current_screen_idx / len(SCREENS)) * 100)
    progress_bar = generate_progress_bar(progress)
    
    text = ""
    if avni_push:
        text += f"{LOCALIZATION[ln]['coach_reply']}<i>\"{avni_push}\"</i>\n\n━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
    text += f"📝 <b>{LOCALIZATION[ln]['phase']}: {screen_data['section'][ln]}</b>\n{LOCALIZATION[ln]['progress']}: {progress_bar}\n━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
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
            row, short_id = [], ID_MAP.get(field['id'], "v1")
            for idx, opt in enumerate(field['options'][ln]):
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
    if session.review_editing_mode:
        nav_row.append(InlineKeyboardButton("📋 CANCEL EDIT", callback_data="jump_review"))
    else:
        if session.current_screen_idx > 0:
            nav_row.append(InlineKeyboardButton(LOCALIZATION[ln]["back"], callback_data="back_screen"))
            
    if has_multi or len(screen_data['fields']) > 1 or session.review_editing_mode:
        if check_screen_satisfied(session, screen_data): 
            cb_target = "jump_review" if session.review_editing_mode else "next_screen"
            nav_row.append(InlineKeyboardButton(LOCALIZATION[ln]["continue"], callback_data=cb_target))
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
    keyboard = [[InlineKeyboardButton("🇬🇧 English", callback_data="setlang_en"), InlineKeyboardButton("🇮🇳 हिन्दी", callback_data="setlang_hi")]]
    await update.message.reply_text(LOCALIZATION["en"]["welcome"], reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    session = context.user_data.get(user_id)
    if not session: return await query.answer("Session timeout! Run /start", show_alert=True)
    
    data = query.data
    if data in ["ignore", "locked"]: return await query.answer()
    
    if data.startswith("setlang_"):
        await query.answer()
        session.lang = data.split("_")[1]
        try: await query.message.delete()
        except Exception: pass
        await render_screen(update, context, target_chat_id=query.message.chat_id)
        return

    if data.startswith("editf_"):
        await query.answer()
        session.current_screen_idx = int(data.split("_")[1])
        session.review_editing_mode = True
        await render_screen(update, context, target_message_id=query.message.message_id, target_chat_id=query.message.chat_id)
        return

    if data == "jump_review":
        await query.answer()
        session.current_screen_idx = len(SCREENS)
        await render_review_screen(update, context, target_message_id=query.message.message_id, target_chat_id=query.message.chat_id)
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
        session.current_screen_idx = len(SCREENS) if session.review_editing_mode else session.current_screen_idx + 1
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
            avni_wit = get_avni_commentary(field_id, target_field['options']['en'][opt_idx], session.lang)
            
            if target_field['type'] == 'buttons_multi':
                current_ans = session.answers.get(field_id, [])
                if chosen_option in current_ans: current_ans.remove(chosen_option)
                else: current_ans.append(chosen_option)
                session.answers[field_id] = current_ans
                await query.answer()
            else:
                session.answers[field_id] = chosen_option
                await query.answer()
                if len(screen_data['fields']) == 1:
                    session.current_screen_idx = len(SCREENS) if session.review_editing_mode else session.current_screen_idx + 1

            await render_screen(update, context, target_message_id=query.message.message_id, target_chat_id=query.message.chat_id, avni_push=avni_wit)

async def inbound_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = context.user_data.get(user_id)
    if not session or session.is_submitted or session.current_screen_idx >= len(SCREENS): return

    screen_data = SCREENS[session.current_screen_idx]
    target_field_id = session.awaiting_custom_field_id or next((f['id'] for f in screen_data['fields'] if f['type'] in ['text', 'media'] and not session.answers.get(f['id'])), None)
    if not target_field_id: return

    val = update.message.text.strip() if update.message.text else "[File/Photo Document]"
    session.answers[target_field_id] = val
    if target_field_id == "q1": session.name = val
    session.awaiting_custom_field_id = None

    if check_screen_satisfied(session, screen_data):
        session.current_screen_idx = len(SCREENS) if session.review_editing_mode else session.current_screen_idx + 1
        
    await render_screen(update, context, target_chat_id=update.effective_chat.id)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT | filters.VOICE | filters.PHOTO, inbound_message_handler))
    print("🚀 Coach Avni Personality Engine Active and Polling.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
