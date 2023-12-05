import requests
import json
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pytz
import tkinter as tk
from tkinter import ttk, messagebox

# Replace with your IEX Cloud API key
api_key = "pk_c92e43454f9c4261beb6c891360f1b0e"

# User's initial cash and stock holdings
initial_cash = 10000
initial_stock_quantity = 0

# User's current portfolio
cash_balance = initial_cash
stock_quantity = initial_stock_quantity

# Variable to store the last known real-time price
last_known_price = None

# Initialize global variables for historical data
timestamps_combined = []
prices_combined = []

# Function to update stock information and plot
def update_stock():
    global cash_balance, stock_quantity, last_known_price, timestamps_combined, prices_combined

    symbol = stock_entry.get()

    # Fetch real-time data
    url_real_time = f"https://cloud.iexapis.com/v1/stock/{symbol}/quote?token={api_key}"
    response_real_time = requests.get(url_real_time)

    if response_real_time.status_code == 200:
        # Parse the JSON data
        data_real_time = json.loads(response_real_time.text)

        # Extract real-time data
        real_time_price = data_real_time.get("latestPrice")

        if real_time_price is not None:
            # Log real-time data for debugging
            print(f"Real-time Data: {symbol} - {real_time_price}")

            # Initialize last_known_price if not set
            if last_known_price is None:
                last_known_price = real_time_price

            # Update the last known real-time price
            last_known_price = real_time_price

            # Update the plot only if real_time_price is not None
            current_timestamp = datetime.now(local_timezone).strftime('%H:%M')

            # Skip the update if real_time_price is None
            if real_time_price is not None:
                # Fill in missing values with the closest available value
                if timestamps_combined and prices_combined:
                    current_timestamp = datetime.strptime(current_timestamp, '%H:%M')

                    # Find the closest timestamp in the historical data
                    closest_timestamp = min(timestamps_combined, key=lambda x: abs(current_timestamp - datetime.strptime(x, '%H:%M')))

                    # Find the index of the closest timestamp
                    closest_index = timestamps_combined.index(closest_timestamp)

                    # Use the price corresponding to the closest timestamp as the value for the missing timestamp
                    timestamps_combined.append(current_timestamp.strftime('%H:%M'))
                    prices_combined.append(prices_combined[closest_index])

                else:
                    timestamps_combined.append(current_timestamp.strftime('%H:%M'))
                    prices_combined.append(real_time_price)

                # Remove None values from the data
                timestamps_combined = [t for t, p in zip(timestamps_combined, prices_combined) if p is not None]
                prices_combined = [p for p in prices_combined if p is not None]

                # Draw the plot explicitly after updating the data
                plt.clf()
                plt.plot(timestamps_combined, prices_combined, label='Stock Price', marker='o', linestyle='-', color='Yellow')
                plt.xlabel('Timestamp')
                plt.ylabel('Price ($)')
                plt.title(f'Real-time and Historical Stock Price for {symbol}')
                plt.legend()
                plt.grid(True, linestyle='--', alpha=0.7)
                plt.tight_layout()

                # Format timestamp labels for better readability
                plt.xticks(rotation=45, ha='right')

                # Display the real-time price on the plot
                plt.annotate(f'Real-time Price: ${real_time_price:.2f}', 
                             xy=(0.95, 0.05), 
                             xycoords='axes fraction', 
                             fontsize=8, 
                             ha='right', 
                             bbox=dict(boxstyle='round', alpha=0.1))

                plt.draw()
                plt.pause(0.001)  # Add a small pause to update the plot

                # Update balance label
                balance_label.config(text=f'Cash Balance: ${cash_balance:.2f}')

        else:
            # Log that latestPrice is None for debugging
            print("Latest price not available for the current timestamp. Ignoring this data point.")

        # Schedule the next update after 10 seconds
        root.after(10000, update_stock)

    else:
        print("Error fetching real-time data")

