#hello everyone this is my banking system project
#I have used tkinter for GUI and json for data storage
#I have also used hashlib for password hashing and random for generating account numbers
#I have also used datetime for transaction logging
#I have also used os for file handling
#I have also used tkinter.messagebox for displaying messages

import tkinter as tk
from tkinter import messagebox
import json
import os
import random
import hashlib
from datetime import datetime

# File paths
ACCOUNTS_FILE = "accounts.json"
TRANSACTIONS_FILE = "transactions.json"

# ------------------- Utility Functions -------------------

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_account_number():
    return str(random.randint(100000, 999999))

def load_accounts():
    if os.path.exists(ACCOUNTS_FILE):
        with open(ACCOUNTS_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_accounts(data):
    with open(ACCOUNTS_FILE, 'w') as file:
        json.dump(data, file, indent=4)

def load_transactions():
    if os.path.exists(TRANSACTIONS_FILE):
        with open(TRANSACTIONS_FILE, 'r') as file:
            return json.load(file)
    return []

def save_transactions(data):
    with open(TRANSACTIONS_FILE, 'w') as file:
        json.dump(data, file, indent=4)

def log_transaction(account, t_type, amount):
    transactions = load_transactions()
    transactions.append({
        "account": account,
        "type": t_type,
        "amount": amount,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    save_transactions(transactions)

# ------------------- GUI Windows -------------------

def open_create_account_window():
    def create_account():
        name = name_entry.get()
        password = password_entry.get()
        try:
            initial_balance = float(deposit_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid deposit amount.")
            return

        if not name or not password:
            messagebox.showwarning("Missing Info", "Please fill out all fields.")
            return

        accounts = load_accounts()
        account_number = generate_account_number()
        while account_number in accounts:
            account_number = generate_account_number()

        accounts[account_number] = {
            "name": name,
            "password": hash_password(password),
            "balance": initial_balance
        }

        save_accounts(accounts)
        log_transaction(account_number, "Initial Deposit", initial_balance)
        messagebox.showinfo("Account Created", f"Your account number is: {account_number}")
        window.destroy()

    window = tk.Toplevel()
    window.title("Create Account")
    window.geometry("300x250")

    tk.Label(window, text="Name:").pack(pady=5)
    name_entry = tk.Entry(window)
    name_entry.pack()

    tk.Label(window, text="Initial Deposit:").pack(pady=5)
    deposit_entry = tk.Entry(window)
    deposit_entry.pack()

    tk.Label(window, text="Password:").pack(pady=5)
    password_entry = tk.Entry(window, show="*")
    password_entry.pack()

    tk.Button(window, text="Create Account", command=create_account).pack(pady=15)

def open_login_window():
    def login():
        acc_number = acc_entry.get()
        password = password_entry.get()
        accounts = load_accounts()

        if acc_number not in accounts:
            messagebox.showerror("Login Failed", "Account not found.")
            return
        if accounts[acc_number]['password'] != hash_password(password):
            messagebox.showerror("Login Failed", "Incorrect password.")
            return

        messagebox.showinfo("Login Successful", f"Welcome, {accounts[acc_number]['name']}!")
        window.destroy()
        open_dashboard(acc_number)

    window = tk.Toplevel()
    window.title("Login")
    window.geometry("300x200")

    tk.Label(window, text="Account Number:").pack(pady=5)
    acc_entry = tk.Entry(window)
    acc_entry.pack()

    tk.Label(window, text="Password:").pack(pady=5)
    password_entry = tk.Entry(window, show="*")
    password_entry.pack()

    tk.Button(window, text="Login", command=login).pack(pady=15)

def open_dashboard(account_number):
    window = tk.Toplevel()
    window.title("Dashboard")
    window.geometry("350x400")

    def refresh_balance():
        accounts = load_accounts()
        balance = accounts[account_number]["balance"]
        balance_var.set(f"₹{balance:.2f}")

    def deposit():
        try:
            amount = float(deposit_entry.get())
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Invalid deposit amount.")
            return

        accounts = load_accounts()
        accounts[account_number]['balance'] += amount
        save_accounts(accounts)
        log_transaction(account_number, "Deposit", amount)
        refresh_balance()
        deposit_entry.delete(0, tk.END)

    def withdraw():
        try:
            amount = float(withdraw_entry.get())
            accounts = load_accounts()
            if amount <= 0 or amount > accounts[account_number]['balance']:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Invalid amount or insufficient funds.")
            return

        accounts[account_number]['balance'] -= amount
        save_accounts(accounts)
        log_transaction(account_number, "Withdrawal", amount)
        refresh_balance()
        withdraw_entry.delete(0, tk.END)

    def view_transactions():
        transactions = load_transactions()
        user_transactions = [t for t in transactions if t["account"] == account_number]

        if not user_transactions:
            messagebox.showinfo("No Transactions", "No transactions found.")
            return

        txn_window = tk.Toplevel()
        txn_window.title("Transaction History")
        txn_window.geometry("400x300")

        for txn in user_transactions:
            info = f"{txn['date']} - {txn['type']} - ₹{txn['amount']:.2f}"
            tk.Label(txn_window, text=info).pack(anchor='w')

    # UI layout
    tk.Label(window, text=f"Account Number: {account_number}", font=("Helvetica", 12)).pack(pady=10)

    balance_var = tk.StringVar()
    refresh_balance()
    tk.Label(window, textvariable=balance_var, font=("Helvetica", 14)).pack(pady=5)

    tk.Label(window, text="Deposit Amount:").pack(pady=5)
    deposit_entry = tk.Entry(window)
    deposit_entry.pack()
    tk.Button(window, text="Deposit", command=deposit).pack(pady=5)

    tk.Label(window, text="Withdraw Amount:").pack(pady=5)
    withdraw_entry = tk.Entry(window)
    withdraw_entry.pack()
    tk.Button(window, text="Withdraw", command=withdraw).pack(pady=5)

    tk.Button(window, text="View Transactions", command=view_transactions).pack(pady=10)
    tk.Button(window, text="Logout", command=window.destroy).pack(pady=10)

# ------------------- Main Window -------------------

root = tk.Tk()
root.title("JSON Banking System")
root.geometry("300x250")

tk.Label(root, text="Welcome to Rich Bank", font=("Helvetica", 16)).pack(pady=20)

tk.Button(root, text="Create Account", command=open_create_account_window, width=20).pack(pady=5)
tk.Button(root, text="Login", command=open_login_window, width=20).pack(pady=5)
tk.Button(root, text="Exit", command=root.quit, width=20).pack(pady=5)

root.mainloop()
