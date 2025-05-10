#!/usr/bin/env python3
import random
import time
import re
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# -------OPERATION METEOR: WING ZERO TACTICAL SIMULATION-------
# Global setup
alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
grid_size = 10
grids = []
unit_positions = []
missiles_left = 50
game_over = False
num_of_units = 8
num_of_units_destroyed = 0
destroyed_ships = []
debug_mode = False  # Toggle fleet visibility

# OZ Fleet ship names
oz_ship_names = [
    "Leviathan", "Valkyrie", "Hydra", "Beowulf", "Grendel",
    "Fenrir", "Basilisk", "Chimera", "Tiamat", "Kraken"
]


def display_banner():
    banner = f"""
{Fore.RED}

MOBILE SUIT
 ██████╗ ██╗   ██╗███╗   ██╗██████╗  █████╗ ███╗   ███╗    ██╗    ██╗██╗███╗   ██╗ ██████╗
██╔════╝ ██║   ██║████╗  ██║██╔══██╗██╔══██╗████╗ ████║    ██║    ██║██║████╗  ██║██╔════╝
██║  ███╗██║   ██║██╔██╗ ██║██║  ██║███████║██╔████╔██║    ██║ █╗ ██║██║██╔██╗ ██║██║  ███╗
██║   ██║██║   ██║██║╚██╗██║██║  ██║██╔══██║██║╚██╔╝██║    ██║███╗██║██║██║╚██╗██║██║   ██║
╚██████╔╝╚██████╔╝██║ ╚████║██████╔╝██║  ██║██║ ╚═╝ ██║    ╚███╔███╔╝██║██║ ╚████║╚██████╔╝
 ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝     ╚══╝╚══╝ ╚═╝╚═╝  ╚═══╝ ╚═════╝
OPERATION METEOR: WING ZERO TACTICAL SIMULATION | RETRO REVIVAL | b145k0 | github.com/xblaskox

{Style.RESET_ALL}
    """
    print(banner)


def color_tile(char):
    if char == "X":
        return Fore.GREEN + "X" + Style.RESET_ALL
    elif char == "#":
        return Fore.BLUE + "#" + Style.RESET_ALL
    elif char == "G":
        return Fore.YELLOW + "■" + Style.RESET_ALL if debug_mode else "."
    else:
        return char


def print_grid():
    print("   " + " ".join(str(i) for i in range(grid_size)))
    for row in range(grid_size):
        row_label = alphabet[row]
        print(f"{row_label}) ", end="")
        for col in range(grid_size):
            cell = grids[row][col]
            print(color_tile(cell), end=" ")
        print()


def enemy_chatter():
    ship = random.choice(oz_ship_names)
    destroyed_ships.append(ship)
    lines = [
        "Enemy Pilot: It's no use, it's a Gundam!",
        "Zechs Merquise: That pilot... he fights like he's possessed...",
        "Enemy Pilot: Eject! EJECT!",
        "Control Tower: We're losing ships at Sector 7!",
        "Enemy Unit: All squads, retreat! The Wing is here!",
        f"Enemy Fleet: The {ship} has been destroyed!"
    ]
    print(Fore.MAGENTA + random.choice(lines) + Style.RESET_ALL)


def display_debrief():
    print("\n--- Mission Debrief ---")
    print(f"Total enemy ships destroyed: {len(destroyed_ships)}")
    print("Destroyed ships:")
    for ship in destroyed_ships:
        print(f" - {ship}")
    exit()


def check_for_game_over():
    global game_over
    if num_of_units_destroyed == num_of_units:
        print(Fore.CYAN + "\nMission complete! All enemy ships destroyed." + Style.RESET_ALL)
        game_over = True
        display_debrief()
    elif missiles_left <= 0:
        print(Fore.RED + "\nMission failed. Out of missiles." + Style.RESET_ALL)
        game_over = True
        display_debrief()


def create_grid():
    global grids, unit_positions
    grids = [["." for _ in range(grid_size)] for _ in range(grid_size)]
    unit_positions = []
    placed = 0
    while placed < num_of_units:
        r = random.randint(0, grid_size - 1)
        c = random.randint(0, grid_size - 1)
        direction = random.choice(["left", "right", "up", "down"])
        size = random.randint(3, 5)
        if try_to_place_unit(r, c, direction, size):
            placed += 1


def validate_grid_and_place_unit(start_row, end_row, start_col, end_col):
    for r in range(start_row, end_row):
        for c in range(start_col, end_col):
            if grids[r][c] != ".":
                return False
    unit_positions.append([start_row, end_row, start_col, end_col])
    for r in range(start_row, end_row):
        for c in range(start_col, end_col):
            grids[r][c] = "G"
    return True


def try_to_place_unit(row, col, direction, length):
    start_row, end_row = row, row + 1
    start_col, end_col = col, col + 1
    if direction == "left":
        if col - length < 0:
            return False
        start_col = col - length + 1
    elif direction == "right":
        if col + length >= grid_size:
            return False
        end_col = col + length
    elif direction == "up":
        if row - length < 0:
            return False
        start_row = row - length + 1
    elif direction == "down":
        if row + length >= grid_size:
            return False
        end_row = row + length
    return validate_grid_and_place_unit(start_row, end_row, start_col, end_col)


def check_for_unit_destroyed(row, col):
    for pos in unit_positions:
        s_row, e_row, s_col, e_col = pos
        if s_row <= row < e_row and s_col <= col < e_col:
            for r in range(s_row, e_row):
                for c in range(s_col, e_col):
                    if grids[r][c] != "X":
                        return False
    return True


def fire_missile():
    global missiles_left, num_of_units_destroyed
    placement = input("Target coordinates (e.g., A5): ").upper()
    if not re.match(r"^[A-J][0-9]{1,2}$", placement):
        print("Invalid targeting format.")
        return
    row = alphabet.find(placement[0])
    col = int(placement[1:])
    if not (0 <= row < grid_size and 0 <= col < grid_size):
        print("Coordinates out of range.")
        return
    if grids[row][col] in ["#", "X"]:
        print("You’ve already targeted that location.")
        return
    print("\nMissile fired! Impact in 3...2...1...")
    time.sleep(1)
    if grids[row][col] == ".":
        print(Fore.BLUE + "Missile missed. Empty sector." + Style.RESET_ALL)
        grids[row][col] = "#"
    elif grids[row][col] == "G":
        print(Fore.GREEN + "Direct hit on enemy ship!" + Style.RESET_ALL)
        grids[row][col] = "X"
        if check_for_unit_destroyed(row, col):
            print(Fore.RED + "Enemy ship destroyed!" + Style.RESET_ALL)
            enemy_chatter()
            num_of_units_destroyed += 1
    missiles_left -= 1


def main():
    global game_over
    display_banner()
    create_grid()
    while not game_over:
        print_grid()
        print(Fore.CYAN + f"Remaining targets: {num_of_units - num_of_units_destroyed}    Missiles left: {missiles_left}" + Style.RESET_ALL)
        fire_missile()
        check_for_game_over()


if __name__ == '__main__':
    main()

