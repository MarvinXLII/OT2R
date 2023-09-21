## ABOUT

This is a randomizer for the Steam release of Octopath Traveler II.

## OPTIONS

See the executable for full descriptions of each option. Options include:

* Shuffle job skills
* Shuffle job weapons\*
* Randomize skill JP costs
* Randomize skill power
* Shuffle support skills
* Shuffle job stats
* Shuffle chests, hidden items, NPCs' items, guild licenses
* Shuffle jerky produced from captures
* Randomize enemy shields\*\*
* Shuffle enemies from random encounters
* Shuffle bosses
* Shuffle stealable items from enemies
* Shuffle items dropped by enemies
* Shuffle requirements for getting licenses from guilds

\* Many Attack animations don't exist and are messed up. Plus optimizing weapons won't work properly.

\*\* This is incomplete for some bosses.

## Events & Key Item Shuffle

The intent of these options is to shuffle around main story chapters
along with a few very important key items: Al's bag, the Mercantile
Manuscript, the Gramophone, the Grand Terry, and the Cloudy/Shiny
Mirror.  These items and chapters are unlocked whenever you finish a
chapter. Other options include how PCs are recruited, when EX Skills are
learned, when boats spawn, and more. Read the explanations in the
executable to get a better idea of what each option does.

Logic is included to ensure all seeds are beatable (or at least they
should be!), but make sure to start with the correct character. Seeds
are only designed for a single character to be beatable. See the
STARTING_CHARACTER.txt output file for which main protagonist to use.

A known issue is that sprites won't always spawn when a new PC joins
your party. They will spawn properly as soon as you open and close the
menu, or change screen. Please see this only as a minor inconvenience.

Other issues are mainly with NPCs spawning twice when doing chapters
out of order. Again, this is just a minor inconvenience and shouldn't
affect gameplay.

For technical reasons, Fast Travel had to be toggled off for Cross
Path chapters Thief & Cleric 1 and Dancer & Warrior 2. It shouldn't
affect completing these chapters as they should always be trivial.

## USAGE

Download and run the executable from the Releases page. Load the
game's Pak file, select your desired options, and press the
`Randomize` button. The randomizer will build a patch and dump it into
the folder `seed_###`. Copy the patch `rando_P.pak` into the folder
containing the game's Pak file, then load the game. If all is working,
you should see `Randomizer` on the game's title screen.

