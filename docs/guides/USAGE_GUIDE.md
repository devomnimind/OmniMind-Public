# OmniMind Quantum Physics-Inspired AI - Usage Guide

## Overview

This guide demonstrates how to use all 10 quantum physics-inspired features implemented in OmniMind.

## Installation

All features are included in the OmniMind repository. Required dependencies:
- Python 3.12+
- NumPy
- PyTorch (optional, for attention mechanisms)

## Feature Usage Examples

### Phase 1: Event Horizon Memory

```python
from src.memory import EventHorizonMemory
import numpy as np

# Create holographic memory with Bekenstein bounds
memory = EventHorizonMemory(
    initial_area=1000.0,  # Surface area in Planck units
    spawn_threshold=0.95   # Saturation threshold
)

# Store 3D volumetric data (automatically projected to 2D)
data_3d = np.random.randn(64, 64, 64)
result = memory.store({"tensor": data_3d})

print(f"Stored with entropy: {result['entropy']:.2f}")
print(f"Saturation ratio: {result['saturation_ratio']:.2f}")

# Retrieve information
query = {"tensor": data_3d[:32, :32, :32]}  # Partial query
retrieved = memory.retrieve(query, search_children=True)

# Get statistics
stats = memory.get_statistics()
print(f"Total memories in hierarchy: {stats['total_memories']}")
print(f"Hierarchy depth: {stats['total_hierarchy_depth']}")
```

### Phase 2: Hawking Radiation Motivation

```python
from src.motivation import HawkingMotivationEngine
from datetime import datetime, timedelta, timezone

# Create knowledge evaporation system
motivator = HawkingMotivationEngine(
    base_temperature=2.0,           # Hawking temperature
    evaporation_threshold_days=7.0  # Evaporation threshold
)

# Add knowledge
motivator.add_knowledge("python_basics", "Python fundamentals", mass=3.0)
motivator.add_knowledge("ml_theory", "Machine learning theory", mass=5.0)
motivator.add_knowledge("quantum_physics", "Quantum mechanics", mass=4.0)

# Add correlations (preserves info during evaporation)
motivator.add_correlation("python_basics", "ml_theory")

# Use knowledge (prevents evaporation)
motivator.use_knowledge("python_basics")

# Evaporate unused knowledge
evaporated_ids, motivation_data = motivator.evaporate_unused_knowledge()

print(f"Evaporated: {len(evaporated_ids)} items")
print(f"Frustration energy: {motivation_data['frustration']:.2f}")
print(f"Motivation boost: {motivation_data['motivation']:.2f}")
print(f"At risk: {len(motivation_data['correlations_at_risk'])}")

# Check specific knowledge status
status = motivator.get_knowledge_status("ml_theory")
if status:
    print(f"Status: {status['status']}")
    print(f"Evaporation risk: {status['evaporation_risk']:.2f}")
```

### Phase 3: Page Curve Learning

```python
from src.learning import PageCurveLearner, LearningPhase
import numpy as np

# Create Page curve tracker
learner = PageCurveLearner(
    detection_window=10,
    page_time_threshold=0.95,
    min_epochs_before_page=5
)

# Training loop
for epoch in range(100):
    # Your training code here
    model_state = {
        "weights": np.random.randn(256)  # Model parameters
    }
    
    loss = 1.0 / (epoch + 1)  # Decreasing loss
    
    result = learner.record_epoch(model_state, loss=loss)
    
    # Check learning phase
    if result["phase"] == LearningPhase.PAGE_TIME.value:
        print(f"Page time detected at epoch {epoch}!")
        print("Recommendation: Reduce learning rate")
        # learning_rate *= 0.5
        
    elif result["phase"] == LearningPhase.CONSOLIDATION.value:
        print(f"Consolidation phase - entropy decreasing")
        
    elif result["phase"] == LearningPhase.SATURATED.value:
        print("Learning saturated - consider early stopping")
        if not result["recommendations"]["continue_training"]:
            break

# Get final Page curve
curve = learner.get_page_curve()
print(f"Max entropy: {curve.max_entropy:.2f}")
print(f"Page time epoch: {curve.page_time_epoch}")

# Plot entropy evolution (if matplotlib available)
# import matplotlib.pyplot as plt
# plt.plot(curve.epochs, curve.entropy_history)
# plt.xlabel("Epoch")
# plt.ylabel("Entropy")
# plt.show()
```

