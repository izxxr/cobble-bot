# Loot Tables
Loot tables are JSON files located in `data/loot_tables` directory that determine the loot
that can be obtained from different types.

In a loot table, there must be a `name` key which is typically but not necessarily same as loot
table file name. The other keys are item IDs that can be obtained in the loot with value being
a loot table item object.

The structure of loot table item object is like so:

|        name         |                           description                                                            |
|:-------------------:|:------------------------------------------------------------------------------------------------:|
|   `probability`     | The probability of obtaining the item. In range `0` to `1` inclusive.                            |
|   `quantity`        | A two-element tuple (array) representing lower and upper bound of quantity obtained.             |
|   `durability`      | (only for durable items), A two-element tuple representing lower and upper bound of durability.  |

The values for `quantity` and `durability` are two-element fixed array representing the range of quantity or durability
of item obtained. A random integer is generated between the range (both endpoints inclusive) to represent quantity and durability.

Loot tables are referenced under the "Loot Tables" heading on the relevant pages.
 
