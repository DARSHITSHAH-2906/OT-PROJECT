import os
import sys
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import ast  # This is crucial for reading the list/tuple strings from the CSV

# --- Fix ModuleNotFoundError ---
# Add the parent directory (OT-MINI-PROJECT) to the Python path
# This allows us to import from 'nsga_vrp'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nsga_vrp.NSGA2_vrp import load_instance, routeToSubroute, eval_indvidual_fitness


# Loading locations and customers to dataframe
def getCoordinatesDframe(json_instance):
  num_of_cust = json_instance['Number_of_customers']
  # Getting all customer coordinates
  customer_list = [i for i in range(1, num_of_cust + 1)]
  x_coord_cust = [json_instance[f'customer_{i}']['coordinates']['x'] for i in customer_list]
  y_coord_cust = [json_instance[f'customer_{i}']['coordinates']['y'] for i in customer_list]
  # Getting depot x,y coordinates
  depot_x = [json_instance['depart']['coordinates']['x']]
  depot_y = [json_instance['depart']['coordinates']['y']]
  # Adding depot details
  customer_list = [0] + customer_list
  x_coord_cust = depot_x + x_coord_cust
  y_coord_cust = depot_y + y_coord_cust
  df = pd.DataFrame({"X": x_coord_cust, "Y": y_coord_cust, "customer_list": customer_list })
  return df


def plotSubroute(subroute, dfhere, color):
  totalSubroute = [0] + subroute + [0]
  subroutelen = len(subroute)
  for i in range(subroutelen + 1):
    firstcust = totalSubroute[0]
    secondcust = totalSubroute[1]
    plt.plot([dfhere.X[firstcust], dfhere.X[secondcust]],
         [dfhere.Y[firstcust], dfhere.Y[secondcust]], c=color)
    totalSubroute.pop(0)


def plotRoute(route, csv_title):
  # Loading the instance
  json_instance = load_instance('./data/json/Input_Data.json')

  subroutes = routeToSubroute(route, json_instance)
    # Added more colors in case of many vehicles
  colorslist = ["blue", "green", "red", "cyan", "magenta", "yellow", "black", "purple", "orange", "brown"]
  colorindex = 0

  # getting df
  dfhere = getCoordinatesDframe(json_instance)

  # Plotting scatter
  plt.figure(figsize=(10, 10))

  for i in range(dfhere.shape[0]):
    if i == 0:
      plt.scatter(dfhere.X[i], dfhere.Y[i], c='green', s=200, zorder=10) # Made depot green
      plt.text(dfhere.X[i], dfhere.Y[i], "depot", fontsize=12)
    else:
      plt.scatter(dfhere.X[i], dfhere.Y[i], c='orange', s=200, zorder=10) # Made customers orange
      plt.text(dfhere.X[i], dfhere.Y[i], f'{i}', fontsize=12)

  # Plotting routes
  for sub_route in subroutes:
    plotSubroute(sub_route, dfhere, color=colorslist[colorindex % len(colorslist)])
    colorindex += 1

  # Plotting is done, adding labels, Title
  plt.xlabel("X - Coordinate")
  plt.ylabel("Y - Coordinate")
  plt.title(csv_title)
    
    # Save the figure to the 'figures' directory (make sure it exists!)
    # Create figures directory if it doesn't exist
  if not os.path.exists('./figures'):
        os.makedirs('./figures')
        
  plt.savefig(f"./figures/Route_{csv_title}.png")
  print(f"Saved route plot to: ./figures/Route_{csv_title}.png")


