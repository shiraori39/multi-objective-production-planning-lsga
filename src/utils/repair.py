"""Constraint repair mechanism for chromosomes."""

import numpy as np
from ..models import Chromosome, ProblemData


class ConstraintRepair:
    """Repairs chromosomes to satisfy all constraints.
    
    Follows SRP: Only responsible for constraint enforcement.
    """
    
    def __init__(self, problem_data: ProblemData):
        """Initialize with problem data.
        
        Args:
            problem_data: Problem instance data
        """
        self.data = problem_data
    
    def repair(self, chromosome: Chromosome) -> Chromosome:
        """Ensure chromosome respects all constraints.
        
        Args:
            chromosome: Chromosome to repair
            
        Returns:
            Repaired chromosome
        """
        P = chromosome.production.copy()
        W = chromosome.workforce.copy()
        
        # Repair production constraints
        P = self._repair_production_bounds(P)
        P = self._repair_inventory_constraints(P)
        
        # Repair workforce constraints
        W = self._repair_workforce_bounds(W)
        
        return Chromosome(P, W)
    
    def _repair_production_bounds(self, P: np.ndarray) -> np.ndarray:
        """Ensure production is within [0, capacity]."""
        for i in range(self.data.num_products):
            for t in range(self.data.num_periods):
                if P[i, t] < 0:
                    P[i, t] = 0
                if P[i, t] > self.data.production_capacity[i, t]:
                    P[i, t] = int(self.data.production_capacity[i, t])
        return P
    
    def _repair_inventory_constraints(self, P: np.ndarray) -> np.ndarray:
        """Adjust production to respect inventory capacity and demand."""
        inv = np.zeros(self.data.num_products, dtype=int)
        
        for t in range(self.data.num_periods):
            for i in range(self.data.num_products):
                inv[i] += P[i, t] - self.data.demand[i, t]
                
                # Handle excess inventory
                if inv[i] > self.data.inventory_capacity[i]:
                    excess = inv[i] - self.data.inventory_capacity[i]
                    reduction = min(excess, P[i, t])
                    P[i, t] -= reduction
                    inv[i] -= reduction
                
                # Handle backlog
                if inv[i] < 0:
                    need = -inv[i]
                    available = self.data.production_capacity[i, t] - P[i, t]
                    addition = min(need, available)
                    P[i, t] += addition
                    inv[i] += addition
        
        return P
    
    def _repair_workforce_bounds(self, W: np.ndarray) -> np.ndarray:
        """Ensure workforce is within [min, max] bounds."""
        return np.clip(W, self.data.min_workers, self.data.max_workers)
