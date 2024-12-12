# Risk/Reward Calculator

def calculate_risk_reward(risk_amount, entry_price, take_profit, stop_loss):
    # Calculate risk per unit
    risk_per_unit = entry_price - stop_loss

    # Calculate quantity
    quantity = risk_amount / risk_per_unit

    # Calculate profit per unit
    profit_per_unit = take_profit - entry_price

    # Calculate total profit
    total_profit = quantity * profit_per_unit

    return quantity, total_profit

# Inputs
risk_amount = 10  # The amount you're willing to risk (in $)
entry_price = 229.405  # Entry price
take_profit = 230.9304  # Take profit price
stop_loss = 228.9136  # Stop loss price

# Calculate
quantity, profit = calculate_risk_reward(risk_amount, entry_price, take_profit, stop_loss)

# Output
print(f"Quantity: {quantity:.2f}")
print(f"Profit: ${profit:.2f}")
