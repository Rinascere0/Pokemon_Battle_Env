# Pokémon Battle Environment

A research- and play-oriented battle simulator for **Pokémon Generation VII** **6v6** singles (full teams of six), targeting **OU** and **UU** tier mechanics. The project is in **alpha**: core rules are largely implemented, but edge cases and parity with official cartridges or [Pokémon Showdown](https://pokemonshowdown.com/) are not guaranteed.

---

## Overview

This environment provides:

- **Human vs. built-in AI** (offline, graphical client)
- **Human vs. human** over a **custom TCP server** (online), with optional **Redis**-backed accounts and match logging
- **AI vs. AI** headless battles for automated testing or training workflows
- **Replay playback** from saved battle logs

Bug reports and notes on missing or incorrect mechanics are welcome.

---

## Features

| Area | Notes |
|------|--------|
| Ruleset | Gen VII–oriented; OU/UU-oriented move, ability, and item behavior (see changelog for incremental coverage) |
| Clients | PyQt5-based battle UI; server UI for hosting |
| Networking | Multi-game server; login and reconnect supported on the online branch |
| Data | Pokémon and move datasets derived from **Pokémon Showdown**–style sources; sample teams credited below |

---

## Requirements

- **Python** 3.8 or newer (recommended)
- **Operating system**: Windows is the primary development target; other platforms may work if dependencies install cleanly
- **Online / persistence** (when enabled): **Redis** (default server configuration expects port **6380**; adjust in `main/server.py` if needed)

---

## Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/Rinascere0/Pokemon_Battle_Env.git
cd Pokemon_Battle_Env
pip install -r requirements.txt
```

Main runtime dependencies are listed in `requirements.txt` (including **PyQt5**, **redis**, and **werkzeug** for the online server).

---

## Usage

### Entry point: `run.py`

From the repository root, run:

```bash
python run.py
```

You will be prompted to select a mode:

| Key | Mode | Description |
|-----|------|-------------|
| `0` | **AI vs. AI** | Non-interactive automatic battle (no GUI for play; suitable for smoke tests) |
| `1` | **PVE** | Human vs. built-in AI (GUI) |
| `2` | **PVP online** | Connect to a running server (GUI client) |
| `3` | **Replay** | Playback-only mode using saved logs |

### Online play

1. Start the server (host machine):

   ```bash
   python main/server.py
   ```

2. Ensure **Redis** is running if you rely on account storage and logging features configured in the server.

3. Each player runs `python run.py`, chooses **PVP online** (`2`), and connects using the host address and credentials as required by your deployment.

The server supports multiple concurrent games; see `main/server.py` for host/port and Redis settings.

### Local two-player (advanced)

Local **human vs. human** on one machine is implemented via `Game(mode='2p')` and `run_client_2p()` in `main/client.py`. This path is not exposed in the default `run.py` menu; developers may call `run_client_2p()` from a small launcher script or extend `run.py` to expose it.

### Swapping AI or player implementations (offline)

Default offline participants are wired in `main/game.py` (e.g. `AlphaPlayer`, `BetaPlayer`, `RandomPlayer`, and `myPlayer` from `main/ui_player.py`). Edit the constructor logic there to change which classes are used for `test` / `1p` modes, or subclass `Player` as described below.

---

## Implementing a custom agent

1. Subclass **`Player`** in `main/player.py` (or a module of your choice) and implement the abstract interface used by the battle loop.
2. Register your class in `main/game.py` (or inject it where `Game` builds its `players` list) according to your experiment or match setup.
3. Add team definitions under the **`team/`** package and reference them from your player class, or reuse the built-in teams.

---

## Repository layout (high level)

| Path | Role |
|------|------|
| `run.py` | Interactive launcher |
| `main/` | Game loop, UI client, server, players |
| `lib/` | Shared battle logic helpers |
| `data/` | Static game data (e.g. dex, moves) |
| `team/` | Team definitions |
| `docs/` | Documentation assets (e.g. screenshots) |
| `replays/` | Typical location for replay files (if used) |

---

## Screenshots

![Battle GUI example](docs/gui_cur.jpg)

---

## Acknowledgments

- **[Pokémon Showdown](https://pokemonshowdown.com/)** — Pokémon, move, and related data used as a reference and data source.
- **BJK** — Sample battle teams.

---

## Contributing and support

Issues and pull requests are welcome. When reporting bugs, please include:

- Python version and OS  
- Mode (offline PVE, online, AI vs. AI, replay)  
- Steps to reproduce and, if possible, a minimal log or replay  

---

## Legal notice

*Pokémon* is a trademark of Nintendo, Game Freak, and The Pokémon Company. This project is an independent, non-commercial fan work and is not affiliated with or endorsed by those entities.

---

<details>
<summary>Example battle log</summary>

The game between Satoshi and BJK started!\
Satoshi's pokemons: Garchomp/Landorus-Therian/Tapu Fini/Heatran/Amoonguss/Weavile\
BJK's pokemons: Pelipper/Kingdra/Crawdaunt/Magearna/Araquanid/Swampert\

Satoshi sent out Landorus-Therian!\
BJK sent out Crawdaunt!\
[Satoshi 's Landorus-Therian 's intimidate]\
BJK 's Crawdaunt 's Atk fell!

Round 1\
BJK 's Crawdaunt used Aqua Jet!\
It's super effective!\
(Satoshi 's Landorus-Therian lost 67.5% of it's health!)\
Satoshi 's Landorus-Therian used U-turn!\
It's super effective!\
(BJK 's Crawdaunt lost 80.5% of it's health!)\
Satoshi withdrew Landorus-Therian!\
Satoshi sent out Tapu Fini!\
[Satoshi 's Tapu Fini 's Misty Surge]\
Mist swirled around the battlefield!

Round 2\
BJK 's Crawdaunt used Aqua Jet!\
It's not very effective...\
(Satoshi 's Tapu Fini lost 13.9% of it's health!)\
Satoshi 's Tapu Fini used Taunt!\
BJK 's Crawdaunt was taunted!\
Satoshi 's Tapu Fini restored HP with Leftovers.\
(Satoshi 's Tapu Fini was healed 6.1% of it's health!)

Round 3\
BJK 's Crawdaunt used Aqua Jet!\
It's not very effective...\
(Satoshi 's Tapu Fini lost 14.2% of it's health!)\
Satoshi 's Tapu Fini used Taunt!\
BJK 's Crawdaunt is already taunted!\
Satoshi 's Tapu Fini restored HP with Leftovers.\
(Satoshi 's Tapu Fini was healed 6.1% of it's health!)

Round 4\
BJK 's Crawdaunt used Aqua Jet!\
It's not very effective...\
(Satoshi 's Tapu Fini lost 13.9% of it's health!)\
Satoshi 's Tapu Fini used Taunt!\
BJK 's Crawdaunt is already taunted!\
BJK 's Crawdaunt 's taunt ended!\
Satoshi 's Tapu Fini restored HP with Leftovers.\
(Satoshi 's Tapu Fini was healed 6.1% of it's health!)

Round 5\
BJK 's Crawdaunt used Aqua Jet!\
It's not very effective...\
(Satoshi 's Tapu Fini lost 13.9% of it's health!)\
Satoshi 's Tapu Fini used Taunt!\
BJK 's Crawdaunt was taunted!\
Satoshi 's Tapu Fini restored HP with Leftovers.\
(Satoshi 's Tapu Fini was healed 6.1% of it's health!)\
The mist disappeared from the battlefield.

Round 6\
BJK withdrew Crawdaunt!\
BJK sent out Kingdra!\
Satoshi 's Tapu Fini used Hydro Pump!\
BJK 's Kingdra avoided the attack!\
Satoshi 's Tapu Fini restored HP with Leftovers.\
(Satoshi 's Tapu Fini was healed 6.1% of it's health!)

Round 7\
BJK withdrew Kingdra!\
BJK sent out Araquanid!\
Satoshi 's Tapu Fini used Taunt!\
BJK 's Araquanid was taunted!\
Satoshi 's Tapu Fini restored HP with Leftovers.\
(Satoshi 's Tapu Fini was healed 6.1% of it's health!)

Round 8\
BJK withdrew Araquanid!\
BJK sent out Magearna!\
Satoshi 's Tapu Fini used Hydro Pump!\
(BJK 's Magearna lost 28.8% of it's health!)\
Satoshi 's Tapu Fini restored HP with Leftovers.\
(Satoshi 's Tapu Fini was healed 6.1% of it's health!)

Round 9\
Satoshi 's Tapu Fini used Hydro Pump!\
BJK 's Magearna avoided the attack!\
BJK 's Magearna used Ice Beam!\
It's not very effective...\
(Satoshi 's Tapu Fini lost 8.4% of it's health!)\
Satoshi 's Tapu Fini restored HP with Leftovers.\
(Satoshi 's Tapu Fini was healed 6.1% of it's health!)

Round 10\
Satoshi 's Tapu Fini used Nature's Madness!\
(BJK 's Magearna lost 35.4% of it's health!)\
BJK 's Magearna used Trick Room!\
It twisted the dimensions!\
Satoshi 's Tapu Fini restored HP with Leftovers.\
(Satoshi 's Tapu Fini was healed 6.1% of it's health!)

Round 11\
BJK 's Magearna used Fleur Cannon!\
Satoshi 's Tapu Fini avoided the attack!\
Satoshi 's Tapu Fini used Defog!\
BJK 's Magearna 's Evasion fell!\
Satoshi 's Tapu Fini restored HP with Leftovers.\
(Satoshi 's Tapu Fini was healed 6.1% of it's health!)

Round 12\
BJK 's Magearna used Fleur Cannon!\
A critical hit!\
(Satoshi 's Tapu Fini lost 62.3% of it's health!)\
BJK 's Magearna 's Sp. Atk fell harshly!\
Satoshi 's Tapu Fini used Defog!\
BJK 's Magearna 's Evasion fell!\
Satoshi 's Tapu Fini restored HP with Leftovers.\
(Satoshi 's Tapu Fini was healed 6.1% of it's health!)

Round 13\
BJK 's Magearna used Ice Beam!\
It's not very effective...\
(Satoshi 's Tapu Fini lost 4.2% of it's health!)\
Satoshi 's Tapu Fini used Hydro Pump!\
(BJK 's Magearna lost 31.2% of it's health!)\
(BJK 's Magearna used Iapapa Berry!)\
(BJK 's Magearna was healed 33.3% of it's health!)\
Satoshi 's Tapu Fini restored HP with Leftovers.\
(Satoshi 's Tapu Fini was healed 6.1% of it's health!)

Round 14\
Satoshi 's Tapu Fini used Defog!\
BJK 's Magearna 's Evasion fell!\
BJK 's Magearna used Trick Room!\
The twisted dimensions returned to normal!\
Satoshi 's Tapu Fini restored HP with Leftovers.\
(Satoshi 's Tapu Fini was healed 6.1% of it's health!)

Round 15\
Satoshi 's Tapu Fini used Nature's Madness!\
(BJK 's Magearna lost 18.9% of it's health!)\
BJK 's Magearna used Ice Beam!\
It's not very effective...\
(Satoshi 's Tapu Fini lost 4.2% of it's health!)\
Satoshi 's Tapu Fini restored HP with Leftovers.\
(Satoshi 's Tapu Fini was healed 6.1% of it's health!)

Round 16\
Satoshi 's Tapu Fini used Nature's Madness!\
(BJK 's Magearna lost 9.3% of it's health!)\
BJK 's Magearna used Volt Switch!\
It's super effective!\
A critical hit!\
(Satoshi 's Tapu Fini lost 21.3% of it's health!)\
BJK withdrew Magearna!\
BJK sent out Pelipper!\
[BJK 's Pelipper 's Drizzle]\
It started to rain!\
Satoshi 's Tapu Fini restored HP with Leftovers.\
(Satoshi 's Tapu Fini was healed 6.1% of it's health!)\
Rain continues to fall.

Round 17\
Satoshi 's Tapu Fini used Defog!\
BJK 's Pelipper 's Evasion fell!\
BJK 's Pelipper used Scald!\
It's not very effective...\
(Satoshi 's Tapu Fini lost 13.9% of it's health!)\
Satoshi 's Tapu Fini restored HP with Leftovers.\
(Satoshi 's Tapu Fini was healed 6.1% of it's health!)\
Rain continues to fall.

Round 18\
Satoshi 's Tapu Fini used Taunt!\
BJK 's Pelipper was taunted!\
BJK 's Pelipper used U-turn!\
It's not very effective...\
(Satoshi 's Tapu Fini lost 3.5% of it's health!)\
BJK withdrew Pelipper!\
BJK sent out Magearna!\
Satoshi 's Tapu Fini restored HP with Leftovers.\
(Satoshi 's Tapu Fini was healed 6.1% of it's health!)\
Rain continues to fall.

Round 19\
Satoshi withdrew Tapu Fini!\
Satoshi sent out Weavile!\
[Satoshi 's Weavile 's Pressure]\
Satoshi 's Weavile is exerting pressure!\
BJK withdrew Magearna!\
BJK sent out Pelipper!\
[BJK 's Pelipper 's Drizzle]\
Rain continues to fall.

Round 20\
Satoshi 's Weavile used Knock Off!\
(BJK 's Pelipper lost 50.3% of it's health!)\
BJK 's Pelipper used Defog!\
Satoshi 's Weavile 's Evasion fell!\
Rain continues to fall.

Round 21\
Satoshi 's Weavile used Icicle Crash!\
(BJK 's Pelipper lost 42.8% of it's health!)\
BJK 's Pelipper used Defog!\
Satoshi 's Weavile 's Evasion fell!\
Rain continues to fall.

Round 22\
Satoshi 's Weavile was surrounded by Z-Power!\
Satoshi 's Weavile used Subzero Slammer!\
(BJK 's Pelipper lost 6.8% of it's health!)\
BJK 's Pelipper fainted!\
Rain continues to fall.\
BJK sent out Kingdra!

Round 23\
BJK 's Kingdra used Hydro Pump!\
(Satoshi 's Weavile lost 100.0% of it's health!)\
Satoshi 's Weavile fainted!\
The rain stopped.\
Satoshi sent out Heatran!

Round 24\
BJK withdrew Kingdra!\
BJK sent out Araquanid!\
Satoshi 's Heatran used Earth Power!\
It's not very effective...\
(BJK 's Araquanid lost 10.1% of it's health!)

Round 25\
Satoshi 's Heatran used Earth Power!\
It's not very effective...\
(BJK 's Araquanid lost 10.4% of it's health!)\
BJK 's Araquanid used Liquidation!\
It's super effective!\
(Satoshi 's Heatran lost 100.0% of it's health!)\
Satoshi 's Heatran fainted!\
Satoshi sent out Amoonguss!

Round 26\
BJK 's Araquanid used Liquidation!\
It's not very effective...\
(Satoshi 's Amoonguss lost 50.0% of it's health!)\
Satoshi 's Amoonguss used Giga Drain!\
(BJK 's Araquanid lost 19.5% of it's health!)\
(Satoshi 's Amoonguss was healed 7.5% of it's health!)\
Satoshi 's Amoonguss restored HP with Black Sludge.\
(Satoshi 's Amoonguss was healed 6.0% of it's health!)

Round 27\
BJK 's Araquanid used Liquidation!\
It's not very effective...\
A critical hit!\
(Satoshi 's Amoonguss lost 63.6% of it's health!)\
Satoshi 's Amoonguss fainted!\
Satoshi sent out Tapu Fini!\
[Satoshi 's Tapu Fini 's Misty Surge]\
Mist swirled around the battlefield!

Round 28\
Satoshi withdrew Tapu Fini!\
Satoshi sent out Landorus-Therian!\
[Satoshi 's Landorus-Therian 's intimidate]\
BJK 's Araquanid 's Atk fell!\
BJK 's Araquanid used Liquidation!\
It's super effective!\
(Satoshi 's Landorus-Therian lost 32.5% of it's health!)\
Satoshi 's Landorus-Therian fainted!\
Satoshi sent out Tapu Fini!\
[Satoshi 's Tapu Fini 's Misty Surge]

Round 29\
Satoshi 's Tapu Fini used Defog!\
BJK 's Araquanid 's Evasion fell!\
BJK 's Araquanid used Liquidation!\
It's not very effective...\
(Satoshi 's Tapu Fini lost 30.6% of it's health!)\
Satoshi 's Tapu Fini fainted!\
Satoshi sent out Garchomp!

Round 30\
Satoshi 's Garchomp evolved into Garchomp-Mega!\
Satoshi 's Garchomp-Mega used Stone Edge!\
It's super effective!\
(BJK 's Araquanid lost 60.1% of it's health!)\
BJK 's Araquanid fainted!\
BJK sent out Magearna!

Round 31\
Satoshi 's Garchomp-Mega used Swords Dance!\
Satoshi 's Garchomp-Mega 's Atk rose rapidly!\
BJK 's Magearna used Trick Room!\
It twisted the dimensions!

Round 32\
Satoshi 's Garchomp-Mega used Earthquake!\
It's super effective!\
(BJK 's Magearna lost 9.6% of it's health!)\
BJK 's Magearna fainted!\
The mist disappeared from the battlefield.\
BJK sent out Crawdaunt!

Round 33\
BJK 's Crawdaunt used Crunch!\
(Satoshi 's Garchomp-Mega lost 86.2% of it's health!)\
Satoshi 's Garchomp-Mega used Stone Edge!\
(BJK 's Crawdaunt lost 19.5% of it's health!)\
BJK 's Crawdaunt fainted!\
BJK sent out Swampert!

Round 34\
BJK withdrew Swampert!\
BJK sent out Kingdra!\
Satoshi 's Garchomp-Mega used Stealth Rock!\
Pointed stone floated on BJK 's field.

Round 35\
BJK 's Kingdra used Hydro Pump!\
(Satoshi 's Garchomp-Mega lost 13.8% of it's health!)\
Satoshi 's Garchomp-Mega fainted!\
Satoshi lost!

</details>

<details>
<summary>Update log (historical)</summary>

2023.6.3
【Add】\
Guardian of Alola
Dark Aura
Fairy Aura
Stance Change

【Todo】\
Primordial Sea
Desolate Land
Delta Stream

2022.9.26
【Todo】\
end game upon vs/ut kill foe 

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

2022.5.1

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

2022.5.2

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

2022.5.3

【Todo】\
✔Own Tempo\
✔Vital Spirit\
✔Healing Wish\
✔Synthesis\
✔Water Bubble\
✔Skill Link

2022.5.4

【Add】\
Mega

【Todo】\
✔Roost\
✔Z-move\
✔Ability log in utils\
✔Berry\
✔struggle\
✔Ditto

2022.5.5

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
✔Gravity [immue judge]\
✔sleep talk

2022.5.6

【Add】\
all gen7 ou abilities\
water shuriken ash\
mega seq

【Todo】\
破格时机

2022.5.7

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

2022.5.8

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
✔mind blown\
✔damp

2022.5.9

【Add】\
Arranged code

【Todo】\
✔Natural Gift\
Soak etc.

2022.5.11

【Todo】\
embargo log

【ToFix】\
subsitute judge->whether damaged dealt to true body

2022.5.13

【Todo】\
✔Cloud Nine

2022.7.23

【Add】\
heartswap
powerswap
guardswap
speedswap

【ToFix】\
landorus switch on bug(maybe alakazam trace bug?fixed)

2025.6.2

【Add】\
(new branch server)Split out client code which only interactive with game object\
Fix alakazam trace bug

2025.6.5

【Add】\
(new branch online)Built server and client for online gaming, compatible with current modes

【ToFix】\
✔foe pivot still display when fainted

2025.6.5

【Add】\
server support multi-games

【ToFix】\
✔client disconnect(socket peer port changes every connection)\
✔black HP bar before game start

2025.6.11

【Add】\
enable login and reconnect
enable redis store userinfo and log

【ToFix】\
1. Solar Beam 2nd round can use z-move\
2. thunder punch and paralyse elec-mons\
3. login after game finished still in last game\
4. magic guard no status(e.g burn) hp loss but hurt log
</details>
