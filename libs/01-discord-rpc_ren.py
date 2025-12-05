# Discord RPC Creator-Defined Statement for RenPy
# Provides custom 'discord' statement for easy status updates in scripts

# IDE hints (not executed by Ren'Py)
from typing import Any, Dict, Callable

renpy: Any = None
discord_set_custom: Callable = None
discord_set_dialogue: Callable = None
discord_set_in_game: Callable = None
discord_set_menu: Callable = None
discord_set_paused: Callable = None
discord_set_loading: Callable = None
discord_set_main_menu: Callable = None

"""renpy
python early:
"""

def parse_discord(lexer):
    """Parse discord statement arguments"""
    subcommand = lexer.word()
    args = {}
    
    if subcommand == "custom":
        args["state"] = lexer.string()
        args["details"] = lexer.string()
    elif subcommand == "dialogue":
        args["character"] = lexer.string()
        args["scene"] = lexer.string()
    elif subcommand == "in_game":
        args["chapter"] = lexer.string()
        args["character"] = lexer.string()
    elif subcommand == "menu":
        args["menu_name"] = lexer.string()
    elif subcommand in ["paused", "loading", "main_menu"]:
        pass  # No args
    else:
        renpy.error("Unknown discord subcommand: " + str(subcommand))
        
    return {"subcommand": subcommand, "args": args}


def execute_discord(p):
    """Execute discord statement"""
    subcommand = p["subcommand"]
    args = p["args"]
    
    if subcommand == "custom":
        discord_set_custom(args["state"], args["details"])
    elif subcommand == "dialogue":
        discord_set_dialogue(args["character"], args["scene"])
    elif subcommand == "in_game":
        discord_set_in_game(args["chapter"], args["character"])
    elif subcommand == "menu":
        discord_set_menu(args["menu_name"])
    elif subcommand == "paused":
        discord_set_paused()
    elif subcommand == "loading":
        discord_set_loading()
    elif subcommand == "main_menu":
        discord_set_main_menu()


def lint_discord(p):
    """Lint discord statement for errors"""
    subcommand = p["subcommand"]
    if subcommand not in ["custom", "dialogue", "in_game", "paused", "loading", "main_menu", "menu"]:
        renpy.error("Unknown discord subcommand: " + str(subcommand))


renpy.register_statement(
    name="discord",
    parse=parse_discord,
    execute=execute_discord,
    lint=lint_discord,
)
