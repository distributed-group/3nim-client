import os
import terminedia as pr
import pyfiglet as fig

def print_title(player_number):
    clear()
    pr.print(fig.figlet_format('N I M Game', font='5lineoblique'), color='yellow')
    print('You are player ' + str(player_number) + '.')

def print_gamestate(announcement, player_in_turn, my_number, gamequeue):
    pr.print('', color='white')
    print(announcement + '\n')
    print('STICKS:\n')
    for stick in gamequeue:
        if stick == 1:
            pr.print('|', color='blue', end=' ')
        else:
            pr.print('O', color='red', end=' ')
    pr.print('', color='white')
    if my_number != player_in_turn:
        print('\nNow in turn: Player ' + str(player_in_turn) + '\n')

def print_results(announcement, winner):
    pr.print('', color='white')
    print(announcement + '\n')
    pr.print('_______PLAYER ' + str(winner) + ' WINS!_________', color='green')
    pr.print(fig.figlet_format('END', font='5lineoblique'), color='yellow')
    pr.print('press ctrl + c to quit', color='white')

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

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

"""
Here are ready-made strings to be used as announcements.
"""
def starting():
    return 'Welcome to the game.'

def sticks(player_number, amount):
    if amount == 1:
        return 'Player ' + str(player_number) + ' picked 1 stick.\n'
    return 'Player ' + str(player_number) + ' picked ' + str(amount) + ' sticks.\n'

def rotten_apple(player_number):
    return 'Player ' + str(player_number) + ' picked a rotten apple!\n'