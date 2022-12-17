import os
import terminedia as pr
import pyfiglet as fig

"""
This library contains the code for printing UI text to the terminal window.
"""

def print_title(player_number):
    clear()
    pr.print(fig.figlet_format('3 N I M', font='5lineoblique'), color='yellow')
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
    pr.print('', color='white')

def print_results_no_winner(announcement):
    pr.print('', color='white')
    print(announcement + '\n')
    pr.print('_______PLEASE QUEUE AGAIN!_________', color='green')
    pr.print(fig.figlet_format('END', font='5lineoblique'), color='yellow')
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

"""
Clears the terminal.
"""
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


# Ready-made strings to be used as announcements.

def starting():
    return 'Welcome to the game.'

def sticks(player_number, amount):
    if amount == 1:
        return 'Player ' + str(player_number) + ' picked 1 stick.\n'
    return 'Player ' + str(player_number) + ' picked ' + str(amount) + ' sticks.\n'

def rotten_apple(player_number):
    return 'Player ' + str(player_number) + ' picked a rotten apple!\n'

def disconnect_and_winner(disconnected_player, winner):
    return "Player " + str(disconnected_player) + " has disconnected and player " + str(winner) + " has won!"

def disconnect(disconnected_player):
    return "Player " + str(disconnected_player) + " has left the game.\nThe game has ended with no winner."


# Helper functions

"""
Creates a new message.
Status is given as a parameter. If players is set to True, player IP's will be included in the message. 
Game state can be given as a parameter, otherwise it will be an empty dictionary.
"""
def create_message(game, status, players = True, state = {}):
    data = {}
    if players:
        data['1'] = game.state['players'][0]
        data['2'] = game.state['players'][1]
        data['3'] = game.state['players'][2]
    data['status'] = status
    data['state'] = state
    return data


"""
Finds a given node's player number from the 'start game' -message based on the node's IP.
"""
def get_player_number(data, node_ip):
    for number in data:
        if (data[number] == node_ip):
            return number
    return 0
