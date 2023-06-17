# Mining
Mining is a way of collecting valuable minerals.

## Required Items
In order to mine, the player must have a pickaxe in their inventory. While the pickaxe could
be of any material, it is worth noting that certain pickaxes are not able to mine certain
minerals.

If a player has multiple pickaxes of the different material, the best one (in terms of material)
is selected for mining.

The priority order (lowest to highest) is:
```
Wooden Pickaxe -> Stone Pickaxe -> Iron Pickaxe -> Gold Pickaxe -> Diamond Pickaxe
```
That means if a player has both stone and iron pickaxe in their inventory, the iron one is
automatically used for mining. Note that while gold tools are "brittle" and are not able
to mine all materials, it still follows the same priority order. This means gold takes
priority over iron pickaxe.

Except gold pickaxe, the better a pickaxe is, the better the loot is in terms of both
quantity and probability of getting rarer materials.

## Basic Mechanics
Mining can be performed using the `/mine` command. This command has a 30 minutes of cooldown.
While mining, it is guaranteed to obtain stone in some quantity.

## Statistics
**XP:** Depending on the amount of loot obtained, player gains random amount of XP.

**Durability:** The pickaxe used will lose durability points depending on the amount
of loot obtained.

**Health:** On mining, the player will lose either full health or half health point. Health lost
is independent of obtained loot. If a player dies while mining, no loot is obtained.

## Loot Tables
The loot obtained from mining is determined by the following loot table:

- [mining_wooden_pickaxe.json](../../data/loot_tables/mining_wooden_pickaxe.json)
- [mining_stone_pickaxe.json](../../data/loot_tables/mining_stone_pickaxe.json)
- [mining_iron_pickaxe.json](../../data/loot_tables/mining_iron_pickaxe.json)
- [mining_gold_pickaxe.json](../../data/loot_tables/mining_gold_pickaxe.json)
- [mining_diamond_pickaxe.json](../../data/loot_tables/mining_diamond_pickaxe.json)
