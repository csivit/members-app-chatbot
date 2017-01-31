==============
API Definition
==============

Workflow
========

The exact workflow of the ChatBot is as follows:

For every message from the user,
1. Initialize a chatbot with existing context (if any).
2. Get the response for a user message.
3. Serialize the chatbot and store that somewhere for passing to a new instance on the next initialization.

ChatBot Class
=============

.. autoclass:: chatbot.ChatBot
    :members:
