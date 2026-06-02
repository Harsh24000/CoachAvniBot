#!/usr/bin/env python3
"""
COACH AVNI BOT - GROUPED SCREENS VERSION
✅ Multiple related questions per screen
✅ Dynamic inline keyboard with checkmarks
✅ App-like experience in Telegram
✅ Zero confusion & fast completion
"""

import os
import sys
import asyncio
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TOKEN:
    print("ERROR: TELEGRAM_TOKEN not found in .env")
    sys.exit(1)

# ============================================================================
# SCREENS CONFIGURATION (Grouped Questions)
# ============================================================================

SCREENS = [
    # --- TEXT INPUT SCREENS (Kept separate for clean UX) ---
    {"id": 1, "section": "👤 About You", "fields": [
        {"id": "name", "text": "👤 What's your full name?", "type": "text", "required": True}
    ]},
    {"id": 2, "section": "👤 About You", "fields": [
        {"id": "age", "text": "🎂 What's your age?", "type": "text", "required": True}
    ]},
    {"id": 3, "section": "👤 About You", "fields": [
        {"id": "height", "text": "📏 Height (cm)?", "type": "text", "required": True}
    ]},
    {"id": 4, "section": "👤 About You", "fields": [
        {"id": "weight", "text": "⚖️ Weight (kg)?", "type": "text", "required": True}
    ]},
    
    # --- GROUPED BUTTON SCREENS ---
    {"id": 5, "section": "💼 Work & Details", "fields": [
        {"id": "profession", "text": "💼 Profession?", "type": "buttons", "required": True,
         "options": ["💻 Software Eng", "👨‍⚕️ Doctor", "📚 Student", "🏫 Teacher", "👔 Business", "🤵 Consultant", "🏥 Healthcare", "📊 Finance", "🎯 Sales", "➕ Other"]},
        {"id": "sex", "text": "⚡ Biological sex?", "type": "buttons", "required": True,
         "options": ["👨 Male", "👩 Female", "🌈 Other"]}
    ]},
    
    {"id": 6, "section": "🍽️ Diet & Food", "fields": [
        {"id": "diet", "text": "🍽️ Dietary preference?", "type": "buttons", "required": True,
         "options": ["🍗 Non-Veg", "🥕 Vegetarian", "🥚 Eggetarian", "🌱 Vegan", "☪️ Jain"]},
        {"id": "dislike", "text": "🚫 Foods you HATE? (Select all)", "type": "buttons_multi", "required": False,
         "options": ["🥒 Bitter gourd", "🍆 Eggplant", "🍄 Mushroom", "🐟 Fish", "🥚 Egg", "🥛 Dairy"]}
    ]},
    
    {"id": 7, "section": "☀️ Your Day", "fields": [
        {"id": "wake", "text": "🌅 Wake up time?", "type": "buttons", "required": True,
         "options": ["⏰ 5:00", "⏰ 6:00", "⏰ 7:00", "⏰ 8:00", "🛏️ 8:30+"]},
        {"id": "sleep", "text": "😴 Sleep time?", "type": "buttons", "required": True,
         "options": ["🌙 9:00", "🌙 10:00", "🌙 11:00", "🌙 12:00", "🌙 12:30+"]}
    ]},
    
    {"id": 8, "section": "💪 Fitness & Goals", "fields": [
        {"id": "activity", "text": "💪 Active days per week?", "type": "buttons", "required": True,
         "options": ["😴 0", "🚶 1-2", "🏃 3-4", "🏋️ 5-6", "⚡ 7"]},
        {"id": "goal", "text": "🎯 PRIMARY goal?", "type": "buttons", "required": True,
         "options": ["📉 Lose weight", "💪 Build muscle", "⚡ Get stronger", "✨ All"]}
    ]},
    
    {"id": 9, "section": "🤝 Commitment", "fields": [
        {"id": "days", "text": "📅 Training days per week?", "type": "buttons", "required": True,
         "options": ["1️⃣ 1", "2️⃣ 2", "3️⃣ 3", "4️⃣ 4", "5️⃣ 5", "6️⃣ 6", "7️⃣ 7"]},
        {"id": "ready", "text": "🚀 Ready to START?", "type": "buttons", "required": True,
         "options": ["🔥 YES! 100%!", "✅ Yes, somewhat", "🤔 Maybe", "⏳ Not yet"]}
    ]},
]

