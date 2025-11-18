"""Solution container with chromosome and objectives."""

from dataclasses import dataclass
from typing import Tuple
from .chromosome import Chromosome


@dataclass
class Solution:
    """Represents a complete solution with chromosome and objective values.
    
    Follows SRP: Only responsible for bundling chromosome with its objectives.
    """
    
    chromosome: Chromosome
    objectives: Tuple[float, float]  # (Z1: cost, Z2: instability)
    
    @property
    def total_cost(self) -> float:
        """Get total cost objective (Z1)."""
        return self.objectives[0]
    
    @property
    def instability(self) -> float:
        """Get workforce instability objective (Z2)."""
        return self.objectives[1]
    
    def dominates(self, other: 'Solution') -> bool:
        """Check if this solution dominates another (minimization).
        
        Args:
            other: Another solution to compare
            
        Returns:
            True if this solution dominates the other
        """
        obj_a = self.objectives
        obj_b = other.objectives
        return ((obj_a[0] <= obj_b[0] and obj_a[1] <= obj_b[1]) and 
                (obj_a[0] < obj_b[0] or obj_a[1] < obj_b[1]))
    
    def __eq__(self, other: 'Solution') -> bool:
        """Check if two solutions are equal (same objectives and chromosome)."""
        if not isinstance(other, Solution):
            return False
        return (self.objectives == other.objectives and 
                self.chromosome == other.chromosome)
