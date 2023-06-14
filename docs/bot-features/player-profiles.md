# Player Profiles
In order to interact with the most features of Cobble bot, a user must create a player profile.
Often referred to as "Survival Profile", player profile stores all the progress of a player.

## Creating a profile (`/profile start`)
In order to create a profile, the `/profile start` slash command is used. There is no extra
arguments in this command and no extra setup is needed. As soon as the command is used, a profile
is created.

A user can only have one survival profile and if a user has a profile and uses the command, the
result would be an error message.

## Viewing your profile (`/profile view`)
You can view your profile using the `/profile view` command. The profile view shows the basic
information of a player including:

- The current level and XP
- The health of player
- The number of biomes discovered so far

## Deleting the profile (`/profile delete`)
A profile can be deleted using the `/profile delete` command. Deleting a profile completely
removes all the progress of a player from the database and this action cannot be undone.

After command has been used, a confirmation message will be shown and upon confirming, the
profile will be deleted.

