"""Mutation operators for genetic algorithm."""

import numpy as np
from abc import ABC, abstractmethod
from ..models import Chromosome, ProblemData


class MutationOperator(ABC):
    """Abstract base class for mutation operators.
    
    Follows OCP: Open for extension, closed for modification.
    """
    
    def __init__(self, problem_data: ProblemData):
        """Initialize with problem data.
        
        Args:
            problem_data: Problem instance data
        """
        self.data = problem_data
    
    @abstractmethod
    def mutate(self, chromosome: Chromosome) -> Chromosome:
        """Perform mutation on a chromosome.
        
        Args:
            chromosome: Chromosome to mutate
            
        Returns:
            Mutated chromosome
        """
        pass


class ProductionMutation(MutationOperator):
    """Mutation operator for production matrix.
    
    Randomly changes production value at one position.
    """
    
    def mutate(self, chromosome: Chromosome) -> Chromosome:
        """Mutate production matrix at random position.
        
        Args:
            chromosome: Chromosome to mutate
            
        Returns:
            Mutated chromosome
        """
        P = chromosome.production.copy()
        
        # Select random product and period
        i = np.random.randint(0, self.data.num_products)
        t = np.random.randint(0, self.data.num_periods)
        
        # Mutate to random value within capacity
        low = 0
        high = self.data.production_capacity[i, t]
        
        if low < high:
            P[i, t] = np.random.randint(low, high + 1)
        
        return Chromosome(P, chromosome.workforce.copy())


class WorkforceMutation(MutationOperator):
    """Mutation operator for workforce vector.
    
    Randomly changes workforce at one period.
    """
    
    def mutate(self, chromosome: Chromosome) -> Chromosome:
        """Mutate workforce at random period.
        
        Args:
            chromosome: Chromosome to mutate
            
        Returns:
            Mutated chromosome
        """
        W = chromosome.workforce.copy()
        
        # Select random period
        t = np.random.randint(0, self.data.num_periods)
        
        # Mutate to random workforce value
        W[t] = np.random.randint(self.data.min_workers, self.data.max_workers + 1)
        
        return Chromosome(chromosome.production.copy(), W)
