
from MusicSp import app
from MusicSp.utils.database import get_assistant

from pyrogram import Client, filters, enums
from pyrogram.types import (
    ChatMemberUpdated,
    ChatJoinRequest,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Message,
)

from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageChops
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_DB_URI

import asyncio
import random
import os
import aiohttp
from logging import getLogger

LOGGER = getLogger(__name__)

mongo = AsyncIOMotorClient(MONGO_DB_URI)
db = mongo["Myanmar_DB"]
welcomedb = db["welcome_toggle_system"]


DEFAULT_WELCOME_BG = "https://files.catbox.moe/jebxwm.jpg"

async def get_welcome(chat_id: int):
    data = await welcomedb.find_one({"chat_id": chat_id})
    if not data:
        return True
    return data.get("welcome", True)

async def enable_welcome(chat_id: int):
    await welcomedb.update_one(
        {"chat_id": chat_id},
        {"$set": {"welcome": True}},
        upsert=True
    )

async def disable_welcome(chat_id: int):
    await welcomedb.update_one(
        {"chat_id": chat_id},
        {"$set": {"welcome": False}},
        upsert=True
    )

class temp:
    MELCOW = {}

def circle(pfp, size=(390, 390), brightness_factor=1.4):
    pfp = pfp.resize(size).convert("RGBA")
    pfp = ImageEnhance.Brightness(pfp).enhance(brightness_factor)

    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size[0], size[1]), fill=255)

    pfp.putalpha(mask)
    return pfp


async def download_bg():
    bg_path = "downloads/shiviwel2.png"
    if os.path.exists(bg_path):
        return bg_path
    os.makedirs("downloads", exist_ok=True)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(DEFAULT_WELCOME_BG) as resp:
                if resp.status == 200:
                    with open(bg_path, "wb") as f:
                        f.write(await resp.read())
                    return bg_path
    except:
        pass
    return None


async def welcomepic(pic, user, chatname, id, uname, brightness_factor=1.3):
    bg_file = await download_bg()
    if bg_file and os.path.exists(bg_file):
        background = Image.open(bg_file).convert("RGBA")
    else:
        background = Image.new("RGBA", (1280, 720), (30, 30, 30, 255))

    try:
        pfp = Image.open(pic).convert("RGBA")
        pfp = circle(pfp, size=(390, 390), brightness_factor=brightness_factor)
        
        background.paste(pfp, (90, 115), pfp)
    except:
        pass

    output_path = f"downloads/welcome_{id}.png"
    background.save(output_path)
    return output_path
 
@app.on_message(filters.command("welcome") & filters.group)
async def welcome_cmd(_, message: Message):
    chat = message.chat
    chat_id = chat.id

    user = await app.get_chat_member(chat_id, message.from_user.id)
    if user.status not in (enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER):
        return await message.reply_text("**» ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ʜᴀɴᴅʟᴇ ᴡᴇʟᴄᴏᴍᴇ ꜱʏꜱᴛᴇᴍ**")

    state = await get_welcome(chat_id)   
    status = "ᴇɴᴀʙʟᴇᴅ" if state else "ᴅɪꜱᴀʙʟᴇᴅ"

    btn = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("ᴇɴᴀʙʟᴇ", callback_data=f"wlc_on_{chat_id}"),
            InlineKeyboardButton("ᴅɪꜱᴀʙʟᴇ", callback_data=f"wlc_off_{chat_id}")
        ]
    ])

    await message.reply_text(
        f"» ᴄᴜʀʀᴇɴᴛʟʏ ᴡᴇʟᴄᴏᴍᴇ ꜱᴛᴀᴛᴜꜱ **{status}** ɪɴ **{chat.title}**",
        reply_markup=btn
    )
    
@app.on_callback_query(filters.regex("wlc_"))
async def welcome_toggle(_, query):
    data = query.data.split("_")
    action = data[1]
    chat_id = int(data[2])

    member = await app.get_chat_member(chat_id, query.from_user.id)
    if member.status not in (enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER):
        return await query.answer("ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴅᴍɪɴ ʙᴀʙʏ 🥺", show_alert=True)

    if action == "on":
        await enable_welcome(chat_id)
        new_status = "ᴇɴᴀʙʟᴇᴅ"
    else:
        await disable_welcome(chat_id)
        new_status = "ᴅɪꜱᴀʙʟᴇᴅ"

    chat = await app.get_chat(chat_id)

    await query.message.edit_text(
        f"» ᴡᴇʟᴄᴏᴍᴇ ᴍᴇꜱꜱᴀɢᴇ **{new_status}** ɪɴ **{chat.title}** ʙʏ :- **{query.from_user.mention}**"
    )
    await query.answer()


@app.on_chat_member_updated(filters.group, group=-3)
async def greet_new_member(_, member: ChatMemberUpdated):
    chat_id = member.chat.id
    is_enabled = await get_welcome(chat_id)
    if not is_enabled:
        return

    user = member.new_chat_member.user if member.new_chat_member else None
    if not user:
        return

    if member.new_chat_member and not member.old_chat_member and member.new_chat_member.status != "kicked":
        try:
            pic = await app.download_media(
                user.photo.big_file_id, file_name=f"pp{user.id}.png"
            )
        except:
            pic = None

        old = temp.MELCOW.get(f"welcome-{chat_id}")
        if old:
            try:
                await old.delete()
            except:
                pass

        welcomeimg = await welcomepic(
            pic,
            user.first_name,
            member.chat.title,
            user.id,
            user.username
        )

        msg = await app.send_photo(
            chat_id,
            photo=welcomeimg,
            caption=f"""
**⏤͟͟͞͞★ ʜᴇʟʟᴏ ᴅᴇᴀʀ ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ : {member.chat.title}**

<u>**❖ ᴜsᴇʀ sʜᴏʀᴛ ɪɴғᴏ**</u>

**➻ ɴᴀᴍᴇ »** {user.mention}
**➻ ᴄʜᴀᴛ_ɪᴅ »** `{user.id}`
**➻ ᴜ_ɴᴀᴍᴇ »** @{user.username}
**➻ DEV »** @Cores_999
**➻ ᴛʜᴀɴᴋs ғᴏʀ ᴊᴏɪɴɪɴɢ ᴜs ⚡️~! 
❅─────✧❅✦❅✧─────❅**
""",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "⊚ ᴧᴅᴅ ᴍᴇ ᴛᴏ ʏᴏυʀ ᴄʜᴧᴛ ⊚",
                        url=f"https://t.me/{app.username}?startgroup=true"
                    )
                ]
            ])
        )

        async def delete_welcome():
            await asyncio.sleep(30)
            try:
                await msg.send_photo if False else await msg.delete()
                if f"welcome-{chat_id}" in temp.MELCOW:
                    del temp.MELCOW[f"welcome-{chat_id}"]
            except:
                pass

        asyncio.create_task(delete_welcome())
        temp.MELCOW[f"welcome-{chat_id}"] = msg
