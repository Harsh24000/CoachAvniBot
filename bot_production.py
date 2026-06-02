#!/usr/bin/env python3
import os
import asyncio
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TOKEN:
    print("ERROR: TELEGRAM_TOKEN not in .env!")
    exit(1)

SCREENS = {
    1: {"title": "👤 Basic Info", "questions": {
        "name": {"q": "👤 Full name?", "type": "text", "req": True},
        "age": {"q": "🎂 Age?", "type": "text", "req": True},
    }},
    2: {"title": "💼 Work", "questions": {
        "profession": {"q": "💼 Profession?", "type": "buttons", "req": True, "opts": ["💻 Software", "👨‍⚕️ Doctor", "📚 Student", "➕ Other"], "custom": True},
    }},
    3: {"title": "🎯 Ready?", "questions": {
        "ready": {"q": "🚀 Ready to start?", "type": "buttons", "req": True, "opts": ["🔥 YES!", "✅ Yes", "🤔 Maybe"], "custom": False},
    }},
}

class Session:
    def __init__(self):
        self.screen = 1
        self.inputs = {}
        self.name = None
        self.waiting_custom = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    context.user_data[uid] = Session()
    
    text = "🤖 MEALZY COACH 🎉\n\n💪 Transform Your Body\n✨ Transform Your Life\n\nLet's go! 🚀"
    kb = [[InlineKeyboardButton("🎯 START", callback_data="start")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb))

async def show_screen(update: Update, context: ContextTypes.DEFAULT_TYPE, query=None):
    uid = update.effective_user.id
    if uid not in context.user_data:
        await start(update, context)
        return
    
    sess = context.user_data[uid]
    sn = sess.screen
    
    if sn > 3:
        msg = f"🎉 COMPLETE!\n\n👋 {sess.name or 'Champion'}!\n\nYour profile READY!\nCoaches creating plan!\n\nThank you! 🙏"
        if query:
            await query.edit_message_text(msg)
        else:
            await update.message.reply_text(msg)
        return
    
    screen = SCREENS[sn]
    prog = int((sn / 3) * 100)
    bar = "█" * (prog // 10) + "░" * (10 - (prog // 10))
    
    text = f"{bar} {prog}%\n\n{screen['title']}\n\n"
    
    for fk, qd in screen['questions'].items():
        if fk in sess.inputs:
            text += f"{qd['q']} ✅\n"
    
    buttons = []
    first_unanswered = None
    for fk, qd in screen['questions'].items():
        if fk not in sess.inputs and first_unanswered is None:
            first_unanswered = (fk, qd)
    
    if first_unanswered:
        fk, qd = first_unanswered
        text += f"\n{qd['q']} [Tap below]\n\n"
        
        if qd['type'] == 'buttons':
            for i, opt in enumerate(qd['opts']):
                btn = InlineKeyboardButton(opt, callback_data=f"a_{sn}_{fk}_{i}")
                if not buttons or len(buttons[-1]) >= 2:
                    buttons.append([btn])
                else:
                    buttons[-1].append(btn)
            
            if qd.get('custom'):
                buttons.append([InlineKeyboardButton("📝 Custom", callback_data=f"c_{sn}_{fk}")])
        
        elif qd['type'] == 'text':
            text += "*(Type in chat)*\n\n"
    
    buttons.append([InlineKeyboardButton("✅ NEXT →", callback_data=f"nx_{sn}")])
    
    kb = InlineKeyboardMarkup(buttons)
    if query:
        await query.edit_message_text(text, reply_markup=kb)
    else:
        await update.message.reply_text(text, reply_markup=kb)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    
    if uid not in context.user_data:
        await start(update, context)
        return
    
    await query.answer()
    sess = context.user_data[uid]
    data = query.data
    
    if data == "start":
        sess.screen = 1
        await show_screen(update, context, query)
        return
    
    if data.startswith("a_"):
        parts = data.split("_")
        sn, fk, aidx = int(parts[1]), parts[2], int(parts[3])
        screen = SCREENS[sn]
        qd = screen['questions'][fk]
        ans = qd['opts'][aidx]
        
        sess.inputs[fk] = ans
        qtxt = qd['q'].replace("?", "").strip()
        await update.callback_query.message.reply_text(f"✅ {qtxt}\n→ {ans}")
        
        await asyncio.sleep(0.5)
        await show_screen(update, context, query)
    
    if data.startswith("c_"):
        parts = data.split("_")
        sn, fk = int(parts[1]), parts[2]
        sess.waiting_custom = (sn, fk)
        screen = SCREENS[sn]
        qd = screen['questions'][fk]
        qtxt = qd['q'].replace("?", "").strip()
        await update.callback_query.message.reply_text(f"📝 Type your answer for:\n{qtxt}")
    
    if data.startswith("nx_"):
        sn = int(data.split("_")[1])
        screen = SCREENS[sn]
        
        for fk, qd in screen['questions'].items():
            if qd['req'] and fk not in sess.inputs:
                await query.answer("⚠️ Answer all!", show_alert=True)
                return
        
        sess.screen += 1
        sess.inputs = {}
        await show_screen(update, context, query)

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in context.user_data:
        await start(update, context)
        return
    
    sess = context.user_data[uid]
    txt = update.message.text.strip()
    
    if sess.waiting_custom:
        sn, fk = sess.waiting_custom
        screen = SCREENS[sn]
        qd = screen['questions'][fk]
        
        sess.inputs[fk] = txt
        sess.waiting_custom = None
        
        qtxt = qd['q'].replace("?", "").strip()
        await update.message.reply_text(f"✅ {qtxt}\n→ {txt}")
        
        await asyncio.sleep(1)
        await show_screen(update, context)
        return
    
    sn = sess.screen
    screen = SCREENS[sn]
    
    text_fields = [k for k, v in screen['questions'].items() if v['type'] == 'text' and k not in sess.inputs]
    if not text_fields:
        return
    
    fk = text_fields[0]
    qd = screen['questions'][fk]
    
    sess.inputs[fk] = txt
    sess.name = txt if fk == 'name' else sess.name
    
    qtxt = qd['q'].replace("?", "").strip()
    await update.message.reply_text(f"✅ {qtxt}\n→ {txt}")
    
    await asyncio.sleep(1)
    await show_screen(update, context)

def main():
    print("🚀 BOT STARTING...\n")
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    
    print("✅ BOT RUNNING!\n")
    app.run_polling()

if __name__ == "__main__":
    main()
