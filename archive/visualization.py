import seaborn as sns
import matplotlib.pyplot as plt



def plot_snake_value(position_counts):
    print("Position Counts Data:", position_counts)  # Add this line
    plt.figure(figsize=(10, 6))
    sns.barplot(x='Owner', y='counts', hue='position', data=position_counts)
    plt.title('Number of Times Each Position Was Picked in the First Round by Each Manager')
    plt.xlabel('Manager')
    plt.ylabel('Count')
    plt.show()

def plot_auction_value(position_values):
    print("Position Values Data:", position_values)  # Add this line
    plt.figure(figsize=(10, 6))
    sns.barplot(x='Owner', y='total_value', hue='position', data=position_values)
    plt.title('Total Draft Value Spent on Each Position by Each Manager')
    plt.xlabel('Manager')
    plt.ylabel('Total Draft Value')
    plt.show()



