# Discord RPC Creator-Defined Statement for RenPy
# Provides custom 'discord' statement for easy status updates in scripts

# IDE hints (not executed by Ren'Py)
from typing import Any, Dict, Callable

try:
    import renpy
except ImportError:
    pass

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
    """Parse discord statement arguments with support for optional parameters."""
    subcommand = lexer.word()
    if not subcommand:
        renpy.error("Expected subcommand after discord statement (e.g. custom, dialogue, in_game, menu, paused, loading, main_menu)")

    args = {}

    if subcommand == "custom":
        state = lexer.string()
        if not state:
            renpy.error("discord custom requires at least a state string")
        details = lexer.string() if not lexer.eol() else None
        args["state"] = state
        args["details"] = details
    elif subcommand == "dialogue":
        character = lexer.string() if not lexer.eol() else None
        scene = lexer.string() if not lexer.eol() else None
        args["character"] = character
        args["scene"] = scene
    elif subcommand == "in_game":
        chapter = lexer.string() if not lexer.eol() else None
        character = lexer.string() if not lexer.eol() else None
        args["chapter"] = chapter
        args["character"] = character
    elif subcommand == "menu":
        menu_name = lexer.string() if not lexer.eol() else "Меню"
        args["menu_name"] = menu_name
    elif subcommand in ["paused", "loading", "main_menu"]:
        pass
    else:
        renpy.error(f"Unknown discord subcommand: {subcommand}")

    lexer.expect_eol()
    return {"subcommand": subcommand, "args": args}


def execute_discord(p):
    """Execute parsed discord statement."""
    subcommand = p.get("subcommand")
    args = p.get("args", {})

    if subcommand == "custom":
        discord_set_custom(args.get("state"), args.get("details"))
    elif subcommand == "dialogue":
        discord_set_dialogue(args.get("character"), args.get("scene"))
    elif subcommand == "in_game":
        discord_set_in_game(args.get("chapter"), args.get("character"))
    elif subcommand == "menu":
        discord_set_menu(args.get("menu_name", "Меню"))
    elif subcommand == "paused":
        discord_set_paused()
    elif subcommand == "loading":
        discord_set_loading()
    elif subcommand == "main_menu":
        discord_set_main_menu()


def lint_discord(p):
    """Lint discord statement for syntax correctness."""
    subcommand = p.get("subcommand")
    valid_subcommands = {"custom", "dialogue", "in_game", "paused", "loading", "main_menu", "menu"}

    if subcommand not in valid_subcommands:
        renpy.error(f"Unknown discord subcommand: {subcommand}")

    if subcommand == "custom" and not p.get("args", {}).get("state"):
        renpy.error("discord custom statement is missing required state text")


if 'renpy' in globals() and hasattr(renpy, 'register_statement'):
    renpy.register_statement(
        name="discord",
        parse=parse_discord,
        execute=execute_discord,
        lint=lint_discord,
    )
