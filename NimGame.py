import time
import printer

class NimGame ():

    def __init__(self, my_ip, player_number, player1_ip, player2_ip, player3_ip):
        self.my_ip = my_ip
        self.my_number = player_number
        print(self.my_number)
        self.state = {'sticks': [1,1,0,1,1,0],
                      'players': [player1_ip, player2_ip, player3_ip],
                      'phase': 'starting', # Possible values are: starting, playing, ended
                      'announcement': printer.waiting(), # Possible values can be found in class printer
                      'next': player1_ip, # This would be better if it showed player number instead of IP
                      'winner': None,
                      'lost': [],
                      'moves_count': 0}

    def turn_manager(self):
        if self.state['phase'] == 'starting':
            printer.print_title()
        printer.print_gamestate(self.state['announcement'], self.state['next'], self.state['sticks'])
        if self.our_turn():
            if not self.lost():
                # It is this node's turn and we are still in the game
                return self.make_move()
            elif self.lost(): 
                # It would be this node's turn, but we have lost the game
                self.increment_turn_count()
                return self.state
        if self.state['phase'] == 'ended':
            printer.print_results(self.state['announcement'], self.state['winner'])

    def our_turn(self):
        return self.state['next'] == self.my_ip

    def lost(self):
        return self.my_ip in self.state['lost']

    def make_move(self):
        self.state['phase'] = 'playing'
        moves = self.get_user_input()
        self.pick_sticks(moves, self.my_ip) # Here it would also be better to use player number instead of IP
        # Check if the game has ended
        if self.is_end():
            printer.print_results(self.state['announcement'], self.state['winner'])
            return self.state
        self.increment_turn_count()
        printer.print_gamestate(self.state['announcement'], self.state['next'], self.state['sticks'])
        return self.state

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
        self.state['moves_count'] = self.state['moves_count'] + 1
        self.state['next'] = self.state['players'][(self.state['moves_count']) % 3]
        
    def pick_sticks(self, amount, player):
        for i in range(0, amount):
            if self.state['sticks'].pop(0) == 0:
                self.state['lost'].append(player)
                self.state['announcement'] = printer.rotten_apple(player)
                return
        self.state['announcement'] = printer.sticks(player, amount)

    def is_end(self):
        if len(self.state['sticks']) == 0 and len(self.state['lost']) == 2:
            self.state['phase'] = 'ended'
            for p in self.state['players']:
                if p not in self.state['lost']:
                    self.state['winner'] = p
            return True
        return False

    def update_state(self, new_state):
        if abs(new_state['moves_count'] < self.state['moves_count']):
            # Don't update from older state
            print('ERROR! Moves out of syncronization!')
        else:
            self.state = new_state
        
#if __name__ == '__main__':
#    nimgame = NimGame('1.1', '1.1', '2.2','3.3')
#    clear()
#    pr.print(fig.figlet_format('N I M Game', font='5lineoblique'), color='yellow')
#    nimgame.turn_manager()