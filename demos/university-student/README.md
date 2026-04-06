# 🎓 University Student

> **Your AI study partner that connects concepts across courses and remembers everything you've learned.**

## The Scenario

**Alex** — a CS undergrad taking 4 courses simultaneously: Algorithms, Databases, Operating Systems, and Machine Learning. Same concepts appearing in different contexts, confusion between similar ideas, and cross-course connections that no syllabus makes explicit.

## What Dragon Brain Finds

### 1. Cross-Course Connections
```
search_memory("concepts that appear across multiple courses")
```
**Result:** Hashing (Algorithms + Databases), scheduling (OS + Algorithms), optimization (ML + Algorithms). The same ideas taught by different professors in different notation — connected by Dragon Brain.

### 2. Concept Mapping
```
get_hologram("B-trees")
```
**Result:** Which course teaches it, prerequisites (search trees, disk I/O), the analogy to page tables in OS (*"a page table for data"* — Professor Kim's explanation that made both click), and assignments that used it.

### 3. Confusion Pairs
```
search_memory("concepts I keep confusing")
```
**Result:** Amortized analysis (Algorithms) vs. gradient accumulation (ML) — both involve "averaging over time" but for completely different purposes. With notes on WHY they're confusing and what distinguishes them.

### 4. Exam Prep
```
search_memory("what are my weak areas for the algorithms exam")
```
**Result:** Weak topics with specific evidence: dynamic programming (can solve simple cases but not optimization variants), graph algorithms (DFS vs BFS application confusion). Targeted study plan.

### 5. Study Insights
```
semantic_radar(gradient_descent_id)
```
**Result:** *"Gradient descent semantically similar to hill climbing in Algorithms — no graph link. Same optimization family?"* Both are iterative optimization — one continuous, one discrete. Understanding one helps with both.

## 💡 The Holy Shit Moment

Semantic radar discovers that gradient descent (ML) is linked to hill climbing (Algorithms) but Alex never connected them. Dragon Brain: *"These are both iterative optimization algorithms — one continuous, one discrete."* A study insight that no textbook explicitly makes because they live in different departments.

## Sample Data

| Category | Count | Examples |
|----------|-------|---------|
| Courses | 4 | Algorithms, Databases, Operating Systems, ML |
| Concepts | 20 | Hashing, B-trees, page tables, gradient descent, Big-O |
| Assignments | 8 | With approaches and grades |
| Study Sessions | 10 | What was covered, confusion points |
| Connections | 6 | Cross-course concept links discovered |
| Relationships | 55 | TAUGHT_IN, PREREQUISITE_FOR, ANALOGOUS_TO, CONFUSED_WITH, WEAK_IN |
