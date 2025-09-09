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