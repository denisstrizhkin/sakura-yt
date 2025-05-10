import asyncio
import logging
import sys
from os import getenv
from typing import Optional

import yt_dlp
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message
from pydantic import BaseModel


class VideoFormat(BaseModel):
    format_id: str
    fps: Optional[float] = None


class VideoInfo(BaseModel):
    title: str
    formats: list[VideoFormat]


# Bot token can be obtained via https://t.me/BotFather
TOKEN = getenv("BOT_TOKEN")

# All handlers should be attached to the Router (or Dispatcher)

dp = Dispatcher()


def parse_url(uri: str) -> VideoInfo:
    ydl_opts = {}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(uri, download=False)

        # ℹ️ ydl.sanitize_info makes the info json-serializable
        return VideoInfo.model_validate(ydl.sanitize_info(info))


@dp.message()
async def echo_handler(message: Message) -> None:
    info = parse_url(message.text)
    logging.info(info)
    try:
        # Send a copy of the received message
        await message.answer(str(info))
    except Exception as e:
        logging.exception(e)
        await message.answer("Oopsie! Something went wrong... (>_<)")


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties())

    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
