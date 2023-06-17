# JSON files
For the sake of convenience and ease of development, Cobble uses JSON files to store data about
in-game assets such as items and biomes. These JSON files are inside the `data` directory.

These JSON files are cached by the bot at the start up and are not read again until next
startup unless `?reloadmeta` command is used by a bot admin.

## Items (`items.json`)
This file stores the information about items. The key is the item ID while the value is
an item object. Following table shows the attributes used in an item object.

|        name         |                           description                                        |
|:-------------------:|:----------------------------------------------------------------------------:|
|   `display_name`    | The name used in the bot's interface to represent this item.                 |
|   `rarity`          | The rarity of item. \*                                                       |
|   `type`            | The type of item. \*\*                                                       |
|   `description`     | A short description of item.                                                 |
|   `emoji`           | The emoji for representing this item in bot's interface. \*\*\*              |
|  `food_hp_restored` | The amount of HP (in float) restored when eaten (only for food items.)       |
|  `durability`       | For durable items, the maximum or total durability of item.                  |
|  `crafting_recipe`  | Mapping of key being item ID and value for quantity for crafting this item.  |
| `crafting_quantity` | The quantity of item produced on crafting the item once.                     |
|  `smelting_recipe`  | The ID of item that's needed to be smelted to produce this item.             |
|  `smelting_product` | The item obtained on smelting this item.                                     |

\* One of `common`, `uncommon` or `rare`

\*\* One of `mineral`, `food`, `materials`, `collectibles`

\*\*\* For custom emojis, use the ID + name format. For default emojis, use the unicode symbol instead of Discord's markdown format.


## Biomes (`biomes.json`)
This file stores information about biomes.

|        name              |                           description                                        |
|:------------------------:|:----------------------------------------------------------------------------:|
|   `display_name`         | The name used in the bot's interface to represent this biome.                |
|   `rarity`               | The rarity of biome. \*                                                      |
|   `description`          | A short description of biome.                                                |
|   `emoji`                | The emoji for representing this biome in bot's interface. \*\*               |
|  `discovery_probability` | The probability of discovering this biome while exploration.                 |
|  `background`            | An image URL for the background of this biome (image in discovery embed)     |
|  `discovery achievement` | The bitwise value for the achievement given to player on discovery of biome. |

\* One of `common`, `uncommon` or `rare`

\*\* For custom emojis, use the ID + name format. For default emojis, use the unicode symbol instead of Discord's markdown format.

## Loot Tables
See [Loot Tables](loot-tables.md) page.
