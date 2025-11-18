"""Main entry point for running the LS-GA algorithm.

This script demonstrates the usage of the refactored OOP implementation
following SOLID principles and KISS methodology.
"""

from src.models import ProblemData
from src.algorithms import LSGAAlgorithm
from src.utils import ParetoPlotter, ResultsDisplay
from config import AlgorithmConfig


def main():
    """Run the LS-GA algorithm with default configuration."""
    
    print("="*80)
    print("Local Search Genetic Algorithm for Aggregate Production Planning")
    print("="*80)
    print()
    
    # Create problem data
    print("Loading problem data...")
    problem_data = ProblemData.create_default()
    print(f"Problem size: {problem_data.num_products} products, {problem_data.num_periods} periods")
    print()
    
    # Create configuration
    print("Initializing algorithm configuration...")
    config = AlgorithmConfig.create_default()
    print(f"Population size: {config.population_size}")
    print(f"Max generations: {config.max_generations}")
    print()
    
    # Create visualization callback
    plotter = ParetoPlotter()
    
    def progress_callback(generation: int, pareto_front):
        """Callback to visualize progress during evolution."""
        if config.plot_progress and (generation % config.plot_interval == 0 or 
                                     generation == 1 or 
                                     generation == config.max_generations):
            try:
                # Clear output in notebook environments
                from IPython.display import clear_output
                clear_output(wait=True)
            except ImportError:
                pass
            
            # Get algorithm instance to access history
            if hasattr(progress_callback, 'algorithm'):
                plotter.plot_evolution(
                    progress_callback.algorithm.pareto_history,
                    generation - 1
                )
    
    # Create and run algorithm
    print("Running LS-GA algorithm...")
    print("-"*80)
    
    algorithm = LSGAAlgorithm(problem_data, config, progress_callback)
    progress_callback.algorithm = algorithm  # Attach for callback access
    
    solutions, pareto_coords = algorithm.run()
    
    print("-"*80)
    print(f"\nAlgorithm completed successfully!")
    print()
    
    # Display results
    display = ResultsDisplay(problem_data)
    
    # Summary
    display.display_summary(solutions)
    
    # Plot final Pareto front
    print("\nGenerating final Pareto front plot...")
    plotter.plot_final_pareto(solutions)
    
    # Detailed results
    print("\nDisplaying detailed results for all solutions...")
    display.display_detailed(solutions)
    
    print("\n" + "="*80)
    print("END OF RESULTS")
    print("="*80)


if __name__ == "__main__":
    main()
