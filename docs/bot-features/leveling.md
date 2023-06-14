# Leveling
Cobble has a basic leveling system. When a profile is created, the level is 0 and as user gains
XP, the level is advanced. Levels are used to represent the progress of a player.

## Viewing level and XP
Use the `/profile view` command to view your level and XP. A progress bar is shown
representing the progress in the current level in terms of XP.

## Experience Points (XP)
XP, aka experience points, can be gained by various survival commands such as `/explore`. the amount of XP obtained from each command varies and in certain cases, such as obtaining a rare
loot in `/explore` command, would result in getting higher XP than normal.

Each level requires a specific XP to finish and levels increase, the XP required to advance to
next level also increases. Following formula is used to calculate required XP for a level:
```
required_xp = level_number * 100
```
 
## Level Advancement
Everytime a player reaches a certain amount of XP, the level is advanced. As soon as level
is advanced, a message is sent to notify the player about the advancement.
