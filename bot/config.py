import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Config:
    api_id: int
    api_hash: str
    bot_token: str
    session_string: str
    owner_id: int
    download_dir: str = "downloads"


def get_config() -> Config:
    required = ["API_ID", "API_HASH", "BOT_TOKEN", "SESSION_STRING", "OWNER_ID"]
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        raise RuntimeError(f"Missing required env vars: {', '.join(missing)}")

    return Config(
        api_id=int(os.environ["API_ID"]),
        api_hash=os.environ["API_HASH"],
        bot_token=os.environ["BOT_TOKEN"],
        session_string=os.environ["SESSION_STRING"],
        owner_id=int(os.environ["OWNER_ID"]),
        download_dir=os.getenv("DOWNLOAD_DIR", "downloads"),
    )
