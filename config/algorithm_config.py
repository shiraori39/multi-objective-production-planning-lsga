"""Configuration management for the algorithm."""

from dataclasses import dataclass


@dataclass
class AlgorithmConfig:
    """Configuration parameters for LS-GA algorithm.
    
    Follows SRP: Only responsible for holding configuration.
    """
    
    # Population parameters
    population_size: int = 60
    max_generations: int = 200
    
    # Crossover probabilities
    partheno_crossover_prob: float = 0.6
    arithmetic_crossover_prob: float = 0.7
    
    # Mutation probabilities
    production_mutation_prob: float = 0.1
    workforce_mutation_prob: float = 0.1
    
    # Selection parameters
    tournament_size: int = 2
    
    # Local search parameters
    production_ls_attempts: int = 10  # Reduced from 30 for efficiency
    workforce_ls_neighborhood: int = 3
    
    # Visualization
    plot_progress: bool = True
    plot_interval: int = 10
    
    # Random seed
    random_seed: int = 42
    
    @classmethod
    def create_default(cls) -> 'AlgorithmConfig':
        """Create configuration with default values."""
        return cls()
    
    @classmethod
    def create_fast(cls) -> 'AlgorithmConfig':
        """Create configuration optimized for speed."""
        return cls(
            population_size=30,
            max_generations=100,
            production_ls_attempts=5,
            plot_interval=20
        )
    
    @classmethod
    def create_thorough(cls) -> 'AlgorithmConfig':
        """Create configuration for thorough search."""
        return cls(
            population_size=100,
            max_generations=300,
            production_ls_attempts=30,
            plot_interval=15
        )
