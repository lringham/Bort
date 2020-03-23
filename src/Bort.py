from discord.ext.commands import Bot
import glob

def parse_settings_from_file(settings_filename):
    settings_dict = {}
    try:
        # Read settings from init file
        ini_file = open(settings_filename, "r")
        settings = [f.split("=") for f in ini_file]
        ini_file.close()

        # Parse settings
        for setting in settings:
            if len(setting) == 2:
                settings_dict[setting[0].strip().lower()] = setting[1].strip()
            else:
                print("Invalid setting:", setting)
    except IOError:
        print("Could not open ini file...")
    return settings_dict


def to_extension(path):
    return path.strip().replace("\\", ".").replace(".py", "")


def parse_cogs(cogs_directory):
    cogs = glob.glob(cogs_directory + "/*Cog.py")
    return [to_extension(c) for c in cogs]


def main():
    # Parse bot settings and extensions
    ini_filename = "../Bort.ini"
    cogs_directory = "cogs"
    settings = parse_settings_from_file(ini_filename)
    cogs = parse_cogs(cogs_directory)

    # Create the bot
    command_prefixes = ["!", "\\"]
    bort = Bot(command_prefix=command_prefixes)

    print("Loading cogs...", cogs)
    [bort.load_extension(cog) for cog in cogs]

    print("Running Bort...")
    bort.run(settings["token"])

    print("Shutting down Bort...")
    [bort.unload_extension(cog) for cog in cogs]


main()
