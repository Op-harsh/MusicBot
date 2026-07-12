import asyncio

import speedtest
from pyrogram import filters
from pyrogram.types import Message

from AnonXMusic import app
from AnonXMusic.misc import SUDOERS
from AnonXMusic.utils.decorators.language import language


def run_speedtest():
    """Run speedtest in a blocking thread (no async calls inside)."""
    test = speedtest.Speedtest()
    test.get_best_server()
    test.download()
    test.upload()
    test.results.share()
    return test.results.dict()


@app.on_message(filters.command(["speedtest", "spt"]) & SUDOERS)
@language
async def speedtest_function(client, message: Message, _):
    m = await message.reply_text(_["server_11"])
    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, run_speedtest)
        output = _["server_15"].format(
            result["client"]["isp"],
            result["client"]["country"],
            result["server"]["name"],
            result["server"]["country"],
            result["server"]["cc"],
            result["server"]["sponsor"],
            result["server"]["latency"],
            result["ping"],
        )
        await message.reply_photo(photo=result["share"], caption=output)
        await m.delete()
    except Exception as e:
        await m.edit_text(f"\u274c **Speedtest Error:**\n\n`{e}`")
