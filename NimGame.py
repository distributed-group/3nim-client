import os
import terminedia as pr
import pyfiglet as fig

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

class NimGame ():

    def __init__(self, my_ip, player1, player2, player3):
        self.my_ip = my_ip
        self.player1 = player1
        self.player2 = player2
        self.player3 = player3
        self.state = {'sticks': [1,1,1,1,1,0,1,1,1,1,0],
                        'last': None,
                        'last_move': None,
                        'last_note': 'Waiting first player to start',
                        'next': player1,
                        'phase': 'starting',
                        'lost': [],
                        'players': [player1, player2, player3],
                        'winner': None,
                        'moves_count': 0}
    
    def show_end_game(self):
        clear()
        print(self.state['last_note'])
        pr.print('_______PLAYER ' + self.state['winner'] + ' WINS!_________', color='green')
        pr.print(fig.figlet_format('END', font='5lineoblique'), color='yellow')
        pr.print('press ctrl + c to quit', color='white')

    def show_game(self):
        clear()
        if self.state['phase'] == 'starting':
            pr.print(fig.figlet_format('N I M Game', font='5lineoblique'), color='yellow')
        pr.print('', color='white')
        print(self.state['last_note'])
        print('Next turn: ' + self.state['next'] + '\n')
        print('STICKS:\n')
        for stick in self.state['sticks']:
            if stick == 1:
                pr.print('|', color='blue', end=' ')
            else:
                pr.print('O', color='red', end=' ')
        pr.print('', color='white')

    def turn_manager(self):
        if self.state['phase'] == 'ended':
            self.show_end_game()
        elif self.state['next'] == self.my_ip and self.my_ip not in self.state['lost']:
            self.show_game()
            self.state['phase'] = 'playing'
            pr.print('', color='yellow')
            print('_______It is your turn_______')
            print('Do you want to pick one or two sticks?')
            answer = int(input())
            self.pick_sticks(answer, self.my_ip)
            self.state['last'] = self.my_ip
            self.state['last_move'] = answer
            self.state['moves_count'] = self.state['moves_count'] + 1
            self.state['next'] = self.state['players'][(self.state['moves_count']) % 3]
            if self.state['phase'] == 'ended':
                self.show_end_game()
                return self.state
            self.show_game()
            return self.state
        elif self.state['next'] == self.my_ip and self.my_ip in self.state['lost']:
            self.state['moves_count'] = self.state['moves_count'] + 1
            self.state['next'] = self.state['players'][(self.state['moves_count']) % 3]
            return self.state
        else:
            self.show_game()
        

    def pick_sticks(self, amount, player):
        for i in range(0, amount):
            if self.state['sticks'].pop(0) == 0:
                self.state['lost'].append(player)
                self.state['last_note'] = player + ' picked rotten apple!'
                #when game ends
                if len(self.state['sticks']) == 0 and len(self.state['lost']) == 2:
                    self.state['phase'] = 'ended'
                    for p in self.state['players']:
                        if p not in self.state['lost']:
                            self.state['winner'] = p
                            break
                return
        self.state['last_note'] = self.my_ip + ' picked ' + str(amount)

    #not yet used
    def get_state(self):
        return self.state

    def update_state(self, new_state):
        if abs(new_state['moves_count'] < self.state['moves_count']):
            #don't update from older state
            print('ERROR! Moves out of syncronization!')
        else:
            self.state = new_state
    
#if __name__ == '__main__':
#    nimgame = NimGame('1.1', '1.1', '2.2','3.3')
#    clear()
#    pr.print(fig.figlet_format('N I M Game', font='5lineoblique'), color='yellow')
#    nimgame.turn_manager()
