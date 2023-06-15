# Inventory and Crafting
Cobble provides an interactive inventory and crafting system.

## Inventory
The inventory is a basic storage space where all the items obtained by the user are placed. The
inventory can be viewed using the `/inventory view` command that features an interactive pagination
for viewing the items in inventory.

## Discarding an item
An item can be discarded from inventory using the `/inventory discard` command. This command
takes two arguments, the name of item to discard and the quantity to discard. The quantity
defaults to complete amount present in inventory. Alternatively, `all` can be passed to
quantity to discard the complete amount.

Discarded items are lost and the action cannot be undone.

## Viewing information of an item
The `/inventory info` command shows information about an item regardless of whether the item
is present in inventory or not. The information includes crafting recipe and other metadata
about the item.

## Crafting items
Certain items are able to be crafted. Crafting takes a specific number of raw materials and in
cost of those materials, provide a final crafted item as product.

The `/inventory craft` command is used to craft items. In order to craft an item, the required
materials in its crafting recipe must be present in inventory. An optional quantity argument
can be added to the command to specify the quantity to craft. Note that all items cannot be
crafted.

The quantity argument determines the number of craftings to perform. The final amount of product
obtained is `quantity * crafting_quantity`. For example, two oak woods produce four sticks. If the
command `/inventory craft item: sticks quantity: 2` is ran, it would use up four oak woods and
produce 8 sticks.
