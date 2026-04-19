# I wasnt able to get your thing to work so i got claude to micimc it

"""A small arithmetic demo and a Pokemon-style turn-based battle game.

Run the module and pick `demo` for the scripted demo or `game` for the
three-trainer battle adventure.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass


# ---------- Demo ----------

def _fizzbuzz(n: int) -> None:
    for i in range(1, n + 1):
        if i % 15 == 0:
            print("FizzBuzz 🔥")
        elif i % 3 == 0:
            print("Fizz ✨")
        elif i % 5 == 0:
            print("Buzz 🎉")
        else:
            print(i)


def demo() -> None:
    print(f"The sum of 1 and 2 is: {1 + 2}")

    while True:
        raw = input("Enter a number for fizzbuzz: ").strip()
        if raw.isdigit():
            _fizzbuzz(int(raw))
            break
        print("Please enter a non-negative integer.")

    arr = [random.randint(1, 100) for _ in range(5)]
    print(f"Sorted {arr} -> {sorted(arr)}")


# ---------- Game data model ----------

@dataclass
class Move:
    name: str
    type: str
    power: int
    accuracy: int
    priority: int = 0
    paralyze_chance: float = 0.0
    burn_chance: float = 0.0
    halve_opponent_spd: bool = False
    drain_fraction: float = 0.0


@dataclass
class Pokemon:
    name: str
    type: str
    level: int
    max_hp: int
    hp: int
    atk: int
    defense: int
    spd: int
    moves: list[Move]
    xp: int = 0
    status: str | None = None  # "paralyze" or "burn"
    spd_multiplier: float = 1.0

    @property
    def fainted(self) -> bool:
        return self.hp <= 0

    def effective_atk(self) -> int:
        return self.atk // 2 if self.status == "burn" else self.atk

    def effective_spd(self) -> int:
        value = self.spd * self.spd_multiplier
        if self.status == "paralyze":
            value /= 2
        return int(value)


THUNDER_SHOCK = Move("Thunder Shock", "electric", 40, 100, paralyze_chance=0.10)
QUICK_ATTACK = Move("Quick Attack", "normal", 40, 100, priority=1)
EMBER = Move("Ember", "fire", 40, 100, burn_chance=0.10)
SCRATCH = Move("Scratch", "normal", 40, 100)
VINE_WHIP = Move("Vine Whip", "grass", 45, 100)
TACKLE = Move("Tackle", "normal", 35, 100)
STRING_SHOT = Move("String Shot", "bug", 0, 95, halve_opponent_spd=True)
POISON_STING = Move("Poison Sting", "bug", 15, 100)
ABSORB = Move("Absorb", "grass", 20, 100, drain_fraction=0.5)


def _make_starter(choice: int) -> Pokemon:
    if choice == 1:
        return Pokemon("Pikachu", "electric", 5, 35, 35, 55, 40, 90, [THUNDER_SHOCK, QUICK_ATTACK])
    if choice == 2:
        return Pokemon("Charmander", "fire", 5, 39, 39, 52, 43, 65, [EMBER, SCRATCH])
    return Pokemon("Bulbasaur", "grass", 5, 45, 45, 49, 49, 45, [VINE_WHIP, TACKLE])


_TYPE_CHART: dict[tuple[str, str], float] = {
    ("electric", "water"): 2.0, ("electric", "flying"): 2.0,
    ("electric", "grass"): 0.5, ("electric", "electric"): 0.5,
    ("electric", "ground"): 0.0,
    ("fire", "grass"): 2.0, ("fire", "ice"): 2.0, ("fire", "bug"): 2.0,
    ("fire", "water"): 0.5, ("fire", "fire"): 0.5, ("fire", "rock"): 0.5,
    ("grass", "water"): 2.0, ("grass", "ground"): 2.0, ("grass", "rock"): 2.0,
    ("grass", "fire"): 0.5, ("grass", "grass"): 0.5, ("grass", "flying"): 0.5,
    ("normal", "rock"): 0.5, ("normal", "ghost"): 0.0,
}


def type_effectiveness(atk_type: str, def_type: str) -> float:
    return _TYPE_CHART.get((atk_type, def_type), 1.0)


# ---------- I/O helpers ----------

SEPARATOR = "-" * 50


def _prompt_int(prompt: str, lo: int, hi: int) -> int:
    while True:
        raw = input(prompt).strip()
        try:
            value = int(raw)
        except ValueError:
            print(f"Please enter a whole number between {lo} and {hi}.")
            continue
        if lo <= value <= hi:
            return value
        print(f"Out of range. Please enter a number between {lo} and {hi}.")


def _format_inventory(inv: dict[str, int]) -> str:
    parts = [f"{n}x {k}" for k, n in inv.items() if n > 0]
    return ", ".join(parts) if parts else "(empty)"


def _show_pokemon(p: Pokemon) -> None:
    print(f"{p.name} ({p.type.title()}) — Lv {p.level}  HP {p.hp}/{p.max_hp}  XP {p.xp}")
    print(f"  Stats: atk {p.atk}  def {p.defense}  spd {p.spd}")
    print("  Moves:")
    for i, m in enumerate(p.moves, start=1):
        print(f"    {i}) {m.name} ({m.type}, pwr {m.power}, acc {m.accuracy})")


# ---------- Damage resolution ----------

def _damage(attacker: Pokemon, defender: Pokemon, move: Move) -> tuple[int, float]:
    eff = type_effectiveness(move.type, defender.type)
    if move.power == 0 or eff == 0.0:
        return 0, eff
    base = math.floor(
        ((2 * attacker.level / 5 + 2) * move.power * attacker.effective_atk() / defender.defense) / 50
    ) + 2
    dmg = int(base * eff * random.uniform(0.85, 1.0))
    return max(1, dmg), eff


def _effectiveness_message(eff: float) -> str | None:
    if eff == 0.0:
        return "It had no effect..."
    if eff > 1.0:
        return "It's super effective!"
    if 0 < eff < 1.0:
        return "It's not very effective..."
    return None


def _perform_move(attacker: Pokemon, defender: Pokemon, move: Move) -> None:
    print(f"{attacker.name} used {move.name}!")
    if random.randint(1, 100) > move.accuracy:
        print("It missed!")
        return

    dmg, eff = _damage(attacker, defender, move)
    if move.power > 0:
        defender.hp = max(0, defender.hp - dmg)
        msg = _effectiveness_message(eff)
        if msg:
            print(msg)
        if dmg > 0:
            print(f"{defender.name} took {dmg} damage. (HP {defender.hp}/{defender.max_hp})")

    if move.drain_fraction > 0 and dmg > 0:
        heal = math.floor(dmg * move.drain_fraction)
        attacker.hp = min(attacker.max_hp, attacker.hp + heal)
        print(f"{attacker.name} drained {heal} HP. (HP {attacker.hp}/{attacker.max_hp})")

    if move.halve_opponent_spd:
        defender.spd_multiplier *= 0.5
        print(f"{defender.name}'s speed fell!")

    if defender.status is None:
        if move.paralyze_chance and random.random() < move.paralyze_chance:
            defender.status = "paralyze"
            print(f"{defender.name} was paralyzed!")
        elif move.burn_chance and random.random() < move.burn_chance:
            defender.status = "burn"
            print(f"{defender.name} was burned!")


def _take_turn(attacker: Pokemon, defender: Pokemon, move: Move) -> None:
    if attacker.status == "paralyze" and random.random() < 0.25:
        print(f"{attacker.name} is paralyzed and can't move!")
        return
    _perform_move(attacker, defender, move)


def _end_of_turn_burn(p: Pokemon) -> None:
    if p.status == "burn" and not p.fainted:
        tick = max(1, p.max_hp // 16)
        p.hp = max(0, p.hp - tick)
        print(f"{p.name} is hurt by its burn! ({tick} dmg, HP {p.hp}/{p.max_hp})")


# ---------- Battle loop ----------

def _player_chooses_move(player: Pokemon) -> Move:
    print("Your moves:")
    for i, m in enumerate(player.moves, start=1):
        print(f"  {i}) {m.name}")
    pick = _prompt_int(f"Choose a move (1-{len(player.moves)}): ", 1, len(player.moves))
    return player.moves[pick - 1]


def _battle(player: Pokemon, opponent: Pokemon) -> bool:
    print(SEPARATOR)
    print(f"A battle begins: {player.name} vs {opponent.name}!")
    print(SEPARATOR)

    while not player.fainted and not opponent.fainted:
        print(f"\n[{player.name} {player.hp}/{player.max_hp}]  vs  [{opponent.name} {opponent.hp}/{opponent.max_hp}]")
        player_move = _player_chooses_move(player)
        opponent_move = random.choice(opponent.moves)

        order = sorted(
            [
                (player, opponent, player_move, 1),
                (opponent, player, opponent_move, 0),
            ],
            key=lambda t: (t[2].priority, t[0].effective_spd(), t[3]),
            reverse=True,
        )

        for attacker, defender, move, _ in order:
            if attacker.fainted or defender.fainted:
                continue
            _take_turn(attacker, defender, move)

        _end_of_turn_burn(player)
        _end_of_turn_burn(opponent)

    if opponent.fainted:
        print(f"\n{opponent.name} fainted!")
        return True
    print(f"\n{player.name} fainted!")
    return False


# ---------- Progression ----------

def _grant_xp(player: Pokemon, defeated_level: int) -> None:
    gained = defeated_level * 15
    player.xp += gained
    print(f"{player.name} gained {gained} XP.")
    while player.xp >= player.level * 10:
        player.xp -= player.level * 10
        player.level += 1
        player.max_hp += 5
        player.atk += 2
        player.defense += 2
        player.spd += 2
        player.hp = player.max_hp
        print(f"{player.name} grew to level {player.level}! (HP restored)")


# ---------- Trainer roster ----------

def _trainers() -> list[tuple[str, list[Pokemon]]]:
    return [
        ("Youngster Joey", [
            Pokemon("Rattata", "normal", 5, 30, 30, 56, 35, 72, [TACKLE, QUICK_ATTACK]),
        ]),
        ("Bug Catcher Rick", [
            Pokemon("Caterpie", "bug", 6, 45, 45, 30, 35, 45, [TACKLE, STRING_SHOT]),
            Pokemon("Weedle", "bug", 7, 40, 40, 35, 30, 50, [POISON_STING, TACKLE]),
        ]),
        ("Lass Janice", [
            Pokemon("Oddish", "grass", 8, 45, 45, 50, 55, 30, [ABSORB, TACKLE]),
            Pokemon("Vulpix", "fire", 9, 38, 38, 41, 40, 65, [EMBER, QUICK_ATTACK]),
        ]),
    ]


_INSULTS = [
    "That was pathetic. A Magikarp could've done better.",
    "Bro got swept. Are you even trying?",
    "Skill issue, honestly.",
]


def _heal_fully(p: Pokemon) -> None:
    p.hp = p.max_hp
    p.status = None
    p.spd_multiplier = 1.0


def game() -> None:
    print(SEPARATOR)
    print("Welcome to the Pokemon adventure!")
    print(SEPARATOR)
    print("Choose your starter:")
    print("  1) Pikachu (Electric) — hp 35, atk 55, def 40, spd 90")
    print("  2) Charmander (Fire)  — hp 39, atk 52, def 43, spd 65")
    print("  3) Bulbasaur (Grass)  — hp 45, atk 49, def 49, spd 45")
    player = _make_starter(_prompt_int("Pick 1-3: ", 1, 3))
    inventory = {"Potion": 3, "Super Potion": 1, "Revive": 2}

    print(SEPARATOR)
    print("You chose:")
    _show_pokemon(player)

    for name, team in _trainers():
        _heal_fully(player)
        print(SEPARATOR)
        print(f"{player.name} was fully healed!")
        _show_pokemon(player)
        print(f"Inventory: {_format_inventory(inventory)}")
        print(f"Next opponent: {name}")
        print(SEPARATOR)

        for i, foe in enumerate(team):
            if i > 0:
                player.status = None
                player.spd_multiplier = 1.0
            while True:
                if _battle(player, foe):
                    break
                if inventory["Revive"] <= 0:
                    print("\nYou lost. Game over.")
                    print(random.choice(_INSULTS))
                    return
                inventory["Revive"] -= 1
                player.hp = max(1, player.max_hp // 2)
                player.status = None
                print(
                    f"Used a Revive! {player.name} is back with {player.hp} HP. "
                    f"(Revives left: {inventory['Revive']})"
                )
            _grant_xp(player, foe.level)

    print(SEPARATOR)
    print("🏆 VICTORY! You defeated all three trainers! 🏆")
    print(SEPARATOR)
    _show_pokemon(player)


# ---------- Entry point ----------

def pick_which(user_input: str) -> None:
    choice = user_input.strip().lower()
    if "demo" in choice:
        demo()
    elif "game" in choice:
        game()
    else:
        print("I didn't understand that. Please run again and type 'demo' or 'game'.")


if __name__ == "__main__":
    pick_which(input("do u want the demo or the game?: "))
