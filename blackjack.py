import random

class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    @property
    def value(self):
        if self.rank in ['J', 'Q', 'K']:
            return 10
        elif self.rank == 'A':
            return 11
        else:
            return int(self.rank)

    def __repr__(self):
        return f"{self.rank}{self.suit}"


class Shoe:
    def __init__(self, num_decks=6, penetration=0.75):
        self.num_decks = num_decks
        self.penetration = penetration
        self.shuffle()

    def shuffle(self):
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        suits = ['♠', '♥', '♦', '♣']
        self.cards = [Card(rank, suit) for rank in ranks for suit in suits] * self.num_decks
        random.shuffle(self.cards)

    def deal_card(self):
        # Shuffle if penetration reached
        if len(self.cards) < (1 - self.penetration) * 52 * self.num_decks:
            self.shuffle()
        return self.cards.pop()

class Hand:
    def __init__(self, bet=1):
        self.cards = []
        self.bet = bet
        self.doubled = False
        self.surrendered = False

    def add_card(self, card):
        self.cards.append(card)

    def value(self):
        total = sum(c.value for c in self.cards)
        aces = sum(1 for c in self.cards if c.rank == 'A')
        while total > 21 and aces:
            total -= 10
            aces -= 1
        return total
    
    def is_soft(self):
        total = sum(c.value for c in self.cards)
        aces = sum(1 for c in self.cards if c.rank == 'A')
        if not aces:
            return False
        
        while aces:
            total -= 10
            aces -= 1
        return total < 11

    def is_blackjack(self):
        return len(self.cards) == 2 and self.value() == 21

    def is_bust(self):
        return self.value() > 21

    def is_pair(self):
        return len(self.cards) == 2 and self.cards[0].value == self.cards[1].value
    
    def can_double(self):
        return len(self.cards) == 2

class BlackjackGame:
    def __init__(self, num_decks=6, penetration=0.75, dealer_hits_soft_17=True, surrender_allowed=True):
        self.shoe = Shoe(num_decks, penetration)
        self.dealer_hits_soft_17 = dealer_hits_soft_17
        self.surrender_allowed = surrender_allowed

    def play_round(self, player_strategy):
        player_hands = [Hand()]
        dealer_hand = Hand()
        split_count = 0  # track number of splits done

        # Initial deal
        for _ in range(2):
            player_hands[0].add_card(self.shoe.deal_card())
            dealer_hand.add_card(self.shoe.deal_card())

        i = 0
        while i < len(player_hands):
            hand = player_hands[i]

            while True:
                action = player_strategy(hand, dealer_hand.cards[0], split_count < 3, self.dealer_hits_soft_17, self.surrender_allowed)
                
                if action == "split":                 
                    split_count += 1

                    new_hand = Hand(bet=hand.bet)
                    new_hand.add_card(hand.cards.pop())  # move one card to new hand
                    hand.add_card(self.shoe.deal_card())  # draw card for first hand
                    new_hand.add_card(self.shoe.deal_card())
                    player_hands.append(new_hand)
                    
                    if hand.cards[0].rank == 'A' and hand.cards[1].rank == 'A':
                        i = len(player_hands)  # end turn after splitting aces
                        break
                    else:
                        continue  # re-evaluate the current hand after split

                elif action == "hit":
                    hand.add_card(self.shoe.deal_card())
                    if hand.is_bust():
                        i += 1
                        break

                elif action == "stand":
                    i += 1
                    break

                elif action == "double":
                    hand.bet *= 2
                    hand.doubled = True
                    hand.add_card(self.shoe.deal_card())
                    i += 1
                    break
                
                elif action == "surrender":
                    hand.surrendered = True
                    i += 1
                    break
                else:
                    print("Error: Wrong action selected by strategy.")
                    break

        # Dealer's turn
        while self.dealer_should_hit(dealer_hand):
            dealer_hand.add_card(self.shoe.deal_card())

        # Settle results
        results_round = []
        for hand in player_hands:
            bet = hand.bet
            if hand.is_blackjack() and not dealer_hand.is_blackjack() and split_count == 0:
                profit = 1.5 * bet
            elif (not hand.is_blackjack() or split_count != 0) and dealer_hand.is_blackjack():
                profit = -bet
            elif hand.surrendered:
                profit = -bet / 2
            elif hand.is_bust():
                profit = -bet
            elif dealer_hand.is_bust():
                profit = bet
            elif hand.value() > dealer_hand.value():
                profit = bet
            elif hand.value() < dealer_hand.value():
                profit = -bet
            else:
                profit = 0

            results_round.append((profit, bet))
            
        return results_round


    def dealer_should_hit(self, hand):
        if hand.value() < 17:
            return True
        if hand.value() == 17 and self.dealer_hits_soft_17 and hand.is_soft():
            return True
        return False

