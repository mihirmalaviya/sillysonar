import os
import inspect
from groq import Groq
import os
import sys
import math
import random
import datetime
import time
import re
import json
import collections
import itertools
import functools
import pathlib
import subprocess
import threading
import multiprocessing
import queue
import logging
import argparse
import shutil
import glob
import csv
import pickle
import typing
import uuid
import hashlib
import statistics
import socket
import urllib
import http
import enum

true, false, null = True, False, None

# this is the future of python
# vibethon (tm)

# this is basically what we want python to be like in the future. you just write code with holes in it, and the llm fills in the holes for you. and if it messes up, you just run it again and it tries again until it gets it right. no more debugging syntax errors or anything, you just keep running it until it works. and you can also have different levels of "goodness" for the code, so if you want it to be really good you can use the @verygood decorator, and if you're okay with it being a little worse you can just leave that off. it's really up to you how much you want to rely on the llm to fill in the blanks for you.

_client = Groq(api_key=os.environ["GROQ_API_KEY"])


def retry(func):
    def wrapper(*args, **kwargs):
        while True:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print("retrying")
                # pass
                # print(f"[retry] {func.__name__} crashed: {type(e).__name__}: {e} — retrying")
    return wrapper


@retry
def call_llm(prompt: str) -> str:
    response = _client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


def verygood(func):
    def wrapper(*args, **kwargs):
        code = inspect.getsource(func)
        lines = [l for l in code.split("\n") if not l.strip().startswith("@")]
        defn = next(l for l in lines if l.strip().startswith("def "))
        code = "\n".join(lines)

        existing = [n for n, v in func.__globals__.items() if callable(v) and not n.startswith("_") and n != func.__name__]
        prompt = (
            f"Implement this Python function. Return ONLY the function definition, nothing else. "
            f"Do NOT redefine or stub any other functions. Do NOT call the function. "
            f"These functions already exist in globals and you may call them: {existing}. "
            f"Signature: {defn.strip()}\n\n{code}"
        )
        better_code = call_llm(prompt).replace("```python", "").replace("```", "").strip()
        # print(better_code)
        ns = dict(func.__globals__)
        exec(better_code, ns)
        return ns[func.__name__](*args, **kwargs)
    return wrapper


@retry
def demo():
    @verygood
    def add(a, b):
        # basically i want this to add the numbers
        return # lmao

    print(f"The sum of 1 and 2 is: {add(1, 2)}")

    @verygood
    def fizzbuzz(n):
        # do fizzbuzz
        # just print it
        # add some cool emojis aswell
        return # nothing

    fizzbuzz(int(input("Enter a number for fizzbuzz: ")))

    @verygood
    def rando():
        import random
        # return a random number. IT BETTER WORK.
        return # it
        
    @verygood
    def sort_arr(arr):
        # sort it
        return # it
    
    arr = [rando() for _ in range(5)]
    print(f"Sorted {arr} -> {sort_arr(arr)}")


