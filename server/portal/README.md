### websocket.py

Implements a lightly modified subclass of Evennia's core websocket protocol. It adds a couple custom send methods, as well as using the modified text2html parser to support the client's MXP-link handling.

### text2html

Implements an even more lightly modified subclass of Evennia's `TextToHTMLparser` in order to override the MXP-link syntax. Slap whatever other alterations you want to the parsing in here with impunity.