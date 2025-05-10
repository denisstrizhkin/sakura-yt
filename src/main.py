import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from .yt import Yt, VideoFormat, AudioFormat, YtError


# Bot token can be obtained via https://t.me/BotFather
TOKEN = getenv("BOT_TOKEN")

# All handlers should be attached to the Router (or Dispatcher)

dp = Dispatcher()
yt = Yt()


@dp.message()
async def echo_handler(message: Message) -> None:
    info = None
    msg = None
    try:
        info = yt.get_video_info(message.text)
    except YtError as e:
        msg = str(e)

    try:
        if msg:
            await message.answer(msg)
            return

        logging.info(info)
        # Send a copy of the received message
        buttons: list[[InlineKeyboardButton]] = list()
        for format in info.formats:
            if isinstance(format, VideoFormat):
                buttons.append(
                    [
                        InlineKeyboardButton(
                            text=f"video: {format.width}x{format.height}@{format.fps}",
                            callback_data=str(format.format_id),
                        )
                    ]
                )
            elif isinstance(format, AudioFormat):
                buttons.append(
                    [
                        InlineKeyboardButton(
                            text="audio", callback_data=str(format.format_id)
                        )
                    ]
                )
        markup = InlineKeyboardMarkup(inline_keyboard=buttons)
        await message.answer(info.title, reply_markup=markup)
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
