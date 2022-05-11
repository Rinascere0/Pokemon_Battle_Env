# Pokemon_Battle_Env

## About it

It's an alpha version of Pokemon 6v6 battle env, implementing most mechanism of OU and UU tier.\
Any reports of bugs and unimplemented mechanisms are always welcome!\

Thanks to database provided by Pokemon Showdown.\
Thanks to teams provide by BJK.
## How to use?

Run `game.py`, and built-in AI will automatically perform a 6v6 battle!

## How to create my own AI?

1. Create your own player class by inheriting Player class in `player.py`,
2. Implement abstract methods in your class according to your strategy,
3. Import your own team into 'team' directory, and edit according parameters in your class (Of course you ccan just use
   built-in teams!).


<details>
<summary>Update Log</summary>

2022.4.30

【Add】\
Base physical/special moves\
Spikes (add and effect)

【Todo】\
✔defog \
✔rapid spin\
✔leech seed\
✔knock off\ ✔status moves fail after taunt\
✔contrary\
✔counter\
✔mirror coat\
✔U-turn\
✔volt switch

2020.5.1

【Add】\
weather, ability & stop\
terrain, ability & stop\    
terrain seeds\
pressure\
pp\
protect\
hidden power\
unburden\
use item\
acrobatics\
rocky helmet & rough skin\
beast boost\
soul heart\
air balloon \
focus sash

【Todo】\
✔download \
✔anticipation\
✔unnerve\
✔intimidate\
✔frisk\
✔trace\
✔silvally\
✔arceus\
✔match-up switch-\
is to ==

2020.5.2

【Add】\
Justified\
Steadfast\
Fake Out\
First Impression

【Todo】\
✔Trick\
✔Sucker Punch\
✔Pain Split\
✔Choice Items

【ToFix】\
✔Faint over and over!

2020.5.3

【Todo】\
✔Own Tempo\
✔Vital Spirit\
✔Healing Wish\
✔Synthesis\
✔Water Bubble\
✔Skill Link

2020.5.4

【Add】\
Mega

【Todo】\
✔Roost\
✔Z-move\
✔Ability log in utils\
✔Berry\
✔struggle\
Ditto

2020.5.5

【Add】\
heal bell\
vstatus\
black sludge\
magic guard\
confusion hit self\
Infiltrator\
light screen reflect\
confusion hit\
brick break wall\
nightmare

【Todo】\
Gravity [immue judge]\
sleep talk

2020.5.6

【Add】\
all gen7 ou abilities\
water shuriken ash\
mega seq

【Todo】\
破格时机

2020.5.7

【Add】\
Prankster\
natural cure

【Todo】\
✔wish\
✔roar\
✔change move type before effecting\
✔z move not effected by skin

【ToFix】\
Wrong struggle

2020.5.8

【Add】\
Arceus Z Inner Focus\
moxie\
magician, pickpocket\
heatproof\
gooey\
insomnia\
weak armor\
rock head\
heavy/light metal\
Poison Touch\
Shield dust\
oblivious\
Illusion\
Emergency Exit

【ToFix】\
✔Partiallytrapped\
mind blown\
damp

2020.5.9

【Add】\
Arranged code

【Todo】\
Natural Gift\
Soak etc.

</details>