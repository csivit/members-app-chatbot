"""A chatbot developed for CSI-VIT's member's application.

The following is a simple usage example::

  import chatbot

  # Initialize for a new chat
  bot = chatbot.ChatBot(context=None, events=[])

  # Get a response from the bot
  print(bot.get_response("Hello!"))

  # Get a JSON dump of the current state of the bot
  dump = bot.serialize()

  # Recreate a bot by providing the same JSON dump as context.
  bot2 = chatbot.ChatBot(context=dump)

  # Get a response from the bot
  print(bot.get_response("When is the next CSI event?"))
"""


# TODO: Add tests.
class ChatBot(object):
    """Represents a chatbot for a certain conversation.

    :param context: A previously serialized version of a bot. Do not pass if
                    there was no previous context.
    :param events: A list of all the current events.
    """

    def __init__(self, context=None, events=None):
        # type: (Optional[str], Optional[List[Event]]) -> None
        super(ChatBot, self).__init__()
        if events is None:
            events = []

        self._context = self._deserialize(context)
        self._events = events

    # TODO: Actually do something.
    def serialize(self):
        """Returns a JSON object that represents the state of the context.
        """

        return "{}"

    def get_response(self, message):
        # type: (str) -> Tuple[str, Optional[str]]
        """Get a response for the user's message.

        :param message: The message from user to generate a response for.
        :rtype: A tuple of 2 strings - (response, action)
        """

        action = None
        return "You said - " + message, action

    @staticmethod
    def _deserialize(dump):
        """
        :rtype: An object that contains the de-serialized state.
        """

        return {}
