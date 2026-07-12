from pyrogram.types import InlineKeyboardButton

import config
from AnonXMusic import app


def start_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_1"], url=f"https://t.me/{app.username}?startgroup=true"
            ),
            InlineKeyboardButton(text=_["S_B_2"], url=config.SUPPORT_CHAT),
        ],
    ]
    return buttons


def private_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_3"],
                url=f"https://t.me/{app.username}?startgroup=true",
            )
        ],
        [InlineKeyboardButton(text=_["S_B_4"], callback_data="settings_back_helper")],
        [
            InlineKeyboardButton(text=_["S_B_6"], user_id=config.OWNER_ID),
            InlineKeyboardButton(text=_["S_B_5"], url=config.SUPPORT_CHANNEL),
        ],
        [
            InlineKeyboardButton(text=_["S_B_2"], url=config.SUPPORT_CHAT),
        ],
        [InlineKeyboardButton(text="\u2615 ʙᴜʏ ᴍᴇ ᴀ ᴄᴏꜰꜰᴇᴇ \u2615", url="https://upi.me/pay?pa=opharsh@upi&pn=Harsh&am=10&cu=INR&tn=Support%20MusicBot")],
        [InlineKeyboardButton(text="\u2022 s\u1d0f\u1d1c\u0280\u1d04\u1d07 \u1d04\u1d0f\u1d05\u1d07 \u2022", url="https://github.com/Op-harsh/MusicBot")],
    
    ]
    
    return buttons
