import time
import printer
from Logger import Logger


class NimGame:

    def __init__(self, my_ip, player_number, player1_ip, player2_ip, player3_ip):
        self.my_ip = my_ip
        self.my_number = int(player_number)
        self.state = {'sticks': [1,1,1,1,0,1,1,1,1,0],
                      'players': [player1_ip, player2_ip, player3_ip],
                      'phase': 'starting', # Possible values are: starting, playing, ended and ended_no_winner
                      'announcement': printer.starting(), # Possible values can be found in printer.py
                      'player_in_turn': 1,
                      'winner': None,
                      'lost': [],
                      'turn_count': 0}

        # Log the events
        self.logger = Logger('log.txt', my_ip)

    def get_player_in_turn(self):
        return self.state['player_in_turn']

    def get_game_state(self):
        return self.state

    def get_turn_count(self):
        return self.state['turn_count']

    def get_player_number(self):
        return self.my_number

    def set_announcement(self, announcement):
        self.state['announcement'] = announcement

    def set_phase(self, phase):
        self.state['phase'] = phase

    """
    Makes a move.
    We ask the user for input, update the local game state and display the updated game state to the user.
    Returns updated game state.
    """
    def make_move(self):

        self.set_phase('playing')
        moves = self.get_user_input()
        self.pick_sticks(moves, self.my_number)

        if self.is_end():
            self.find_winner()
            self.display_game_state()
            return self.state
        
        self.increment_turn_count()
        self.display_game_state()
        return self.state

    """
    Asks the user for input.
    Returns 1 or 2.
    """
    def get_user_input(self):
        answer = printer.ask_for_move()
        while True:
            if len(answer) <= 2:
                if answer.isnumeric():
                    answer = int(answer)
                    if answer == 1 or answer == 2:
                        return answer
            answer = printer.ask_again()

    """
    Removes the given amount of sticks from the local game queue.
    If the player picked up a rotten apple, this player is added to the list of lost players.
    """
    def pick_sticks(self, amount, player):
        for i in range(0, amount):
            if self.state['sticks'].pop(0) == 0:
                self.add_player_to_lost(player)
                self.state['announcement'] = printer.rotten_apple(player)
                return
        self.state['announcement'] = printer.sticks(player, amount)

    """
    Prints the current game state and relevant information to the user, based on the local game phase, using printer.py.
    """
    def display_game_state(self):
        if self.state['phase'] == 'starting':
            printer.print_title(self.my_number)
            printer.print_gamestate(self.state['announcement'], self.state['player_in_turn'], self.my_number, self.state['sticks'])
        elif self.state['phase'] == 'ended':
            printer.print_results(self.state['announcement'], self.state['winner'])
        elif self.state['phase'] == 'ended_no_winner':
            printer.print_results_no_winner(self.state['announcement'])
        else: 
            printer.print_gamestate(self.state['announcement'], self.state['player_in_turn'], self.my_number, self.state['sticks'])

    """
    Checks if the game has ended.
    Returns True or False.
    """
    def is_end(self):
        if len(self.state['lost']) >= 2:
            return True
        return False

    """
    Finds the last remaining player, the winner. 
    Updates the local game state's slot 'winner'.
    Returns winner's player number.
    """
    def find_winner(self):
        self.set_phase('ended')
        for player_number in range(1, 4):
            if player_number not in self.state['lost']:
                self.state['winner'] = player_number
                return player_number

    """
    Increases the turn count by one and finds the next player in turn.
    """
    def increment_turn_count(self):
        self.state['turn_count'] = self.state['turn_count'] + 1
        self.update_player_in_turn()

    """
    Finds the next player in turn, meaning the next player in the turn order that has not lost. 
    Updates the local game state's slot 'player_in_turn'.
    """
    def update_player_in_turn(self):
        next_player = (self.state['player_in_turn'] % 3) + 1
        while next_player in self.state['lost']:
            next_player = (next_player % 3) + 1
        self.state['player_in_turn'] = next_player

    """
    Replaces the local game state with the given game state, if it is newer.
    """
    def update_state(self, new_state):
        if abs(new_state['turn_count'] < self.state['turn_count']):
            # Don't update from older state
            self.logger.write_log('ERROR! Moves out of syncronization!')
        else:
            self.state = new_state

    """
    Checks if it's this player's turn.
    Returns True or False.
    """
    def our_turn(self):
        return self.state['player_in_turn'] == self.my_number

    """
    Adds the given player to the list of lost players, if not already there.
    """
    def add_player_to_lost(self, lost_player):
        if lost_player not in self.state['lost']:
            self.state['lost'].append(lost_player)
