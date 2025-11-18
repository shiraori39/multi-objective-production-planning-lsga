"""Chromosome representation for production planning."""

import numpy as np
from copy import deepcopy
from typing import Dict


class Chromosome:
    """Represents a solution chromosome with production and workforce decisions.
    
    Follows SRP: Only responsible for holding and copying chromosome data.
    """
    
    def __init__(self, production: np.ndarray, workforce: np.ndarray):
        """Initialize chromosome.
        
        Args:
            production: Production matrix (products × periods)
            workforce: Workforce vector (workers per period)
        """
        self.production = production.copy()
        self.workforce = workforce.copy()
    
    @property
    def P(self) -> np.ndarray:
        """Alias for production matrix."""
        return self.production
    
    @property
    def W(self) -> np.ndarray:
        """Alias for workforce vector."""
        return self.workforce
    
    def copy(self) -> 'Chromosome':
        """Create a deep copy of the chromosome."""
        return Chromosome(self.production.copy(), self.workforce.copy())
    
    def to_dict(self) -> Dict[str, np.ndarray]:
        """Convert to dictionary format for backward compatibility."""
        return {'P': self.production, 'W': self.workforce}
    
    @classmethod
    def from_dict(cls, data: Dict[str, np.ndarray]) -> 'Chromosome':
        """Create chromosome from dictionary format."""
        return cls(data['P'], data['W'])
    
    def __eq__(self, other: 'Chromosome') -> bool:
        """Check if two chromosomes are equal."""
        if not isinstance(other, Chromosome):
            return False
        return (np.array_equal(self.production, other.production) and 
                np.array_equal(self.workforce, other.workforce))
