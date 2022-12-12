import time
import printer

class NimGame ():

    def __init__(self, my_ip, player_number, player1_ip, player2_ip, player3_ip):
        self.my_ip = my_ip
        self.my_number = int(player_number)
        self.state = {'sticks': [1,1,1,1,0,1,1,1,1,0],
                      'players': [player1_ip, player2_ip, player3_ip],
                      'phase': 'starting', # Possible values are: starting, playing, ended
                      'announcement': printer.starting(), # Possible values can be found in class printer
                      'player_in_turn': 1, # Number of the player in turn
                      'winner': None,
                      'lost': [],
                      'turn_count': 0}

    def get_current_player(self):
        return self.state['player_in_turn']

    def set_announcement(self, announcement):
        self.state['announcement'] = announcement

    def set_phase(self, phase):
        self.state['phase'] = phase

    def update_state(self, new_state):
        if abs(new_state['turn_count'] < self.state['turn_count']):
            # Don't update from older state
            print('ERROR! Moves out of syncronization!')
        else:
            self.state = new_state

    def update_player_in_turn(self):
        next_player = (self.state['player_in_turn'] % 3) + 1
        while next_player in self.state['lost']:
            next_player = (next_player % 3) + 1
        self.state['player_in_turn'] = next_player

    def update_winner(self):
        self.set_phase('ended')
        for player_number in range(1, 4):
            if player_number not in self.state['lost']:
                self.state['winner'] = player_number
                return player_number

    def make_move(self):
        # We make a move
        self.set_phase('playing')
        moves = self.get_user_input()
        self.pick_sticks(moves, self.my_number)

        if self.is_end(): # Check if the game has ended
            self.update_winner()
            printer.print_results(self.state['announcement'], self.state['winner'])
            return self.state
            
        self.increment_turn_count()
        self.display_game_state()
        return self.state

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

    def our_turn(self):
        return self.state['player_in_turn'] == self.my_number

    def lost(self):
        return self.my_number in self.state['lost']

    def is_end(self):
        if len(self.state['lost']) >= 2:
            return True
        return False

    def add_player_to_lost(self, lost_player):
        if lost_player not in self.state['lost']:
            self.state['lost'].append(lost_player)

    def get_user_input(self):
        answer = printer.ask_for_move()
        while True:
            if len(answer) <= 2:
                if answer.isnumeric():
                    answer = int(answer)
                    if answer == 1 or answer == 2:
                        return answer
            answer = printer.ask_again()

    def increment_turn_count(self):
        self.state['turn_count'] = self.state['turn_count'] + 1
        self.update_player_in_turn()
        
    def pick_sticks(self, amount, player):
        for i in range(0, amount):
            if self.state['sticks'].pop(0) == 0:
                self.add_player_to_lost(player)
                self.state['announcement'] = printer.rotten_apple(player)
                return
        self.state['announcement'] = printer.sticks(player, amount)
