def calculate_risk_reward_with_dips(risk_amount, entry_price, take_profit, stop_loss, current_price):
    # Divide the portion between entry price and stop loss into two equal parts
    risk_distance = entry_price - stop_loss
    dip1 = entry_price - (risk_distance / 2)
    dip2 = stop_loss

    # Calculate quantities for Dip 1 and Dip 2
    risk_per_unit_dip1 = entry_price - dip1
    risk_per_unit_dip2 = dip1 - dip2

    qty_dip1 = risk_amount / 2 / risk_per_unit_dip1
    qty_dip2 = risk_amount / 2 / risk_per_unit_dip2

    # Average entry price if both dips are hit
    avg_entry_price = (qty_dip1 * dip1 + qty_dip2 * dip2) / (qty_dip1 + qty_dip2)

    # Profit calculation based on current price
    if current_price >= entry_price:
        profit_dip1 = (entry_price - dip1) * qty_dip1
        profit_remaining = (current_price - avg_entry_price) * (qty_dip1 + qty_dip2)
    elif dip2 <= current_price < dip1:
        profit_dip1 = (current_price - dip1) * qty_dip1
        profit_remaining = 0  # Not enough recovery to reach entry price
    elif current_price < dip2:
        profit_dip1 = 0  # Loss occurs if price hits below Dip 2
        profit_remaining = (current_price - avg_entry_price) * (qty_dip1 + qty_dip2)
    else:
        profit_dip1 = 0
        profit_remaining = 0

    total_profit = profit_dip1 + profit_remaining

    return {
        "Dip 1": dip1,
        "Dip 2": dip2,
        "Qty Dip 1": qty_dip1,
        "Qty Dip 2": qty_dip2,
        "Avg Entry Price": avg_entry_price,
        "Profit Dip 1": profit_dip1,
        "Profit Remaining": profit_remaining,
        "Total Profit": total_profit
    }

# Inputs
risk_amount = 10  # The amount you're willing to risk (in $)
entry_price = 229.405  # Entry price
take_profit = 230.9304  # Take profit price
stop_loss = 228.9136  # Stop loss price
current_price = 228.8  # Current market price

# Calculate
results = calculate_risk_reward_with_dips(risk_amount, entry_price, take_profit, stop_loss, current_price)

# Output
for key, value in results.items():
    print(f"{key}: {value:.2f}") if isinstance(value, float) else print(f"{key}: {value}")