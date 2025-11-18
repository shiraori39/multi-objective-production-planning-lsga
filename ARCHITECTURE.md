# Architecture Diagram

## Project Structure

```
c:/repo/
│
├── config/                          # Configuration Layer
│   ├── __init__.py
│   └── algorithm_config.py          # AlgorithmConfig class
│
├── src/                             # Source Code
│   ├── __init__.py
│   │
│   ├── models/                      # Data Models (SRP)
│   │   ├── __init__.py
│   │   ├── chromosome.py            # Chromosome (production + workforce)
│   │   ├── problem_data.py          # ProblemData (all parameters)
│   │   └── solution.py              # Solution (chromosome + objectives)
│   │
│   ├── algorithms/                  # Algorithm Implementations
│   │   ├── __init__.py
│   │   ├── nsga2.py                 # NSGA2Selector, ParetoArchive
│   │   └── lsga.py                  # LSGAAlgorithm (main orchestrator)
│   │
│   ├── operators/                   # Genetic Operators (OCP)
│   │   ├── __init__.py
│   │   ├── crossover.py             # CrossoverOperator (abstract)
│   │   │                            #   - ParthenoProductionCrossover
│   │   │                            #   - ArithmeticCrossover
│   │   ├── mutation.py              # MutationOperator (abstract)
│   │   │                            #   - ProductionMutation
│   │   │                            #   - WorkforceMutation
│   │   ├── selection.py             # SelectionOperator (abstract)
│   │   │                            #   - TournamentSelection
│   │   └── local_search.py          # LocalSearchOperator (abstract)
│   │                                #   - ProductionLocalSearch
│   │                                #   - WorkforceLocalSearch
│   │
│   └── utils/                       # Utility Modules
│       ├── __init__.py
│       ├── evaluator.py             # CostEvaluator, InstabilityEvaluator
│       │                            # ObjectiveEvaluator (coordinates both)
│       ├── repair.py                # ConstraintRepair
│       ├── initializer.py           # PopulationInitializer
│       └── visualization.py         # ParetoPlotter, ResultsDisplay
│
├── main.py                          # CLI Entry Point
├── ls_ga_notebook.ipynb             # Jupyter Notebook Interface
├── requirements.txt                 # Python Dependencies
└── README.md                        # Documentation
```

## Component Dependencies (Dependency Injection)

```
LSGAAlgorithm (orchestrator)
    │
    ├─► ProblemData (data)
    ├─► AlgorithmConfig (config)
    │
    ├─► ObjectiveEvaluator
    │       ├─► CostEvaluator
    │       └─► InstabilityEvaluator
    │
    ├─► ConstraintRepair
    ├─► PopulationInitializer
    │       └─► ConstraintRepair
    │
    ├─► Crossover Operators
    │       ├─► ParthenoProductionCrossover
    │       └─► ArithmeticCrossover
    │
    ├─► Mutation Operators
    │       ├─► ProductionMutation
    │       └─► WorkforceMutation
    │
    ├─► SelectionOperator
    │       └─► TournamentSelection
    │
    ├─► Local Search Operators
    │       ├─► ProductionLocalSearch
    │       └─► WorkforceLocalSearch
    │
    ├─► NSGA2Selector
    └─► ParetoArchive
```

## Data Flow

