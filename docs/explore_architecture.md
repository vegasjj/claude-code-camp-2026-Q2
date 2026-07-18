# Preliminary Agent Architecture

## Agent Details

Model: Gemini Flash 3.5 (medium)
Harness: Antigrvity CLI

The [ANTIGRAVITY.md](../week0_explore/explore_architecture/001_playing_agent/ANTIGRAVITY.md) file set the agent role and states basic intrucctions to connect to the MUD along with the relevant credentials to play with the "dummy" character.

To mantain the player status and world memory, the agent is instructed to update the [player.md](../week0_explore/explore_architecture/001_playing_agent/data/player.md) and [world.md](../week0_explore/explore_architecture/001_playing_agent/data/world.md) respectively.

## Goal

A test run is needed to assess whether a simple agent is efficient enough to navigate the MUD World without detailed knowledge of the world of playing instrucctions beforehand.

## Prompt

"Find the bakery and list what is on the menu."

# Observations

The agent stayed confined withing the [agent's directory](../week0_explore/explore_architecture/001_playing_agent/) looking for clues to "find the bakery" until it found the [ANTIGRAVITY.md](../week0_explore/explore_architecture/001_playing_agent/ANTIGRAVITY.md) with the initial instrucctions to connect the the MUD which trigger a flow the create a series of [scripts](../week0_explore/explore_architecture/001_playing_agent/scripts/) to interact witht the MUD interface.