"""NSGA-II selection and Pareto archive management."""

from typing import List, Tuple
from ..models import Solution


class NSGA2Selector:
    """NSGA-II based selection using Pareto ranking and crowding distance.
    
    Follows SRP: Only responsible for NSGA-II selection logic.
    """
    
    def select(self, population: List[Solution], target_size: int) -> List[Solution]:
        """Select individuals using NSGA-II.
        
        Args:
            population: Population to select from
            target_size: Desired population size
            
        Returns:
            Selected population
        """
        fronts = self._nondominated_sort(population)
        
        new_population = []
        for front in fronts:
            if len(new_population) + len(front) <= target_size:
                new_population.extend(front)
            else:
                # Need to select some from this front using crowding distance
                remaining = target_size - len(new_population)
                distances = self._crowding_distance(front)
                
                # Sort by distance (descending) and select best
                sorted_front = sorted(
                    zip(front, distances),
                    key=lambda x: x[1],
                    reverse=True
                )
                new_population.extend([sol for sol, _ in sorted_front[:remaining]])
                break
        
        return new_population
    
    def _nondominated_sort(self, population: List[Solution]) -> List[List[Solution]]:
        """Perform non-dominated sorting.
        
        Args:
            population: Solutions to sort
            
        Returns:
            List of fronts, each containing non-dominated solutions
        """
        N = len(population)
        
        # For each solution, track domination relationships
        S = [[] for _ in range(N)]  # Solutions dominated by i
        n = [0] * N  # Number of solutions dominating i
        rank = [0] * N
        
        fronts = [[]]
        
        # Build domination relationships
        for i in range(N):
            for j in range(N):
                if i == j:
                    continue
                
                if population[i].dominates(population[j]):
                    S[i].append(j)
                elif population[j].dominates(population[i]):
                    n[i] += 1
            
            if n[i] == 0:  # Not dominated by anyone
                rank[i] = 0
                fronts[0].append(population[i])
        
        # Build subsequent fronts
        current_front = 0
        while fronts[current_front]:
            next_front = []
            
            for sol_i in fronts[current_front]:
                i = population.index(sol_i)
                
                for j in S[i]:
                    n[j] -= 1
                    if n[j] == 0:
                        rank[j] = current_front + 1
                        next_front.append(population[j])
            
            current_front += 1
            if next_front:
                fronts.append(next_front)
        
        return [f for f in fronts if f]  # Remove empty fronts
    
    def _crowding_distance(self, front: List[Solution]) -> List[float]:
        """Calculate crowding distance for solutions in a front.
        
        Args:
            front: Solutions in the same front
            
        Returns:
            Crowding distance for each solution
        """
        n = len(front)
        if n == 0:
            return []
        
        distances = [0.0] * n
        
        # For each objective
        for obj_idx in range(2):  # Z1 and Z2
            # Sort by this objective
            sorted_indices = sorted(
                range(n),
                key=lambda i: front[i].objectives[obj_idx]
            )
            
            # Boundary solutions get infinite distance
            distances[sorted_indices[0]] = float('inf')
            distances[sorted_indices[-1]] = float('inf')
            
            # Get objective range
            obj_min = front[sorted_indices[0]].objectives[obj_idx]
            obj_max = front[sorted_indices[-1]].objectives[obj_idx]
            
            if obj_max == obj_min:
                continue
            
            # Calculate crowding distance for intermediate solutions
            for i in range(1, n - 1):
                idx = sorted_indices[i]
                prev_obj = front[sorted_indices[i - 1]].objectives[obj_idx]
                next_obj = front[sorted_indices[i + 1]].objectives[obj_idx]
                
                distances[idx] += (next_obj - prev_obj) / (obj_max - obj_min)
        
        return distances


class ParetoArchive:
    """Maintains Pareto-optimal solutions archive.
    
    Follows SRP: Only responsible for archive management.
    """
    
    def __init__(self):
        """Initialize empty archive."""
        self.solutions: List[Solution] = []
    
    def update(self, candidate: Solution) -> bool:
        """Update archive with candidate solution.
        
        Args:
            candidate: Solution to potentially add
            
        Returns:
            True if solution was added to archive
        """
        # Check for duplicates
        for existing in self.solutions:
            if self._is_duplicate(existing, candidate):
                return False
        
        # Check if dominated by any existing solution
        for existing in self.solutions:
            if existing.dominates(candidate):
                return False
        
        # Remove solutions dominated by candidate
        self.solutions = [
            sol for sol in self.solutions
            if not candidate.dominates(sol)
        ]
        
        # Add candidate
        self.solutions.append(candidate)
        return True
    
    def get_sorted(self) -> List[Solution]:
        """Get archive sorted by first objective.
        
        Returns:
            Sorted list of solutions
        """
        return sorted(self.solutions, key=lambda s: s.total_cost)
    
    def _is_duplicate(self, sol1: Solution, sol2: Solution) -> bool:
        """Check if two solutions are duplicates.
        
        Args:
            sol1: First solution
            sol2: Second solution
            
        Returns:
            True if solutions are duplicates
        """
        return sol1 == sol2
    
    def __len__(self) -> int:
        """Get number of solutions in archive."""
        return len(self.solutions)
    
    def __iter__(self):
        """Iterate over archive solutions."""
        return iter(self.solutions)
