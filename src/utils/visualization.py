"""Visualization and display utilities."""

import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple
from ..models import Solution, ProblemData


class ParetoPlotter:
    """Plots Pareto fronts over generations.
    
    Follows SRP: Only responsible for visualization.
    """
    
    @staticmethod
    def plot_evolution(history: List[List[Tuple[float, float]]], current_gen: int):
        """Plot Pareto front evolution.
        
        Args:
            history: History of Pareto fronts
            current_gen: Current generation number (0-indexed)
        """
        plt.figure(figsize=(10, 6))
        
        for gen_idx, front in enumerate(history):
            if not front:
                continue
            
            Z1_values = [z[0] for z in front]
            Z2_values = [z[1] for z in front]
            
            # Highlight current generation
            alpha = 0.3 if gen_idx < current_gen else 1.0
            label = f'Gen {gen_idx + 1}' if gen_idx == current_gen else None
            
            plt.scatter(Z1_values, Z2_values, alpha=alpha, label=label)
        
        plt.xlabel('Z1: Total Cost')
        plt.ylabel('Z2: Workforce Instability')
        plt.title(f'Pareto Front Evolution (Generation {current_gen + 1})')
        plt.grid(True, alpha=0.3)
        if current_gen >= 0:
            plt.legend()
        plt.tight_layout()
        plt.show()
    
    @staticmethod
    def plot_final_pareto(solutions: List[Solution]):
        """Plot final Pareto front.
        
        Args:
            solutions: Final Pareto-optimal solutions
        """
        if not solutions:
            print("No solutions to plot.")
            return
        
        Z1_values = [sol.total_cost for sol in solutions]
        Z2_values = [sol.instability for sol in solutions]
        
        plt.figure(figsize=(10, 6))
        plt.scatter(Z1_values, Z2_values, s=100, alpha=0.7, edgecolors='black')
        
        for i, (z1, z2) in enumerate(zip(Z1_values, Z2_values)):
            plt.annotate(f'{i+1}', (z1, z2), xytext=(5, 5), textcoords='offset points')
        
        plt.xlabel('Z1: Total Cost')
        plt.ylabel('Z2: Workforce Instability')
        plt.title('Final Pareto Front')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()


class ResultsDisplay:
    """Displays detailed results for solutions.
    
    Follows SRP: Only responsible for formatting and displaying results.
    """
    
    def __init__(self, problem_data: ProblemData):
        """Initialize with problem data.
        
        Args:
            problem_data: Problem instance data
        """
        self.data = problem_data
    
    def display_summary(self, solutions: List[Solution]):
        """Display summary of all solutions.
        
        Args:
            solutions: Solutions to display
        """
        print(f"\nFound {len(solutions)} Pareto-optimal solutions:")
        print("\n" + "="*80)
        print("PARETO FRONT SUMMARY")
        print("="*80)
        print(f"{'Solution':<10} {'Z1 (Cost)':<20} {'Z2 (Instability)':<20}")
        print("-"*80)
        
        for i, sol in enumerate(solutions, 1):
            print(f"{i:<10} {sol.total_cost:<20.2f} {sol.instability:<20.2f}")
        
        print("="*80)
    
    def display_detailed(self, solutions: List[Solution]):
        """Display detailed information for all solutions.
        
        Args:
            solutions: Solutions to display in detail
        """
        if not solutions:
            print("No solutions to display.")
            return
        
        for idx, sol in enumerate(solutions, 1):
            self._display_solution(idx, sol, len(solutions))
    
    def _display_solution(self, solution_num: int, solution: Solution, total: int):
        """Display detailed information for one solution.
        
        Args:
            solution_num: Solution number
            solution: Solution to display
            total: Total number of solutions
        """
        ch = solution.chromosome
        
        print("\n" + "="*80)
        print(f"SOLUTION {solution_num} of {total} - DETAILED INFORMATION")
        print("="*80)
        print(f"Z1 (Total Cost) = {solution.total_cost:.2f}")
        print(f"Z2 (Workforce Instability) = {solution.instability:.2f}")
        
        # Production quantities
        self._display_production(ch.production)
        
        # Inventory levels
        self._display_inventory(ch.production)
        
        # Workforce levels
        self._display_workforce(ch.workforce)
        
        # Hiring and firing
        self._display_workforce_changes(ch.workforce)
    
    def _display_production(self, production: np.ndarray):
        """Display production matrix."""
        print("\n" + "-"*80)
        print("PPit - Production quantity of product i in period t (units):")
        print("-"*80)
        
        # Header
        print("Product\\Period", end="")
        for t in range(self.data.num_periods):
            print(f"{t+1:8d}", end="")
        print()
        
        # Rows
        for i in range(self.data.num_products):
            print(f"Product {i:2d}   ", end="")
            for t in range(self.data.num_periods):
                print(f"{production[i, t]:8d}", end="")
            print()
    
    def _display_inventory(self, production: np.ndarray):
        """Display inventory levels."""
        print("\n" + "-"*80)
        print("CIit - Inventory of product i in period t (units):")
        print("-"*80)
        
        # Calculate inventory
        inv = np.zeros(self.data.num_products, dtype=int)
        inventory_matrix = np.zeros((self.data.num_products, self.data.num_periods), dtype=int)
        
        for t in range(self.data.num_periods):
            for i in range(self.data.num_products):
                inv[i] += production[i, t] - self.data.demand[i, t]
                inv[i] = max(0, inv[i])
                inventory_matrix[i, t] = inv[i]
        
        # Header
        print("Product\\Period", end="")
        for t in range(self.data.num_periods):
            print(f"{t+1:8d}", end="")
        print()
        
        # Rows
        for i in range(self.data.num_products):
            print(f"Product {i:2d}   ", end="")
            for t in range(self.data.num_periods):
                print(f"{inventory_matrix[i, t]:8d}", end="")
            print()
    
    def _display_workforce(self, workforce: np.ndarray):
        """Display workforce levels."""
        print("\n" + "-"*80)
        print("Wt - Number of workers in period t:")
        print("-"*80)
        
        print("Period: ", end="")
        for t in range(self.data.num_periods):
            print(f"{t+1:6d}", end="")
        print()
        
        print("Workers:", end="")
        for t in range(self.data.num_periods):
            print(f"{workforce[t]:6d}", end="")
        print()
    
    def _display_workforce_changes(self, workforce: np.ndarray):
        """Display hiring and firing."""
        print("\n" + "-"*80)
        print("WHt - Workers hired in period t:")
        print("WLt - Workers laid off in period t:")
        print("-"*80)
        
        print("Period:  ", end="")
        for t in range(self.data.num_periods):
            print(f"{t+1:6d}", end="")
        print()
        
        # Hiring
        print("Hired:   ", end="")
        prev = self.data.initial_workers
        for t in range(self.data.num_periods):
            hired = max(0, workforce[t] - prev)
            print(f"{hired:6d}", end="")
            prev = workforce[t]
        print()
        
        # Layoffs
        print("Laid off:", end="")
        prev = self.data.initial_workers
        for t in range(self.data.num_periods):
            laid_off = max(0, prev - workforce[t])
            print(f"{laid_off:6d}", end="")
            prev = workforce[t]
        print()
