"""Crossover operators for genetic algorithm."""

import numpy as np
from abc import ABC, abstractmethod
from typing import Tuple
from ..models import Chromosome, ProblemData


class CrossoverOperator(ABC):
    """Abstract base class for crossover operators.
    
    Follows OCP: Open for extension (new crossover types), closed for modification.
    """
    
    def __init__(self, problem_data: ProblemData):
        """Initialize with problem data.
        
        Args:
            problem_data: Problem instance data
        """
        self.data = problem_data
    
    @abstractmethod
    def crossover(self, parent1: Chromosome, parent2: Chromosome) -> Tuple[Chromosome, Chromosome]:
        """Perform crossover on two parents.
        
        Args:
            parent1: First parent chromosome
            parent2: Second parent chromosome
            
        Returns:
            Tuple of two offspring chromosomes
        """
        pass


class ParthenoProductionCrossover(CrossoverOperator):
    """Partheno crossover for production matrix.
    
    Swaps production values at two random positions for one product.
    """
    
    def crossover(self, parent1: Chromosome, parent2: Chromosome) -> Tuple[Chromosome, Chromosome]:
        """Perform partheno crossover on production matrices.
        
        Args:
            parent1: First parent
            parent2: Second parent
            
        Returns:
            Two offspring with crossed production
        """
        P1 = parent1.production.copy()
        P2 = parent2.production.copy()
        
        # Select random product and two time periods
        i = np.random.randint(0, self.data.num_products)
        t1 = np.random.randint(0, self.data.num_periods)
        t2 = np.random.randint(0, self.data.num_periods)
        
        # Swap values
        P1[i, t1], P2[i, t1] = P2[i, t1], P1[i, t1]
        P1[i, t2], P2[i, t2] = P2[i, t2], P1[i, t2]
        
        child1 = Chromosome(P1, parent1.workforce.copy())
        child2 = Chromosome(P2, parent2.workforce.copy())
        
        return child1, child2


class ArithmeticCrossover(CrossoverOperator):
    """Arithmetic crossover for both production and workforce.
    
    Creates offspring as weighted combinations of parents.
    """
    
    def crossover(self, parent1: Chromosome, parent2: Chromosome) -> Tuple[Chromosome, Chromosome]:
        """Perform arithmetic crossover.
        
        Args:
            parent1: First parent
            parent2: Second parent
            
        Returns:
            Two offspring as arithmetic combinations
        """
        alpha = np.random.rand()
        
        # Crossover production (flatten, combine, reshape)
        flat1 = parent1.production.flatten()
        flat2 = parent2.production.flatten()
        
        child1_flat = np.round(alpha * flat1 + (1 - alpha) * flat2).astype(int)
        child2_flat = np.round(alpha * flat2 + (1 - alpha) * flat1).astype(int)
        
        P1 = child1_flat.reshape(self.data.num_products, self.data.num_periods)
        P2 = child2_flat.reshape(self.data.num_products, self.data.num_periods)
        
        # Crossover workforce
        W1 = np.round(alpha * parent1.workforce + (1 - alpha) * parent2.workforce).astype(int)
        W2 = np.round(alpha * parent2.workforce + (1 - alpha) * parent1.workforce).astype(int)
        
        child1 = Chromosome(P1, W1)
        child2 = Chromosome(P2, W2)
        
        return child1, child2
