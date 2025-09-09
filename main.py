from blackjack import BlackjackGame
from strategy import basic_strategy

def print_house_edge(results):
    total_profit = sum(p for p, _ in results)
    total_wagered = sum(w for _, w in results)
    house_edge = total_profit / total_wagered
    print(house_edge)
    
if __name__ == "__main__":
    game = BlackjackGame(num_decks=6, penetration=0.75, dealer_hits_soft_17=True, surrender_allowed=True)
    num_runs = 100000
    
    results = []
    for _ in range(num_runs):
        round_results = game.play_round(basic_strategy, bet=1)  # list of (profit, bet)
        results.extend(round_results)  # flatten
    
    print_house_edge(results)