```
1. Initialization
   ┌─────────────────────────┐
   │ PopulationInitializer   │
   │  ├─ create random       │
   │  └─ repair constraints  │
   └─────────────────────────┘
              │
              ▼
   ┌─────────────────────────┐
   │ Initial Population      │
   │ (List[Chromosome])      │
   └─────────────────────────┘

2. Evolution Loop (per generation)
   ┌─────────────────────────┐
   │ Current Population      │
   └─────────────────────────┘
              │
              ▼
   ┌─────────────────────────┐
   │ Selection               │
   │  (Tournament)           │
   └─────────────────────────┘
              │
              ▼
   ┌─────────────────────────┐
   │ Crossover               │
   │  (Partheno + Arithmetic)│
   └─────────────────────────┘
              │
              ▼
   ┌─────────────────────────┐
   │ Mutation                │
   │  (Production + Workforce│
   └─────────────────────────┘
              │
              ▼
   ┌─────────────────────────┐
   │ Repair Constraints      │
   └─────────────────────────┘
              │
              ▼
   ┌─────────────────────────┐
   │ Local Search            │
   │  (Refine solutions)     │
   └─────────────────────────┘
              │
              ▼
   ┌─────────────────────────┐
   │ Evaluate Objectives     │
   │  (Z1: cost, Z2: instab) │
   └─────────────────────────┘
              │
              ▼
   ┌─────────────────────────┐
   │ Combine Parent+Offspring│
   └─────────────────────────┘
              │
              ▼
   ┌─────────────────────────┐
   │ NSGA-II Selection       │
   │  (Pareto ranking +      │
   │   crowding distance)    │
   └─────────────────────────┘
              │
              ▼
   ┌─────────────────────────┐
   │ Update Archive          │
   │  (Non-dominated sols)   │
   └─────────────────────────┘

3. Output
   ┌─────────────────────────┐
   │ Pareto Archive          │
   │  (Optimal solutions)    │
   └─────────────────────────┘
              │
              ▼
   ┌─────────────────────────┐
   │ Visualization           │
   │  (Plots + Tables)       │
   └─────────────────────────┘
```

## SOLID Principles Applied

### Single Responsibility Principle (SRP)
- `CostEvaluator`: Only evaluates cost
- `ConstraintRepair`: Only repairs constraints
- `ParetoPlotter`: Only plots visualizations
- `ResultsDisplay`: Only formats/displays results

### Open/Closed Principle (OCP)
- Abstract base classes: `CrossoverOperator`, `MutationOperator`, `LocalSearchOperator`
- New operators can be added without modifying existing code
- Example: Add `UniformCrossover` by extending `CrossoverOperator`

### Liskov Substitution Principle (LSP)
- All concrete operators can replace their base class
- Algorithm works with any compatible operator implementation

### Interface Segregation Principle (ISP)
- Small, focused interfaces
- `crossover(parent1, parent2) -> (child1, child2)`
- `mutate(chromosome) -> chromosome`
- `evaluate(chromosome) -> objectives`

### Dependency Inversion Principle (DIP)
- `LSGAAlgorithm` depends on operator interfaces, not concrete classes
- Components injected via constructor (Dependency Injection)
- Easy to swap implementations for testing or customization

## Key Design Patterns

1. **Strategy Pattern**: Interchangeable operators
2. **Factory Pattern**: `create_default()`, `create_fast()`, `create_thorough()`
3. **Repository Pattern**: `ParetoArchive` manages solutions
4. **Template Method**: Abstract operators define interface, subclasses implement details
5. **Dependency Injection**: All dependencies passed to constructor

## Extension Points

### Adding New Crossover Operator
```python
class UniformCrossover(CrossoverOperator):
    def crossover(self, parent1, parent2):
        # Implementation
        return child1, child2
```

### Adding New Objective
```python
class EnergyEvaluator:
    def evaluate(self, chromosome):
        # Calculate energy consumption
        return energy_cost
```

### Adding New Local Search
```python
class InventoryLocalSearch(LocalSearchOperator):
    def improve(self, chromosome):
        # Optimize inventory levels
        return improved_chromosome
```

## Benefits

✅ **Maintainability**: Changes isolated to specific modules  
✅ **Testability**: Each component independently testable  
✅ **Extensibility**: Easy to add features without breaking existing code  
✅ **Readability**: Clear structure, self-documenting code  
✅ **Reusability**: Components can be reused in other projects  
✅ **Scalability**: Easy to parallelize or optimize specific components
