# Jackie Boy
- [Introduction](#introduction)
- [Game exe](#game_exe)
- [Run source yourself](#run_source_yourself)
- [Credits](#credits)

## <a name="introduction"></a>Introduction
todo and UML

## <a name="game_exe"></a>Game exe
You will find all the releases zipped in the \Releases folder. Simply download the desired zipped folder, unzip it, and then execute the shortcut file named 'JackieBoy'.

## <a name="run_source_yourself"></a>Run source yourself
If you would like to run the source code locally; clone the project and then be sure to install the involved libraries. Afterwards, within your IDE, run main.py (python ./main.py)
| library | pip |
|---|---|
| pygame-ce | pip install pygame-ce |
| pytmx | pip install pytmx |

Map editor:
- Tiled (https://www.mapeditor.org/)

Within the folder \data:
- \levels contains the tmx files for the maps
- \tilesets contains the tsx files for the tile sets

## <a name="credits"></a>Credits
### Tutorials

Clear Code<br>
Creating an amazing 2D platformer in Python [ SNES inspired ]<br>
https://www.youtube.com/watch?v=WViyCAa6yLI<br>
- Greatly helpful by providing insight on how he organizes the files and classes, which enabled me to more easily implement my own features. For the features he has in this tutorial that I chose to include in my game, I would implement it on my own before comparing it with his method.

CDcodes<br>
Pygame Tile Based Game Tutorial: Physics and Delta Time<br>
https://www.youtube.com/watch?v=v_linpA7uXo<br>
- Helped me understand the fundamentals of implementing movement and sprinkling some pseudo momentum. 

DaFluffyPotato<br>
Ramps - Pygame Tutorial<br>
https://www.youtube.com/watch?v=EHfqrAEmVyg<br>
- Helped me understand how to implement a ramp, which is an image contained in a rectangluar tile, in the game so that the player interact properly with it.

### Graphics

Very thankful to https://opengameart.org !!!

Clear Code
- ./graphics/effects/particle
- ./graphics/enemies/floor_spikes
- ./graphics/items/skull
- ./graphics/level/bg/tiles
- ./graphics/level/big_chains
- ./graphics/level/clouds
- ./graphics/level/flag
- ./graphics/level/platform
- ./graphics/level/small_chains
- ./graphics/level/water
- ./graphics/objects/boat

Platformer Art Complete Pack by Kenney Vleugels (www.kenney.nl). License (CC0)<br>
https://opengameart.org/content/platformer-art-complete-pack-often-updated
- ./graphics/enemies/bats
- ./graphics/level/torch
- ./graphics/objects/environment
- ./graphics/tiles
- ./graphics/weapons/umbrella

MoikMellah. License (CC0)<br>
https://opengameart.org/content/animated-birds-32x32
- ./graphics/enemies/bird_brown
- ./graphics/enemies/bird_white

Shepardskin (https://twitter.com/Shepardskin). License (CC0)<br>
https://opengameart.org/content/german-shepherd-0
- ./graphics/enemies/dog

Hellkipz. Shepardskin (https://twitter.com/Shepardskin). License (CC0)<br>
https://opengameart.org/content/husky-sprites
- ./graphics/npcs/husky

alizard. License (CC0)<br>
https://opengameart.org/content/pixel-squirrel
- ./graphics/enemies/squirrel

loltsilol. License (CC0)<br>
https://opengameart.org/content/tennisball
- ./graphics/projectile/ball

Overaction Game Studio. License (CC0)<br>
https://opengameart.org/content/wooden-stick
- ./graphics/weapons/stick


### Audio

cynicmusic.com pixelsphere.org. License (CC0)<br>
https://opengameart.org/content/battle-theme-a
- ./audio/music/battleThemeA.mp3
- ./audio/music/TownTheme.mp3

Johan Brodd. License (CC BY-SA 3.0)<br>
https://opengameart.org/content/sunny-paradise-act-1
- ./audio/music/Sunny paradise act 1.mp3

tcarisland. License (CC BY 4.0)<br>
https://opengameart.org/content/the-end
- ./audio/music/End Theme.wav

mieki256. License (CC0)<br>
https://opengameart.org/content/male-dead-voice
- ./audio/sound_effects/enemy_hit

Little Robot Sound Factory (www.littlerobotsoundfactory.com). License (CC BY 3.0)<br>
https://opengameart.org/content/8-bit-sound-effects-library
- ./audio/sound_effects/menu_select
- ./audio/sound_effects/player_collect

artisticdude. License (CC0)<br>
https://opengameart.org/content/rpg-sound-pack
- ./audio/sound_effects/player_attacks
- ./audio/sound_effects/shop
- ./audio/sound_effects/sign_hit
- ./audio/sound_effects/sign_spin

sauer2. License (CC0)<br>
https://opengameart.org/content/oldschool-win-and-die-jump-and-run-sounds
- ./audio/sound_effects/player_death
- ./audio/sound_effects/round_end.wav

Michel Baradari. License (CC BY 3.0)<br>
https://opengameart.org/content/11-male-human-paindeath-sounds
- ./audio/sound_effects/player_hit

Jesus Lastra. License (CC0)<br>
https://opengameart.org/content/8-bit-jump-1
- ./audio/sound_effects/player_jump

dklon. License (CC BY 3.0)<br>
https://opengameart.org/content/boom-pack-1
- ./audio/sound_effects/sign_fire_poles

Bart Kelsey. License (GPL 2.0)/(GPL 3.0)/(CC-BY-SA 3.0)<br>
https://opengameart.org/content/whoosh-2
- ./audio/sound_effects/sign_moving

Composed by: Jon K. Fite. License (CC BY 3.0)<br>
https://opengameart.org/content/victory-2
- ./audio/sound_effects/Victory!.wav
