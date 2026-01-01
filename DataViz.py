from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import pandas as pd
import os
print(os.getcwd())
# Change working directory and load data
os.chdir("Data Scraping")
path = "cricket_data.csv"
print(os.getcwd())
# Load and preprocess data
data = pd.read_csv(path)
data['Start Date'] = pd.to_datetime(data['Start Date'])
data = data.sort_values(by='Start Date')

# Create a new column 'Century #' for cumulative centuries
data['Century #'] = data.groupby('Player').cumcount() + 1

# Select the top 20 players based on century counts
player_counts = data['Player'].value_counts()
player_names = player_counts.head(20).index.tolist()

# Filter data for the selected players and sort by date
new_data = data[data['Player'].isin(player_names)]
new_data = new_data.sort_values(by='Start Date')

# Define the animation function
def animate(i):
    plt.cla()  # Clear the axes
    for k in player_names:
        # Filter player data and plot their step function
        player_data = new_data[new_data['Player'] == k]
        plt.step(player_data['Start Date'][:i], player_data['Century #'][:i], label=k, where='mid')
    
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.xticks(rotation=45)
    plt.xlabel('Year')
    plt.ylabel('Century #')
    plt.title('Top 20 ODI Centurions')

# Create the figure and initialize the animation
fig, ax = plt.subplots()
ani = FuncAnimation(fig, animate, frames=400, interval=200)

try:
    plt.tight_layout()
    plt.subplots_adjust(left=0.1, right=0.70, bottom=0.2, top=0.9)
    ani.save('odi centurions.gif', writer='pillow', fps=10)  # Save animation as GIF
    print("GIF saved successfully.")
except Exception as e:
    print(f"Error saving GIF: {e}")

plt.show()
