# Polybot
> The Team WP Discord Server has a matchmaking bot!

This is a Discord bot that allows matchmaking between players. Once you add yourself (a beacon) to a waiting list, the bot will @ you when someone else joins the same waiting list. Now you can get on your day and not have to stare at the matchmaking channel!

This is a new version of Polybot, written in Python and using the brilliant and battle-tested discord.py library. The testing library has been expanded to allow end-to-end testing in a live Discord environment.

## How to use 🤔
### Instructions
1. Add yourself to a list! Post: `!games sfv 2.5` That adds you to the SFV list for 2.5 hours
1. You can specify a platform! Post `!games tekken 2.5 xbox` You can also specify PC, but the bot will default to PC anyway 😊
1. You can list everyone waiting for all games! Post: `!games`
1. Or just the game you want! `!games sfv`
1. Remove yourself from the list: Post: `!stop`

Spam as much as you want during this Beta Test, cooldowns exist just in case.
`!g` / `!games` do the same thing. Use whatever you like.

### Current games list
Command | Title | Platforms
------- | ----- | ---------
**3S** | 3rd Strike | `PS4, PC, FC`
**BBXTAG** | BlazBlue x Tag Battle | `PS4, PC, SWITCH`
**DBZ** | Dragonball FighterZ | `PS4, PC, XBOX, SWITCH`
**FC** | Fightcade | `PC`
**FEXL** | Fighting EX Layer | `PC, PS4`
**GG** | Guilty Gear Xrd: Rev2 | `PS4, PC`
**KOF98** | KoF98 (UM) | `FC, PC`
**KOF2002** | KoF2002 (UM)| `FC, PC`
**KOF14** | King of Fighters 14 | `PS4, PC`
**MHW** | Monster Hunter World | `PS4, PC`
**MK11** | Mortal Kombat 11 | `PC, PS4, XBOX, SWITCH`
**MVCI** | Marvel vs Capcom: Infinite | `PS4, PC, XBOX`
**SAMSHO** | Samurai Shodown | `PS4, PC, XBOX, SWITCH`
**SC6** | SoulCalibur 6 | `PS4, PC, XBOX`
**SFV** | Street Fighter V | `PS4, PC`
**SMASH** | Super Smash Bros. Ultimate | `SWITCH`
**ST** | Super Turbo | `PS4, PC, FC`
**SFA** | Street Fighter Alpha 2 / 3 | `FC`
**TEKKEN** | Tekken 7 | `PS4, PC, XBOX`
**UNIST** | Under Nigh... The other ST | `PS4, PC`
**USF4** | Ultra Street Fighter 4 | `PS4, PC, 360, PS3`

## Feedback, issues
If you really love me, you'll signup to GitHub and use the `Issues` tab to post any problems you've encountered! Not just bugs 🐞 though, submit any new features you'd like as well!

Why? Cause GitHub is pretty neat!

## Contributing
There will be a lot of you that are better at programming that I am, so if you'd like to contribute to fixing an issue or feature, let me know in that particular issue in the tracker.

## Installing
Pre-requisites: Git, Python 3.7+, Docker. Your python3 command may be setup as `python` or `python3`. Check before proceeding. This guide is for Unix-likes.

#### 1. Clone the repo from github to your local storage.
> `git clone https://github.com/monkiepaws/polybotpy.git polybotpy`
> 
> `cd polybotpy`

#### 2. Create a Python virtual environment and download packages.
> `python -m venv env`
> 
> `source ./env/bin/activate`
> 
> `pip install -r requirements.txt`

#### 3. Create an environment file TODO

#### 4. Run Amazon DynamoDb Local via Docker, allow build script to execute, and set up database

> `sudo docker run -d -p 8000:8000 amazon/dynamodb-local`
> 
> `chmod -x ./testing/dynamodb/build.sh`
> 
> `./testing/dynamodb/build.sh`

#### 5. Run the bot
> `python bot.py`
