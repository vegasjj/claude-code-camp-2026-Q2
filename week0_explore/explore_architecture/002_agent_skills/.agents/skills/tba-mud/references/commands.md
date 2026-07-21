# tbaMUD / CircleMUD Reference Guide

This reference outlines the common commands for playing and navigating in tbaMUD (which is a variation of CircleMUD).

## 1. Basic Movement
You can move around the world using the cardinal directions. You can use full names or their single-letter abbreviations:
*   `north` (or `n`)
*   `south` (or `s`)
*   `east` (or `e`)
*   `west` (or `w`)
*   `up` (or `u`)
*   `down` (or `d`)

## 2. Information & State
*   `look` (or `l`): Inspect your current room, its exits, items, and NPCs.
*   `look <direction>`: Look into an adjacent room (e.g. `look north`).
*   `look <item/NPC>`: Inspect a specific object or character.
*   `exits`: Display the exits in the current room and where they lead.
*   `score` (or `sc`): Show your character's stats, level, gold, experience, hit points (HP), mana, and moves.
*   `inventory` (or `i`): List items currently in your inventory.
*   `equipment` (or `eq`): List items currently equipped on your body.
*   `who`: List players currently online.
*   `time`: Show the current game time.
*   `weather`: Show the current weather conditions.

## 3. Object Interaction
*   `get <item>` / `take <item>`: Pick up an item from the floor.
*   `get all`: Pick up all items from the floor.
*   `get <item> <container>`: Retrieve an item from a container (e.g. chest, bag).
*   `drop <item>`: Drop an item onto the floor.
*   `put <item> <container>`: Put an item into a container.
*   `wear <item>` / `wield <item>`: Equip an item.
*   `remove <item>`: Unequip an item.
*   `examine <object>`: Take a closer look at an object or container.

## 4. Communication
*   `say <message>` (or `' <message>`): Speak to everyone in the same room.
*   `shout <message>`: Shout a message to the entire zone.
*   `tell <character> <message>`: Send a private message to a specific player.
*   `gossip <message>`: Talk on the global gossip channel.
*   `ask <NPC> <question>`: Talk to an NPC.

## 5. Combat & Survival
*   `kill <NPC>` / `hit <NPC>`: Initiate combat with a target.
*   `flee`: Attempt to run away from combat to a random adjacent room.
*   `consider <NPC>` (or `con`): Assess an NPC's strength relative to yours.
*   `diagnose <NPC>`: Check the health status of an NPC or player.

## 6. Miscellaneous
*   `color off`: Turn off ANSI color codes (this client automates this to make parsing clean).
*   `color on`: Turn on ANSI color codes.
*   `help <topic>`: Show the MUD's in-game help text for a command or keyword.
*   `commands`: List all commands available to your character.