@retry
@verygood
def game():
    # code this it has to work and just use like number inputs simple there will be alot of functions but its ok ur very smart and i am very proud of you
    # you NEED to take user input in each step also validate it (re-prompt on bad input, never crash)
    # import everything you need
    # use clear print statements with separators between sections so the player can follow along
    #
    # ============ STARTER SELECTION ============
    # Three starters available, each with type, base stats (hp, atk, def, spd), and two moves:
    #   1) Pikachu  — Electric. hp 35, atk 55, def 40, spd 90.
    #        moves: Thunder Shock (electric, power 40, acc 100, may paralyze 10%)
    #               Quick Attack  (normal,   power 40, acc 100, always goes first)
    #   2) Charmander — Fire. hp 39, atk 52, def 43, spd 65.
    #        moves: Ember     (fire,   power 40, acc 100, may burn 10%)
    #               Scratch   (normal, power 40, acc 100)
    #   3) Bulbasaur  — Grass. hp 45, atk 49, def 49, spd 45.
    #        moves: Vine Whip (grass,  power 45, acc 100)
    #               Tackle    (normal, power 35, acc 100)
    # Player picks starter by number (1-3). Show them their pick's stats and moves.
    #
    # ============ PLAYER STATE ============
    # Player tracks: their pokemon (with current hp, level, xp, stats), and an inventory of items.
    # Starting level = 5. Starting xp = 0.
    # Starting inventory: 3x Potion (heals 20 hp), 1x Super Potion (heals 50 hp), 2x Revive (restores fainted to 50% hp).
    # Items only usable BETWEEN battles, not during. Show inventory before each battle.
    #
    # ============ LEVELING ============
    # XP needed to level up = level * 10 (so 50 to go from 5→6, 60 to go from 6→7, etc.)
    # On level up: hp +5, atk +2, def +2, spd +2. Restore to full hp on level up. Print level-up message.
    # XP gained from winning a battle = defeated_pokemon_level * 15. Apply xp AFTER battle, may level up multiple times.
    #
    # ============ BATTLE RULES ============
    # Turn order: whoever has higher spd goes first. Ties = player first. Quick Attack ALWAYS goes first regardless.
    # Each turn the active side picks a move (player chooses by number, opponent picks randomly between its 2 moves).
    # Accuracy check: roll 1-100, miss if > acc. On miss print "It missed!" and turn ends.
    # Damage formula: floor(((2*level/5 + 2) * power * atk / def) / 50) + 2, then multiply by type effectiveness, then multiply by random 0.85-1.0.
    # Type effectiveness chart (attacker → defender, multiplier):
    #   electric vs water/flying = 2.0, electric vs grass/electric = 0.5, electric vs ground = 0.0
    #   fire vs grass/ice/bug   = 2.0, fire vs water/fire/rock     = 0.5
    #   grass vs water/ground/rock = 2.0, grass vs fire/grass/flying = 0.5
    #   normal vs rock = 0.5, normal vs ghost = 0.0, otherwise 1.0
    # Print effectiveness message ("It's super effective!" / "It's not very effective..." / "It had no effect...").
    # Status effects:
    #   Paralyze: 25% chance each turn the affected pokemon can't move ("X is paralyzed and can't move!"). spd halved while paralyzed.
    #   Burn:     loses 1/16 max hp at end of each turn, atk halved while burned.
    # A pokemon can only have ONE status at a time; ignore new status if already statused.
    # When a pokemon's hp hits 0 it faints. Battle ends when one side faints.
    # If the player's pokemon faints AND they have no Revives left → game over, print loss and return.
    #
    # ============ BETWEEN BATTLES ============
    # Before each trainer fight, fully restore the player's pokemon to max hp and clear any status.
    # Print the heal message and show current pokemon hp/level/xp and the next opponent's name.
    # No menu, no items — just auto-heal and continue.
    #
    # ============ THE THREE TRAINERS (fight in order) ============
    #   Trainer 1: "Youngster Joey"
    #     - Rattata (Normal). level 5. hp 30, atk 56, def 35, spd 72.
    #       moves: Tackle (normal, power 35, acc 100), Quick Attack (normal, power 40, acc 100, first)
    #   Trainer 2: "Bug Catcher Rick"
    #     - Caterpie (Bug). level 6. hp 45, atk 30, def 35, spd 45.
    #       moves: Tackle (normal, power 35, acc 100), String Shot (bug, power 0, acc 95) — String Shot does no damage but halves player's spd for the rest of the battle.
    #     - Weedle (Bug). level 7. hp 40, atk 35, def 30, spd 50.
    #       moves: Poison Sting (bug, power 15, acc 100), Tackle (normal, power 35, acc 100)
    #   Trainer 3: "Lass Janice" (FINAL)
    #     - Oddish (Grass). level 8. hp 45, atk 50, def 55, spd 30.
    #       moves: Absorb (grass, power 20, acc 100, heals attacker for 50% of damage dealt), Tackle (normal, power 35, acc 100)
    #     - Vulpix (Fire). level 9. hp 38, atk 41, def 40, spd 65.
    #       moves: Ember (fire, power 40, acc 100, may burn 10%), Quick Attack (normal, power 40, acc 100, first)
    # Trainer with multiple pokemon: when one faints, immediately send out the next. Player's pokemon does NOT auto-heal between trainer's pokemon (but status clears).
    # Status clears between battles (between trainers).
    #
    # ============ WIN CONDITION ============
    # Beat all 3 trainers in order → print big victory message with final pokemon level and stats. Return.
    # Lose at any point → print game over message and a mean insult. Return.
    return # nothing but just print the result of the adventure

@retry
@verygood
def pick_which(input):
    # based on the input either run the demo() or game() function only
    # you dont need to write them, they already exist out of ur context as globals
    return # nothing


if __name__ == "__main__":
    pick_which(input("do u want the demo or the game?: "))

if __name__ != "__main__":
    @retry
    @verygood
    def cake():
        # ok so i want a cake recipe. not just any cake recipe, but a really good one that includes flour, sugar, and eggs. those are the basics, but i want it to be something special, something that will really impress my friends when they taste it. i want it to be moist and fluffy and just overall delicious. also it has to have a unique twist that sets it apart from regular cake recipes. maybe it's a chocolate cake with a spicy kick, or a vanilla cake with a surprising ingredient that adds an extra layer of flavor. whatever it is, i want it to be creative and sound amazing. and of course, the recipe needs to be easy to follow with clear instructions and measurements for each ingredient. i also need the baking time and temperature so i can get this cake in the oven as soon as possible. please make sure to meet all of these requirements and give me a fantastic cake recipe that will blow my friends' minds! thank you so much in advance, i can't wait to see what you come up with!
        # give a cake recipe that includes at least flour, sugar, and eggs and is actually good
        # not only that but also make it a fun recipe that has a unique twist to it, like maybe its a chocolate cake but also has some spicy element to it or something, just be creative and make it sound delicious
        # the recipe should be easy to follow with clear instructions and measurements for each ingredient. also make sure to include the baking time and temperature. i want to bake this cake asap
        # also make sure the recipe is actually good, like it should taste amazing and be moist and fluffy and just overall a great cake. i want to impress my friends with this recipe so it better be good
        # here are the requirements again to make sure you dont forget:
        # - includes flour, sugar, and eggs
        # - is actually good and tastes amazing
        # - has a unique twist that makes it stand out from regular cake recipes
        # - easy to follow with clear instructions and measurements
        # - includes baking time and temperature
        # please make sure to meet all of these requirements and give me a cake recipe that i will love and that will impress my friends. i am counting on you to deliver a fantastic recipe that meets all of these criteria. thank you in advance for your help, i am so excited to see what kind of delicious and unique cake recipe you come up with!
        # here is the recipe:
        return # the recipe