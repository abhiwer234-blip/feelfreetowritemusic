# Telegram Music Bot

Pyrogram session string par chalne wala Telegram group voice-chat music bot.

## Features

- `/play song name or link`
- `/pause`
- `/resume`
- `/skip`
- `/stop`
- `/queue`
- `/current`
- Per-group queue
- YouTube/search audio via `yt-dlp`
- Voice chat streaming via `PyTgCalls`

Use this bot only for music/audio you have the right to stream in your group.

## Requirements

- Python 3.10+
- FFmpeg installed on server
- Telegram bot token from BotFather
- Telegram `API_ID` and `API_HASH` from `my.telegram.org`
- Assistant user account session string

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Install FFmpeg.

Ubuntu/Debian:

```bash
sudo apt update
sudo apt install ffmpeg -y
```

Windows:

Download FFmpeg from `https://ffmpeg.org/download.html` and add `ffmpeg/bin` to PATH.

3. Generate Pyrogram session string:

```bash
python generate_session.py
```

Login with the assistant/user account that will join voice chats.

4. Create `.env`:

Copy `.env.example` to `.env` and fill values:

```env
API_ID=123456
API_HASH=your_api_hash_here
BOT_TOKEN=123456:your_bot_token_here
SESSION_STRING=your_pyrogram_user_session_string_here
OWNER_ID=123456789
DOWNLOAD_DIR=downloads
```

5. Run:

```bash
python run.py
```

## Deploy on Railway

Railway par deploy karne ke liye repo mein `Dockerfile`, `Procfile`, aur `railway.json` already included hain.

1. Is project ko GitHub repo mein upload karo.

2. Railway dashboard open karo and `New Project` select karo.

3. `Deploy from GitHub repo` choose karo and apna bot repo select karo.

4. Railway automatically Dockerfile use karega. FFmpeg container ke andar install ho jayega.

5. Railway project ke `Variables` tab mein ye env vars add karo:

```env
API_ID=123456
API_HASH=your_api_hash_here
BOT_TOKEN=123456:your_bot_token_here
SESSION_STRING=your_pyrogram_user_session_string_here
OWNER_ID=123456789
DOWNLOAD_DIR=downloads
```

6. Deploy start karo. Logs mein `Started @your_bot_username` dikhe to bot online hai.

7. Telegram group mein:

- bot add karo
- assistant user account add karo
- group voice chat start karo
- `/play song name` send karo

Important: Railway par free/sleeping plan use karoge to bot sleep ho sakta hai. Music bot ke liye always-on plan better hota hai.

## Telegram Group Setup

1. Add the bot to your group.
2. Add the assistant user account to your group.
3. Start a group voice chat.
4. Send:

```text
/play your song name
```

## Notes

- If `/play` says it cannot join, check that the assistant account is in the group and the voice chat is active.
- If audio download fails, check FFmpeg and `yt-dlp`.
- For 24/7 hosting, use a VPS. Free hosts often sleep and break voice streaming.
