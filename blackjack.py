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
        if len(self.cards) == 0:
            print("Shoe is empty, cannot deal card.")
            return None
        return self.cards.pop()
    
    def penetration_reached(self):
        return len(self.cards) < (1 - self.penetration) * self.num_decks * 52

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

    def play_round(self, player_strategy, bet=1):
        if self.shoe.penetration_reached():
            self.shoe.shuffle()
            
        player_hands = [Hand(bet)]
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


