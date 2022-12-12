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

    def make_move(self):
        # We make a move
        self.state['phase'] = 'playing'
        moves = self.get_user_input()
        self.pick_sticks(moves, self.my_number)
        # Check if the game has ended
        if self.is_end():
            printer.print_results(self.state['announcement'], self.state['winner'])
            return self.state
        self.increment_turn_count()
        printer.print_gamestate(self.state['announcement'], self.state['player_in_turn'], self.my_number, self.state['sticks'])
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

    def update_player_in_turn(self):
        next_player = (self.state['player_in_turn'] % 3) + 1
        while next_player in self.state['lost']:
            next_player = (next_player % 3) + 1
        self.state['player_in_turn'] = next_player

        
    def pick_sticks(self, amount, player):
        for i in range(0, amount):
            if self.state['sticks'].pop(0) == 0:
                self.state['lost'].append(player)
                self.state['announcement'] = printer.rotten_apple(player)
                return
        self.state['announcement'] = printer.sticks(player, amount)

    def is_end(self):
        if len(self.state['sticks']) == 0 and len(self.state['lost']) >= 2:
            self.update_winner()
            return True
        return False

    def update_winner(self):
        self.state['phase'] = 'ended'
        for player_number in range(1, 4):
            if player_number not in self.state['lost']:
                self.state['winner'] = player_number

    def update_state(self, new_state):
        if abs(new_state['turn_count'] < self.state['turn_count']):
            # Don't update from older state
            print('ERROR! Moves out of syncronization!')
        else:
            self.state = new_state
        
#if __name__ == '__main__':
#    nimgame = NimGame('1.1', '1.1', '2.2','3.3')
#    clear()
#    pr.print(fig.figlet_format('N I M Game', font='5lineoblique'), color='yellow')
#    nimgame.turn_manager()