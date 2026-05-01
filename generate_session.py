from pyrogram import Client


print("Get API_ID and API_HASH from https://my.telegram.org/apps")
api_id = int(input("API_ID: ").strip())
api_hash = input("API_HASH: ").strip()

with Client("session_generator", api_id=api_id, api_hash=api_hash, in_memory=True) as app:
    print("\nSESSION_STRING:")
    print(app.export_session_string())