### Phase 4: Soft Hair Encoding

```python
from src.memory import SoftHairEncoder, SoftHairMemory
import numpy as np

# Create soft hair encoder
encoder = SoftHairEncoder(
    soft_mode_cutoff=0.2,  # Keep 20% of frequencies
    max_modes=128
)

# Encode high-entropy data
data = np.random.randn(256, 256)
soft_hair = encoder.encode_to_soft_hair(data)

print(f"Compression ratio: {soft_hair.compression_ratio:.2f}x")
print(f"Soft modes shape: {soft_hair.soft_modes.shape}")

# Decode data
reconstructed = encoder.decode_from_soft_hair(soft_hair)

# Compute fidelity
fidelity = encoder.compute_fidelity(data, reconstructed)
print(f"Reconstruction fidelity: {fidelity:.2f}")

# Use soft hair memory system
memory = SoftHairMemory()

# Store multiple items
for i in range(5):
    data_item = np.random.randn(128, 128) * (i + 1)
    memory.store(f"data_{i}", data_item)

# Retrieve
retrieved = memory.retrieve("data_3")

# Get compression statistics
stats = memory.get_compression_stats()
print(f"Average compression: {stats['average_compression']:.2f}x")
print(f"Total items: {stats['total_items']}")
```

### Phase 5: Quantum Entanglement Network

```python
from src.distributed import EntangledAgentNetwork, BellState

# Create network of entangled agents
network = EntangledAgentNetwork(num_agents=5)

# Create Bell pair entanglement
network.create_bell_pair("agent_0", "agent_1", BellState.PHI_PLUS)
network.create_bell_pair("agent_1", "agent_2", BellState.PSI_PLUS)

# Entanglement swapping (create non-local correlation)
new_pair = network.entanglement_swapping("agent_0", "agent_2")
print(f"Created entanglement: agent_0 <-> agent_2")

# Measure correlation
correlation = network.measure_correlation("agent_0", "agent_2")
print(f"Correlation strength: {correlation:.2f}")

# Network statistics
stats = network.get_statistics()
print(f"Total agents: {stats['total_agents']}")
print(f"Total entanglements: {stats['total_entanglements']}")
print(f"Bell state distribution: {stats['bell_state_distribution']}")
```

### Phase 6: Thermodynamic Attention

```python
# Requires PyTorch
try:
    import torch
    from src.attention import ThermodynamicAttention, MultiHeadThermodynamicAttention
    
    # Single-head thermodynamic attention
    attention = ThermodynamicAttention(
        embed_dim=512,
        temperature=1.0,
        entropy_weight=1.0
    )
    
    # Input tensors
    batch_size, seq_len = 2, 20
    query = torch.randn(batch_size, seq_len, 512)
    key = torch.randn(batch_size, seq_len, 512)
    value = torch.randn(batch_size, seq_len, 512)
    
    # Apply entropy-based attention
    output = attention(query, key, value)
    print(f"Output shape: {output.shape}")
    
    # Multi-head version
    multi_head_attention = MultiHeadThermodynamicAttention(
        embed_dim=512,
        num_heads=8,
        base_temperature=1.0
    )
    
    output_multi = multi_head_attention(query, key, value)
    print(f"Multi-head output shape: {output_multi.shape}")
    
except ImportError:
    print("PyTorch not available - thermodynamic attention requires torch")
```

### Phase 7: Black Hole Meta-Learning

