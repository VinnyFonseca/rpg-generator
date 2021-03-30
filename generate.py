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
with open('./data/{}.json'.format(FEED_TYPE), 'r') as myfile:
    FEED_FILE = json.loads(myfile.read())


# Single entry generation
def get_die_type(rolls):
    last_roll = list(rolls.keys())[-1].split('-')
    highest_roll = last_roll[1] if len(last_roll) > 1 else last_roll[0]

    return int(highest_roll) if highest_roll.isnumeric() else 6


# Random die roll based on autodetected number of faces
def roll_die(attribute):
    die = get_die_type(attribute)
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
def generate_entry():
    headers = []
    cells = []

    # Recursive function
    def get_attribute(header, attribute, die):
        is_rollable = '-' in header or header.isnumeric()

        if not is_rollable:
            if header != 'Value':
                headers.append(header)
                roll_result = roll_die(attribute)

                for key, value in attribute.items():
                    get_attribute(key, value, roll_result)
            else:
                cells.append([die, attribute] if is_debug else attribute)
        elif die_match(die, header.split('-')):
            if isinstance(attribute, dict):
                roll_result = roll_die(attribute)

                for key, value in attribute.items():
                    get_attribute(key, value, roll_result)
            else:
                cells.append([die, attribute] if is_debug else attribute)

    # Init recursion
    for header, attribute in FEED_FILE.items():
        roll_result = roll_die(attribute)
        get_attribute(header, attribute, roll_result)

    return (headers, cells)


# Final list generation
def generate():
    file = open('./results/{}_{}.txt'.format(
        FEED_TYPE,
        datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    ), mode='a')
    counter = 0

    while counter < generation_amount:
        # Entry deconstruction
        (headers, cells) = generate_entry()

        # Generate entry table
        pretty_table = PrettyTable()
        pretty_table.field_names = headers
        pretty_table.add_row(cells)

        # Write table to file
        file.write(str(pretty_table) + '\n')

        # Loop 1up
        counter += 1

    file.close()


# Write to disk
if not os.path.exists('results'):
    os.makedirs('results')

generate()
