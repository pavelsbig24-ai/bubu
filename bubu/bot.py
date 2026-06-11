import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiohttp import web

BOT_TOKEN = os.getenv("BOT_TOKEN")
# Замени на свой URL после деплоя на Render (например, https://имя-сервиса.onrender.com)
BASE_WEBAPP_URL = "https://ваш-сервис.onrender.com/index.html"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎮 Play Word Sort", web_app=WebAppInfo(url=BASE_WEBAPP_URL))]
    ])
    await message.answer(
        "🌸 Hello! Sort the words into correct categories.\n"
        "Drag & drop or tap a word then tap a category.\n"
        "Click ⓘ to see translation and example.\n"
        "Switch language in the top right corner!",
        reply_markup=keyboard
    )

# Веб-сервер для раздачи статики
async def handle_index(request):
    return web.FileResponse('index.html')

async def handle_static(request):
    filename = request.match_info['filename']
    # разрешаем только .html, .js, .css, .png, .jpg, .ico — для безопасности
    if os.path.exists(filename) and os.path.isfile(filename):
        return web.FileResponse(filename)
    return web.Response(status=404, text="Not found")

async def run_web_server():
    app = web.Application()
    app.router.add_get('/', handle_index)
    app.router.add_get('/index.html', handle_index)
    app.router.add_get('/{filename}', handle_static)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()
    print("✅ Web server started on port 8080")

async def main():
    await run_web_server()
    print("🤖 Bot is polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())