# Imports
from datetime import datetime
import json
import os
import random
from tabulate import tabulate

# User choices
while True:
    choice = input ("What would you like to generate?\n[1] Traps\n[2] Treasures\n[q] quit\nOption: ")
    if choice == "1":
        feed_type = 'traps'
        break
    elif choice == "2":
        feed_type = 'treasures'
        break
    elif choice == "q":
        break

generation_amount = int(input("How many? -> "))

# Read chose feed
with open('data/{}.json'.format(feed_type), 'r') as myfile:
    data = myfile.read()

feed = json.loads(data)

# Single entry generation
def generate_entry():
    headers = []
    entry = []

    def get_die_type(rolls):
        last_roll = list(rolls.keys())[-1].split('-')
        highest_roll = last_roll[1] if len(last_roll) > 1 else last_roll[0]

        return int(highest_roll) if highest_roll.isnumeric() else 6

    def roll_die(faces):
        return random.randint(1, faces)

    def save_attribute(attribute):
        entry.append(attribute)

    def get_attribute(header, attribute, die):
        is_rollable = '-' in header or header.isnumeric()

        if not is_rollable:
            if header != 'Value':
                headers.append(header)
                die = get_die_type(attribute)
                roll_result = roll_die(die)

                for key, value in attribute.items():
                    get_attribute(key, value, roll_result)
            else:
                save_attribute(attribute)
        else:
            rollable_range = is_rollable and header.split('-')
            matches_roll_value = rollable_range and (die == int(rollable_range[0]) or (len(rollable_range) > 1 and int(rollable_range[0]) <= die <= int(rollable_range[1])))

            if matches_roll_value:
                if type(attribute) is dict:
                    die = get_die_type(attribute)
                    roll_result = roll_die(die)

                    for key, value in attribute.items():
                        get_attribute(key, value, roll_result)
                else:
                    save_attribute(attribute)

    for header, attribute in feed.items():
        roll_result = roll_die(6)
        get_attribute(header, attribute, roll_result)

    return tabulate([entry], headers=headers)

# Final list generation
def generate():
    f = open('results/{}_{}.txt'.format(feed_type, datetime.now().strftime("%Y-%m-%d_%H:%M:%S")), 'a')
    i = 0

    while i < generation_amount:
        f.write(generate_entry() + '\n\n')
        i += 1

    f.close()

# Write to disk
if not os.path.exists('results'):
    os.makedirs('results')

generate()