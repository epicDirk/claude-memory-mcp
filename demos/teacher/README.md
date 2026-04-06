# 📚 Teacher / Course Designer

> **Track every student's journey, every misconception, every 'aha moment' — teaching that actually adapts.**

## The Scenario

**Introduction to Data Science** — a semester teaching 25 students. Misconceptions that repeat across cohorts, interventions that work (and don't), and the pedagogical insights that make next semester better than this one.

## What Dragon Brain Finds

### 1. Struggling Student Patterns
```
search_memory("students struggling with the same concept")
```
**Result:** Pattern detection: 80% of students initially confuse accuracy with the right metric for imbalanced datasets. Introducing confusion matrices in Week 4 (instead of Week 7) cut this misconception in half.

### 2. Intervention History
```
get_hologram("correlation vs causation misconception")
```
**Result:** Which students hit this misconception, what explanations were tried, which worked (ice cream/drowning example), which didn't (textbook definition), and the evidence for each.

### 3. What Works
```
search_memory("teaching methods that improved outcomes")
```
**Result:** Flipped classroom for pandas (deeper questions), peer tutoring for complementary skills (Jake + Priya pairing), early introduction of confusion matrix. Each with evidence.

### 4. Student Progress
```
point_in_time_query("Maria's understanding of statistics", as_of="week-4")
```
**Result:** Maria's progress state mid-semester vs. end — what interventions changed the trajectory from struggling to proficient.

### 5. Curriculum Insights
```
find_semantic_opportunities(project_id="data-science-101")
```
**Result:** *"Feature engineering and data cleaning are semantically related but taught 6 weeks apart. Students struggling with one tend to struggle with both — consider teaching them together."*

## 💡 The Holy Shit Moment

Dragon Brain discovers that students who struggle with feature engineering ALSO tend to struggle with data cleaning — but these topics are taught 6 weeks apart. The semantic link reveals a curriculum design improvement the teacher hadn't considered.

## Sample Data

| Category | Count | Examples |
|----------|-------|---------|
| Students | 10 | With learning profiles and progress |
| Topics | 12 | Statistics, pandas, visualization, ML basics |
| Assignments | 8 | With rubrics and common mistakes |
| Misconceptions | 10 | Common across cohorts |
| Interventions | 6 | Office hours, peer tutoring, flipped classroom |
| Relationships | 60 | PREREQUISITE_FOR, STRUGGLES_WITH, CORRECTED_BY, BREAKTHROUGH_IN |
