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
