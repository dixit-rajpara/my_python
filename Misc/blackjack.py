import random
import time
from colorama import init
from colorama import Fore

init(autoreset=True)

SUITS = ('Hearts', 'Diamonds', 'Spades', 'Clubs')
RANKS = ('Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Jack', 'Queen', 'King', 'Ace')
VALUES = {  
    'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5, 'Six': 6, 'Seven': 7, 'Eight': 8, 'Nine': 9, 'Ten': 10, 
    'Jack': 10, 'Queen': 10, 'King': 10, 'Ace': 11
}

DEALER = 'Dealer'
PLAYERS = ['Player1']

CHOICE_HIT = 1
CHOICE_STAND = 2

class InsufficientChips(Exception):
    pass

class Card():
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __str__(self):
        return '{:8} {}'.format(self.suit, self.rank)

    def value(self):
        return VALUES[self.rank]
    
    def isAce(self):
        return self.rank == 'Ace'

class Deck():
    def __init__(self):
        self.cards = []
        for suit in SUITS:
            for rank in RANKS:
                self.cards.append(Card(suit, rank))
    
    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self):
        return self.cards.pop()

    def __str__(self):
        return '\n'.join([str(c) for c in self.cards])

class Hand():
    def __init__(self):
        self.cards = []
        self.value = 0
        self.aces  = 0
    
    def __str__(self):
        return f'Hand Value : {self.hand_value()} \n' + \
            'Cards : \n' + '\n'.join([str(c) for c in self.cards])

    def add_card(self, card):
        self.cards.append(card)        
        self.value += card.value()
        if card.isAce():
            self.aces += 1

    def show_hand(self, not_last_card = False):
        card_list = self.cards
        if not_last_card:
            print('<Hidden Card>')
            card_list = card_list[0:-1]
        print('\n'.join([str(c) for c in card_list]))
        
    def adjust_for_ace(self):
        while self.value > 21 and self.aces > 0:
            self.value -= 10
            self.aces  -= 1

    def hand_value(self):
        self.adjust_for_ace()
        return self.value

class Chips():
    def __init__(self):
        self.total = 100
        self.bet   = 0

    def place_bet(self, chips):
        if self.total >= chips:
            self.bet = chips
        else:
            raise InsufficientChips()

    def win_bet(self):
        self.total += self.bet
        self.bet = 0

    def lose_bet(self):
        self.total -= self.bet
        self.bet = 0

    def clear_bet(self):
        self.bet = 0

    def __str__(self):
        return f'Total Chips : {self.total}, Current Bet : {self.bet}'

class Player():
    def __init__(self, name, chips, isDealer = False):
        self.name = name
        self.chips = chips
        self.hand = None
        self.isDealer = isDealer

    def show_hand(self, show_all = False):
        print(Fore.YELLOW + self.name + "'s Hand:")
        self.hand.show_hand(self.isDealer and not show_all)
        if not self.isDealer or (self.isDealer and show_all):
            print(f'Total hand value : {self.hand.hand_value()}')
        print()

def enter_to_continue():
    input('Press enter to continue.')
    print()

def get_dealer():
    return Player(DEALER, None, True)

def get_players():
    return [
        Player('Player1', Chips())
    ]

def deal_cards(player, deck, no_of_cards, print_card = False):
    for _ in range(0, no_of_cards):
        c = deck.deal()
        if print_card:
            print(Fore.CYAN + 'New card dealt : ' + str(c))
            time.sleep(1)
        player.hand.add_card(c)

def get_player_choice():
    valid_choices = [ CHOICE_HIT, CHOICE_STAND ]
    choice = -1
    while True:
        try:
            choice = int(input('Enter Option : 1. Hit, 2. Stand : '))
        except ValueError:
            print(Fore.RED + 'Sorry, a bet must be an integer!')
        
        if choice not in valid_choices:
            print(Fore.RED + 'Please enter a valid choice.')
        else:
            return choice

def take_bet(chips):
    print(Fore.GREEN + f'You have {chips.total} chips.')
    while True:
        try:
            chip_count = int(input('How many chips would you like to bet: '))
            chips.place_bet(chip_count)
        except ValueError:
            print(Fore.RED + 'Sorry, a bet must be an integer!')
        except InsufficientChips:
            print(Fore.RED + 'Sorry, you do not have sufficient chips.')
        else:
            print(Fore.GREEN + f'Successfully bet {chips.bet} chips')
            break

def take_all_bets(players):
    for player in all_players:
        print(Fore.YELLOW + f'\n{player.name}')
        take_bet(player.chips)
        print()
    enter_to_continue()

def start_new_hand(all_players, dealer):
    for player in all_players + [ dealer ]:
        player.hand = Hand()

