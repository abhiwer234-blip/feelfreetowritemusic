import asyncio
import logging
from pathlib import Path

from pyrogram import Client, filters, idle
from pyrogram.enums import ChatType
from pyrogram.types import Message
from tgcaller import AudioConfig, TgCaller

from .config import get_config
from .queue import MusicQueue, Track
from .youtube import download_track, format_track


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
log = logging.getLogger("music-bot")

config = get_config()
queues = MusicQueue()

bot = Client(
    "music_bot",
    api_id=config.api_id,
    api_hash=config.api_hash,
    bot_token=config.bot_token,
    in_memory=True,
)

assistant = Client(
    "assistant",
    api_id=config.api_id,
    api_hash=config.api_hash,
    session_string=config.session_string,
    in_memory=True,
)

calls = TgCaller(assistant)
audio_config = AudioConfig.high_quality()


def _command_text(message: Message) -> str:
    text = message.text or message.caption or ""
    parts = text.split(maxsplit=1)
    return parts[1].strip() if len(parts) > 1 else ""


def _display_user(message: Message) -> str:
    if not message.from_user:
        return "Unknown"
    return message.from_user.mention


async def _ensure_group(message: Message) -> bool:
    if message.chat.type not in {ChatType.GROUP, ChatType.SUPERGROUP}:
        await message.reply_text("Please use me inside a Telegram group with an active voice chat.")
        return False
    return True


async def play_track(chat_id: int, track: Track) -> None:
    if not calls.is_connected(chat_id):
        await calls.join_call(chat_id, audio_config=audio_config)
    await calls.play(chat_id, track.file_path)


async def start_next(chat_id: int) -> Track | None:
    next_track = queues.pop_next(chat_id)
    if not next_track:
        await calls.leave_call(chat_id)
        return None

    if not calls.is_connected(chat_id):
        await calls.join_call(chat_id, audio_config=audio_config)
    await calls.play(chat_id, next_track.file_path)
    return next_track


@bot.on_message(filters.command("start"))
async def start_cmd(_: Client, message: Message) -> None:
    await message.reply_text(
        "Hi, I am a Pyrogram music bot.\n\n"
        "Commands:\n"
        "/play song name or link\n"
        "/pause, /resume, /skip, /stop\n"
        "/queue, /current"
    )


@bot.on_message(filters.command("play"))
async def play_cmd(_: Client, message: Message) -> None:
    if not await _ensure_group(message):
        return

    query = _command_text(message)
    if not query:
        await message.reply_text("Send a song name or a direct/YouTube link.\nExample: /play lofi beats")
        return

    status = await message.reply_text("Searching and preparing audio...")
    try:
        track = await download_track(query, config.download_dir, _display_user(message))
    except Exception as exc:
        log.exception("Failed to prepare track")
        await status.edit_text(f"Could not prepare that track.\nReason: {exc}")
        return

    current = queues.current(message.chat.id)
    position = queues.add(message.chat.id, track)

    if current:
        await status.edit_text(f"Added to queue #{position}: {format_track(track)}")
        return

    next_track = queues.pop_next(message.chat.id)
    if not next_track:
        await status.edit_text("Queue is empty.")
        return

    try:
        await play_track(message.chat.id, next_track)
    except Exception as exc:
        log.exception("Failed to join/play")
        queues.clear(message.chat.id)
        await status.edit_text(
            "Could not join the voice chat. Start a group voice chat first and add the assistant account to this group.\n"
            f"Reason: {exc}"
        )
        return

    await status.edit_text(f"Now playing: {format_track(next_track)}\nRequested by: {next_track.requested_by}")


@bot.on_message(filters.command("pause"))
async def pause_cmd(_: Client, message: Message) -> None:
    if not await _ensure_group(message):
        return
    await calls.pause(message.chat.id)
    await message.reply_text("Paused.")


@bot.on_message(filters.command("resume"))
async def resume_cmd(_: Client, message: Message) -> None:
    if not await _ensure_group(message):
        return
    await calls.resume(message.chat.id)
    await message.reply_text("Resumed.")


@bot.on_message(filters.command("skip"))
async def skip_cmd(_: Client, message: Message) -> None:
    if not await _ensure_group(message):
        return

    next_track = await start_next(message.chat.id)
    if next_track:
        await message.reply_text(f"Skipped. Now playing: {format_track(next_track)}")
    else:
        await message.reply_text("Skipped. Queue ended.")


@bot.on_message(filters.command("stop"))
async def stop_cmd(_: Client, message: Message) -> None:
    if not await _ensure_group(message):
        return

    queues.clear(message.chat.id)
    await calls.leave_call(message.chat.id)
    await message.reply_text("Stopped and cleared queue.")


@bot.on_message(filters.command("queue"))
async def queue_cmd(_: Client, message: Message) -> None:
    if not await _ensure_group(message):
        return

    current = queues.current(message.chat.id)
    pending = queues.list(message.chat.id)
    if not current and not pending:
        await message.reply_text("Queue is empty.")
        return

    lines = []
    if current:
        lines.append(f"Now: {format_track(current)}")
    lines += [f"{idx}. {format_track(track)}" for idx, track in enumerate(pending, start=1)]
    await message.reply_text("\n".join(lines))


@bot.on_message(filters.command("current"))
async def current_cmd(_: Client, message: Message) -> None:
    current = queues.current(message.chat.id)
    if not current:
        await message.reply_text("Nothing is playing.")
        return
    await message.reply_text(f"Now playing: {format_track(current)}\nRequested by: {current.requested_by}")


@calls.on_stream_end
async def stream_end_handler(_: TgCaller, update) -> None:
    chat_id = getattr(update, "chat_id", None)
    if chat_id is None:
        return

    next_track = await start_next(chat_id)
    if next_track:
        await bot.send_message(chat_id, f"Now playing: {format_track(next_track)}")


async def main() -> None:
    Path(config.download_dir).mkdir(parents=True, exist_ok=True)
    await bot.start()
    await assistant.start()
    await calls.start()
    me = await bot.get_me()
    log.info("Started @%s", me.username)
    await idle()
    await calls.stop()
    await assistant.stop()
    await bot.stop()


if __name__ == "__main__":
    asyncio.run(main())
