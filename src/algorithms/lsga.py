"""Main LS-GA algorithm orchestrator."""

import random
import numpy as np
from typing import List, Tuple, Optional, Callable
from ..models import Chromosome, ProblemData, Solution
from ..operators import (
    ParthenoProductionCrossover, ArithmeticCrossover,
    ProductionMutation, WorkforceMutation,
    TournamentSelection,
    ProductionLocalSearch, WorkforceLocalSearch
)
from ..utils import ObjectiveEvaluator, ConstraintRepair, PopulationInitializer
from .nsga2 import NSGA2Selector, ParetoArchive
from ...config import AlgorithmConfig


class LSGAAlgorithm:
    """Main Local Search Genetic Algorithm orchestrator.
    
    Follows DIP: Depends on abstractions (operators), not concrete implementations.
    Follows SRP: Only responsible for coordinating the algorithm flow.
    """
    
    def __init__(
        self,
        problem_data: ProblemData,
        config: AlgorithmConfig,
        progress_callback: Optional[Callable[[int, List[Tuple[float, float]]], None]] = None
    ):
        """Initialize LS-GA algorithm.
        
        Args:
            problem_data: Problem instance data
            config: Algorithm configuration
            progress_callback: Optional callback for progress updates
        """
        self.data = problem_data
        self.config = config
        self.progress_callback = progress_callback
        
        # Set random seeds
        random.seed(config.random_seed)
        np.random.seed(config.random_seed)
        
        # Initialize components (Dependency Injection)
        self.evaluator = ObjectiveEvaluator(problem_data)
        self.repair = ConstraintRepair(problem_data)
        self.initializer = PopulationInitializer(problem_data, self.repair)
        
        # Genetic operators
        self.partheno_crossover = ParthenoProductionCrossover(problem_data)
        self.arithmetic_crossover = ArithmeticCrossover(problem_data)
        self.production_mutation = ProductionMutation(problem_data)
        self.workforce_mutation = WorkforceMutation(problem_data)
        self.selection = TournamentSelection(config.tournament_size)
        
        # Local search operators
        self.production_ls = ProductionLocalSearch(
            problem_data, self.evaluator, config.production_ls_attempts
        )
        self.workforce_ls = WorkforceLocalSearch(
            problem_data, self.evaluator, config.workforce_ls_neighborhood
        )
        
        # NSGA-II and archive
        self.nsga2_selector = NSGA2Selector()
        self.archive = ParetoArchive()
        
        # History tracking
        self.pareto_history: List[List[Tuple[float, float]]] = []
    
    def run(self) -> Tuple[List[Solution], List[Tuple[float, float]]]:
        """Run the LS-GA algorithm.
        
        Returns:
            Tuple of (archive solutions, pareto front coordinates)
        """
        # Initialize population
        chromosomes = self.initializer.initialize(self.config.population_size)
        population = [self.evaluator.create_solution(ch) for ch in chromosomes]
        
        # Main evolution loop
        for generation in range(1, self.config.max_generations + 1):
            # Generate offspring
            offspring_chromosomes = self._reproduce(population)
            
            # Apply local search
            refined_chromosomes = self._apply_local_search(offspring_chromosomes)
            
            # Evaluate offspring
            offspring = [self.evaluator.create_solution(ch) for ch in refined_chromosomes]
            
            # Combine and select
            combined = population + offspring
            population = self.nsga2_selector.select(combined, self.config.population_size)
            
            # Update archive
            self._update_archive(combined)
            
            # Track history
            pareto_front = self._extract_pareto_front(combined)
            self.pareto_history.append(pareto_front)
            
            # Progress reporting
            if generation % self.config.plot_interval == 0 or generation == 1 or generation == self.config.max_generations:
                self._report_progress(generation, pareto_front)
        
        # Return results
        archive_solutions = self.archive.get_sorted()
        pareto_coords = [(sol.total_cost, sol.instability) for sol in archive_solutions]
        
        return archive_solutions, pareto_coords
    
    def _reproduce(self, population: List[Solution]) -> List[Chromosome]:
        """Generate offspring through selection, crossover, and mutation.
        
        Args:
            population: Current population
            
        Returns:
            List of offspring chromosomes
        """
        offspring = []
        
        while len(offspring) < self.config.population_size:
            # Select parents
            parent1 = self.selection.select(population)
            parent2 = self.selection.select(population)
            
            child1 = parent1.chromosome.copy()
            child2 = parent2.chromosome.copy()
            
            # Apply crossover
            if random.random() < self.config.partheno_crossover_prob:
                child1, child2 = self.partheno_crossover.crossover(
                    parent1.chromosome, parent2.chromosome
                )
            
            if random.random() < self.config.arithmetic_crossover_prob:
                child1, child2 = self.arithmetic_crossover.crossover(
                    parent1.chromosome, parent2.chromosome
                )
            
            # Apply mutation
            if random.random() < self.config.production_mutation_prob:
                child1 = self.production_mutation.mutate(child1)
            if random.random() < self.config.production_mutation_prob:
                child2 = self.production_mutation.mutate(child2)
            
            if random.random() < self.config.workforce_mutation_prob:
                child1 = self.workforce_mutation.mutate(child1)
            if random.random() < self.config.workforce_mutation_prob:
                child2 = self.workforce_mutation.mutate(child2)
            
            # Repair
            child1 = self.repair.repair(child1)
            child2 = self.repair.repair(child2)
            
            offspring.append(child1)
            if len(offspring) < self.config.population_size:
                offspring.append(child2)
        
        return offspring
    
    def _apply_local_search(self, chromosomes: List[Chromosome]) -> List[Chromosome]:
        """Apply local search to chromosomes.
        
        Args:
            chromosomes: Chromosomes to improve
            
        Returns:
            Improved chromosomes
        """
        refined = []
        for ch in chromosomes:
            # Production local search
            ch = self.production_ls.improve(ch)
            # Workforce local search
            ch = self.workforce_ls.improve(ch)
            refined.append(ch)
        return refined
    
    def _update_archive(self, population: List[Solution]):
        """Update Pareto archive with non-dominated solutions.
        
        Args:
            population: Population to check for archive updates
        """
        # Get non-dominated front
        fronts = self.nsga2_selector._nondominated_sort(population)
        if fronts:
            for solution in fronts[0]:  # First front is non-dominated
                self.archive.update(solution)
    
    def _extract_pareto_front(self, population: List[Solution]) -> List[Tuple[float, float]]:
        """Extract Pareto front coordinates from population.
        
        Args:
            population: Population to extract from
            
        Returns:
            List of (Z1, Z2) tuples
        """
        fronts = self.nsga2_selector._nondominated_sort(population)
        if fronts:
            return [(sol.total_cost, sol.instability) for sol in fronts[0]]
        return []
    
    def _report_progress(self, generation: int, pareto_front: List[Tuple[float, float]]):
        """Report progress for current generation.
        
        Args:
            generation: Current generation number
            pareto_front: Current Pareto front
        """
        # Print statistics
        if pareto_front:
            best_solutions = sorted(pareto_front, key=lambda x: x[0])[:3]
            print(f"Gen {generation:4d}: Best 3 by Z1: {best_solutions}")
        
        # Call progress callback if provided
        if self.progress_callback:
            self.progress_callback(generation, pareto_front)