def deal_initial_cards(deck, all_players, dealer):
    for player in all_players + [ dealer ]:
        deal_cards(player, deck, 2)
        player.show_hand()
    enter_to_continue()

def player_loses(player):
    print(Fore.RED + f'{player.name} loses {player.chips.bet} chips.')
    print(f'{player.name}\'s hand value was {player.hand.hand_value()}')
    player.chips.lose_bet()
    print(Fore.CYAN + f"{player.name} now has {player.chips.total} chips.\n")

def player_wins(player):
    print(Fore.GREEN + f'{player.name} wins {player.chips.bet} chips.')
    print(f'{player.name}\'s hand value was {player.hand.hand_value()}')
    player.chips.win_bet()
    print(Fore.CYAN + f"{player.name} now has {player.chips.total} chips.\n")

def player_ties(player):
    print(Fore.CYAN + f'{player.name} ties and does not loose or win any chips.')
    print(f'{player.name}\'s hand value was {player.hand.hand_value()}')
    player.chips.clear_bet()
    print(Fore.CYAN + f"{player.name} now has {player.chips.total} chips.\n")

def play_player(player, deck, busted_players):
    while True:
        player.show_hand()
        p_choice = get_player_choice()
        
        if p_choice == CHOICE_STAND:
            print(f'{player.name} chose to stand.')
            print(f"{player.name}'s' current hand value is {player.hand.hand_value()}.\n")
            break

        print(f'{player.name} chose to hit.')
        print()
        deal_cards(player, deck, 1, True)
        print()
        
        if player.hand.hand_value() > 21:
            print(Fore.RED + f"{player.name} busted.")
            player_loses(player)
            busted_players.append(player)
            print()
            enter_to_continue()
            break

def start_new_game(all_players, dealer):
    busted_players = []
    d = Deck()
    d.shuffle()

    start_new_hand(all_players, dealer)

    print(Fore.CYAN + 'Time to place bets.')
    take_all_bets(all_players)

    print(Fore.CYAN + 'Time to deal initial cards.\n')
    deal_initial_cards(d, all_players, dealer)
    
    # Play with each player
    for player in all_players:
        print(Fore.MAGENTA + f"{player.name}'s turn.\n")
        time.sleep(1)
        play_player(player, d, busted_players)

    print(Fore.MAGENTA + f"{dealer.name}'s turn.\n")
    time.sleep(1)
    
    if len(busted_players) == len(all_players):
        dealer.show_hand(True)
        print(Fore.GREEN + 'All players busted. Dealer Wins.\n')
        return

    while dealer.hand.hand_value() <= 17:
        dealer.show_hand(True)
        print(f'{dealer.name} chose to hit.')
        deal_cards(dealer, d, 1, True)
        time.sleep(2)
    else:
        if dealer.hand.hand_value() <= 21:
            print(f'{dealer.name} chose to stand.')

    d_hand_value = dealer.hand.hand_value()
    
    print(Fore.CYAN + f"\n{dealer.name}'s current hand value is {d_hand_value}.\n")

    enter_to_continue()
    
    if d_hand_value <= 21:
        for player in all_players:
            p_hand_value = player.hand.hand_value()
            if p_hand_value > d_hand_value:
                player_wins(player)
            elif d_hand_value > p_hand_value:
                player_loses(player)
            else:
                player_ties(player)
    else:
        print(Fore.RED + f'{dealer.name} busted.\n')
        for player in all_players:
            if player not in busted_players:
                player_wins(player)
                time.sleep(1)

if __name__ == '__main__':
    print(Fore.MAGENTA + 'Welcome to BlackJack! Get as close to 21 as you can without going over!\n' + \
    'Dealer hits until she reaches 17. Aces count as 1 or 11.\n')

    all_players = get_players()
    dealer      = get_dealer()

    while len(all_players) > 0:
        print(Fore.MAGENTA + 'Starting a new game\n')
        time.sleep(1)
        start_new_game(all_players, dealer)
        
        next_players = []
        for player in all_players:
            if player.chips.total > 0:
                c = input(f'{player.name} do you want to play next game? Enter Y/n : ')
                if len(c) > 0 and c[0].lower() == 'n':
                    print(Fore.RED + f'{player.name} will not play next game.')
                else:
                    next_players.append(player)
                    print(Fore.GREEN + f'{player.name} will play next game.')
            else:
                print(Fore.RED + f'{player.name} will not play next game because of insuffecient chips.')
            
            print()
        
        all_players = next_players

        if len(all_players) > 0:
            enter_to_continue()
    else:
        print(Fore.GREEN + '\nThank you everyone for playing!.')
        