```python
from src.meta_learning.black_hole_collapse import BlackHoleMetaLearner

# Create meta-learner
meta_learner = BlackHoleMetaLearner(critical_density=10.0)

# Knowledge base
knowledge = {
    "concept_1": {"importance": 5.0},
    "concept_2": {"importance": 3.0},
    "concept_3": {"importance": 4.0},
    "concept_4": {"importance": 2.0},
}

# Calculate knowledge mass and volume
knowledge_mass = sum(k["importance"] for k in knowledge.values())
knowledge_volume = len(knowledge)

# Check if collapse should occur
should_collapse = meta_learner.check_collapse_condition(
    knowledge_mass, knowledge_volume
)

if should_collapse:
    print("Knowledge density exceeds Schwarzschild radius!")
    
    # Trigger collapse to meta-level
    meta_knowledge = meta_learner.collapse_to_meta_level(knowledge)
    
    print(f"Singularity (core axioms): {meta_knowledge.singularity}")
    print(f"Event horizon radius: {meta_knowledge.event_horizon}")
    print(f"Hawking radiation (derived): {meta_knowledge.hawking_radiation}")

# Statistics
stats = meta_learner.get_statistics()
print(f"Total meta-levels: {stats['total_meta_levels']}")
```

### Phase 10: Bekenstein Architecture Capacity

```python
from src.architecture.bekenstein_capacity import BekensteinArchitect

# Create architecture advisor
architect = BekensteinArchitect()

# Compute maximum parameters from physical limits
compute_budget = 1e10  # Energy budget (normalized)
spatial_extent = 1e6    # Model size (normalized)

max_params = architect.compute_max_parameters(
    compute_budget, spatial_extent
)

print(f"Bekenstein bound: {max_params:,} parameters maximum")

# Get architecture recommendations
architecture = architect.recommend_architecture(max_params)

print(f"Recommended layers: {architecture['num_layers']}")
print(f"Parameters per layer: {architecture['params_per_layer']:,}")
print(f"Total parameters: {architecture['total_params']:,}")
```

## Integration Example

Combining multiple features:

```python
from src.memory import EventHorizonMemory, SoftHairEncoder
from src.motivation import HawkingMotivationEngine
from src.learning import PageCurveLearner
import numpy as np

# Create integrated system
memory = EventHorizonMemory(initial_area=1000.0)
encoder = SoftHairEncoder(soft_mode_cutoff=0.2)
motivator = HawkingMotivationEngine(base_temperature=2.0)
learner = PageCurveLearner()

# Training loop with all features
for epoch in range(50):
    # Generate model state
    model_state = {"weights": np.random.randn(256)}
    
    # Track learning phase (Page curve)
    learning_result = learner.record_epoch(model_state)
    
    # Store compressed in memory (soft hair + holographic)
    data = np.random.randn(128, 128)
    soft_hair = encoder.encode_to_soft_hair(data)
    memory_result = memory.store({"tensor": soft_hair.soft_modes})
    
    # Add knowledge and track evaporation
    motivator.add_knowledge(f"epoch_{epoch}", f"Learning at epoch {epoch}", mass=1.0)
    
    # Check evaporation
    if epoch % 10 == 0:
        evaporated, motivation = motivator.evaporate_unused_knowledge()
        print(f"Epoch {epoch}: Phase={learning_result['phase']}, "
              f"Evaporated={len(evaporated)}, "
              f"Memory saturation={memory_result['saturation_ratio']:.2f}")
```

## Best Practices

1. **Memory Management**: Use holographic memory for large-scale data with automatic hierarchy
2. **Knowledge Dynamics**: Combine Hawking motivation with Lacanian lack for productive urgency
3. **Learning Monitoring**: Track Page curve to detect phase transitions
4. **Compression**: Use soft hair encoding for long-term storage
5. **Distributed**: Leverage quantum entanglement for agent coordination
6. **Attention**: Use thermodynamic attention for information-seeking behavior

## Performance Considerations

- Event Horizon Memory: O(n) storage, O(log n) hierarchy depth
- Soft Hair Encoding: Compression ratio 5-50x depending on cutoff
- Quantum Entanglement: O(1) correlation measurement
- Thermodynamic Attention: Same complexity as standard attention
- All features optimized for GTX 1650 (4GB VRAM) constraints

## Troubleshooting

**Issue**: PyTorch not available
- **Solution**: Thermodynamic attention is optional. Other features work without PyTorch.

**Issue**: Memory saturation too fast
- **Solution**: Increase `initial_area` or reduce `spawn_threshold`

**Issue**: Knowledge evaporating too quickly
- **Solution**: Reduce `base_temperature` or increase `evaporation_threshold_days`

## References

See `docs/PHASES_6_10_SUMMARY.md` for complete scientific references and implementation details.
