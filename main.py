import src.bot.bot as bot


def main():
    """Setup and run Polybot. Blocking, so not suitable for testing."""
    polybot = bot.PolyBot.instance(command_prefix="!")
    polybot.run(polybot.mp_discord_client_token)


if __name__ == '__main__':
    main()
