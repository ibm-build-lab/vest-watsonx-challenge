import os
import logging
import asyncio
from dotenv import load_dotenv
from slack_bolt.app.async_app import AsyncApp
from operator import itemgetter
from simple_api import make_queries
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from server import app
from simple_api import ACCEPTED_PRODUCTS
from slack_views import HelpBlock
from utils import pretty_json

DEFAULT_VALUES = {
    'ENV': 'development'
}

# For some reason we can't get the human readable channel name from app_mention event.
CHANNEL_MAP = {
    'C05N0P844F7': 'hackathon-bot-dev',
    'C05KDDPF9QF': 'hackathon-bot',
    'C05MXM97B25': 'instana',
    'C05MK2DB8TC': 'maximo'
}

# access environment variables
load_dotenv()
ENV, SLACK_BOT_TOKEN, SOCKET_TOKEN = itemgetter('ENV', 'SLACK_BOT_TOKEN', 'SOCKET_TOKEN')({ **DEFAULT_VALUES, **dict(os.environ) })
is_dev = ENV == 'development'

# Set up slack_app logger instance
logger = logging.getLogger('slack_app')
debug_level = logging.DEBUG if ENV == 'development' else logging.INFO
logger.setLevel(debug_level)
logger.addHandler(logging.StreamHandler())

# Slack APP
slack_app = AsyncApp(token=SLACK_BOT_TOKEN)

logger.info(f"Starting slack app in {'DEV' if ENV=='development' else 'PROD'} mode.")

def determin_product(channel, question):
    if "MAXIMO" in question:
        product = 'MAXIMO'
    elif 'INSTANA' in question:
        product = 'INSTANA'
    else:
        product = 'ALL'

    # Channel name takes precedence over keyword in question
    # Just to discourage someone asking INSTANA question in MAXIMO channel
    if channel in ACCEPTED_PRODUCTS:
        product = channel
    
    return product

def is_dev_channel(n):
    logger.info(f"channel name: {n}")
    return n == "hackathon-bot-dev"

# SLASH COMMANDS

# Slash commands must be set in Slack app configuration: https://api.slack.com/apps/A05KT2RCM39/slash-commands
@slack_app.command("/resell-bot")
async def command_resell(ack, body, client):
    # https://slack.dev/bolt-python/api-docs/slack_bolt/kwargs_injection/args.html#slack_bolt.kwargs_injection.args.Args.context
    channel_name, channel_id, user_id, text = itemgetter('channel_name', 'channel_id', 'user_id', 'text')(body)

    # Separate PROD & DEV
    if (is_dev and is_dev_channel(channel_name)) or (not is_dev and not is_dev_channel(channel_name)):
        if text and text != "help":
            # Acknowledge receipt
            await ack()
            product = determin_product(channel_name.strip().upper(), text.strip().upper())
            # Message only visible to user.
            await client.chat_postEphemeral(
                channel=channel_id,
                text=f"{'DEV_BOT - ' if is_dev else ''}Querying WatsonX for: {text}...",
                user=user_id
            )
            res = await make_queries(text, product)
            logger.info(res)
            text = res["Error"] if res["Error"] else res["answer"]
            await client.chat_postEphemeral(
                channel=channel_id,
                text=text,
                user=user_id
            )
        else:
            # Acknowledge receipt
            await ack()
            help_block = HelpBlock('help', user_id, channel_id, is_dev)
            message = help_block.get_message_payload()
            await client.chat_postEphemeral(**message)

# EVENT HANDLERS
@slack_app.event("app_mention")
async def event_mention(event, ack, say, client):
    channel_id = event.get('channel', '') # Here channel_id is called channel
    channel_name = CHANNEL_MAP.get(channel_id, '')
    original_text = event.get('text', '')
    text = original_text.lower().strip()
    user_id = event.get('user')

    # Separate PROD & DEV
    if (is_dev and is_dev_channel(channel_name)) or (not is_dev and not is_dev_channel(channel_name)):
        # App encoded username is part of text here
        if text == "<@u05ll88u02v>" or text == "<@u05ll88u02v> help":
            help_block = HelpBlock('help', user_id, channel_id, is_dev)
            message = help_block.get_message_payload()
            await client.chat_postMessage(**message)
        else:
            await ack()
            await say(f"{'DEV_BOT - ' if is_dev else ''}Querying WatsonX for: {original_text[15:]}...")
            product = determin_product(channel_name.strip().upper(), text.strip().upper())
            res = await make_queries(text[15:], product)
            text = res["Error"] if res["Error"] else res["answer"]
            await say(text)

# Just for debugging...
@slack_app.event("message")
async def event_message(event):
    type = event.get('type')
    subtype = event.get('subtype')
    text = event.get('text')
    logger.info(f"Event: {type}{(', ' + subtype) if subtype else ''}{(', ' + text) if text else ''}")


# App Home tab.
@slack_app.event("app_home_opened")
async def event_home_opened(client, ack, event, logger):
    await ack()
    view = event.get("view", {})
    view_id = view.get("id, '")
    logger.error(view_id)
    user_id = event["user"]
    # App home is distinct for user viewing; no need to separate PROD and DEV views
    help_block = HelpBlock('home', user_id, None, is_dev)
    message = help_block.get_message_payload()
    blocks = message.get("blocks", [])
    # In development, PROD and DEV will both try and update home view. Wait until PROD updates, then do DEV update
    if is_dev:
        import time
        time.sleep(2)
    try:
        if not view_id:
            await client.views_publish(
                user_id=user_id,
                view={
                    "type": "home",
                    "callback_id": "home_view",
                    "blocks": blocks
                }
            )
        else:
            await client.views_update(
                user_id=user_id,
                view_id=view_id,
                view={
                    "type": "home",
                    "callback_id": "home_view",
                    "blocks": blocks
                }
            )
    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")
        await ack('Sorry, an error occurred.')


async def start_slack():
    with app.app_context():
        handler = AsyncSocketModeHandler(slack_app, SOCKET_TOKEN)
        await handler.start_async()

if __name__ == "__main__":
    # Start async slack app in socket mode
    asyncio.run(start_slack())
