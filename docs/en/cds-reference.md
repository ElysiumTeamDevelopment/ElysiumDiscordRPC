# Creator-Defined Statements (CDS) for Discord RPC

ElysiumDiscordRPC supports a convenient command syntax (CDS) for controlling Discord status directly from Ren'Py scripts, without needing to use Python blocks or function calls with `$`.

## Installation

To use CDS, ensure that the `01-discord-rpc.rpy` file is located in the `game/libs/` folder of your project.

## Usage

### Basic Commands

#### 1. Custom Status
Sets custom text for state and details.

```renpy
# Syntax: discord custom "State" "Details"
discord custom "Exploring World" "Chapter 2"
```

#### 2. Dialogue Status
Sets the dialogue reading status with character and scene information.

```renpy
# Syntax: discord dialogue "Character Name" "Scene Name"
discord dialogue "Eileen" "Room"
```

#### 3. In-Game Status
Sets the active game status.

```renpy
# Syntax: discord in_game "Chapter Name" "Character Name"
discord in_game "Chapter 1" "Eileen"
```

#### 4. Paused
Sets the status to "Paused".

```renpy
# Syntax: discord paused
discord paused
```

#### 5. Loading
Sets the status to "Loading...".

```renpy
# Syntax: discord loading
discord loading
```

#### 6. Main Menu
Sets the status to the main menu.

```renpy
# Syntax: discord main_menu
discord main_menu
```

#### 7. Menu
Sets the status to being in a menu (e.g., Settings, Gallery).

```renpy
# Syntax: discord menu "Menu Name"
discord menu "Settings"
```

## Script Usage Examples

```renpy
label start:
    # Game start
    discord custom "Game Start" "Prologue"

    "Welcome to the game!"

    # Character interaction
    discord dialogue "Eileen" "Living Room"
    e "Hello! How are you?"

    # Transition to gameplay
    discord in_game "Chapter 1" "Searching for Clues"
    
    # ... gameplay ...

    # Pause (e.g., before a difficult choice)
    discord paused
    menu:
        "Go left":
            pass
        "Go right":
            pass

    return
```

## Benefits of CDS

1.  **Clean Code**: Commands look like native Ren'Py instructions.
2.  **Convenience**: No need to type `$` and parentheses `()`.
3.  **Readability**: It's immediately clear what the command does.
