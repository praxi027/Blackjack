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
    def __init__(self, bet=1, is_split_aces=False):
        self.cards = []
        self.bet = bet
        self.doubled = False
        self.is_split_aces = is_split_aces

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
    def __init__(self, num_decks=6, penetration=0.75, dealer_hits_soft_17=True):
        self.shoe = Shoe(num_decks, penetration)
        self.dealer_hits_soft_17 = dealer_hits_soft_17

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
                
            # If this hand is from splitting aces, stand immediately
            if hand.is_split_aces:
                i += 1
                continue

            while True:
                action = player_strategy(hand, dealer_hand.cards[0], split_allowed=split_count < 3)

                if action == "hit":
                    hand.add_card(self.shoe.deal_card())
                    if hand.is_bust():
                        break

                elif action == "stand":
                    break

                elif action == "double":
                    hand.bet *= 2
                    hand.doubled = True
                    hand.add_card(self.shoe.deal_card())
                    break

                elif action == "split":                 
                    # Check if splitting aces now
                    splitting_aces = (hand.cards[0].rank == 'A' and hand.cards[1].rank == 'A')

                    split_count += 1

                    new_hand = Hand(bet=hand.bet)
                    new_hand.add_card(hand.cards.pop())  # move one card to new hand
                    hand.add_card(self.shoe.deal_card())  # draw card for first hand
                    new_hand.add_card(self.shoe.deal_card())
                    player_hands.append(new_hand)

                    # If splitting aces, flag both hands
                    if splitting_aces:
                        new_hand.is_split_aces = True
                        hand.is_split_aces = True
                        break
                    continue
                else:
                    print("error")
                    break

            i += 1

        # Dealer's turn
        while self.dealer_should_hit(dealer_hand):
            dealer_hand.add_card(self.shoe.deal_card())

        # Settle results
        results = []
        for hand in player_hands:
            if hand.is_blackjack() and not dealer_hand.is_blackjack() and split_count == 0:
                results.append(1.5 * hand.bet)
            elif (not hand.is_blackjack() or split_count != 0) and dealer_hand.is_blackjack():
                results.append(-hand.bet)
            elif hand.is_bust():
                results.append(-hand.bet)
            elif dealer_hand.is_bust():
                results.append(hand.bet)
            elif hand.value() > dealer_hand.value():
                results.append(hand.bet)
            elif hand.value() < dealer_hand.value():
                results.append(-hand.bet)
            else:
                results.append(0)

        return results


    def dealer_should_hit(self, hand):
        if hand.value() < 17:
            return True
        if hand.value() == 17 and self.dealer_hits_soft_17 and hand.is_soft():
            return True
        return False

def basic_strategy(hand, dealer_upcard, split_allowed):
    if hand.value() == 21: 
        return "stand"
    
    up = dealer_upcard.value
    total = hand.value()
    ranks = [c.rank for c in hand.cards]

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
                if up in [7, 8]:
                    return "stand"
            elif other == 8 and up == 6:
                return "double"
            elif other == 9:
                return "stand"
        else: 
            other = total - 11
            if other in [2, 3] and up in [5, 6]:
                return "hit"
            elif other in [4, 5] and up in range(4, 7):
                return "hit"
            elif other == 6 and up in range(3, 7):
                return "hit"
            elif other == 7:
                if up in range(2, 9):
                    return "stand"
            elif other in [8, 9]:
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

# Example usage with a simple "hit under 17" strategy
if __name__ == "__main__":
    game = BlackjackGame(num_decks=6, penetration=0.75, dealer_hits_soft_17=True)
    num_runs = 1000000
    results = [game.play_round(basic_strategy) for _ in range(num_runs)]
    print(sum(bet for hand in results for bet in hand)/num_runs)
