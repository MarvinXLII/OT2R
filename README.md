## About

This is a randomizer for the Steam release of Octopath Traveler II.

## Options

See the executable for full descriptions of each option. Options include:

* Shuffle job skills
* Shuffle job weapons\*
* Randomize skill JP costs
* Randomize skill power
* Shuffle support skills
* Shuffle job stats
* Shuffle key items, guild licenses, and chapters/events
* Shuffle chests, hidden items, NPCs' items, sidequest rewards
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
along with key items. These key items are shuffled separately from
the rest of the item pool so there should be no need to check each and
every chest and NPC to complete a seed.

Logic is included to ensure all seeds are beatable (or at least they
should be!), but make sure to start with the correct character. See
the STARTING_CHARACTER.txt output file for which main protagonist to
use. Bear in mind that there is currently not logic for shuffling
bosses. If you shuffle both bosses and Main Story Chapters/Events, it
is recommended that you keep mid/late game bosses separate.

For a full list of options, see the executable on the releases page.

Key Items from the Main Story included are:

* Agnea Ch. 2: Theater Ticket
* Agnea Ch. 3: Wooden Sword
* Agnea Ch. 4: Cute Shoes
* Castti Ch. 2 (Winterbloom): Rosa's Medicine
* Hikari Ch. 3: Weapons Deal Details
* Ochette's Beasts: Acta, Tera, and Glacis
* Partitio Ch. 2: Clockite
* Partitio Scent of Commerce: Grand Terry, Manuscript, Gramophone
* Temenos Ch. 2: The Culprit's True Identity
* Temenos Ch. 3 (Crackridge): Mysterious Notebook
* Temenos Ch. 3 (finish both routes): Kaldena's Notebook
* Throne Ch. 2 (Mother's Route): Horse Coin, Mask
* Throne Ch. 3 (Mother's Route): Mother's Key
* Throne Ch. 3 (Fathers's Route): Fathers's Key
* Osvald Ch. 4: Library Rumor, Harvey's Whereabouts, An Eyewitness to Harvey
* Osvald Ch. 5: All 5 Black Crystals
* Crossed Path Cleric & Thief 1: Cloudy Mirror Fragment
* Crossed Path Cleric & Thief 2: Folded Paper, Cloudy Mirror
* Crossed Path Dancer & Warrior 1: Horse Tail
* Crossed Path Dancer & Warrior 2: Dancer's Mask, Sacred Wood, Wine Offering
* Crossed Path Scholar & Merchant 1: Mirror, Precision Lens, Metalworking Lens
* Rusty Weapons: Rusty Sword, Rusty Polearm, Rusty Dagger, Rusty Axe, Rusty Bow, Rusty Staff
* Inventor Parts: Rainbow Glass Bottle, Scrap Metal, Natural Magnetite, Ancient Cog, Mythical Horn, Tin Toy
* Galdera's Sidequest "The Traveler's Bag": Al's Bag
* Galdera's Sidequest "Procuring Peculiar Tomes": all 3 tomes
* Galdera's Sidequest "From the Far Reaches of Hell": How to Decipher Unknown Languages

Key Items from Sidequests included are:
* A Devilishly Delicious Dish: Special Bait, Delsta Devil
* A Gambling Man: Truth of the Game Parlor
* A Mysterious Box: Mysterious Box
* A Present for My Son: Silver Quill
* A Young Girl's Wish: Deluxe Crepe, Adventures of an Apprentice Cleric’s Sequel
* Alpione's Next Chapter: Hunting Request
* Building Bridges: Amulet of Affection
* Crop Revival: Crop Tapestry Pattern
* Culinary Cunning: Spicy Chicken Recipe
* Descended from Royalty: Nyx Royal Family Tree, Nyx Family History
* Goading the Grapes: Tricks to Growing Grapes
* Lingering Love: Treasured Necklace
* Melia's Next Chapter: Letter from the Snowhares
* Mikka’s Next Chapter: Earrings
* Misha’s Next Chapter: Man in a Brown Coat, Garbage Collector
* Pearl Hunt: 4 Pretty Pearls
* Pilgrim Protection: 3 Sacred Flame Candles
* Plans from a Ruined Nation: Fort Orochi Plans
* Proof of Guilt: Azure Sun Sword
* Proof of Justice: A Killer's Motive, Stolen Sword
* Shirlutto's Next Chapter: Lute, Paper Play, History Book
* Stolen Goods: Stocked Goods
* The Missing Girl: Cloudy Crystal Bracelet
* The Sword in the Stone: Sturdy Pickaxe
* The Treasures of Ku: Dragon Vase, Phoenix Fan
* The Washed-Up Letter: Message in a Bottle
* Traveler's Lost and Found: Aelmorite Reflector, Bottle of White Powder
* Useless Fruit: Well Iris Uses
* Veronica's Next Chapter: Dolcinaea and Gifts
* Wanted: A Good Joke: 3 jokes

Some items were already mandatory in the vanilla game for progression,
while others weren't and are now made mandatory. For reference, here's
a list of new requirements enforced when the Main Story Key Items option is selected:

* Hikary Ch. 3: Weapon Deal Details is needed to trigger cutscenes in the forest.
* Ochette Ch. 3: All 3 beasts are needed to start the first cutscene with Juvah.
* Throne Ch. 2 (Mother's Route): The Horse Coin must be given to the man in the saddelry.
* Throne Ch. 2 (Mother's Route): The Mask is needed to play the game at Death's Table.
* Throne Ch. 3 (Mother's Route): The Habit is needed to enter the Garden Orphanage.
* Temenos Ch. 2: Guards won't disappear until you know the Culprit's True Identity.
* Temenos Ch. 3 (Crackridge Route): The Mysterious Notebook is needed to trigger final cutscenes in the Fellsun Ruins.
* Temenos Ch. 4: Kaldena's Notebook is needed to trigger cutscenes in the Wandering Wood.
* Osvald Ch. 4: All 3 pieces of info on Harvey are needed to unlock the dungeon in the Montwise Library.
* Osvald Ch. 5: All 5 Black Crystals are needed to trigger the battle with Harvey.
* Crossed Path Cleric & Thief 2: Both the Cloudy Mirror Fragment and Folded Paper are needed to trigger cutscenes in the Cavern of the Moon and Sun.

## Known Issues

* When shuffling PCs, they won't always spawn properly when just
  recruited. They will spawn properly by opening/closing the menu,
  spawning a battle, or changing screens.

* When shuffling Main Story Chapter/Events, some NPCs might spawn
  twice, most notable in Agnea's Ch. 2 and Castti's Ch. 2 (Winterbloom).

* For technical reasons, Fast Travel had to be toggled off for Cross
  Path chapters Thief & Cleric 1 and Dancer & Warrior 2 when shuffling
  Main Story Chapters/Events with Sacred Flames.

* When shuffling key items, some spots can only give 1 Clockite,
  rather than 5. This was fixed by tweaking Partitio's
  Chapter 2 to need only 1 Clockite for progression.

## Usage

Download and run the executable from the Releases page. Load the
game's Pak file, select your desired options, and press the
`Randomize` button. The randomizer will build a patch and dump it into
the folder `seed_###`. Copy the patch `rando_P.pak` into the folder
containing the game's Pak file, then load the game. If all is working,
you should see `Randomizer` on the game's title screen.
