# WoW-SoD-Timer-Discord-Bots
Discord Timer Bots for both the weekly and biweekly SoD reset, written in Python

How to run the bots:
- Create a Application & Bot in Discords admin panel, only permission needed is for the bot to change its nickname. Copy bot-token on creation
- Install python, make sure to set the environment variable on install if on windows
- make sure all imports are available:
    pip install -U discord.py
    pip install audioop-lts
    pip install datetime
    pip install dotenv
- create or edit ".env" file in directory of python script, contains: 
    TOKEN=insertBotTokenHere
    STATUS="insertDiscordStatusForBotHere"

Probably a good idea to create a shell/batchfile and autostart it on serverreboot.
