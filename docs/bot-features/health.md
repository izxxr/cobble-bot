# Health
Player health determines the amount of HP the player has. The HP decreases gradually (often as a
result of certain commands) and if it drops to zero, the player dies.

## Viewing health
The health is viewed from the profile view command and is represented by "hearts". Each player has
8 hearts and one completely filled red coloured heart represent one HP while a half filled red heart
represents 0.5 HP. A black (non-filled) heart represents no HP.

## Dying
As soon as the health of a player drops to 0 HP (all hearts unfilled), the player dies. As a result
of dying, the player loses all the XP and levels and these statistics reset to zero.

## Healing
Health can be restored by eating food. Using the `/use` command on a food item will consume
that food item resulting in restoration of HP. If a player has full HP, they won't be able to
eat the food item.
