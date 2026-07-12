import time
import re
import random
import asyncio

from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram.errors.exceptions.not_acceptable_406 import ChannelPrivate
from pyrogram.errors.exceptions.flood_420 import SlowmodeWait
from AnonXMusic import YouTube

import config
from AnonXMusic import app
from AnonXMusic.misc import _boot_
from AnonXMusic.plugins.sudo.sudoers import sudoers_list
from AnonXMusic.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_lang,
    is_banned_user,
    is_on_off,
    blacklist_chat,
)
from AnonXMusic.utils.decorators.language import LanguageStart
from AnonXMusic.utils.formatters import get_readable_time
from AnonXMusic.utils.inline import help_pannel, private_panel, start_panel
from config import BANNED_USERS, LOGGER_ID
from strings import get_string


@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    await add_served_user(message.from_user.id)
    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]
        if name[0:4] == "help":
            keyboard = help_pannel(_)

            return await message.reply_photo(
                photo=random.choice(config.START_IMG_URL),
                caption=_["help_1"].format(config.SUPPORT_CHAT),
                reply_markup=keyboard,
            )
        if name[0:3] == "sud":
            await sudoers_list(client=client, message=message, _=_)
            if await is_on_off(2):
                return await app.send_message(
                    chat_id=config.LOGGER_ID,
                    text=f"{message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ᴄʜᴇᴄᴋ <b>sᴜᴅᴏʟɪsᴛ</b>.\n\n<b>ᴜsᴇʀ ɪᴅ :</b> <code>{message.from_user.id}</code>\n<b>ᴜsᴇʀɴᴀᴍᴇ :</b> @{message.from_user.username}",
                )
            return
        if name[0:3] == "inf":
            m = await message.reply_text("\U0001f50e")
            query = (str(name)).replace("info_", "", 1)
            try:
                title, duration, duration_sec, thumbnail, vidid = await YouTube.details(
                    query, videoid=True
                )
                link = f"https://www.youtube.com/watch?v={query}"
                info = await YouTube._extract_info(link)
                views = info.get("view_count", 0)
                views_short = f"{views:,}" if views else "N/A"
                channel = info.get("uploader", "Unknown")
                channellink = info.get("uploader_url", link)
                published = info.get("upload_date", "Unknown")
                searched_text = _["start_6"].format(
                    title, duration, views_short, published, channellink, channel, app.mention
                )
                key = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(text=_["S_B_8"], url=link),
                            InlineKeyboardButton(text=_["S_B_9"], url=config.SUPPORT_CHAT),
                        ],
                    ]
                )
                await m.delete()
                await app.send_photo(
                    chat_id=message.chat.id,
                    photo=thumbnail,
                    caption=searched_text,
                    reply_markup=key,
                )
            except Exception as e:
                await m.edit_text(f"\u274c Error: `{e}`")
            if await is_on_off(2):
                return await app.send_message(
                    chat_id=config.LOGGER_ID,
                    text=f"{message.from_user.mention} \u1d0a\u1d1cs\u1d1b s\u1d1b\u1d00\u0280\u1d1b\u1d07\u1d05 \u1d1b\u029c\u1d07 \u0299\u1d0f\u1d1b \u1d1b\u1d0f \u1d04\u029c\u1d07\u1d04\u1d0b <b>\u1d1b\u0280\u1d00\u1d04\u1d0b \u026a\u0274\u0493\u1d0f\u0280\u1d0d\u1d00\u1d1b\u026a\u1d0f\u0274</b>.\n\n<b>\u1d1cs\u1d07\u0280 \u026a\u1d05 :</b> <code>{message.from_user.id}</code>\n<b>\u1d1cs\u1d07\u0280\u0274\u1d00\u1d0d\u1d07 :</b> @{message.from_user.username}",
                )
    else:
        out = private_panel(_)
        await message.reply_photo(
            photo=random.choice(config.START_IMG_URL),
            caption=_["start_2"].format(message.from_user.mention, app.mention),
            reply_markup=InlineKeyboardMarkup(out),
        )
        if await is_on_off(2):
            return await app.send_message(
                chat_id=config.LOGGER_ID,
                text=f"{message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ.\n\n<b>ᴜsᴇʀ ɪᴅ :</b> <code>{message.from_user.id}</code>\n<b>ᴜsᴇʀɴᴀᴍᴇ :</b> @{message.from_user.username}",
            )


@app.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_gp(client, message: Message, _):
    out = start_panel(_)
    uptime = int(time.time() - _boot_)
    try:
        await message.reply_photo(
        photo=random.choice(config.START_IMG_URL),
        caption=_["start_1"].format(app.mention, get_readable_time(uptime)),
        reply_markup=InlineKeyboardMarkup(out),
    )
        return await add_served_chat(message.chat.id)
    except ChannelPrivate:
        return
    except SlowmodeWait as e:
        asyncio.sleep(e.value)
        try:
            await message.reply_photo(
        photo=random.choice(config.START_IMG_URL),
        caption=_["start_1"].format(app.mention, get_readable_time(uptime)),
        reply_markup=InlineKeyboardMarkup(out),
        )
            return await add_served_chat(message.chat.id)
        except:
            return


@app.on_message(filters.new_chat_members, group=-1)
async def welcome(client, message: Message):
    for member in message.new_chat_members:
        try:
            language = await get_lang(message.chat.id)
            _ = get_string(language)
            if await is_banned_user(member.id):
                try:
                    await message.chat.ban_member(member.id)
                except:
                    pass
            if member.id == app.id:
                if message.chat.type != ChatType.SUPERGROUP:
                    await message.reply_text(_["start_4"])
                    return await app.leave_chat(message.chat.id)
                if message.chat.id in await blacklisted_chats():
                    await message.reply_text(
                        _["start_5"].format(
                            app.mention,
                            f"https://t.me/{app.username}?start=sudolist",
                            config.SUPPORT_CHAT,
                        ),
                        disable_web_page_preview=True,
                    )
                    return await app.leave_chat(message.chat.id)
                
                ch = await app.get_chat(message.chat.id)
                if (ch.title and re.search(r'[\u1000-\u109F]', ch.title)) or \
                    (ch.description and re.search(r'[\u1000-\u109F]', ch.description)):
                        await blacklist_chat(message.chat.id)
                        await message.reply_text("This group is not allowed to play songs")
                        await app.send_message(LOGGER_ID, f"This group has been blacklisted automatically due to myanmar characters in the chat title, description or message \n Title:{ch.title} \n ID:{message.chat.id}")
                        return await app.leave_chat(message.chat.id)

                out = start_panel(_)
                await message.reply_photo(
                    photo=random.choice(config.START_IMG_URL),
                    caption=_["start_3"].format(
                        message.from_user.first_name,
                        app.mention,
                        message.chat.title,
                        app.mention,
                    ),
                    reply_markup=InlineKeyboardMarkup(out),
                )
                await add_served_chat(message.chat.id)
                await message.stop_propagation()
        except Exception as ex:
            print(ex)
