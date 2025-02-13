# utils.py
import matplotlib.pyplot as plt


def plot_portfolio_value(dates, values):
    plt.figure(figsize=(12, 6))
    plt.plot(dates, values, 'b-', linewidth=2)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.title('Portfolio Value Over Time', fontsize=14)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Portfolio Value ($)', fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
