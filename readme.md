# Jackie Boy
- [Video](#video)
- [Introduction](#introduction)
- [Game exe](#game_exe)
- [Run source yourself](#run_source_yourself)
- [Credits](#credits)

## <a name="video"></a>Video
https://youtu.be/jIfb4QSSqZA

## <a name="introduction"></a>Introduction
This project is a video game written in Python with the use of Pygame-ce. I decided to design and implement a 2D platformer with my dog, Jackie, as the playable character because I am tremendously fond of both.

The reason I chose to create my first game with Pygame is because I think of it like 'learning to walk before I run.' I've played around with modern game engines like Unreal, but I wanted to start at near 'ground level' without all the tools already provided to me. I enjoy understanding and working on the entire stack of a system/project from the front to back. Pygame provided the fundamental modules to access the i/o like the display and key inputs and then it was up to me to implement the rest of game, for example; positions and behaviours of the graphics and simple physics. By being able to implement the entire project, from attempting to design 'decent' maps for the levels to implementing the game code and managing all the assets' behaviours frame by frame, it was incredibly rewarding. Since I am result oriented, being able to view my progress by running the current version of the game was extremely satisfying.

The most difficult challenge, aside from trying to create some graphics and being a level designer, was implementing the key component of a platformer, collisions. I spent a lot of time debugging with individual entities and in different combinations by analyzing all their collision states at each frame by checking the x and y vectors and which were overlapping.<br>
For example, I had one collision problem where while going up a ramp the player encounters a tile above them, but they were able to phase through it. The reason was the calculation for the player's y position to 'stand' on the ramp caused the player to surpass the above tile's collision y value threshold. The threshold contains two components, collision True/False and side of approach.
<br>
For this case, my solution was to create an additional flag for if the player is currently on a ramp, in combination with the player's current side collision states, conduct a final collision check at the end of the update cycle to correct the player's position in relation to the ramp and other involved tile.

With this accrued experience, when I do develop with a modern game engine and use their built in systems or even when I am just playing a game, I have some insight of what may have been involved to get a feature or mechanic to work a certain way.

On a final note, something personal, the reason I chose to make a video game is simply because I'm still attempting to 'determine' what I'd like to pursue. I have no requirement of salary, location, or title, I'd like a career that I'm proud of doing. Since I've never specialized in any field and I have no goals, I am truly lost. I read this quote recently and it's applicable;<br>
>*'If a man knows not to which port he sails, no wind is favorable'* - **Seneca.**

## <a name="game_exe"></a>Game exe
You will find all the releases zipped in the \Releases folder. Simply download the desired zipped folder, unzip it, and then execute the shortcut file named 'JackieBoy'.

## <a name="run_source_yourself"></a>Run source yourself
If you would like to run the source code locally; clone the project and then be sure to install the involved libraries. Afterwards, within your IDE, in \code run main.py (e.g. python .\code\main.py)
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
