import asyncio
import os
from pathlib import Path
from aiogram import Bot, Dispatcher, types
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiohttp import web

BOT_TOKEN = os.getenv("BOT_TOKEN")
BASE_WEBAPP_URL = "https://bubu-28lm.onrender.com/index.html"  # твой реальный URL

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ---------- Указываем папку, где лежит этот скрипт ----------
BASE_DIR = Path(__file__).parent.absolute()

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

# Раздача статики с правильными путями
async def handle_index(request):
    index_path = BASE_DIR / 'index.html'
    if index_path.exists():
        return web.FileResponse(str(index_path))
    return web.Response(text="index.html not found", status=404)

async def handle_static(request):
    filename = request.match_info['filename']
    # Безопасность: не отдаём файлы вне BASE_DIR
    requested_path = BASE_DIR / filename
    # Проверяем, что путь не выходит за пределы BASE_DIR (защита от directory traversal)
    try:
        requested_path.resolve().relative_to(BASE_DIR.resolve())
    except ValueError:
        return web.Response(status=403, text="Forbidden")
    
    if requested_path.is_file():
        return web.FileResponse(str(requested_path))
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
    print(f"✅ Web server started on port 8080, serving from {BASE_DIR}")

async def main():
    await run_web_server()
    await bot.delete_webhook(drop_pending_updates=True)  # сброс вебхука
    print("🤖 Bot is polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
