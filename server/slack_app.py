import os
import logging
from dotenv import load_dotenv
from slack_bolt.app.async_app import AsyncApp
from operator import itemgetter
from simple_api import make_queries
from utils import pretty_json
import asyncio
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from server import app
from simple_api import ACCEPTED_PRODUCTS

DEFAULT_VALUES = {
    'ENV': 'development'
}

# access environment variables
load_dotenv()
ENV, SLACK_BOT_TOKEN, SOCKET_TOKEN = itemgetter('ENV', 'SLACK_BOT_TOKEN', 'SOCKET_TOKEN')({ **DEFAULT_VALUES, **dict(os.environ) })

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

# SLASH COMMANDS
# Slash commands must be set in Slack app configuration: https://api.slack.com/apps/A05KT2RCM39/slash-commands
@slack_app.command("/resell")
async def command_resell(ack, body, say, client):
    # https://slack.dev/bolt-python/api-docs/slack_bolt/kwargs_injection/args.html#slack_bolt.kwargs_injection.args.Args.context
    channel_name, channel_id, user_id, user_name, text = itemgetter('channel_name', 'channel_id', 'user_id', 'user_name', 'text')(body)

    if text:
        # Acknowledge receipt
        await ack()
        product = determin_product(channel_name.strip().upper(), text.strip().upper())
        # Message only visible to user.
        await client.chat_postEphemeral(
            channel=channel_id,
            text=f"Querying WatsonX for: {text}...",
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
        # TODO: add more sophisticated message
        await client.chat_postEphemeral(
            channel=channel_id,
            text=f"Hi, <@{user_id}>! How can I help?",
            user=user_id
        )

# EVENT HANDLERS
@slack_app.event("app_mention")
async def event_mention(body, event, ack, say, client):
    channel_name = body.get('channel_name', '')
    original_text = event.get('text', '')
    text = original_text.lower().strip()
    user_id = event.get('user')

    # App encoded username is part of text here
    if text == "<@u05ll88u02v>" or text == "<@u05ll88u02v> help":
        # Add more sophisticated message here.
        # message = {
        #     "channel": channel,
        #     "username": "Resell Bot",
        #     "blocks": [{
        #         "type": "section",
        #         "text": {
        #             "type": "mrkdwn",
        #             "text": (f"Hi , <@{user_id}>! How can I help?")
        #         }
        #     }]
        # }
        # await client.chat_postMessage(**message)
        await say(f"Hi , <@{user_id}>! How can I help?")
    else:
        await say(f"Querying WatsonX for: {original_text[15:]}...")
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
async def event_home_opened(client, event, logger):
    try:
        await client.views_publish(
            user_id=event["user"],
            view={
                "type": "home",
                "callback_id": "home_view",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "Welcome to the Resell Lab App! :tada:"
                        }
                    },
                    {
                        "type": "divider"
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "You can ask me questions to get information about various technologies on the <https://vest.buildlab.cloud|Resell Lab website>."
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "Use: `@resell <question>` to ask a question about one of the technologies, such as Maximo or Instana."
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "Use: `/resell <question>` to ask a private question about a technology."
                        }
                    }
                ]
            }
    )
    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")


# Old stuff just to keep for reference...

# ACTION HANDLERS
# @slack_app.action("action-id")
# def action(ack):
#     ack()


# # In memory storage for illustration purposes
# db = {}

# def onboard(user_id: str, channel: str, client: WebClient):
#     test_block = TestBlock(channel)

#     # Get the message payload
#     message = test_block.get_message_payload()

#     # Post the message in Slack
#     response = client.chat_postMessage(**message)

#     # Capture the timestamp of the message we've just posted so
#     # we can use it to update the message after a user
#     # has completed a task.
#     test_block.timestamp = response["ts"]

#     # Save the message sent to in memory "DB"
#     if channel not in db:
#         db[channel] = {}
#     db[channel][user_id] = test_block


# # Note: Bolt provides a WebClient instance as an argument to the listener function
# @slack_app.event("team_join")
# def handle_message(event, client):
#     """Create and send an onboarding welcome message to new users. Save the
#     time stamp of this message so we can update this message in the future.
#     """
#     # Get the id of the Slack user associated with the incoming event
#     user_id = event.get("user", {}).get("id")

#     # Open a DM with the new user.
#     response = client.conversations_open(users=user_id)
#     channel = response["channel"]["id"]

#     # Post the onboarding message.
#     onboard(user_id, channel, client)


# # When a users adds an emoji reaction
# @slack_app.event("reaction_added")
# def update_emoji(event, client):
#     """Update the onboarding welcome message after receiving a "reaction_added"
#     event from Slack. Update timestamp for welcome message as well.
#     """
#     # Get the ids of the Slack user and channel associated with the incoming event
#     channel_id = event.get("item", {}).get("channel")
#     user_id = event.get("user")

#     if channel_id not in db:
#         return

#     # Get the original tutorial sent.
#     test_block = db[channel_id][user_id]

#     # Mark the reaction task as completed.
#     test_block.reaction_task_completed = True

#     # Get the new message payload
#     message = test_block.get_message_payload()

#     # Post the updated message in Slack
#     updated_message = client.chat_update(**message)
#     print(updated_message)


# # When a users pins a message the type of the event will be 'pin_added'.
# @slack_app.event("pin_added")
# def update_pin(event, client):
#     """Update the onboarding welcome message after receiving a "pin_added"
#     event from Slack. Update timestamp for welcome message as well.
#     """
#     # Get the ids of the Slack user and channel associated with the incoming event
#     channel_id = event.get("channel_id")
#     user_id = event.get("user")

#     # Get the original tutorial sent.
#     test_block = db[channel_id][user_id]

#     # Mark the pin task as completed.
#     test_block.pin_task_completed = True

#     # Get the new message payload
#     message = test_block.get_message_payload()

#     # Post the updated message in Slack
#     updated_message = client.chat_update(**message)
#     print(updated_message)

async def start_slack():
    with app.app_context():
        handler = AsyncSocketModeHandler(slack_app, SOCKET_TOKEN)
        await handler.start_async()

if __name__ == "__main__":
    # Start async slack app in socket mode
    asyncio.run(start_slack())
