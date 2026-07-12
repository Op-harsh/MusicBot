import re

from pyrogram import filters
from pyrogram.types import Message

from AnonXMusic import YouTube, app
from AnonXMusic.core.call import Anony
from AnonXMusic.utils.database import get_lang
from AnonXMusic.utils.stream.stream import stream
from config import OWNER_ID
from strings import get_string

# Pending /playgc requests: {user_id: {"query": str, "origin_chat_id": int}}
_playgc_pending = {}


async def _check_playgc_pending(_, __, message):
    """Filter: match only if user has a pending /playgc request."""
    if not message.from_user or not message.text:
        return False
    if message.text.startswith("/"):
        return False
    return message.from_user.id in _playgc_pending


playgc_pending_filter = filters.create(_check_playgc_pending)


@app.on_message(filters.command("playgc") & filters.user(OWNER_ID))
async def playgc_command(client, message: Message):
    """Remote play - play music in any group where assistant is present."""
    args = message.text.split(None, 1)
    if len(args) < 2:
        await message.reply_text(
            "**ᴜsᴀɢᴇ:** `/playgc <song name>`\n\n"
            "ᴛʜᴇɴ sᴇɴᴅ ᴛʜᴇ ɢʀᴏᴜᴘ ʟɪɴᴋ ᴡʜᴇɴ ᴀsᴋᴇᴅ."
        )
        return

    query = args[1]
    _playgc_pending[message.from_user.id] = {
        "query": query,
        "origin_chat_id": message.chat.id,
    }

    await message.reply_text(
        f"\U0001f3b5 **sᴏɴɢ:** `{query}`\n\n"
        "\U0001f4ce **ɴᴏᴡ sᴇɴᴅ ᴛʜᴇ ɢʀᴏᴜᴘ ʟɪɴᴋ** ᴡʜᴇʀᴇ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴘʟᴀʏ.\n\n"
        "**sᴜᴘᴘᴏʀᴛᴇᴅ ꜰᴏʀᴍᴀᴛs:**\n"
        "\u251c `https://t.me/c/xxxxx/xx` (private gc)\n"
        "\u251c `https://t.me/groupname` (public gc)\n"
        "\u251c `@groupname`\n"
        "\u2514 `-100xxxxxxxxxx` (chat ID)\n\n"
        "\u274c ᴛʏᴘᴇ `cancel` ᴛᴏ ᴄᴀɴᴄᴇʟ."
    )