# --- NEW FUNCTION TO PLOT COST COMPARISON ---
def plot_cost_comparison(nsga2_df, nsga3_df, title):
    """
    Plots the 'best cost' from the fitness tuple over generations
    for both algorithms.
    """
    plt.figure(figsize=(12, 7))

    # --- Process NSGA-II Data ---
    # 1. Get 'Generation' column
    generations = nsga2_df['Generation']
    # 2. Convert fitness string '(vehicles, cost)' to a real tuple
    fitness_tuples_2 = nsga2_df['fitness_best_one'].apply(ast.literal_eval)
    # 3. Extract just the cost (the 2nd item, index 1)
    cost_nsga2 = pd.DataFrame(fitness_tuples_2.tolist()).iloc[:, 1]

    # --- Process NSGA-III Data ---
    # 1. Convert fitness string '(vehicles, cost)' to a real tuple
    fitness_tuples_3 = nsga3_df['fitness_best_one'].apply(ast.literal_eval)
    # 2. Extract just the cost (the 2nd item, index 1)
    cost_nsga3 = pd.DataFrame(fitness_tuples_3.tolist()).iloc[:, 1]

    # --- Plot the data ---
    plt.plot(generations, cost_nsga2, label="NSGA-II Best Cost")
    plt.plot(generations, cost_nsga3, label="NSGA-III Best Cost")

    plt.xlabel("Generation")
    plt.ylabel("Total Cost")
    plt.title(title)
    plt.legend()
    plt.grid(True)
    
    plt.savefig(f"./figures/{title}.png")
    print(f"Saved comparison plot to: ./figures/{title}.png")


# --- NEW MAIN BLOCK TO READ CSVs AND PLOT ---
if __name__ == "__main__":
    
    # --- IMPORTANT: Match these parameters to your runAlgo.py command ---
    INSTANCE_NAME = "Input_Data" # from './data/json/Input_Data.json'
    POP_SIZE = 400
    CROSS_PROB = 0.85
    MUT_PROB = 0.02
    NUM_GEN = 200
    # ---
    
    # Define file paths
    base_filename = f"{INSTANCE_NAME}_pop{POP_SIZE}_crossProb{CROSS_PROB}_mutProb{MUT_PROB}_numGen{NUM_GEN}"
    nsga2_csv = f"./results/{INSTANCE_NAME}_NSGA2_pop{POP_SIZE}_crossProb{CROSS_PROB}_mutProb{MUT_PROB}_numGen{NUM_GEN}.csv"
    nsga3_csv = f"./results/{INSTANCE_NAME}_NSGA3_pop{POP_SIZE}_crossProb{CROSS_PROB}_mutProb{MUT_PROB}_numGen{NUM_GEN}.csv"

    try:
        # Load the CSV files
        df_nsga2 = pd.read_csv(nsga2_csv)
        df_nsga3 = pd.read_csv(nsga3_csv)

        print("Successfully loaded CSV files. Generating plots...")

        # --- 1. Plot Cost Comparison ---
        plot_title = f"Cost Convergence (Pop {POP_SIZE}, Gen {NUM_GEN})"
        plot_cost_comparison(df_nsga2, df_nsga3, plot_title)

        # --- 2. Plot NSGA-II Best Route ---
        last_row_2 = df_nsga2.iloc[-1]
        best_route_2 = ast.literal_eval(last_row_2['best_one'])
        fitness_2 = ast.literal_eval(last_row_2['fitness_best_one'])
        title_2 = f"NSGA-II Best Route - Vehicles - {fitness_2[0]}, Cost - {fitness_2[1]:.2f}"
        plotRoute(best_route_2, title_2)

        # --- 3. Plot NSGA-III Best Route ---
        last_row_3 = df_nsga3.iloc[-1]
        best_route_3 = ast.literal_eval(last_row_3['best_one'])
        fitness_3 = ast.literal_eval(last_row_3['fitness_best_one'])
        title_3 = f"NSGA-III Best Route - Vehicles - {fitness_3[0]}, Cost - {fitness_3[1]:.2f}"
        plotRoute(best_route_3, title_3)
        
        print("\nAll plots generated. Showing results...")
        plt.show() # Show all plots at the end

    except FileNotFoundError as e:
        print(f"--- ERROR: Could not find result file! ---")
        print(f"Tried to find: {e.filename}")
        print("Please check the parameters at the top of the 'if __name__ == \"__main__\"' block in this script.")
        print("They MUST match the parameters you used with runAlgo.py")