# 🔬 Research Lab

> **Build a living knowledge graph of your research — papers, concepts, connections, and evolving understanding.**

## The Scenario

A research group studying **Attention Mechanisms in Neural Networks** over 18 months. Papers read, experiments run, concepts debated, breakthroughs discovered. The kind of intellectual journey that's impossible to reconstruct from scattered notes.

## What Dragon Brain Finds

### 1. Concept Evolution
```
search_memory("what replaced standard attention and why")
```
**Result:** Traces the full evolution chain: attention → multi-head → Flash Attention → linear attention → hybrid approaches. Each step linked to the paper that introduced it and the experiment that validated it.

### 2. Research Timeline
```
get_evolution(flash_attention_id)
```
**Result:** Chronological history of Flash Attention in the group's understanding — when it was first read, which experiments tested it, what superseded it, and the current assessment.

### 3. Contradiction Detection
```
search_memory("experiments that contradicted paper claims")
```
**Result:** Finds that Run 3's results directly contradict the sparse attention paper's claims about scalability — including the specific metrics and the meeting where the group decided to abandon that approach.

### 4. Time Travel
```
point_in_time_query("what did we believe about linear attention", as_of="2025-06-01")
```
**Result:** The group's understanding of linear attention BEFORE the breakthrough experiment that changed everything. Compare what they believed then vs. now — intellectual progress made visible.

### 5. Cross-Concept Discovery
```
semantic_radar(sliding_window_id)
```
**Result:** *"Sliding window attention is semantically similar to KV cache compression but no graph link — worth investigating."* A connection the researchers haven't explicitly drawn.

## 💡 The Holy Shit Moment

Time travel. Researchers can literally replay their intellectual journey — what they believed 6 months ago, what experiment changed their mind, and how their understanding evolved. No lab notebook could reconstruct this.

## Sample Data

| Category | Count | Examples |
|----------|-------|---------|
| Papers | 15 | Vaswani 2017, Flash Attention, Ring Attention, Mamba |
| Concepts | 8 | Self-attention, linear attention, state space models, KV cache |
| Researchers | 8 | Group members with expertise areas |
| Experiments | 6 | Runs with results, comparisons, conclusions |
| Decisions | 4 | Architecture choices with rationale |
| Relationships | 65 | CITES, INTRODUCES, SUPERSEDES, CONTRADICTS, DEPENDS_ON |
