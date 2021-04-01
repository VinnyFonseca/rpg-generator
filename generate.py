# Required installation
# pip install prettytable

# Imports
from datetime import datetime
import json
import os
import random
import sys
from prettytable import PrettyTable


# Global vars
is_debug = len(sys.argv) > 1 and sys.argv[1] == 'debug'


# User choices
while True:
    choice = input('''What would you like to generate?

[1] Traps
[2] Treasures
[q] quit

Choose -> ''')

    if choice == '1':
        FEED_TYPE = 'traps'
        break
    if choice == '2':
        FEED_TYPE = 'treasures'
        break
    if choice == 'q':
        sys.exit()

generation_amount = int(input('How many? -> '))


# Read chosen feed
with open('./data/{}.json'.format(FEED_TYPE), 'r') as feed:
    FEED_FILE = json.loads(feed.read())


# Random die roll based on autodetected number of faces
def roll_die(trait):
    last_roll = list(trait.keys())[-1].split('-')
    highest_roll = last_roll[1] if len(last_roll) > 1 else last_roll[0]
    die = int(highest_roll) if highest_roll.isnumeric() else 6

    return random.randint(1, die)


# Detect if rolled die is inside rollable range
def die_match(die, rollable_range):
    return rollable_range and (
        die is int(rollable_range[0]) or (
            len(rollable_range) > 1
            and int(rollable_range[0]) <= die <= int(rollable_range[1])
        )
    )


# Main function
def build():
    headers = []
    cells = []

    # Recursive function
    def get_trait(header, trait, die):
        is_rollable = '-' in header or header.isnumeric()

        if not is_rollable:
            if header != 'Value':
                headers.append(header)
                roll_result = roll_die(trait)

                for key, value in trait.items():
                    get_trait(key, value, roll_result)
            else:
                if isinstance(trait, list):
                    trait = '\n'.join(trait)

                cells.append([die, trait] if is_debug else trait)
        elif die_match(die, header.split('-')):
            if isinstance(trait, dict):
                roll_result = roll_die(trait)

                for key, value in trait.items():
                    get_trait(key, value, roll_result)
            elif '.json' in trait:
                with open('./data/partials/{}'.format(trait), 'r') as feed:
                    partial = json.loads(feed.read())
                    roll_result = roll_die(partial)

                    for key, value in partial.items():
                        get_trait(key, value, roll_result)
            else:
                if isinstance(trait, list):
                    trait = '\n'.join(trait)

                cells.append([die, trait] if is_debug else trait)

    # Init recursion
    for header, trait in FEED_FILE.items():
        roll_result = roll_die(trait)
        get_trait(header, trait, roll_result)

    return (headers, cells)


# Final list generation
def generate():
    # Create results directory if it doesn't exist
    if not os.path.exists('results'):
        os.makedirs('results')

    # Create file
    file = open('./results/{}_{}.txt'.format(
        FEED_TYPE,
        datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    ), mode='a')

    # Create required amount of entries
    for i in range(generation_amount):
        # Entry deconstruction
        (headers, cells) = build()

        # Generate entry table
        pretty_table = PrettyTable()
        pretty_table.field_names = headers
        pretty_table.add_row(cells)

        # Write table to file
        file.write(str(pretty_table) + '\n')

        # Loop 1up
        i += 1

    # Write to disk
    file.close()


# Run
generate()
