import sys
import os
import subprocess
from datetime import datetime
from portfolio import Portfolio
from stock import get_stock_info, plot_stock_chart
import utils as ut
import time
import constants as ct

api_key = ct.api_key_polygon

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def open_new_terminal(mode=None):
    if "--mode" in sys.argv:
        return  # Prevent infinite loop
    
    terminal_command = ["python", __file__, "--mode"]
    if mode:
        terminal_command.append(mode)
    
    print(f"Running: {' '.join(terminal_command)}")  # Debugging line

    if sys.platform == "win32":
        subprocess.Popen(["cmd", "/c", "start", "cmd", "/k", " ".join(terminal_command)], shell=True)
    elif sys.platform == "darwin":
        script = f'tell application "Terminal" to do script "{" ".join(terminal_command)}"'
        subprocess.run(["osascript", "-e", script])
    elif sys.platform == "linux":
        subprocess.Popen(["gnome-terminal", "--", "python", __file__, "--mode", mode or ""])
    else:
        print("Unsupported platform. Cannot open a new terminal window.")
        return False
    return True


def search_mode():
    
    while True:
        command = input("main/search> ").strip().lower()
        if command == "cd ..":
            break
        elif command:
            try:
                stock_info = get_stock_info(command.upper())
                print(stock_info)
            except Exception as e:
                print(f"Error fetching stock info: {e}")

def portfolio_mode():
    print("Portfolio Mode - Type 'cd ..' to return to main.")
    portfolio = Portfolio(api_key)
    while True:
        command = input("/portfolio> ").strip().lower()
        if command == "cd ..":
            break
        elif command == "summary":
            portfolio.display_portfolio()
            print(f"Total Portfolio Value: {portfolio.get_portfolio_value():.2f}")
            print(f"Total Portfolio Change: {portfolio.get_portfolio_change():.2f}%")
            portfolio.plot_portfolio_value()

def add_stock_mode():
    print("Add Stock Mode - Format: <ticker> <shares> <YYYY-MM-DD> | Type 'cd ..' to return to main.")
    portfolio = Portfolio(api_key)
    while True:
        command = input("main/add_stock> ").strip().lower()
        if command == "cd ..":
            break
        try:
            ticker, shares, purchase_date = command.split()
            ticker = ticker.upper()
            shares = int(shares)
            purchase_date = datetime.strptime(purchase_date, "%Y-%m-%d")
            portfolio.add_stock(ticker, shares, purchase_date)
            print(f"Added {shares} shares of {ticker} purchased on {purchase_date.strftime('%Y-%m-%d')}.")
        except ValueError as e:
            print(f"Invalid input: {e}")
        except Exception as e:
            print(f"Error adding stock: {e}")

def main():
    print(f"Portfolio Management System - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Type 'help' for commands.")
    while True:
        print(f"\nCurrent Time: {datetime.now().strftime('%H:%M:%S')} | Date: {datetime.now().strftime('%Y-%m-%d')}")
        command = input("\nmain> ").strip().lower()
        
        if command in ["help", "\x08"]:  # ctrl+H
            print("""
Commands:
  portfolio      - Enter portfolio mode in new window
  add_stock      - Enter add stock mode in new window
  search         - Open search mode in new window
  view <ticker>  - View stock details and chart
  exit          - Exit the program
""")
        
        elif command == "portfolio":
            if open_new_terminal("portfolio"):
                continue
            portfolio_mode()  # Fallback if new window fails
        
        elif command == "add_stock":
            if open_new_terminal("add_stock"):
                continue
            add_stock_mode()  # Fallback if new window fails
        
        elif command == "search":
            if open_new_terminal("search"):
                continue
            search_mode()  # Fallback if new window fails
        
        elif command.startswith("view"):
            try:
                _, ticker = command.split()
                ticker = ticker.upper()
                stock_info = get_stock_info(ticker)
                print(stock_info)
                plot_stock_chart(ticker)
            except Exception as e:
                print(f"Error viewing stock: {e}")
        
        elif command == "exit":
            print("Exiting the program.")
            break
        
        else:
            print("Unknown command. Type 'help' for a list of commands.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--mode":
        mode = sys.argv[2] if len(sys.argv) > 2 else None
        if mode == "search":
            search_mode()
        elif mode == "portfolio":
            portfolio_mode()  # This will run in the new terminal
        elif mode == "add_stock":
            add_stock_mode()  # This will run in the new terminal
        else:
            main()  # Fallback to main if no valid mode is provided
    else:
        # Automatically open main in a new terminal window
        if open_new_terminal():
            sys.exit(0)  # Exit the current instance
        else:
            main()  # Fallback if new window fails