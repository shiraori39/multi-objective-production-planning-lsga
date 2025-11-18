# Production Planning LS-GA

## Overview

This project implements a **Local Search Genetic Algorithm (LS-GA)** for bi-objective **Aggregate Production Planning (APP)**. The solution is designed following **SOLID principles** and **KISS methodology** with a clean, object-oriented architecture.

## Objectives

The algorithm optimizes two conflicting objectives:
- **Z1**: Minimize total cost (production + inventory + workforce)
- **Z2**: Minimize workforce instability (hiring/firing fluctuations)

## Project Structure

```
repo/
├── config/                    # Configuration management 
│   ├── __init__.py
│   └── algorithm_config.py    # Algorithm parameters
│
├── src/                       # Source code
│   ├── __init__.py
│   ├── models/                # Data models (SRP)
│   │   ├── __init__.py
│   │   ├── chromosome.py      # Solution representation
│   │   ├── problem_data.py    # Problem parameters
│   │   └── solution.py        # Solution with objectives
│   │
│   ├── algorithms/            # Core algorithms
│   │   ├── __init__.py
│   │   ├── nsga2.py           # NSGA-II selection & archive
│   │   └── lsga.py            # Main LS-GA orchestrator (DIP)
│   │
│   ├── operators/             # Genetic operators (OCP)
│   │   ├── __init__.py
│   │   ├── crossover.py       # Crossover operators
│   │   ├── mutation.py        # Mutation operators
│   │   ├── selection.py       # Selection operators
│   │   └── local_search.py    # Local search operators
│   │
│   └── utils/                 # Utility modules
│       ├── __init__.py
│       ├── evaluator.py       # Objective evaluation (SRP)
│       ├── repair.py          # Constraint repair (SRP)
│       ├── initializer.py     # Population initialization
│       └── visualization.py   # Plotting and display (SRP)
│
├── main.py                    # Main entry point
├── ls_ga_notebook.ipynb       # Interactive notebook
└── README.md                  # This file
```

## Design Principles

### SOLID Principles

1. **Single Responsibility Principle (SRP)**
   - Each class has one clear purpose
   - `CostEvaluator`: Only evaluates cost
   - `ConstraintRepair`: Only repairs constraints
   - `ParetoPlotter`: Only handles visualization

2. **Open/Closed Principle (OCP)**
   - Operators extend `CrossoverOperator`, `MutationOperator` base classes
   - Easy to add new operators without modifying existing code

3. **Liskov Substitution Principle (LSP)**
   - All operators can be substituted via their abstract base classes
   - Algorithm works with any compatible operator implementation

4. **Interface Segregation Principle (ISP)**
   - Small, focused interfaces (e.g., `evaluate()`, `mutate()`, `repair()`)
   - Classes only depend on methods they actually use

5. **Dependency Inversion Principle (DIP)**
   - `LSGAAlgorithm` depends on abstractions (operators), not concrete implementations
   - Components injected via constructor

### KISS (Keep It Simple, Stupid)

- Clear class names that describe their purpose
- Simple method interfaces
- Each file focuses on one aspect
- Minimal coupling between components

## Usage

### Running from Command Line

```bash
python main.py
```

### Customizing Configuration

```python
# Create custom configuration
config = AlgorithmConfig(
    population_size=100,
    max_generations=300,
    partheno_crossover_prob=0.7,
    production_ls_attempts=20
)
```

### Custom Problem Data

```python
import numpy as np
from src.models import ProblemData

problem_data = ProblemData(
    num_products=10,
    num_periods=12,
    demand=your_demand_array,
    production_capacity=your_capacity_array,
    # ... other parameters
)
```

## Algorithm Components

### Models
- **Chromosome**: Encapsulates production and workforce decisions
- **Solution**: Bundles chromosome with evaluated objectives
- **ProblemData**: Holds all problem parameters and constraints

### Operators
- **Crossover**: Partheno (production) and Arithmetic (both variables)
- **Mutation**: Random changes to production or workforce
- **Selection**: Tournament selection with Pareto dominance
- **Local Search**: Production smoothing and workforce stability improvement

### Algorithm Flow

1. **Initialize** population with feasible solutions
2. **Repeat** for max generations:
   - Select parents via tournament
   - Apply crossover and mutation
   - Repair constraints
   - Apply local search
   - Combine parents and offspring
   - Select next generation using NSGA-II
   - Update Pareto archive
3. **Return** non-dominated solutions

## Requirements

```
numpy
matplotlib
```

For Jupyter notebook support:
```
jupyter
ipython
```

## Features

- ✅ Multi-objective optimization (Pareto front)
- ✅ NSGA-II selection with crowding distance
- ✅ Local search for solution refinement
- ✅ Constraint repair mechanism
- ✅ Progress visualization
- ✅ Detailed solution reporting
- ✅ Configurable parameters
- ✅ Clean OOP architecture

## License

This project is for educational and research purposes.