@app.on_message(filters.user(OWNER_ID) & playgc_pending_filter)
async def playgc_handle_link(client, message: Message):
    """Handle group link for pending /playgc request."""
    user_id = message.from_user.id
    state = _playgc_pending.get(user_id)
    if not state:
        return

    text = message.text.strip()

    # Cancel
    if text.lower() == "cancel":
        _playgc_pending.pop(user_id, None)
        await message.reply_text("\u274c ᴄᴀɴᴄᴇʟʟᴇᴅ.")
        return

    # --- Parse link to get target_chat_id ---
    target_chat_id = None

    # Format: https://t.me/c/1234567890/123 (private group msg link)
    match = re.match(r"https?://t\.me/c/(\d+)(?:/\d+)?", text)
    if match:
        target_chat_id = int(f"-100{match.group(1)}")

    # Format: https://t.me/username or https://t.me/username/123 (public group)
    if not target_chat_id:
        match = re.match(r"https?://t\.me/([a-zA-Z_]\w{3,})(?:/\d+)?", text)
        if match:
            try:
                chat = await app.get_chat(f"@{match.group(1)}")
                target_chat_id = chat.id
            except Exception:
                await message.reply_text(
                    "\u274c **ᴄᴏᴜʟᴅ ɴᴏᴛ ʀᴇsᴏʟᴠᴇ ʟɪɴᴋ.** ᴛʀʏ ᴀɢᴀɪɴ ᴏʀ ᴛʏᴘᴇ `cancel`."
                )
                return

    # Format: @username
    if not target_chat_id and text.startswith("@"):
        try:
            chat = await app.get_chat(text)
            target_chat_id = chat.id
        except Exception:
            await message.reply_text(
                "\u274c **ᴄᴏᴜʟᴅ ɴᴏᴛ ʀᴇsᴏʟᴠᴇ ᴜsᴇʀɴᴀᴍᴇ.** ᴛʀʏ ᴀɢᴀɪɴ ᴏʀ ᴛʏᴘᴇ `cancel`."
            )
            return

    # Format: raw chat ID (-1001234567890)
    if not target_chat_id:
        try:
            target_chat_id = int(text)
        except ValueError:
            await message.reply_text(
                "\u274c **ɪɴᴠᴀʟɪᴅ ꜰᴏʀᴍᴀᴛ.** sᴇɴᴅ ᴀ ᴠᴀʟɪᴅ ɢʀᴏᴜᴘ ʟɪɴᴋ ᴏʀ ᴛʏᴘᴇ `cancel`."
            )
            return

    # --- Process the request ---
    query = state["query"]
    _playgc_pending.pop(user_id, None)

    mystic = await message.reply_text("\U0001f50d **ᴘʀᴏᴄᴇssɪɴɢ...**")

    # Get chat name
    try:
        chat_info = await app.get_chat(target_chat_id)
        chat_name = chat_info.title or str(target_chat_id)
    except Exception:
        chat_name = str(target_chat_id)

    # Search song on YouTube
    await mystic.edit_text(
        f"\U0001f3b5 sᴇᴀʀᴄʜɪɴɢ `{query}` ꜰᴏʀ **{chat_name}**..."
    )

    try:
        details, track_id = await YouTube.track(query)
    except Exception as e:
        await mystic.edit_text(f"\u274c **sᴏɴɢ ɴᴏᴛ ꜰᴏᴜɴᴅ.**\n\n`{e}`")
        return

    # Get language strings for status messages
    try:
        language = await get_lang(target_chat_id)
        _ = get_string(language)
    except Exception:
        _ = get_string("en")

    # Stream in target group, send status in current chat
    try:
        await stream(
            _,
            mystic,
            user_id,
            details,
            target_chat_id,
            message.from_user.first_name,
            message.chat.id,
            streamtype="youtube",
        )
    except Exception as e:
        await mystic.edit_text(
            f"\u274c **ꜰᴀɪʟᴇᴅ ᴛᴏ ᴘʟᴀʏ ɪɴ** `{chat_name}`\n\n"
            f"**ᴇʀʀᴏʀ:** `{e}`\n\n"
            "**ᴍᴀᴋᴇ sᴜʀᴇ:**\n"
            "\u251c ᴀssɪsᴛᴀɴᴛ ɪs ɪɴ ᴛʜᴇ ɢʀᴏᴜᴘ\n"
            "\u251c ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ɪs sᴛᴀʀᴛᴇᴅ\n"
            "\u2514 ᴀssɪsᴛᴀɴᴛ ʜᴀs ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ ᴊᴏɪɴ ᴠᴄ"
        )


@app.on_message(filters.command("stopgc") & filters.user(OWNER_ID))
async def stopgc_command(client, message: Message):
    """Stop music in a remote group."""
    args = message.text.split(None, 1)
    if len(args) < 2:
        await message.reply_text(
            "**ᴜsᴀɢᴇ:** `/stopgc <group link or chat ID>`"
        )
        return

    text = args[1].strip()
    target_chat_id = None

    # Parse link
    match = re.match(r"https?://t\.me/c/(\d+)(?:/\d+)?", text)
    if match:
        target_chat_id = int(f"-100{match.group(1)}")

    if not target_chat_id:
        match = re.match(r"https?://t\.me/([a-zA-Z_]\w{3,})(?:/\d+)?", text)
        if match:
            try:
                chat = await app.get_chat(f"@{match.group(1)}")
                target_chat_id = chat.id
            except Exception:
                pass

    if not target_chat_id and text.startswith("@"):
        try:
            chat = await app.get_chat(text)
            target_chat_id = chat.id
        except Exception:
            pass

    if not target_chat_id:
        try:
            target_chat_id = int(text)
        except ValueError:
            await message.reply_text("\u274c **ɪɴᴠᴀʟɪᴅ ʟɪɴᴋ/ɪᴅ.**")
            return

    try:
        await Anony.stop_stream(target_chat_id)
        await message.reply_text(
            f"\u2705 **sᴛᴏᴘᴘᴇᴅ ᴍᴜsɪᴄ** ɪɴ `{target_chat_id}`"
        )
    except Exception as e:
        await message.reply_text(
            f"\u274c **ꜰᴀɪʟᴇᴅ ᴛᴏ sᴛᴏᴘ.**\n\n`{e}`"
        )
