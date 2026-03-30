from aiohttp import web

async def start_server():
    app = web.Application()
    # Add routes
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 13133)
    await site.start()
