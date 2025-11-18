"""Objective evaluators for production planning problem."""

import numpy as np
from typing import Tuple
from ..models import Chromosome, ProblemData, Solution


class CostEvaluator:
    """Evaluates total cost (Z1) for a chromosome.
    
    Follows SRP: Only responsible for cost calculation.
    """
    
    def __init__(self, problem_data: ProblemData):
        """Initialize with problem data.
        
        Args:
            problem_data: Problem instance data
        """
        self.data = problem_data
    
    def evaluate(self, chromosome: Chromosome) -> float:
        """Calculate total production, inventory, and workforce cost.
        
        Args:
            chromosome: Chromosome to evaluate
            
        Returns:
            Total cost (Z1)
        """
        P = chromosome.production
        W = chromosome.workforce
        
        # Production cost
        prod_cost = (self.data.unit_production_cost.reshape(-1, 1) * P).sum()
        
        # Inventory holding cost and penalties
        inv = np.zeros(self.data.num_products, dtype=int)
        hold_cost = 0.0
        
        for t in range(self.data.num_periods):
            for i in range(self.data.num_products):
                inv[i] += P[i, t] - self.data.demand[i, t]
                
                # Penalty for backlog (negative inventory)
                if inv[i] < 0:
                    hold_cost += 1000.0 * abs(inv[i])
                    inv[i] = 0
                
                # Penalty for exceeding inventory capacity
                if inv[i] > self.data.inventory_capacity[i]:
                    hold_cost += 1000.0 * (inv[i] - self.data.inventory_capacity[i])
                
                # Holding cost
                hold_cost += self.data.unit_inventory_cost[i] * inv[i]
        
        # Workforce costs
        wages = W.sum() * self.data.wage_per_worker_per_period
        
        # Hiring and firing costs
        hire_fire_cost = 0.0
        prev_workers = self.data.initial_workers
        
        for t in range(self.data.num_periods):
            if W[t] > prev_workers:
                hire_fire_cost += (W[t] - prev_workers) * self.data.hire_cost_per_worker
            else:
                hire_fire_cost += (prev_workers - W[t]) * self.data.fire_cost_per_worker
            prev_workers = W[t]
        
        return prod_cost + hold_cost + wages + hire_fire_cost


class InstabilityEvaluator:
    """Evaluates workforce instability (Z2) for a chromosome.
    
    Follows SRP: Only responsible for instability calculation.
    """
    
    def __init__(self, problem_data: ProblemData):
        """Initialize with problem data.
        
        Args:
            problem_data: Problem instance data
        """
        self.data = problem_data
    
    def evaluate(self, chromosome: Chromosome) -> float:
        """Calculate workforce instability.
        
        Args:
            chromosome: Chromosome to evaluate
            
        Returns:
            Workforce instability (Z2)
        """
        W = chromosome.workforce
        prev_workers = self.data.initial_workers
        instability = 0.0
        
        for t in range(self.data.num_periods):
            instability += abs(W[t] - prev_workers)
            prev_workers = W[t]
        
        return instability


class ObjectiveEvaluator:
    """Coordinates evaluation of both objectives.
    
    Follows SRP and DIP: Delegates to specialized evaluators.
    """
    
    def __init__(self, problem_data: ProblemData):
        """Initialize with problem data.
        
        Args:
            problem_data: Problem instance data
        """
        self.cost_evaluator = CostEvaluator(problem_data)
        self.instability_evaluator = InstabilityEvaluator(problem_data)
    
    def evaluate(self, chromosome: Chromosome) -> Tuple[float, float]:
        """Evaluate both objectives for a chromosome.
        
        Args:
            chromosome: Chromosome to evaluate
            
        Returns:
            Tuple of (Z1: total cost, Z2: instability)
        """
        z1 = self.cost_evaluator.evaluate(chromosome)
        z2 = self.instability_evaluator.evaluate(chromosome)
        return (z1, z2)
    
    def create_solution(self, chromosome: Chromosome) -> Solution:
        """Create a Solution object with evaluated objectives.
        
        Args:
            chromosome: Chromosome to evaluate
            
        Returns:
            Solution with chromosome and objectives
        """
        objectives = self.evaluate(chromosome)
        return Solution(chromosome, objectives)