def basic_strategy(hand, dealer_upcard, split_allowed, dealer_hits_soft_17, surrender_allowed):
    if hand.value() == 21: 
        return "stand"
    
    up = dealer_upcard.value
    total = hand.value()
    ranks = [c.rank for c in hand.cards]

    # Surrender 
    if surrender_allowed and len(hand.cards) == 2 and not hand.is_soft():
        if total == 17 and up == 11:
            return "surrender"
        elif total == 16:
            if hand.is_pair() and up == 11:
                return "surrender"
            elif not hand.is_pair() and up in [9, 10, 11]:
                return "surrender"
        elif total == 15 and up in [10, 11]:
            return "surrender"

    # Pair splitting
    if hand.is_pair() and split_allowed:
        r = ranks[0]
        if r in ['A', '8']:
            return "split"
        if r in ['2', '3', '7'] and up in range(2, 8):
            return "split"
        if r == '6' and up in range(2, 7):
            return "split"
        if r == '9' and up in [2, 3, 4, 5, 6, 8, 9]:
            return "split"
        if r == '4' and up in [5, 6]:
            return "split"

    # Soft totals
    if hand.is_soft():
        if hand.can_double():
            other = total - 11
            if other in [2, 3] and up in [5, 6]:
                return "double"
            elif other in [4, 5] and up in range(4, 7):
                return "double"
            elif other == 6 and up in range(3, 7):
                return "double"
            elif other == 7:
                if up in range(2, 7):
                    return "double"
                elif up in [7, 8]:
                    return "stand"
            elif other == 8 and up == 6:
                return "double"
            elif other == 9:
                return "stand"
            return "hit"
        else: 
            other = total - 11
            if other in range(2, 7):
                return "hit"
            elif other == 7:
                if up in range(2, 9):
                    return "stand"
                else:
                    return "hit"
            else:
                return "stand"
                
    # Hard totals
    if hand.can_double():
        if total <= 8:
            return "hit"
        elif total == 9:
            if up in range(3, 7):
                return "double"
            return "hit"
        elif total == 10:
            if up in range(2, 10):
                return "double"
            return "hit"
        elif total == 11:
            return "double"
        elif total == 12:
            if up in range(4, 7):
                return "stand"
            return "hit"
        elif total in range(13, 17):
            if up in range(2, 7):
                return "stand"
            return "hit"
        return "stand"
    else:
        if total <= 11:
            return "hit"
        elif total == 12:
            if up in range(4, 7):
                return "stand"
            return "hit"
        elif total in range(13, 17):
            if up in range(2, 7):
                return "stand"
            return "hit"
        return "stand"

def print_house_edge(results):
    total_profit = sum(p for p, _ in results)
    total_wagered = sum(w for _, w in results)
    house_edge = total_profit / total_wagered
    print(house_edge)
    
if __name__ == "__main__":
    game = BlackjackGame(num_decks=6, penetration=0.75, dealer_hits_soft_17=True, surrender_allowed=True)
    num_runs = 10000000
    
    results = []
    for _ in range(num_runs):
        round_results = game.play_round(basic_strategy)  # list of (profit, bet)
        results.extend(round_results)  # flatten
    
    print_house_edge(results)