class UserSession:
    def __init__(self):
        self.current_screen_idx = 0
        self.answers = {}
        self.name = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    context.user_data[user_id] = UserSession()
    
    text = """🤖 ╔════════════════════════════════════════╗
   ║  WELCOME TO MEALZY COACH! 🎉           ║
   ║                                         ║
   ║  💪 Transform Your Body               ║
   ║  🧠 Transform Your Mind               ║
   ║  ✨ Transform Your Life               ║
   ╚════════════════════════════════════════╝

📋 Smart Assessment
✅ App-like grouped screens
✅ Tap to select
✅ Fast & Easy

Let's go! 🚀"""
    
    keyboard = [[InlineKeyboardButton("🎯 START NOW!", callback_data="start")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def render_screen(update: Update, context: ContextTypes.DEFAULT_TYPE, query=None):
    user_id = update.effective_user.id
    if user_id not in context.user_data:
        await start(update, context)
        return
        
    session = context.user_data[user_id]
    
    # Check for completion
    if session.current_screen_idx >= len(SCREENS):
        final_msg = f"""🎉 ╔════════════════════════════════════════╗
   ║  ASSESSMENT COMPLETE! 🏆               ║
   ╚════════════════════════════════════════╝

👋 {session.name or 'Champion'}! You did it! 💪

Your fitness profile is READY!
Coaches are creating your plan NOW! 🚀"""
        
        if query:
            await query.edit_message_text(final_msg)
        else:
            await update.message.reply_text(final_msg)
        return

    screen_data = SCREENS[session.current_screen_idx]
    
    # 1. Build the text layout
    progress = int(((session.current_screen_idx) / len(SCREENS)) * 100)
    bar = "█" * (progress // 10) + "░" * (10 - (progress // 10))
    
    text_lines = [f"{bar} {progress}%", "", f"*{screen_data['section']}*", ""]
    
    all_required_answered = True
    
    for field in screen_data['fields']:
        ans = session.answers.get(field['id'])
        is_answered = bool(ans) or (field['type'] == 'buttons_multi' and ans is not None)
        
        if field['required'] and not is_answered:
            all_required_answered = False
            
        if is_answered:
            text_lines.append(f"{field['text']} ✅")
        else:
            if field['type'] == 'text':
                text_lines.append(f"{field['text']} [Type in chat] ⌨️")
            else:
                text_lines.append(f"{field['text']} [Tap below] ✔️")
        
        text_lines.append("───────────────────")

    text = "\n".join(text_lines)
    
    # 2. Build the Keyboard
    keyboard = []
    
    for field in screen_data['fields']:
        if field['type'] in ['buttons', 'buttons_multi']:
            # Section Header
            clean_name = field['text'].replace('?', '').replace('!', '').split(' ', 1)[-1]
            keyboard.append([InlineKeyboardButton(f"Select {clean_name}", callback_data="ignore")])
            
            # Options Buttons
            row = []
            for opt in field['options']:
                display_opt = opt
                ans = session.answers.get(field['id'])
                
                # Check if this specific option is selected
                if field['type'] == 'buttons' and ans == opt:
                    display_opt = f"✅ {opt}"
                elif field['type'] == 'buttons_multi' and ans and opt in ans:
                    display_opt = f"✅ {opt}"
                    
                cb_data = f"sel_{field['id']}_{field['options'].index(opt)}"
                row.append(InlineKeyboardButton(display_opt, callback_data=cb_data))
                
                # Max 2 buttons per row
                if len(row) == 2:
                    keyboard.append(row)
                    row = []
            if row:
                keyboard.append(row)
    
    # 3. Add NEXT button if applicable
    if any(f['type'] in ['buttons', 'buttons_multi'] for f in screen_data['fields']):
        if all_required_answered:
            keyboard.append([InlineKeyboardButton("✅ NEXT ➡️", callback_data="next_screen")])
        else:
            keyboard.append([InlineKeyboardButton("🔒 Answer above to proceed", callback_data="locked")])

    markup = InlineKeyboardMarkup(keyboard) if keyboard else None
    
    if query:
        await query.edit_message_text(text, reply_markup=markup, parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=markup, parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    
    if user_id not in context.user_data:
        await start(update, context)
        return
        
    session = context.user_data[user_id]
    data = query.data
    
    if data == "start":
        await query.answer()
        session.current_screen_idx = 0
        await render_screen(update, context, query)
        return
        
    if data == "ignore":
        await query.answer("Header tapped. Select an option below! 👇", show_alert=False)
        return
        
    if data == "locked":
        await query.answer("⚠️ Please answer all required questions first!", show_alert=True)
        return
        
    if data == "next_screen":
        await query.answer("Moving on! 🚀")
        session.current_screen_idx += 1
        await render_screen(update, context, query)
        return
        
    if data.startswith("sel_"):
        parts = data.split("_", 2)
        field_id = parts[1]
        opt_idx = int(parts[2])
        
        # Find field and option text
        screen_data = SCREENS[session.current_screen_idx]
        field = next((f for f in screen_data['fields'] if f['id'] == field_id), None)
        
        if not field:
            await query.answer("Error finding field", show_alert=True)
            return
            
        selected_opt = field['options'][opt_idx]
        
        if field['type'] == 'buttons':
            # Single select
            session.answers[field_id] = selected_opt
        elif field['type'] == 'buttons_multi':
            # Multi select toggle
            current_ans = session.answers.get(field_id, [])
            if selected_opt in current_ans:
                current_ans.remove(selected_opt)
            else:
                current_ans.append(selected_opt)
            session.answers[field_id] = current_ans
            
        await query.answer()
        await render_screen(update, context, query)

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id not in context.user_data:
        await start(update, context)
        return
        
    session = context.user_data[user_id]
    if session.current_screen_idx >= len(SCREENS):
        return
        
    screen_data = SCREENS[session.current_screen_idx]
    
    # We only process text if the current screen has a text field
    text_fields = [f for f in screen_data['fields'] if f['type'] == 'text']
    
    if not text_fields:
        # Ignore text if the current screen only has buttons
        await update.message.reply_text("Please use the buttons above to answer! 👆")
        return
        
    # Assume 1 text field per screen to avoid complex multi-text-parsing
    field = text_fields[0]
    text = update.message.text.strip()
    
    session.answers[field['id']] = text
    
    if field['id'] == 'name':
        session.name = text
        await update.message.reply_text(f"✅ Awesome, {text}!")
    else:
        await update.message.reply_text(f"✅ Saved!")
        
    session.current_screen_idx += 1
    await asyncio.sleep(0.5)
    await render_screen(update, context)

def main():
    print("\n" + "=" * 70)
    print("📱 GROUPED SCREENS BOT RUNNING")
    print("=" * 70)
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    
    app.run_polling()

if __name__ == "__main__":
    main()
