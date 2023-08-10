from pyrogram import Client, filters
import requests
import time
import asyncio
import os
from config import api_id, api_hash, bot_token, name_session

app = Client(name_session, api_id=api_id, api_hash=api_hash, bot_token=bot_token)
user_websites = {}


@app.on_message(filters.command("start"))
async def start_command(client, message):
    user_id = message.from_user.id

    with open("users.txt", "r") as users_file:
        existing_users = users_file.read().splitlines()

    if str(user_id) not in existing_users:
        with open("users.txt", "a") as users_file:
            users_file.write(f"{user_id}\n")

    user_websites[user_id] = None
    await message.reply_text("Привет! Для начала работы используйте команду /set, чтобы задать адрес сайта.")


@app.on_message(filters.command("set"))
async def set_command(client, message):
    user_id = message.from_user.id
    if len(message.command) > 1:
        user_websites[user_id] = message.command[1]
        await message.reply_text("Адрес сайта успешно установлен.")
    else:
        await message.reply_text("Используйте команду в формате: /set <адрес_сайта>")


@app.on_message(filters.command("list"))
async def list_command(client, message):
    user_id = message.from_user.id
    try:
        with open(f"results/{user_id}_results.txt", "r") as file:
            results = file.readlines()
            last_results = results[-5:]
            response_text = "Последние 5 результатов:\n" + "\n".join(last_results)
            await message.reply_text(response_text)
    except FileNotFoundError:
        await message.reply_text("Результаты пинга не найдены.")


async def check_and_ping():
    while True:
        for user_id, website in user_websites.items():
            if website:
                try:
                    response = requests.get(website)
                    result = f"Ping to {website}: Status Code {response.status_code}"
                except requests.RequestException as e:
                    result = f"Ping to {website}: Error - {e}"
            else:
                result = "Адрес сайта не задан"

            if not os.path.exists("results"):
                os.makedirs("results")

            with open(f"results/{user_id}_results.txt", "a") as file:
                file.write(f"{time.ctime()}: {result}\n")

            await app.send_message(user_id, result)

        await asyncio.sleep(60)


async def run_tasks():
    await asyncio.gather(app.start(), check_and_ping())


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(run_tasks())
    loop.run_forever()
