from blackjack import BlackjackGame
from strategy import basic_strategy

def print_house_edge(results):
    total_profit = sum(p for p, _ in results)
    total_wagered = sum(w for _, w in results)
    house_edge = total_profit / total_wagered
    print(house_edge)

def get_bool_input(prompt, default=False):
    val = input(f"{prompt} [{'y' if default else 'n'}/{'n' if default else 'y'}]: ").strip().lower()
    if val == '':
        return default
    return val in ['y', 'yes', 'true', '1']

if __name__ == "__main__":
    # Arguments for BlackjackGame
    num_decks = int(input("Enter number of decks (default 6): ") or 6)
    penetration = float(input("Enter penetration (0-1, default 0.75): ") or 0.75)
    dealer_hits_soft_17 = get_bool_input("Should dealer hit soft 17?", default=True)
    surrender_allowed = get_bool_input("Is surrender allowed?", default=True)
    num_runs = int(input("Enter number of games to simulate (default 100000): ") or 100000)

    game = BlackjackGame(
        num_decks=num_decks,
        penetration=penetration,
        dealer_hits_soft_17=dealer_hits_soft_17,
        surrender_allowed=surrender_allowed
    )

    results = []
    for _ in range(num_runs):
        round_results = game.play_round(basic_strategy, bet=1)  # list of (profit, bet)
        results.extend(round_results)  # flatten
    
    print_house_edge(results)