# Function to buy stocks
def buy_stock():
    global cash_balance, stock_quantity

    symbol = stock_entry.get()
    quantity = int(buy_entry.get())  # Get the quantity from the Entry widget

    # Fetch real-time data
    url_real_time = f"https://cloud.iexapis.com/v1/stock/{symbol}/quote?token={api_key}"
    response_real_time = requests.get(url_real_time)

    if response_real_time.status_code == 200:
        # Parse the JSON data
        data_real_time = json.loads(response_real_time.text)

        # Extract real-time data
        real_time_price = data_real_time.get("latestPrice")

        # Buy logic
        cost = real_time_price * quantity
        if cash_balance >= cost:
            cash_balance -= cost
            stock_quantity += quantity
            message = f"Bought {quantity} shares of {symbol} at ${real_time_price} each. Cash balance: ${cash_balance}"
            messagebox.showinfo("Buy Successful", message)

            # Update the plot and balance label
            update_stock()
        else:
            message = "Insufficient funds to buy"
            messagebox.showerror("Buy Error", message)

    else:
        print("Error fetching real-time data")

# Function to sell stocks
def sell_stock():
    global cash_balance, stock_quantity

    symbol = stock_entry.get()
    quantity = int(sell_entry.get())  # Get the quantity from the Entry widget

    # Fetch real-time data
    url_real_time = f"https://cloud.iexapis.com/v1/stock/{symbol}/quote?token={api_key}"
    response_real_time = requests.get(url_real_time)

    if response_real_time.status_code == 200:
        # Parse the JSON data
        data_real_time = json.loads(response_real_time.text)

        # Extract real-time data
        real_time_price = data_real_time.get("latestPrice")

        # Sell logic
        if stock_quantity >= quantity:
            cash_balance += real_time_price * quantity
            stock_quantity -= quantity
            message = f"Sold {quantity} shares of {symbol} at ${real_time_price} each. Cash balance: ${cash_balance}"
            messagebox.showinfo("Sell Successful", message)

            # Update the plot and balance label
            update_stock()
        else:
            message = "Not enough shares to sell"
            messagebox.showerror("Sell Error", message)

    else:
        print("Error fetching real-time data")

# Create the main application window
root = tk.Tk()
root.title("Stock Trading Simulator")

# Entry for stock name
stock_entry_label = ttk.Label(root, text="Stock Symbol:")
stock_entry_label.pack()

stock_entry = ttk.Entry(root)
stock_entry.pack()

# Entry for buy quantity
buy_label = ttk.Label(root, text="Quantity to Buy:")
buy_label.pack()

buy_entry = ttk.Entry(root)
buy_entry.pack()

# Entry for sell quantity
sell_label = ttk.Label(root, text="Quantity to Sell:")
sell_label.pack()

sell_entry = ttk.Entry(root)
sell_entry.pack()

# Buttons for actions
update_button = ttk.Button(root, text="Update", command=update_stock)
update_button.pack()

buy_button = ttk.Button(root, text="Buy", command=buy_stock)
buy_button.pack()

sell_button = ttk.Button(root, text="Sell", command=sell_stock)
sell_button.pack()

# Label for balance display
balance_label = ttk.Label(root, text=f'Cash Balance: ${cash_balance:.2f}')
balance_label.pack()

# Fetch historical data with 12 timestamps at 3-minute intervals
timestamps_historical = []
prices_historical = []

# Start from the current time in Cambodia time zone
local_timezone = pytz.timezone('Asia/Phnom_Penh')
current_time = datetime.now(local_timezone)

for i in range(12):
    timestamp = (current_time - timedelta(minutes=30 * i)).timestamp()
    timestamps_historical.append(timestamp)

url_historical = f"https://cloud.iexapis.com/v1/stock/AAPL/chart/1d?token={api_key}&chartInterval=3m"
response_historical = requests.get(url_historical)

if response_historical.status_code == 200:
    # Parse the JSON data
    data_historical = json.loads(response_historical.text)

    # Extract prices from historical data
    for entry in data_historical:
        prices_historical.append(entry["close"])

    # Initialize global variables for historical data
    timestamps_combined = [
        datetime.utcfromtimestamp(ts).replace(tzinfo=pytz.utc).astimezone(local_timezone).strftime('%H:%M')
        for ts in timestamps_historical[::-1]
    ]

    prices_combined = prices_historical[:12][::-1]

    # Function to exit the application
    def exit_app():
        root.destroy()

    # Button for exiting the application
    exit_button = ttk.Button(root, text="Exit", command=exit_app)
    exit_button.pack()

    # Run the application
    root.mainloop()
else:
    print("Error fetching historical data")









