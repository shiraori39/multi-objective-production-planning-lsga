"""Selection operators for genetic algorithm."""

import random
from abc import ABC, abstractmethod
from typing import List
from ..models import Solution


class SelectionOperator(ABC):
    """Abstract base class for selection operators.
    
    Follows OCP: Open for extension, closed for modification.
    """
    
    @abstractmethod
    def select(self, population: List[Solution]) -> Solution:
        """Select one solution from population.
        
        Args:
            population: List of solutions to select from
            
        Returns:
            Selected solution
        """
        pass


class TournamentSelection(SelectionOperator):
    """Tournament selection with Pareto dominance.
    
    Selects between random candidates using dominance comparison.
    """
    
    def __init__(self, tournament_size: int = 2):
        """Initialize tournament selection.
        
        Args:
            tournament_size: Number of solutions in each tournament
        """
        self.tournament_size = tournament_size
    
    def select(self, population: List[Solution]) -> Solution:
        """Select solution via tournament.
        
        Args:
            population: List of solutions
            
        Returns:
            Winner of tournament
        """
        # Select random candidates
        candidates = random.sample(population, min(self.tournament_size, len(population)))
        
        if len(candidates) == 1:
            return candidates[0]
        
        # Compare using dominance
        sol_a = candidates[0]
        sol_b = candidates[1]
        
        if sol_a.dominates(sol_b):
            return sol_a
        elif sol_b.dominates(sol_a):
            return sol_b
        else:
            # Non-dominated: random choice
            return random.choice([sol_a, sol_b])
