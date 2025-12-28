# CodeAZ-BOT
Written by CodeAZ Community

### Notable features:
- XP system
- Limiting commands to one channel
- Welcome and farewell messages
- a role given to new users
- Reaction Roles
- Meme command via meme-api

### Requirements:
- discord.py
```
pip install discord.py
```
### Installation:
1. Create the bot in the Discord Developer Portal
2. Enable all bot intents in the Bot tab.
3. Enable following bot permissions:
    - Read Messages / View Channels
    - Send Messages
    - Read Message History
    - Embed Links (for memes)
    - Add Reactions
    - Use External Emojis (if reaction roles use them)
4. Generate the invite link, select the following scopes in the OAuth2 tab:
    - bot
    - application.commands
5. Use the link and add the bot to your server.
6. Modify the config and or the source to your desire. Do not forget to add the token to config.
7. Run the program! preferably host it in a server.

### Configuration:
We have tried to keep the bot as modular as possible, making sure most things can be disabled/enabled through the config file. Despite this, there are still a few imperfections. There are 2 files of configs, one being the active one on our discord sever, and the other being a blank. I belive the config files are relatively intuitive, so please inform us of any confusing parts.

### Overview of most commands
`xp` - lists the top 10 users with the most xp points.

`xp-give [amount] [member]` - sends [amount] many xp points to member [member] and subtracts that amount from the commands user.

`xp-send [amount] [member]` - sends [amount] many xp points to member [member] WITHOUT subtracting that amount from the commands user.

`xp-bet [amount]` - bets [amount] many xp points with a 90/10 chance of losing and winning that much points

`xp-daily` - gives xp to the user, giving them a random amount from the minimum-maximum range. currently this is 10 and 50 in the server (as of 12/28/2025).

`meme` - send a random meme from meme-api.com to the user.
