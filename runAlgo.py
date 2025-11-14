from nsga_vrp.NSGA2_vrp import nsgaAlgo, nsga3Algo, load_instance # Keep explicit imports
import argparse

def main():
    # --- Define ALL command-line arguments ---
    parser = argparse.ArgumentParser(description="Run NSGA-II or NSGA-III for CVRP.")
    
    parser.add_argument('--algorithm', type=str, default="NSGA2", 
                        choices=['NSGA2', 'NSGA3'], required=False,
                        help="Algorithm to run (NSGA2 or NSGA3)")
    
    parser.add_argument('--instance_name', type=str, default="./data/json/Input_Data.json", 
                        required=False, help="Enter the input Json file name")
    
    parser.add_argument('--popSize', type=int, default=400, 
                        required=False, help="Enter the population size")
                        
    parser.add_argument('--crossProb', type=float, default=0.85, 
                        required=False, help="Crossover Probability")
                        
    parser.add_argument('--mutProb', type=float, default=0.02, 
                        required=False, help="Mutation Probabilty")
                        
    parser.add_argument('--numGen', type=int, default=200, 
                        required=False, help="Number of generations to run")
    
    parser.add_argument('--refPointsP', type=int, default=99, 
                        required=False, help="Divisions for NSGA3 reference points (p)")
    
    # --- End of arguments ---

    args = parser.parse_args()

    # --- This is now much cleaner ---
    nsgaObj = None
    
    # Pack common arguments into a dictionary
    common_args = {
        "instance_path": args.instance_name,
        "pop_size": args.popSize,
        "cross_prob": args.crossProb,
        "mut_prob": args.mutProb,
        "num_gen": args.numGen
    }

    if args.algorithm == 'NSGA2':
        print(f"Initializing {args.algorithm} Algorithm...")
        nsgaObj = nsgaAlgo(**common_args)
        
    elif args.algorithm == 'NSGA3':
        # print(f"Initializing {args.im_projectlAlgorithm} Algorithm...")
        # Pass both common args and the specific arg
        nsgaObj = nsga3Algo(ref_points_p=args.refPointsP, **common_args)
    
    if nsgaObj is None:
        print(f"Error: Unknown algorithm '{args.algorithm}'")
        return

    # Running Algorithm - No setup needed!
    print(f"Running {args.algorithm} for {args.numGen} generations...")
    nsgaObj.runMain()
    print(f"\n{args.algorithm} execution finished.")
    print(f"Results saved to the '{nsgaObj.algorithm_name}' CSV file.")


if __name__ == '__main__':
    main()