"""Local search operators for solution improvement."""

import numpy as np
from abc import ABC, abstractmethod
from copy import deepcopy
from ..models import Chromosome, ProblemData
from ..utils import ObjectiveEvaluator


class LocalSearchOperator(ABC):
    """Abstract base class for local search operators.
    
    Follows OCP: Open for extension, closed for modification.
    """
    
    def __init__(self, problem_data: ProblemData, evaluator: ObjectiveEvaluator):
        """Initialize with problem data and evaluator.
        
        Args:
            problem_data: Problem instance data
            evaluator: Objective evaluator
        """
        self.data = problem_data
        self.evaluator = evaluator
    
    @abstractmethod
    def improve(self, chromosome: Chromosome) -> Chromosome:
        """Attempt to improve chromosome through local search.
        
        Args:
            chromosome: Chromosome to improve
            
        Returns:
            Improved (or original) chromosome
        """
        pass


class ProductionLocalSearch(LocalSearchOperator):
    """Local search for production matrix optimization.
    
    Attempts to reduce cost by shifting production between periods.
    """
    
    def __init__(self, problem_data: ProblemData, evaluator: ObjectiveEvaluator, attempts: int = 10):
        """Initialize production local search.
        
        Args:
            problem_data: Problem instance data
            evaluator: Objective evaluator
            attempts: Number of improvement attempts
        """
        super().__init__(problem_data, evaluator)
        self.attempts = attempts
    
    def improve(self, chromosome: Chromosome) -> Chromosome:
        """Improve production by shifting between periods.
        
        Args:
            chromosome: Chromosome to improve
            
        Returns:
            Improved chromosome
        """
        best = chromosome.copy()
        best_cost = self.evaluator.cost_evaluator.evaluate(best)
        
        for _ in range(self.attempts):
            # Select random product and two periods
            i = np.random.randint(0, self.data.num_products)
            t1 = np.random.randint(0, self.data.num_periods)
            t2 = np.random.randint(0, self.data.num_periods)
            
            if t1 == t2:
                continue
            
            # Try different shift amounts
            for delta in [5, 10, -5, -10]:
                P_new = best.production.copy()
                
                # Check feasibility
                if P_new[i, t1] - delta < 0 or P_new[i, t2] + delta < 0:
                    continue
                if P_new[i, t1] - delta > self.data.production_capacity[i, t1]:
                    continue
                if P_new[i, t2] + delta > self.data.production_capacity[i, t2]:
                    continue
                
                # Apply shift
                P_new[i, t1] -= delta
                P_new[i, t2] += delta
                
                candidate = Chromosome(P_new, best.workforce)
                candidate_cost = self.evaluator.cost_evaluator.evaluate(candidate)
                
                # Accept if better
                if candidate_cost < best_cost - 1e-6:
                    best = candidate
                    best_cost = candidate_cost
        
        return best


class WorkforceLocalSearch(LocalSearchOperator):
    """Local search for workforce optimization.
    
    Attempts to reduce instability while maintaining reasonable cost.
    """
    
    def __init__(self, problem_data: ProblemData, evaluator: ObjectiveEvaluator, neighborhood: int = 3):
        """Initialize workforce local search.
        
        Args:
            problem_data: Problem instance data
            evaluator: Objective evaluator
            neighborhood: Size of search neighborhood
        """
        super().__init__(problem_data, evaluator)
        self.neighborhood = neighborhood
    
    def improve(self, chromosome: Chromosome) -> Chromosome:
        """Improve workforce stability.
        
        Args:
            chromosome: Chromosome to improve
            
        Returns:
            Improved chromosome
        """
        best = chromosome.copy()
        best_cost, best_instability = self.evaluator.evaluate(best)
        
        for t in range(self.data.num_periods):
            # Try adjusting workforce at period t
            for delta in range(-self.neighborhood, self.neighborhood + 1):
                if delta == 0:
                    continue
                
                W_new = best.workforce.copy()
                W_new[t] = np.clip(
                    W_new[t] + delta,
                    self.data.min_workers,
                    self.data.max_workers
                )
                
                candidate = Chromosome(best.production, W_new)
                candidate_cost, candidate_instability = self.evaluator.evaluate(candidate)
                
                # Accept if instability improves and cost doesn't worsen too much
                if (candidate_instability < best_instability - 1e-6 and 
                    candidate_cost <= best_cost * 1.02):
                    best = candidate
                    best_cost = candidate_cost
                    best_instability = candidate_instability
        
        return best
