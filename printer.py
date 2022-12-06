import os
import terminedia as pr
import pyfiglet as fig

def print_title():
    clear()
    pr.print(fig.figlet_format('N I M Game', font='5lineoblique'), color='yellow')

def print_gamestate(announcement, player_in_turn, gamequeue):
    pr.print('', color='white')
    print(announcement)
    print('Next in turn: ' + player_in_turn + '\n')
    print('STICKS:\n')
    for stick in gamequeue:
        if stick == 1:
            pr.print('|', color='blue', end=' ')
        else:
            pr.print('O', color='red', end=' ')
    pr.print('', color='white')

def ask_for_move():
    pr.print('', color='yellow')
    print('_______It is your turn_______')
    print('Do you want to pick one or two sticks?')
    answer = input()
    return answer

def ask_again():
    pr.print('', color='yellow')
    print('Please pick either one (1) or two (2) sticks.')
    answer = input()
    return answer

def print_results(announcement, winner):
    print(announcement)
    pr.print('_______PLAYER ' + winner + ' WINS!_________', color='green')
    pr.print(fig.figlet_format('END', font='5lineoblique'), color='yellow')
    pr.print('press ctrl + c to quit', color='white')

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

"""
Here are ready-made strings to be used as announcements.
"""
# Might be a bit inconsistent to only have this for the first player. This could be displayed during other wait times as well.
def waiting():
    return 'Waiting for the first player to make a move.'

def sticks(player, amount):
    if amount == 1:
        return player + ' picked 1 stick.'
    return player + ' picked ' + str(amount) + ' sticks.'

def rotten_apple(player):
    return player + ' picked a rotten apple!'