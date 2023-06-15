# Biomes and Exploration
Different biomes can be discovered by the player during exploration.

## Biomes
The feature of biomes is similar to how it is in Minecraft. Each biome has specific characteristics
and a specific set of loot. Certain biomes are common while others are rarer. The rarer a biome is,
the more valuable its loot will be.

There are currently **3** biomes:

- Plains
- Desert
- Ocean

## Exploration and Discovery
When a player starts a profile, the only biome unlocked and explorable is the Plains. Using
the `/explore` command, the player can explore a specific biome and obtain loot from exploration.
This command has a cooldown of 10 minutes.

When explore command is ran, depending on the rarity of a biome, there is a specific probability
of discovering a new biome. The player will be notified if a new biome is discovered. Upon
discovering a biome, that biome is unlocked and is available to be explored by player.

Each biome has a specific set of loot, generally consistent with the theme of biome.

## Statistics
**XP:** On exploring, depending on the amount of loot obtained, the player gains a random number of
experience points.

**Health:** On exploring, the player will lose either no health or half health point. Health lost
is independent of biome being explored and obtained loot. If a player dies while exploring,
no loot is obtained.

## Loot Tables
The loot obtained from exploration varies depending on the biome explored. Following loot tables
determine the loot obtained along with the probability and quantity of it obtained:

- [exploration_plains.json](../../data/loot_tables/exploration_plains.json)
- [exploration_desert.json](../../data/loot_tables/exploration_desert.json)
- [exploration_ocean.json](../../data/loot_tables/exploration_ocean.json)
