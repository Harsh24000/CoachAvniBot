#!/usr/bin/env python3
"""
COACH AVNI - ULTIMATE 62-QUESTION LIVE CHAT SIMULATION PROTOCOL
Features:
- Pure peer-to-peer chat simulation (one question at a time).
- Infused with Avni's sharp wit, dynamic feedback, and supportive energy.
- Real-time personalization using the client's name across all 62 points.
- Localized multi-language framework (English & Hindi).
- Automated macro allocation & professional HTML-to-PDF generation.
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
    print("CRITICAL CONFIG ERROR: TELEGRAM_TOKEN missing from environment variables.")
    sys.exit(1)

# FULL MASTER LIST: ALL 62 STRATEGIC QUESTIONS (ONE-AT-A-TIME FLOW)
SCREENS = [
    # PHASE 1: BIOLOGICAL & PROFESSIONAL PROFILE
    {"id": "q1", "section": "👤 Biological Profile", "type": "text", "required": True,
     "text": {"en": "🔥 Let's cut right through the noise. First things first, what's your full name?", 
              "hi": "🔥 चलिए सीधे मुद्दे पर आते हैं। सबसे पहले, आपका पूरा नाम क्या है?"}},
    {"id": "q2", "section": "👤 Biological Profile", "type": "text", "required": True,
     "text": {"en": "Awesome {name}. Now, how many years young are you? (Give me the real number!)", 
              "hi": "बहुत बढ़िया {name}। अब ये बताओ कि तुम्हारी उम्र कितने साल है? (सच-सच बताना!)"}},
    {"id": "q3", "section": "👤 Biological Profile", "type": "text", "required": True,
     "text": {"en": "Got it. What's your current height in centimeters, {name}?", 
              "hi": "ठीक है। सेंटीमीटर (cm) में तुम्हारी ऊंचाई कितनी है, {name}?"}},
    {"id": "q4", "section": "👤 Biological Profile", "type": "text", "required": True,
     "text": {"en": "And where is your current scale weight sitting at in kilograms?", 
              "hi": "और अभी तुम्हारा वजन कितने किलोग्राम (kg) पर अटका हुआ है?"}},
    {"id": "q5", "section": "👤 Biological Profile", "type": "buttons", "required": True,
     "text": {"en": "What do you do for work, {name}? Let's see how much desk-sitting we are up against:", 
              "hi": "{name}, तुम काम क्या करते हो? जरा देखें दिनभर में कितनी देर बैठे रहते हो:"},
     "options": {"en": ["💻 Engineer/Tech", "👨‍⚕️ Doctor/Medical", "📚 Student", "👔 Business Owner", "🤵 Consultant", "📊 Corporate Desk"], 
                 "hi": ["💻 इंजीनियर/टेक", "👨‍⚕️ डॉक्टर/मेडिकल", "📚 छात्र", "👔 बिजनेस ओनर", "🤵 सलाहकार", "📊 कॉर्पोरेट डेस्क"]}},
    {"id": "q6", "section": "👤 Biological Profile", "type": "buttons", "required": True,
     "text": {"en": "And what is your biological sex?", 
              "hi": "और तुम्हारा जैविक लिंग (Sex) क्या है?"},
     "options": {"en": ["👨 Male", "👩 Female"], "hi": ["👨 पुरुष", "👩 महिला"]}},

    # PHASE 2: DIETARY HABITS & KITCHEN PROTOCOLS
    {"id": "q7", "section": "🍏 Diet & Kitchen", "type": "buttons", "required": True,
     "text": {"en": "Let's talk food, {name}. What's your primary dietary style?", 
              "hi": "अब खाने की बात करते हैं, {name}। तुम्हारी मुख्य आहार शैली क्या है?"},
     "options": {"en": ["🍗 Non-Veg", "🥕 Veg", "🥚 Eggitarian", "🌱 Vegan", "☪️ Jain Vegetarian"], 
                 "hi": ["🍗 मांसाहारी", "🥕 शाकाहारी", "🥚 अंडाहारी", "🌱 वीगन", "☪️ जैन शाकाहारी"]}},
    {"id": "q8", "section": "🍏 Diet & Kitchen", "type": "buttons_multi", "required": False,
     "text": {"en": "Any foods you absolutely can't stand or refuse to eat? (Pick your food enemies, {name}):", 
              "hi": "कोई ऐसा भोजन जो तुम्हें बिल्कुल पसंद नहीं है? (अपनी नापसंद चुनो {name}):"},
     "options": {"en": ["🥒 Bitter Gourd", "🍆 Eggplant", "🍄 Mushroom", "🐟 Fish", "🥛 Dairy Products", "🧅 No Onion/Garlic"], 
                 "hi": ["🥒 करेला", "🍆 बैंगन", "🍄 मशरूम", "🐟 मछली", "🥛 डेयरी उत्पाद", "🧅 बिना प्याज/लहसुन"]}},
    {"id": "q9", "section": "🍏 Diet & Kitchen", "type": "buttons", "required": True,
     "text": {"en": "Which style of cuisine makes your soul the happiest?", 
              "hi": "किस तरह का खाना तुम्हें मानसिक रूप से सबसे ज्यादा खुश करता है?"},
     "options": {"en": ["🍛 North Indian", "🫓 South Indian", "🥗 Continental", "🥢 Asian Mix"], 
                 "hi": ["🍛 उत्तर भारतीय", "🫓 दक्षिण भारतीय", "🥗 कॉन्टिनेंटल", "🥢 एशियन मिक्स"]}},
    {"id": "q10", "section": "🍏 Diet & Kitchen", "type": "buttons", "required": True,
     "text": {"en": "Be honest, {name}: how dependent are you on tea or coffee to actually function like a human?", 
              "hi": "सच बताना {name}: एक सामान्य इंसान की तरह काम करने के लिए चाय या कॉफी पर कितने निर्भर हो?"},
     "options": {"en": ["☕ Total lifeline", "🍵 Occasionally", "🚫 Total Abstinence"], 
                 "hi": ["☕ हाँ, इसके बिना पत्ता नहीं हिलता", "🍵 कभी-कभी", "🚫 बिल्कुल नहीं"]}},

    # PHASE 3: CHRONOBIOLOGY & DAILY ROUTINE TIMINGS
    {"id": "q11", "section": "🌅 Daily Chronobiology", "type": "buttons", "required": True,
     "text": {"en": "What time does your alarm usually shock you awake, {name}?", 
              "hi": "{name}, तुम्हारा अलार्म आमतौर पर सुबह कितने बजे बजता है?"},
     "options": {"en": ["⏰ 5:00 AM", "⏰ 6:00 AM", "⏰ 7:00 AM", "⏰ 8:00 AM+"], 
                 "hi": ["⏰ सुबह 5:00 बजे", "⏰ सुबह 6:00 बजे", "⏰ सुबह 7:00 बजे", "⏰ सुबह 8:00+ बाद"]}},
    {"id": "q12", "section": "🌅 Daily Chronobiology", "type": "buttons", "required": True,
     "text": {"en": "When do you typically eat your very first solid meal of the day?", 
              "hi": "तुम आमतौर पर दिन का अपना पहला ठोस भोजन किस समय खाते हो?"},
     "options": {"en": ["🌅 8:00 AM", "🌅 9:00 AM", "🌅 10:00 AM", "⏭️ Skip Breakfast"], 
                 "hi": ["🌅 सुबह 8:00 बजे", "🌅 सुबह 9:00 बजे", "🌅 सुबह 10:00 बजे", "⏭️ नाश्ता नहीं"]}},
    {"id": "q13", "section": "🌅 Daily Chronobiology", "type": "buttons", "required": True,
     "text": {"en": "When do you step into active work mode or log on?", 
              "hi": "तुम अपने काम की शुरुआत किस समय करते हो?"},
     "options": {"en": ["💼 8:00 AM", "💼 9:00 AM", "💼 10:00 AM", "⌛ Shift Rotation"], 
                 "hi": ["💼 सुबह 8:00 बजे", "💼 सुबह 9:00 बजे", "💼 सुबह 10:00 बजे", "⌛ शिफ्ट बदलती है"]}},
    {"id": "q14", "section": "🌅 Daily Chronobiology", "type": "buttons", "required": True,
     "text": {"en": "What time do you usually escape or log off from work?", 
              "hi": "तुम आमतौर पर अपने काम से कब आज़ाद होते हो?"},
     "options": {"en": ["⏰ 5:00 PM", "⏰ 6:00 PM", "⏰ 7:00 PM", "🌙 9:00 PM+"], 
                 "hi": ["⏰ शाम 5:00 बजे", "⏰ शाम 6:00 बजे", "⏰ शाम 7:00 बजे", "🌙 रात 9:00+ बाद"]}},
    {"id": "q15", "section": "🌅 Daily Chronobiology", "type": "buttons", "required": True,
     "text": {"en": "What's the typical window for your lunch, {name}?", 
              "hi": "{name}, तुम्हारे दोपहर के भोजन का समय क्या है?"},
     "options": {"en": ["🍱 12:30 PM", "🍱 1:30 PM", "🍱 2:30 PM", "⏳ Variable Daily"], 
                 "hi": ["🍱 दोपहर 12:30 बजे", "🍱 दोपहर 1:30 बजे", "🍱 दोपहर 2:30 बजे", "⏳ कोई तय समय नहीं"]}},
    {"id": "q16", "section": "🌅 Daily Chronobiology", "type": "buttons", "required": True,
     "text": {"en": "When does dinner land on your plate?", 
              "hi": "तुम रात का खाना आमतौर पर किस समय खाते हो?"},
     "options": {"en": ["🍽️ 7:00 PM", "🍽️ 8:00 PM", "🍽️ 9:00 PM", "🌙 10:00 PM+"], 
                 "hi": ["🍽️ शाम 7:00 बजे", "🍽️ रात 8:00 बजे", "🍽️ रात 9:00 बजे", "🌙 रात 10:00+ बाद"]}},
    {"id": "q17", "section": "🌅 Daily Chronobiology", "type": "buttons", "required": True,
     "text": {"en": "What time are lights completely out? (Be honest, scrolling reels in the dark counts as awake!)", 
              "hi": "रात को तुम्हारी बत्ती कितने बजे बुझती है? (सच बताना, अंधेरे में रील्स देखना भी जागने में ही आता है!)"},
     "options": {"en": ["🌙 10:00 PM", "🌙 11:00 PM", "🌙 12:00 AM", "🦉 1:00 AM+"], 
                 "hi": ["🌙 रात 10:00 बजे", "🌙 रात 11:00 बजे", "🌙 रात 12:00 बजे", "🦉 रात 1:00+ बाद"]}},
    {"id": "q18", "section": "🌅 Daily Chronobiology", "type": "buttons", "required": True,
     "text": {"en": "How often are you raiding the snack cabinet between meals, {name}?", 
              "hi": "दोपहर या रात के खाने के बीच में कितनी बार स्नैक्स के डिब्बे खाली होते हैं, {name}?"},
     "options": {"en": ["🍪 Constant grazing", "🍏 Occasional snack", "🚫 Clean - No Snacking"], 
                 "hi": ["🍪 लगातार कुछ न कुछ चाहिए", "🍏 कभी-कभार", "🚫 बिल्कुल नहीं"]}},
    {"id": "q19", "section": "🌅 Daily Chronobiology", "type": "buttons", "required": True,
     "text": {"en": "How much water are you actually drinking every single day?", 
              "hi": "तुम रोजाना असल में कितना पानी पीते हो?"},
     "options": {"en": ["🥛 < 1 Litre", "💧 1-2 Litres", "🚰 2-3 Litres", "🌊 3+ Litres"], 
                 "hi": ["🥛 1 लीटर से कम", "💧 1-2 लीटर", "🚰 2-3 लीटर", "🌊 3 लीटर से ज्यादा"]}},
    {"id": "q20", "section": "🌅 Daily Chronobiology", "type": "buttons", "required": True,
     "text": {"en": "How often is restaurant food, Swiggy, or Zomato landing on your plate, {name}?", 
              "hi": "{name}, बाहर का खाना, Swiggy या Zomato हफ्ते में कितनी बार ऑर्डर हो रहा है?"},
     "options": {"en": ["🍔 Daily", "🍕 2-3x / Week", "🥗 Rarely", "✅ Never/Home only"], 
                 "hi": ["🍔 रोज़ाना", "🍕 हफ्ते में 2-3 बार", "🥗 बहुत कम", "✅ कभी नहीं/सिर्फ घर का"]}},
    {"id": "q21", "section": "🌅 Daily Chronobiology", "type": "buttons", "required": True,
     "text": {"en": "What is your regular relationship with alcohol?", 
              "hi": "क्या तुम अल्कोहल (शराब) का सेवन करते हो?"},
     "options": {"en": ["🍺 High Volume", "🍷 Social/Weekends", "🚫 Completely Clean"], 
                 "hi": ["🍺 काफी ज्यादा", "🍷 केवल वीकेंड", "🚫 बिल्कुल नहीं"]}},
    {"id": "q22", "section": "🌅 Daily Chronobiology", "type": "buttons", "required": True,
     "text": {"en": "Do you currently smoke or consume tobacco items?", 
              "hi": "क्या तुम धूम्रपान (Smoke) या तंबाकू का सेवन करते हो?"},
     "options": {"en": ["🚬 Yes, daily", "💨 Socially", "🚫 No"], 
                 "hi": ["🚬 हाँ, रोज़ाना", "💨 कभी-कभी", "🚫 नहीं"]}},

    # PHASE 4: MEDICAL CLINICAL SYMPTOMS & VITAL ASSESSMENT
    {"id": "q23", "section": "🏥 Vitals & Health", "type": "buttons_multi", "required": False,
     "text": {"en": "Have you been formally diagnosed with any metabolic conditions, {name}?", 
              "hi": "{name}, क्या तुम्हें इनमें से कोई स्वास्थ्य समस्या है?"},
     "options": {"en": ["🔬 Diabetes", "🧬 Thyroid", "🔴 PCOS/PCOD", "❤️ Hypertension", "🍗 Fatty Liver", "✅ None"], 
                 "hi": ["🔬 डायबिटीज", "🧬 थायराइड", "🔴 पीसीओएस", "❤️ हाई बीपी", "🍗 फैटी लिवर", "✅ कोई नहीं"]}},
    {"id": "q24", "section": "🏥 Vitals & Health", "type": "text", "required": False,
     "text": {"en": "Any old or current structural injuries I need to protect while building your workout layout?", 
              "hi": "कोई पुरानी या वर्तमान चोट जिसके बारे में मुझे वर्कआउट डिज़ाइन करते समय ध्यान रखना चाहिए?"}},
    {"id": "q25", "section": "🏥 Vitals & Health", "type": "buttons", "required": True,
     "text": {"en": "Do you suffer from any known severe allergies?", 
              "hi": "क्या तुम्हें किसी प्रकार की गंभीर एलर्जी है?"},
     "options": {"en": ["✅ None", "🍔 Food Specific", "💊 Pharmaceutical", "🌫️ Environmental"], 
                 "hi": ["✅ कोई नहीं", "🍔 भोजन से", "💊 दवाओं से", "🌫️ धूल/मौसम से"]}},
    {"id": "q26", "section": "🏥 Vitals & Health", "type": "text", "required": False,
     "text": {"en": "Any specific prescription medications you are currently taking, {name}?", 
              "hi": "{name}, क्या तुम कोई डॉक्टर की बताई नियमित दवाएं ले रहे हो?"}},
    {"id": "q27", "section": "🏥 Vitals & Health", "type": "buttons", "required": True,
     "text": {"en": "Time for a direct gut check—how is your digestion behaving?", 
              "hi": "ज़रा पेट का हाल बताओ—आजकल तुम्हारा डाइजेशन कैसा चल रहा है?"},
     "options": {"en": ["🟢 Smooth & Regular", "⚠️ Chronic Bloating", "🛑 Regular Constipation", "🔥 Acid Reflux"], 
                 "hi": ["🟢 बिल्कुल ठीक", "⚠️ गैस और ब्लोटिंग", "🛑 कब्ज की समस्या", "🔥 एसिडिटी"]}},
    {"id": "q28", "section": "🏥 Vitals & Health", "type": "buttons", "required": True,
     "text": {"en": "How intense are those sugar cravings hitting you, {name}?", 
              "hi": "{name}, मीठा खाने की क्रेविंग कितनी खतरनाक होती है?"},
     "options": {"en": ["🍩 Intense daily monster", "🍫 Post-meals only", "🚫 Seldom/Never"], 
                 "hi": ["🍩 रोज़ाना बहुत तेज़", "🍫 सिर्फ खाने के बाद", "🚫 कभी नहीं"]}},
    {"id": "q29", "section": "🏥 Vitals & Health", "type": "buttons", "required": True,
     "text": {"en": "Do you regularly hit a wall and get hit by random energy slumps?", 
              "hi": "क्या तुम्हें दिन में अचानक थकान या भारी सुस्ती महसूस होती है?"},
     "options": {"en": ["🥱 Severe 3 PM crash", "🥱 Constant flatline fatigue", "⚡ Steady performance"], 
                 "hi": ["🥱 दोपहर में भारी सुस्ती", "🥱 हमेशा थकान होना", "⚡ एनर्जी बनी रहती है"]}},
    {"id": "q30", "section": "🏥 Vitals & Health", "type": "buttons", "required": True,
     "text": {"en": "Have you noticed any major changes happening with your skin or hair health lately?", 
              "hi": "क्या तुम्हें हाल ही में अपनी त्वचा या बालों में कोई बुरा बदलाव दिख रहा है?"},
     "options": {"en": ["⚠️ High hair fall", "⚠️ Acne breakouts", "✅ Stable/Optimal"], 
                 "hi": ["⚠️ बालों का झड़ना", "⚠️ मुंहासे/एक्ने", "✅ सब सामान्य है"]}},
    {"id": "q31", "section": "🏥 Vitals & Health", "type": "buttons", "required": True,
     "text": {"en": "How often do you catch yourself getting sick or caught by seasonal bugs, {name}?", 
              "hi": "{name}, तुम कितनी जल्दी बीमार पड़ते हो या वायरल की चपेट में आते हो?"},
     "options": {"en": ["🤧 Catch colds easily", "💊 Depend on immunity meds", "🛡️ High immunity/Rarely sick"], 
                 "hi": ["🤧 सर्दी-खांसी जल्दी होना", "💊 दवाओं पर निर्भर", "🛡️ बहुत ही कम"]}},

    # PHASE 5: MICRO-NUTRIENTS, COGNITION & EXPERIENTIAL HABITS
    {"id": "q32", "section": "🧠 Cognition & Micronutrients", "type": "buttons", "required": True,
     "text": {"en": "Are you supplementing your Vitamin D3 regularly, {name}?", 
              "hi": "{name}, क्या तुम विटामिन D3 के सप्लीमेंट ले रहे हो?"},
     "options": {"en": ["💊 Daily/Weekly dose", "🧪 Deficient (No Pill)", "❌ Not Tracking"], 
                 "hi": ["💊 हाँ, नियमित रूप से", "🧪 कमी है पर नहीं ले रहे", "❌ कोई जानकारी नहीं"]}},
    {"id": "q33", "section": "🧠 Cognition & Micronutrients", "type": "buttons", "required": True,
     "text": {"en": "What about your Vitamin B12 status?", 
              "hi": "तुम्हारे विटामिन B12 का क्या हाल है?"},
     "options": {"en": ["💊 Regular Intake", "🧪 Deficient Lab Stats", "❌ Not Tracking"], 
                 "hi": ["💊 नियमित सेवन", "🧪 शरीर में कमी है", "❌ कोई जानकारी नहीं"]}},
    {"id": "q34", "section": "🧠 Cognition & Micronutrients", "type": "buttons", "required": True,
     "text": {"en": "Are you taking an Omega-3 or pure Fish Oil supplement?", 
              "hi": "क्या तुम ओमेगा-3 या फिश ऑयल सप्लीमेंट लेते हो?"},
     "options": {"en": ["✅ Yes, daily", "❌ No Intake"], 
                 "hi": ["✅ हाँ, रोज़ाना", "❌ नहीं लेते"]}},
    {"id": "q35", "section": "🧠 Cognition & Micronutrients", "type": "buttons", "required": True,
     "text": {"en": "Do you pop a regular daily multivitamin?", 
              "hi": "क्या तुम कोई मल्टीविटामिन लेते हो?"},
     "options": {"en": ["✅ Consuming", "❌ No Intake"], 
                 "hi": ["✅ हाँ, ले रहे हैं", "❌ नहीं लेते"]}},
    {"id": "q36", "section": "🧠 Cognition & Micronutrients", "type": "buttons", "required": True,
     "text": {"en": "Do you apply chemical hair dye or salon treatments frequently, {name}?", 
              "hi": "{name}, क्या तुम अक्सर बालों में केमिकल डाई या आर्टिफिशियल ट्रीटमेंट्स कराते हो?"},
     "options": {"en": ["💇 Yes, frequently", "🚫 Minimal/Never"], 
                 "hi": ["💇 हाँ, अक्सर", "🚫 बहुत कम/कभी नहीं"]}},
    {"id": "q37", "section": "🧠 Cognition & Micronutrients", "type": "buttons", "required": True,
     "text": {"en": "Do you suffer from brain fog or scattered focus issues during work hours?", 
              "hi": "क्या तुम्हें काम के दौरान फोकस की कमी या मानसिक धुंधलापन महसूस होता है?"},
     "options": {"en": ["🧠 Yes, regularly", "😐 Mid-day sluggishness", "✅ Clear/Sharp"], 
                 "hi": ["🧠 हाँ, नियमित रूप से", "😐 दोपहर में फोकस कम", "✅ बिल्कुल साफ फोकस"]}},
    {"id": "q38", "section": "🧠 Cognition & Micronutrients", "type": "buttons", "required": True,
     "text": {"en": "How often do unexpected mood swings or anxiety spikes creep up?", 
              "hi": "तुम्हें मूड स्विंग्स या एंग्जायटी के झटके कितनी बार महसूस होते हैं?"},
     "options": {"en": ["⚡ Frequent shifts", "🌊 Under high stress only", "😊 Balanced/Grounded"], 
                 "hi": ["⚡ अक्सर बदलाव", "🌊 सिर्फ अत्यधिक तनाव में", "😊 शांत रहता हूँ"]}},
    {"id": "q39", "section": "🧠 Cognition & Micronutrients", "type": "buttons", "required": True,
     "text": {"en": "How do you physically feel the exact moment you get out of bed, {name}?", 
              "hi": "{name}, सुबह उठते ही तुम्हें शारीरिक रूप से कैसा महसूस होता है?"},
     "options": {"en": ["🐌 Wake up wrecked/tired", "⚡ Fast recovery/Fresh", "🩹 Slow healing/Stiff joints"], 
                 "hi": ["🐌 उठने पर थकान होना", "⚡ शरीर फ्रेश होता है", "🩹 शरीर में जकड़न/दर्द"]}},
    {"id": "q40", "section": "🧠 Cognition & Micronutrients", "type": "buttons", "required": True,
     "text": {"en": "Rate your overall daily mental stress load from 1 to 5:", 
              "hi": "रोजाना के मानसिक तनाव को 1 से 5 के पैमाने पर रेट करो:"},
     "options": {"en": ["😊 1-2 (Low)", "😐 3 (Manageable)", "😫 4-5 (High Screen)"], 
                 "hi": ["😊 1-2 (बहुत कम)", "😐 3 (सामान्य)", "😫 4-5 (अत्यधिक तनाव)"]}},
    {"id": "q41", "section": "🧠 Cognition & Micronutrients", "type": "buttons", "required": True,
     "text": {"en": "When you sleep, are you completely out cold or tossing and turning all night?", 
              "hi": "जब तुम सोते हो, तो तुम्हारी नींद की गहराई कैसी होती है?"},
     "options": {"en": ["🥱 Fragmented/Wakeful", "😐 Average Depth", "😴 Deep Nightly State"], 
                 "hi": ["🥱 बार-बार नींद टूटना", "😐 सामान्य नींद", "😴 गहरी और अच्छी नींद"]}},

    # PHASE 6: BIOMECHANICS & STRUCTURAL INTEGRITY
    {"id": "q42", "section": "🏃 Biomechanics & Structure", "type": "buttons", "required": True,
     "text": {"en": "Has anyone ever told you that you snore pretty heavily, {name}?", 
              "hi": "क्या तुम सोते समय काफी भारी खर्राटे लेते हो, {name}?"},
     "options": {"en": ["🔊 Yes, heavy snoring", "🔉 Light/Occasional", "🚫 No Snoring"], 
                 "hi": ["🔊 हाँ, भारी खर्राटे", "🔉 हल्के/कभी-कभार", "🚫 बिल्कुल नहीं"]}},
    {"id": "q43", "section": "🏃 Biomechanics & Structure", "type": "buttons", "required": True,
     "text": {"en": "What is your core emotional state right after your feet hit the floor?", 
              "hi": "सुबह बिस्तर से उठते ही तुम्हारी मानसिक स्थिति कैसी होती है?"},
     "options": {"en": ["✅ Ready to crush the day", "Usually groggy 🥱", "Exhausted baseline 💤"], 
                 "hi": ["✅ एकदम तरोताज़ा", "आमतौर पर सुस्ती 🥱", "थका हुआ/कमज़ोर 💤"]}},
    {"id": "q44", "section": "🏃 Biomechanics & Structure", "type": "buttons", "required": True,
     "text": {"en": "Are dark circles making a permanent camp under your eyes?", 
              "hi": "क्या तुम्हारी आंखों के नीचे डार्क सर्कल्स स्थायी रूप से बन गए हैं?"},
     "options": {"en": ["👁️ Prominent/Dark", "👁️ Faint shadows", "✅ Fully clean/None"], 
                 "hi": ["👁️ बहुत गहरे", "👁️ हल्के", "✅ एक भी नहीं"]}},
    {"id": "q45", "section": "🏃 Biomechanics & Structure", "type": "buttons", "required": True,
     "text": {"en": "Any history of rapid, unexplained shifts in your body weight, {name}?", 
              "hi": "{name}, क्या तुम्हारे वजन में कभी अचानक बहुत बड़ा बदलाव हुआ है?"},
     "options": {"en": ["📈 Gained fast lately", "📉 Dropped fast lately", "✅ Steady baseline weight"], 
                 "hi": ["📈 हाल ही में तेजी से बढ़ा", "📉 हाल ही में तेजी से घटा", "✅ वजन स्थिर रहा है"]}},
    {"id": "q46", "section": "🏃 Biomechanics & Structure", "type": "buttons", "required": True,
     "text": {"en": "Do your hands, feet, or face feel swollen and puffy when you wake up?", 
              "hi": "क्या तुम्हारे हाथ, पैर या चेहरे पर अक्सर सूजन और भारीपन महसूस होता है?"},
     "options": {"en": ["💧 Heavy ankles/hands", "💧 High face puffiness", "🚫 No fluid retention"], 
                 "hi": ["💧 टखनों/हाथों में सूजन", "💧 चेहरे पर भारीपन", "🚫 नहीं"]}},
    {"id": "q47", "section": "🏃 Biomechanics & Structure", "type": "buttons", "required": True,
     "text": {"en": "Do you get freezing cold hands or cold feet, even when room temperature is warm?", 
              "hi": "क्या तुम्हारे हाथ या पैर सामान्य मौसम में भी बहुत ठंडे पड़ जाते हैं?"},
     "options": {"en": ["🥶 Yes, constantly", "🥶 Only in peak winter", "🚫 Never occurs"], 
                 "hi": ["🥶 हाँ, हमेशा", "🥶 सिर्फ सर्दियों में", "🚫 नहीं"]}},
    {"id": "q48", "section": "🏃 Biomechanics & Structure", "type": "buttons", "required": True,
     "text": {"en": "Are you dealing with any nagging joint or spine pain, {name}?", 
              "hi": "{name}, क्या तुम जोड़ों या शरीर के किसी स्थायी दर्द से परेशान हो?"},
     "options": {"en": ["💥 Lower back issues", "💥 Knee pain structural", "💥 Neck/Shoulders strain", "✅ Fully pain-free"], 
                 "hi": ["💥 पीठ के निचले हिस्से में", "💥 घुटनों का दर्द", "💥 गर्दन/कंधे में दर्द", "✅ कोई दर्द नहीं है"]}},
    {"id": "q49", "section": "🏃 Biomechanics & Structure", "type": "buttons", "required": True,
     "text": {"en": "How quickly do you start gasping for air when moving up structural inclines?", 
              "hi": "चलने-फिरने या सीढ़ियां चढ़ते समय तुम्हारी सांस कितनी जल्दी फूलती है?"},
     "options": {"en": ["🫁 Gasping up stairs", "🫁 Only during sprints", "⚡ Strong cardiorespiratory"], 
                 "hi": ["🫁 सीढ़ियां चढ़ते ही", "🫁 केवल तेज़ दौड़ने पर", "⚡ स्टैमिना अच्छा है"]}},
    {"id": "q50", "section": "🏃 Biomechanics & Structure", "type": "buttons", "required": True,
     "text": {"en": "How many hours is your spine glued to an office desk chair daily?", 
              "hi": "तुम रोजाना कितने घंटे कुर्सी पर लगातार बैठकर बिताते हो?"},
     "options": {"en": ["🚶 Below 4 Hours", "😐 4 - 7 Hours", "💀 8+ Hours total sink"], 
                 "hi": ["🚶 4 घंटे से कम", "😐 4 से 7 घंटे", "💀 8 घंटे से ज्यादा"]}},
    {"id": "q51", "section": "🏃 Biomechanics & Structure", "type": "buttons_multi", "required": False,
     "text": {"en": "Any major chronic health trends running rampant through your family tree, {name}?", 
              "hi": "{name}, क्या तुम्हारे परिवार के मेडिकल इतिहास में इनमें से कोई बीमारी रही है?"},
     "options": {"en": ["🩸 Diabetes trend", "❤️ Cardiovascular issues", "🧬 Chronic Obesity traits", "✅ Clear Medical History"], 
                 "hi": ["🩸 डायबिटीज का इतिहास", "❤️ दिल की बीमारी", "🧬 मोटापे की समस्या", "✅ कोई बीमारी नहीं रही"]}},
    {"id": "q52", "section": "🏃 Biomechanics & Structure", "type": "buttons", "required": True,
     "text": {"en": "How would you describe the natural hydration of your skin structural layers?", 
              "hi": "तुम अपनी त्वचा की प्राकृतिक स्थिति को कैसे दर्शाओगे?"},
     "options": {"en": ["🍂 Very dry/flaky", "💧 Excess oily zones", "✨ Well-hydrated/Normal"], 
                 "hi": ["🍂 बहुत रूखी/ड्राई", "💧 बहुत ऑइली", "✨ बिल्कुल सामान्य/स्वस्थ"]}},
    {"id": "q53", "section": "🏃 Biomechanics & Structure", "type": "buttons", "required": True,
     "text": {"en": "How stable is your daily neuro-appetite signaling?", 
              "hi": "तुम्हारी दैनिक भूख का पैटर्न कैसा रहता है?"},
     "options": {"en": ["🔥 Uncontrollable/Bingeing", "🧊 Low appetite/Forget to eat", "✅ Stable patterns"], 
                 "hi": ["🔥 बहुत ज्यादा भूख", "🧊 बहुत कम भूख लगना", "✅ बिल्कुल स्थिर और सामान्य"]}},

    # PHASE 7: MACRO METABOLIC TARGETS & MINDSET GAP ANALYSIS
    {"id": "q54", "section": "🎯 Targets & Mindset", "type": "buttons", "required": True,
     "text": {"en": "Have you ever meticulously tracked calories or macros before, {name}?", 
              "hi": "{name}, क्या तुमने पहले कभी ईमानदारी से कैलोरी या मैक्रोज़ ट्रैक करने की कोशिश की है?"},
     "options": {"en": ["📈 Yes, did macros", "📉 Tried and abandoned", "🚫 Never tracked tracking"], 
                 "hi": ["📈 हाँ, ट्रैक किया है", "📉 कोशिश की पर नहीं हुआ", "🚫 कभी ट्रैक नहीं किया"]}},
    {"id": "q55", "section": "🎯 Targets & Mindset", "type": "buttons", "required": True,
     "text": {"en": "If we could wave a magic wand right now, what is our absolute primary focus?", 
              "hi": "अगर अभी कोई जादू की छड़ी मिल जाए, तो तुम्हारा सबसे पहला और मुख्य लक्ष्य क्या होगा?"},
     "options": {"en": ["📉 Aggressive Fat Loss", "💪 Hypertrophy Lean Muscle", "⚡ Athletic Endurance", "❤️ Metabolic Correction"], 
                 "hi": ["📉 तेज़ फैट लॉस", "💪 लीन मसल गेन", "⚡ एथलेटिक स्टैमिना", "❤️ मेटाबॉलिज्म ठीक करना"]}},
    {"id": "q56", "section": "🎯 Targets & Mindset", "type": "buttons", "required": True,
     "text": {"en": "What has been your biggest roadmap blocker to internal consistency in the past?", 
              "hi": "अतीत में तुम्हारे नियमित न रह पाने की सबसे बड़ी बाधा क्या रही है?"},
     "options": {"en": ["⏳ Extreme time deficit", "🍳 Cooking complexity", "🍿 Social/Travel habits", "🧠 Lack of internal drive"], 
                 "hi": ["⏳ समय की भारी कमी", "🍳 खाना बनाने की झंझट", "🍿 सोशल लाइफ/ट्रैवल", "🧠 मोटिवेशन की कमी"]}},
    {"id": "q57", "section": "🎯 Targets & Mindset", "type": "buttons", "required": True,
     "text": {"en": "Rate your overall daily energy flow, {name}—are you a firecracker or a slow burn?", 
              "hi": "{name}, तुम्हारी पूरे दिन की एनर्जी कैसी रहती है—आग की तरह या ठंडी?"},
     "options": {"en": ["📈 Peak morning/low night", "📉 Flatline low energy all day", "⚡ High baseline all day"], 
                 "hi": ["📈 सुबह तेज़/रात को कम", "📉 हमेशा लो एनर्जी होना", "⚡ पूरे दिन शानदार एनर्जी"]}},
    {"id": "q58", "section": "🎯 Targets & Mindset", "type": "buttons", "required": True,
     "text": {"en": "Realistically, how many hours can you clip out for your physical training weekly?", 
              "hi": "तुम वर्कआउट के लिए हर हफ्ते असलियत में कितना समय निकाल सकते हो?"},
     "options": {"en": ["⏳ Under 2 Hours", "⏳ 2 to 4 Hours", "⚡ 5+ Hours fully ready!"], 
                 "hi": ["⏳ हर हफ्ते 2 घंटे से कम", "⏳ हर हफ्ते 2 से 4 घंटे", "⚡ हर हफ्ते 5+ घंटे से ज्यादा"]}},
    {"id": "q59", "section": "🎯 Targets & Mindset", "type": "buttons", "required": True,
     "text": {"en": "How often do aerated sodas or energy drinks make an appearance in your routine, {name}?", 
              "hi": "{name}, तुम कोल्ड ड्रिंक्स या मीठे पेय पदार्थों का कितना सेवन करते हो?"},
     "options": {"en": ["🥤 Yes, almost daily", "🥤 Socially/Weekends", "🚫 Complete clean limit"], 
                 "hi": ["🥤 हाँ, लगभग रोज़ाना", "🥤 कभी-कभी/वीकेंड पर", "🚫 बिल्कुल बंद"]}},
    {"id": "q60", "section": "🎯 Targets & Mindset", "type": "buttons", "required": True,
     "text": {"en": "What's our targeted countdown timeline to make this physical transformation real?", 
              "hi": "इस ट्रांसफॉर्मेशन को सच करने के लिए तुम्हारा समय सीमा लक्ष्य क्या है?"},
     "options": {"en": ["🔥 4 to 8 Weeks", "⚡ 12 Weeks (Recommended)", "⏳ Long-term shift"], 
                 "hi": ["🔥 4 से 8 हफ्ते", "⚡ 12 हफ्ते (सुझाया गया)", "⏳ लंबे समय का लाइफस्टाइल बदलाव"]}},
    {"id": "q62", "section": "🎯 Targets & Mindset", "type": "text", "required": False,
     "text": {"en": "Any final burning remarks or personal notes you want to leave for me directly before calculations?", 
              "hi": "कोई अंतिम बात या संदेश जो तुम सीधे मेरे तक पहुंचाना चाहते हो?"}},

    # PHASE 8: BIOMETRIC ASSET UPLOAD
    {"id": "q61", "section": "📸 Biometric Assets", "type": "media", "required": False,
     "text": {"en": "Last step, {name}! Drop a clear full-length posture photo here so I can evaluate structural alignment framework. Completely confidential between us.", 
              "hi": "अंतिम कदम, {name}! यहाँ एक साफ फुल-लेंथ फोटो भेजो ताकि मैं तुम्हारे शरीर के पोस्चर का मूल्यांकन कर सकूँ। ये सिर्फ मेरे पास सुरक्षित रहेगी।"}}
]

# THE INTERACTIVE WIT ENGINE
def get_avni_live_wit(field_id, val, name):
    comments = {
        "q5": {
            "💻 Engineer/Tech": f"An engineer! Say no more, {name}. Translation: Your shoulders are completely rolled forward, your hip flexors are locked up from sitting, and your code compiles faster than your metabolism right now. Let's fix that.",
            "👨‍⚕️ Doctor/Medical": f"A doctor! Saving lives but living on lukewarm coffee and skipped lunches, right {name}? Time to write you a prescription for your own health.",
            "📊 Corporate Desk": f"The classic corporate desk lockdown. Sitting 9 hours straight is toxic for your glutes, {name}. We are going to spark that energy back up."
        },
        "q10": {
            "☕ Total lifeline": f"Running on pure premium liquid adrenaline! Coffee isn't a food group, {name}. We're going to fix your actual natural base energy.",
            "🚫 Total Abstinence": f"Zero caffeine dependency? Wow, absolute respect, {name}! Your central nervous system must be beautifully grounded."
        },
        "q17": {
            "🦉 1:00 AM+": f"1 AM?! {name}, your fat-burning human growth hormones are weeping in the dark. Late nights are the silent, undetected killer of fat loss goals.",
            "🌙 10:00 PM": f"10 PM? Absolute legendary sleep architecture. Your circadian rhythm is already locked and loaded to win."
        },
        "q18": {
            "🍪 Constant grazing": f"Constant grazing means your blood sugar never rests and your insulin is on a roller coaster. We're putting an end to that cycle, {name}!",
            "🚫 Clean - No Snacking": f"Boom! No snacking is a massive structural win for your digestive tract. Love to see it."
        },
        "q20": {
            "🍔 Daily": f"Daily Zomato/Swiggy? Oof, {name}, the amount of hidden industrial seed oils and sky-high sodium in those meals is holding you hostage. Time to clear the slate.",
            "🍕 2-3x / Week": f"2-3 times a week is normal, but commercial kitchens smuggle in crazy calories. Let's optimize it."
        },
        "q27": {
            "⚠️ Chronic Bloating": f"Chronic bloating means your gut microbiome is screaming for structural support. We are going to fix your absorption first.",
            "🟢 Smooth & Regular": f"A smooth gut is an absolute metabolic superpower, {name}. That means half our nutrition battle is already won."
        },
        "q28": {
            "🍩 Intense daily monster": f"That daily sugar monster isn't a lack of willpower, {name}—it's your body crashing from improper macro balances. I'll steady that out.",
            "🚫 Seldom/Never": f"No sugar cravings? Perfect. That makes structuring our calorie targets clean and simple."
        }
    }
    return comments.get(field_id, {}).get(val, "")

class UserSession:
    def __init__(self):
        self.lang = "en"
        self.idx = 0
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
    context.user_data[user_id] = UserSession()
    
    kb = [[InlineKeyboardButton("🇬🇧 Let's chat in English", callback_data="lang_en")],
          [InlineKeyboardButton("🇮🇳 हिन्दी में बात करते हैं", callback_data="lang_hi")]]
    
    await update.message.reply_text(
        "🔥 <b>Hey! Coach Avni here.</b>\n\nNo boring, dry corporate check-in forms. No robotic questionnaires. Just deep biological data, zero judgment, and a highly strategic blueprint engineered for your messy, chaotic life.\n\nLet's get down to business. Pick your language to begin:",
        reply_markup=InlineKeyboardMarkup(kb), parse_mode="HTML"
    )

async def ask_next_chat_step(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id, message_id=None, avni_commentary=""):
    user_id = update.effective_user.id
    session = context.user_data[user_id]
    ln = session.lang

    if session.idx >= len(SCREENS):
        session.review_mode = True
        text = f"📋 <b>Alright {session.name}, I've compiled your entire 62-point comprehensive profile!</b>\n\nLook over your entries. If any data point looks weird, simply click its button below to instantly edit it. If everything looks solid, smash that submit button!"
        kb = []
        for s in SCREENS:
            ans = session.answers.get(s['id'], "Skipped/None")
            ans_str = ", ".join(ans) if isinstance(ans, list) else str(ans)
            if len(ans_str) > 20: ans_str = ans_str[:17] + "..."
            lbl = f"✏️ {s['id'].upper()} ({s['section']}): {ans_str}"
            kb.append([InlineKeyboardButton(lbl, callback_data=f"edit_{s['id']}")])
            
        kb.append([InlineKeyboardButton("🚀 PROFILE LOOKS PERFECT - SUBMIT NOW", callback_data="final_submit")])
        
        if message_id:
            await context.bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, reply_markup=InlineKeyboardMarkup(kb), parse_mode="HTML")
        else:
            await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="HTML")
        return

    q_data = SCREENS[session.idx]
    raw_text = q_data['text'][ln].replace("{name}", session.name)
    
    full_message_text = ""
    if avni_commentary:
        full_message_text += f"🎙️ <b>Coach Avni:</b> <i>\"{avni_commentary}\"</i>\n\n━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    full_message_text += f"💬 <b>[{session.idx + 1}/62]</b> {raw_text}"
    
    kb = []
    if q_data['type'] in ["buttons", "buttons_multi"]:
        is_multi = (q_data['type'] == "buttons_multi")
        for idx, opt in enumerate(q_data['options'][ln]):
            current_ans = session.answers.get(q_data['id'], [])
            lbl = opt
            if is_multi and opt in current_ans:
                lbl = f"✅ {opt}"
            kb.append([InlineKeyboardButton(lbl, callback_data=f"ans_{q_data['id']}_{idx}")])
        if is_multi:
            kb.append([InlineKeyboardButton("➡️ Confirm Selections & Continue", callback_data=f"confirm_multi_{q_data['id']}")])
    elif q_data['type'] == "media":
        kb.append([InlineKeyboardButton("⏭️ Skip photo asset for now", callback_data="ans_q61_skip")])
        
    if session.idx > 0 and not session.review_mode:
        kb.append([InlineKeyboardButton("⬅️ Go Back a Step", callback_data="nav_back")])

    if message_id:
        try:
            await context.bot.edit_message_text(full_message_text, chat_id=chat_id, message_id=message_id, reply_markup=InlineKeyboardMarkup(kb), parse_mode="HTML")
            return
        except Exception:
            pass

    await context.bot.send_message(chat_id=chat_id, text=full_message_text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="HTML")

async def button_dispatcher(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    session = context.user_data.get(user_id)
    if not session: return await query.answer("Session timeout! Type /start to reboot.")
    
    data = query.data
    await query.answer()

    if data.startswith("lang_"):
        session.lang = data.split("_")[1]
        await query.message.delete()
        await ask_next_chat_step(update, context, query.message.chat_id)
        return

    if data == "nav_back":
        if session.idx > 0: session.idx -= 1
        await ask_next_chat_step(update, context, query.message.chat_id, message_id=query.message.message_id)
        return

    if data.startswith("edit_"):
        field_id = data.split("_")[1]
        for i, s in enumerate(SCREENS):
            if s['id'] == field_id:
                session.idx = i
                break
        await ask_next_chat_step(update, context, query.message.chat_id, message_id=query.message.message_id, avni_commentary="Let's update this parameter real quick.")
        return

    if data.startswith("confirm_multi_"):
        if session.review_mode:
            session.idx = len(SCREENS)
        else:
            session.idx += 1
        await ask_next_chat_step(update, context, query.message.chat_id, message_id=query.message.message_id, avni_commentary="Saved those selections inside your blueprint.")
        return

    if data == "final_submit":
        await query.message.delete()
        session.is_submitted = True
        m = session.calculate_macros()
        
        success_text = (
            f"🚀 <b>BOOM! ALL 62 TARGET CHANNELS SECURED.</b>\n\n"
            f"Spectacular focus, {session.name}. I've successfully calculated your primary metabolic indicators and engineered your baseline targets.\n\n"
            f"📊 <b>METABOLIC PROFILE DATA:</b>\n"
            f"• BMR (Resting metabolic output): <code>{m['bmr']} kcal</code>\n"
            f"• Estimated TDEE (Active Maintenance): <code>{m['tdee']} kcal</code>\n\n"
            f"⚡ <b>TARGET PERFORMANCE MACROMATRIX:</b>\n"
            f"• 🍗 Protein Core: <code>{m['protein']}g</code>\n"
            f"• 🌾 Complex Carbs: <code>{m['carbs']}g</code>\n"
            f"• 🥑 Structural Fats: <code>{m['fats']}g</code>\n\n"
            f"Your personal diagnostic report brief has been generated below. Click the scheduling button to secure your strategy call and kick off execution phase!"
        )
        kb = [[InlineKeyboardButton("📅 UNLOCK STRATEGY SESSION", url=CALENDLY_LINK)]]
        await context.bot.send_message(chat_id=query.message.chat_id, text=success_text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="HTML")
        
        if HAS_WEASYPRINT:
            try:
                html_data = f"""
                <html>
                <body style="font-family: Arial, sans-serif; padding: 40px; color: #2D3748;">
                    <div style="background: #1A365D; color: white; padding: 30px; text-align: center; border-radius: 6px;">
                        <h1>COACH AVNI MASTER BIOPRINT REPORT</h1>
                        <p>62-Point Strategic Diagnostic Audit for: {session.name}</p>
                    </div>
                    <h2 style="color: #2B6CB0; border-bottom: 2px solid #E2E8F0; padding-bottom: 5px; margin-top: 30px;">Metabolic Targets</h2>
                    <p><b>Target Baseline TDEE:</b> {m['tdee']} kcal</p>
                    <p><b>Protein Target:</b> {m['protein']}g | <b>Carbs:</b> {m['carbs']}g | <b>Fats:</b> {m['fats']}g</p>
                </body>
                </html>
                """
                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                    HTML(string=html_data).write_pdf(tmp.name)
                    with open(tmp.name, "rb") as f:
                        await context.bot.send_document(chat_id=query.message.chat_id, document=BytesIO(f.read()), filename=f"Coach_Avni_{session.name}_Brief.pdf")
                os.unlink(tmp.name)
            except Exception as e:
                print(f"PDF creation failure: {e}")
        return

    if data.startswith("ans_"):
        parts = data.split("_")
        field_id = parts[1]
        q_data = SCREENS[session.idx]
        
        if parts[2] == "skip":
            session.answers[field_id] = "Skipped Photo Asset"
            wit_remark = "No worries, we can manage visual markers on our 1-on-1 strategy call. Let's head to final review."
        else:
            opt_idx = int(parts[2])
            chosen_val = q_data['options'][session.lang][opt_idx]
            
            if q_data['type'] == "buttons_multi":
                current_ans = session.answers.get(field_id, [])
                if chosen_val in current_ans:
                    current_ans.remove(chosen_val)
                else:
                    current_ans.append(chosen_val)
                session.answers[field_id] = current_ans
                await ask_next_chat_step(update, context, query.message.chat_id, message_id=query.message.message_id)
                return
            else:
                session.answers[field_id] = chosen_val
                eng_val = q_data['options']['en'][opt_idx]
                wit_remark = get_avni_live_wit(field_id, eng_val, session.name)

        if not wit_remark:
            wit_remark = f"Solid. Logged that in your dossier, {session.name}."

        if session.review_mode:
            session.idx = len(SCREENS)
        else:
            session.idx += 1
            
        await ask_next_chat_step(update, context, query.message.chat_id, message_id=query.message.message_id, avni_commentary=wit_remark)

async def message_dispatcher(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = context.user_data.get(user_id)
    if not session or session.is_submitted: return

    val = update.message.text.strip() if update.message.text else "[Visual/Photo Asset Registered]"
    q_data = SCREENS[session.idx]
    
    session.answers[q_data['id']] = val
    
    if q_data['id'] == "q1":
        session.name = val
        remark = f"Awesome name! Let's pull back the curtain on your daily habits, {session.name}."
    else:
        remark = f"Got it, {session.name}. Added to your medical file."

    if session.review_mode:
        session.idx = len(SCREENS)
    else:
        session.idx += 1

    await ask_next_chat_step(update, context, update.effective_chat.id, avni_commentary=remark)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_dispatcher))
    app.add_handler(MessageHandler(filters.TEXT | filters.VOICE | filters.PHOTO, message_dispatcher))
    print("🚀 Coach Avni 62-Question Personality Framework Online.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
