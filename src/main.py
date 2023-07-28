import sys
import asyncio
import traceback
from telethon import TelegramClient, events
from utils import *
from middlewares import allow_origin
from aiohttp import web
import aiohttp
import json
import uvloop
uvloop.install()

def init_app():
    app = web.Application(middlewares=[allow_origin])
    try:
        app['loop'] = asyncio.get_event_loop()
        app['bot_id'] = config["TELEGRAM"]["bot_id"]
        app['api_id'] = config["TELEGRAM"]["api_id"]
        app['api_hash'] = config["TELEGRAM"]["api_hash"]
        app['admin_channel_id'] = int(config["TELEGRAM"]["admin_channel_id"])
        app['bot'] = None
        setup_routes(app)
    except Exception as err:
        logger.critical("Config failed: %s" % err)
        logger.critical("Shutdown")
        sys.exit(0)
    return app

def start(app):
    try:
        app.on_startup.append(start_background_tasks)
        app.on_cleanup.append(cleanup_background_tasks)
    except Exception:
        logger.error("Start error")
        logger.error(traceback.format_exc())

def setup_routes(app):
    app.router.add_route('GET', '/', status_handler)
    app.router.add_route('POST', '/', notification_handler)

async def status_handler(request):
    response = {"status": "OK"}
    return aiohttp.web.json_response(response, dumps=json.dumps, status=200)

async def notification_handler(request):
    await request.post()
    try:
        body = await request.json()
    except:
        body = {}
    message = body["message"] if "message" in body else ""
    channel_id = body["channel_id"] if "channel_id" in body else 0
    if not message:
        response = {"result": "failed", "error":"empty message"}
        status = 500
    else:
        try:
            await app['bot'].send_message(app['admin_channel_id'], message)
        except ConnectionError:
            await app['bot'].start(bot_token=app['bot_id'])
            await app['bot'].send_message(app['admin_channel_id'], message)
        response = {"result": "success"}
        status = 200
        if channel_id:
            try:
                await app['bot'].send_message(int(channel_id), message)
            except:
                logger.error(traceback.format_exc())
                response = {"result": "failed", "error":"incorrect channel_id %s" %channel_id}
                status = 500
    if status!=200:
        logger.error("body: [%s], response [%s]" %(body,response))
    return aiohttp.web.json_response(response, dumps=json.dumps, status=status)


async def start_background_tasks(app):
    app['bot'] = TelegramClient('bot', app['api_id'], app['api_hash'])
    app['bot'].parse_mode = 'html'
    await app['bot'].start(bot_token=app['bot_id'])
    bot_info = await app['bot'].get_me()
    logger.info("Notification bot started: %s" % bot_info)

async def cleanup_background_tasks(app):
    await terminate_coroutine(app)

async def terminate_coroutine(app):
    logger.error('Stop request received')
    await app['bot'].log_out()
    app['bot'].disconnect()
    await asyncio.sleep(1)
    app['loop'].stop()
    app['loop'].close()

app = init_app()
start(app)
