"""Population initialization for genetic algorithm."""

import numpy as np
from typing import List
from ..models import Chromosome, ProblemData
from .repair import ConstraintRepair


class PopulationInitializer:
    """Initializes population with feasible chromosomes.
    
    Follows SRP: Only responsible for population initialization.
    """
    
    def __init__(self, problem_data: ProblemData, repair: ConstraintRepair):
        """Initialize with problem data and repair mechanism.
        
        Args:
            problem_data: Problem instance data
            repair: Constraint repair mechanism
        """
        self.data = problem_data
        self.repair = repair
    
    def initialize(self, population_size: int) -> List[Chromosome]:
        """Create initial population.
        
        Args:
            population_size: Number of chromosomes to create
            
        Returns:
            List of initialized chromosomes
        """
        population = []
        for _ in range(population_size):
            chromosome = self._create_random_chromosome()
            chromosome = self.repair.repair(chromosome)
            population.append(chromosome)
        return population
    
    def _create_random_chromosome(self) -> Chromosome:
        """Create a single random chromosome."""
        P = self._create_random_production()
        W = self._create_random_workforce()
        return Chromosome(P, W)
    
    def _create_random_workforce(self) -> np.ndarray:
        """Generate random valid workforce vector."""
        return np.random.randint(
            self.data.min_workers,
            self.data.max_workers + 1,
            size=self.data.num_periods
        )
    
    def _create_random_production(self) -> np.ndarray:
        """Generate random production trying to meet demand."""
        P = np.zeros((self.data.num_products, self.data.num_periods), dtype=int)
        inv = np.zeros(self.data.num_products, dtype=int)
        
        for t in range(self.data.num_periods):
            for i in range(self.data.num_products):
                # Try to meet demand
                need = max(0, self.data.demand[i, t] - inv[i])
                cap = self.data.production_capacity[i, t]
                
                if need > cap:
                    p = cap
                else:
                    p = np.random.randint(need, cap + 1)
                
                P[i, t] = p
                inv[i] = inv[i] + p - self.data.demand[i, t]
                
                # Reduce if exceeds inventory capacity
                if inv[i] > self.data.inventory_capacity[i]:
                    excess = inv[i] - self.data.inventory_capacity[i]
                    reduce_by = min(excess, P[i, t] - need)
                    P[i, t] -= reduce_by
                    inv[i] -= reduce_by
        
        return P
