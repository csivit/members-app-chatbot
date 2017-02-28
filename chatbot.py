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

For now, it's extremely dumb:

- It cannot hold a conversation.
- It cannot answer anything that is not direct and about CSI events.
- It can only respond to a few things related to things it knows about - which
  are CSI events.

This shall be improved over the coming months.
"""

import textwrap
import dateutil.parser

__all__ = ["ChatBot"]

_WELCOME_MESSAGE = textwrap.dedent("""
    Hello there! I'm ChatBot. You can ask me questions about
    CSI events and about your membership.

    If you wish to know what kind of questions you can ask me, ask me "
    What do you know?"
""").strip("\n")

_UNKNOWN_REQUEST_RESPONSE = (
    "I could not understand what you said. "
    "I'll try to learn how to respond to this..."
)

_WHAT_BOT_KNOWS = textwrap.dedent("""
    I can answer questions such as:
        Which is the next CSI event?
        Where will Codespace be held?
        When is the next event?
        Where will the next event be?
""").strip("\n")

question_word_fields_mapping = {
    "which": ["venue", "datetime"],
    "what": {
        "*": ["description", "venue", "datetime"],
        "time": ["datetime"]
    },
    "when": ["datetime"],
    "where": ["venue"],
}


def _normalize(name):
    # XXX: This shouldn't be needed later.
    for c in "-_":
        name = name.replace(c, " ")

    return tuple(_tokenize(name))


def _tokenize(sentence):
    # XXX: Use NLTK later on for this.
    for c in "_-,!.'?":
        sentence = sentence.replace(c, " ")
    return sentence.lower().split()


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

        self._possible_targets = {
            _normalize(event["name"]): event for event in events
        }

        # TODO: Add semantic similarity measurement
        for term in ["next event", "next CSI event"]:
            self._possible_targets[_normalize(term)] = events[0]

        # XXX: Special cased. Not good.
        self._possible_targets[_normalize("you know")] = "what-bot-knows"

    def get_response(self, message=None):
        # type: (Optional[str]) -> Tuple[str, Optional[str]]
        """Get a response for the user's message.

        :param message: The message from user to generate a response for.
                        If this is None, a welcome message is printed.
        :rtype: A tuple of 2 strings - (response, action)
        """
        action = None

        try:
            if message is None:  # First message
                response = _WELCOME_MESSAGE
            else:  # Needs to be a question
                selector, target_term = self._extract_selector_target(message)
                if selector is None:
                    response = _UNKNOWN_REQUEST_RESPONSE
                else:
                    response, action = self._compose_message(
                        selector, target_term
                    )
        except Exception:
            # TODO: Log an error
            return _UNKNOWN_REQUEST_RESPONSE, None
        else:
            return response, action

    def _extract_selector_target(self, message):
        # Note: Future improvements include the use of a better tokenizer
        #       and POS tagger so as to be able to extract the required
        #       information from input.

        msg_words = _tokenize(message)

        # Determine Question asked
        for q_word, response_match in question_word_fields_mapping.items():
            # Determine selector
            try:
                qw_index = msg_words.index(q_word)
            except ValueError:
                continue
            selector = (q_word,)
            if isinstance(response_match, dict):
                # Check the next word as well
                if msg_words[qw_index + 1] in response_match:
                    selector = (q_word, msg_words[qw_index + 1])

            # target is selected using event selectors
            target_term = None

            for possible_target in self._possible_targets:
                matches = True
                try:
                    first = msg_words.index(possible_target[0])
                except ValueError:
                    continue

                # This next bit is horrible. But I'm lazy and our dataset is
                # never going to be big.
                for i, word in enumerate(possible_target):
                    try:
                        idx = msg_words.index(word, first)
                        if idx != first + i:
                            raise ValueError("not matching")
                    except ValueError as e:
                        matches = False
                        break

                if matches:
                    target_term = possible_target
                    break

            return selector, target_term

        return None, None

    def _compose_message(self, selector, target_term):
        fields = question_word_fields_mapping

        for term in selector:
            fields = fields[term]

        if "*" in fields:
            fields = fields["*"]

        target = self._possible_targets[target_term]

        if target_term == ("you", "know") and selector == ('what',):
            return _WHAT_BOT_KNOWS, None

        parts = []
        if "description" in fields:
            parts.append("{description}")

        if any(i in fields for i in ["venue", "datetime"]):
            parts.append("{name} will be held")
            if "venue" in fields:
                parts.append("in {venue}")
            if "datetime" in fields:
                parts.append("on {datetime}")

            parts[-1] = parts[-1] + "."

        response_template = " ".join(parts)

        datetime_str = dateutil.parser.parse(target["date"]).strftime(
            "%b %d %Y at %I:%M%p"
        )

        di = {
            "name": target["name"],
            "description": target["desc"],
            "datetime": datetime_str,
            "venue": target["venue"]
        }

        return response_template.format(**di), None

    # TODO: Will modify to actually do something later.
    def serialize(self):
        """Returns a JSON object that represents the state of the context.
        """

        return "{}"

    @staticmethod
    def _deserialize(dump):
        """
        :rtype: An object that contains the de-serialized state.
        """

        return {}
