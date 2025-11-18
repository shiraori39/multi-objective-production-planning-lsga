"""Problem data container for production planning."""

import numpy as np
from dataclasses import dataclass


@dataclass
class ProblemData:
    """Encapsulates all problem data and parameters.
    
    Follows SRP: Only responsible for storing and validating problem data.
    """
    
    # Problem dimensions
    num_products: int
    num_periods: int
    
    # Demand and capacity data
    demand: np.ndarray
    production_capacity: np.ndarray
    inventory_capacity: np.ndarray
    
    # Cost parameters
    unit_production_cost: np.ndarray
    unit_inventory_cost: np.ndarray
    hire_cost_per_worker: float
    fire_cost_per_worker: float
    wage_per_worker_per_period: float
    production_per_worker_per_period: np.ndarray
    
    # Workforce constraints
    min_workers: int
    max_workers: int
    initial_workers: int
    
    def __post_init__(self):
        """Validate data dimensions after initialization."""
        assert self.demand.shape == (self.num_products, self.num_periods)
        assert self.production_capacity.shape == (self.num_products, self.num_periods)
        assert len(self.inventory_capacity) == self.num_products
        assert len(self.unit_production_cost) == self.num_products
        assert len(self.unit_inventory_cost) == self.num_products
        assert len(self.production_per_worker_per_period) == self.num_products
        assert self.min_workers <= self.max_workers
        assert self.min_workers <= self.initial_workers <= self.max_workers
    
    @classmethod
    def create_default(cls) -> 'ProblemData':
        """Create problem data with default real production values."""
        I, T = 10, 12
        
        demand = np.array([
            [20160, 19824, 19152, 22848, 20377, 21504, 19824, 25872, 20832, 21168, 20832, 19152],
            [19824, 20160, 19152, 21168, 22809, 20496, 20160, 25536, 20832, 21168, 20832, 19488],
            [23184, 20448, 18432, 20304, 21456, 21024, 20016, 25056, 21456, 20880, 20160, 19440],
            [20160, 19584, 19296, 20448, 21312, 20592, 20160, 25344, 21456, 20448, 20592, 19440],
            [12888, 13472, 13448, 14600, 14720, 14120, 13528, 13312, 14816, 14256, 14128, 13368],
            [13464, 13472, 12872, 15176, 14144, 14696, 12952, 13312, 14816, 14832, 14128, 13368],
            [384, 0, 384, 384, 384, 0, 0, 0, 384, 0, 384, 384],
            [0, 384, 384, 384, 384, 0, 0, 0, 384, 0, 384, 384],
            [1280, 1626, 1280, 1370, 1626, 1626, 1370, 1370, 1716, 1460, 1280, 1220],
            [1658, 1530, 1234, 1568, 1710, 1632, 1440, 1478, 1658, 1170, 1280, 1600],
        ], dtype=int)
        
        production_capacity = np.array([
            [3700*6]*T, [3700*6]*T, [3700*6]*T, [3700*6]*T,
            [2400*6]*T, [2400*6]*T,
            [500*6]*T, [500*6]*T,
            [1200*6]*T, [1200*6]*T,
        ], dtype=int)
        
        inventory_capacity = np.array([2000, 1500, 1200, 1800, 1400, 1100, 2100, 1900, 1000, 9000], dtype=int)
        
        unit_production_cost = np.array([5.0, 6.0, 4.5, 5.5, 6.2, 4.8, 5.8, 6.1, 4.2, 5.3])
        unit_inventory_cost = np.array([0.5, 0.5, 0.4, 0.4, 0.6, 0.6, 0.5, 0.5, 0.4, 0.4])
        production_per_worker = np.array([10, 18, 15, 19, 17, 14, 21, 20, 13, 12])
        
        return cls(
            num_products=I,
            num_periods=T,
            demand=demand,
            production_capacity=production_capacity,
            inventory_capacity=inventory_capacity,
            unit_production_cost=unit_production_cost,
            unit_inventory_cost=unit_inventory_cost,
            hire_cost_per_worker=50.0,
            fire_cost_per_worker=80.0,
            wage_per_worker_per_period=1000.0,
            production_per_worker_per_period=production_per_worker,
            min_workers=0,
            max_workers=50,
            initial_workers=5
        )
