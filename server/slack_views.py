
class HelpBlock:
    DEFAULT_BLOCKS = [
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "You can ask me questions to get information about various technologies on the <https://vest.buildlab.cloud|Resell Lab website>"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Currently supported technologies: \n    • Maximo\n    • Instana"
            }
        },
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "Usage"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Use the `@resell-bot` App mention to ask a publicly visible question, and the slash command `/resell-bot` to ask a question that will only be visible to you. `help` will print this message and exit.\n\n `@resell-bot [help || <question>]` - Public message\n`/resell-bot [help || <question>]` - Private message"
            }
        }
    ]

    def __init__(self, type, user, channel, is_dev):
        self.type = type
        self.user = user
        self.channel = channel
        self.username = "Resell Bot"
        self.dev = is_dev

    def get_message_payload(self):
        blocks = self.DEFAULT_BLOCKS
        if len(blocks) == 5: # Prevent adding multiple headers. (Python idiosynchrasy; looking into it.)
            header_block = self._get_header_block(self.user, self.type, self.dev)
            blocks.insert(0, header_block)
        return {
            "user": self.user,
            "channel": self.channel,
            "username": self.username,
            "blocks": blocks,
            "text": "Failed to fetch message. Please try again."
        }
    
    @staticmethod
    def _get_header_block(user, type, dev):
        if type == 'home':
            message = "Welcome to the Resell Lab Bot Homepage! :tada:"
        else:
            message = "How can I help?"

        return {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"{'DEV_BOT - ' if dev else ''}Hi , <@{user}>! {message}"
            }
        }
