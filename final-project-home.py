import tkinter as tk
from PIL import Image, ImageTk
import bcrypt
import mysql.connector
from tkinter import ttk, messagebox
import requests
import json
import subprocess

# MySQL Database Functions
def create_database_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='login',
            user='root',
            password='root'
        )

        if connection.is_connected():
            print('Connected to MySQL database')
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        messagebox.showerror("Error", f"Failed to connect to the database: {err}")
        return None

def register_user(connection, username, password):
    try:
        cursor = connection.cursor()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
        connection.commit()
        messagebox.showinfo("Registration Successful", "User registered successfully")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        messagebox.showerror("Error", "Failed to register user. Please try again.")

def authenticate_user(connection, username, password, status_label):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user and bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
            status_label.config(text='Login successful', fg='green')
            show_main_window()
        else:
            status_label.config(text='Invalid username or password', fg='red')
    except mysql.connector.Error as err:
        print(f"Error: {err}")

def on_register_click(entry_username, entry_password, connection):
    username = entry_username.get()
    password = entry_password.get()

    if not username or not password:
        messagebox.showwarning("Input Error", "Please enter both username and password.")
    else:
        register_user(connection, username, password)

def on_login_click(entry_username, entry_password, connection, status_label):
    username = entry_username.get()
    password = entry_password.get()

    if not username or not password:
        messagebox.showwarning("Input Error", "Please enter both username and password.")
    else:
        authenticate_user(connection, username, password, status_label)

def fetch_news():
    url = "https://api.polygon.io/v2/reference/news?limit=10&order=descending&sort=published_utc&apiKey=EJH9GbtEAmDVeT9p9mCNhBVV0lm0G2K2"
    try:
        response = requests.get(url)
        news_data = json.loads(response.text)
        return news_data
    except Exception as e:
        messagebox.showerror("Error", "Failed to fetch news data")

def show_news():
    news_window = tk.Toplevel(root)
    news_window.title("News")
    news_window.geometry("800x400")

    canvas = tk.Canvas(news_window)
    scrollbar = ttk.Scrollbar(news_window, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    news_data = fetch_news()

    if news_data:
        for news in news_data['results']:
            title = news.get('title', 'No title available')
            description = news.get('description', 'No description available')
            publisher = news['publisher']['name']
            published_utc = news['published_utc']

            formatted_ratings = ""
            if 'ratings' in news:
                ratings = news['ratings']
                try:
                    lines = ratings.split('\n')
                    for line in lines:
                        formatted_ratings += f"{line.strip()}\n"
                except Exception as e:
                    formatted_ratings = f"Error processing ratings data: {str(e)}"
            else:
                formatted_ratings = "Ratings information not available."

            news_text = f"Title: {title}\n\nPublisher: {publisher}\n\nPublished at: {published_utc}\n\nDescription: {description}\n\nRatings:\n{formatted_ratings}\n\nURL: {news['article_url']}\n\n----\n"
            text = tk.Text(scrollable_frame, wrap='word', height=8, width=80)
            text.insert(tk.END, news_text)
            text.configure(state='disabled')
            text.pack()

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

def call_trade():
    try:
        result = subprocess.run(['python', 'trade.py'], capture_output=True, text=True, check=True)

        trade_result_window = tk.Toplevel(root)
        trade_result_window.title("Trade Result")
        trade_result_window.geometry("400x200")

        result_label = tk.Label(trade_result_window, text=result.stdout, font=("Helvetica", 12), fg='black')
        result_label.pack(pady=20)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Error calling trade.py: {e.stderr}")

def show_main_window():
    main_window = tk.Toplevel(root)
    main_window.title("Main Window")
    main_window.geometry("400x300")

    label_trade = tk.Label(main_window, text="Trade content goes here", font=("Helvetica", 12), fg='black')
    label_trade.pack(pady=20)

    button_trade = tk.Button(main_window, text="Trade", command=call_trade, font=("Helvetica", 12))
    button_trade.pack(pady=10)

    button_news = tk.Button(main_window, text="News", command=show_news, font=("Helvetica", 12))
    button_news.pack(pady=20)

# GUI setup
root = tk.Tk()
root.title("User Authentication")
root.geometry("400x300")

# Background Image
background_image = Image.open("rocket.png")
background_image = background_image.resize((400, 300), Image.LANCZOS)
background_photo = ImageTk.PhotoImage(background_image)

background_label = tk.Label(root, image=background_photo)
background_label.place(relwidth=1, relheight=1)

# Title Label
title_font = ("Helvetica", 20)
title_label = tk.Label(root, text="User Authentication", font=title_font, fg='black')
title_label.place(relx=0.5, rely=0.1, anchor=tk.CENTER)

# Username Label and Entry
label_font = ("Helvetica", 12)
label_username = tk.Label(root, text="Username", font=label_font, fg='black', highlightthickness=0)
label_username.place(relx=0.2, rely=0.3, anchor=tk.W)
entry_username = tk.Entry(root, font=label_font)
entry_username.place(relx=0.5, rely=0.3, anchor=tk.W)

# Password Label and Entry
label_password = tk.Label(root, text="Password", font=label_font, fg='black', highlightthickness=0)
label_password.place(relx=0.2, rely=0.4, anchor=tk.W)
entry_password = tk.Entry(root, show="*", font=label_font)
entry_password.place(relx=0.5, rely=0.4, anchor=tk.W)

# Status Label
status_label = tk.Label(root, text='', font=label_font, fg='red')
status_label.place(relx=0.5, rely=0.7, anchor=tk.CENTER)

# MySQL Database Connection
db_connection = create_database_connection()

# Register Button
register_button = tk.Button(root, text="Register", command=lambda: on_register_click(entry_username, entry_password, db_connection), font=label_font)
register_button.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

# Login Button
login_button = tk.Button(root, text="Login", command=lambda: on_login_click(entry_username, entry_password, db_connection, status_label), font=label_font)
login_button.place(relx=0.5, rely=0.6, anchor=tk.CENTER)

root.mainloop()
