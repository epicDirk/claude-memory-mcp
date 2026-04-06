# 🏥 Medical Practice / Clinical Notes

> **Patient history that connects symptoms, treatments, and outcomes across visits — context your EHR buries.**

⚠️ **DISCLAIMER: This demo uses entirely synthetic data. Dragon Brain is not a medical device and is not intended for clinical decision-making.**

## The Scenario

A family medicine practice tracking **8 patients over 6 months**. Comorbidities, medication interactions, treatment responses, and the longitudinal patterns that get lost in visit-by-visit EHR documentation.

## What Dragon Brain Finds

### 1. Comorbidity Detection
```
search_memory("patients with both diabetes and depression")
```
**Result:** Identifies comorbid patients with treatment overlap analysis — including the dual-benefit discovery where switching to an SNRI improved both mood AND chronic pain.

### 2. Patient 360
```
get_hologram("Patient: Sarah Mitchell")
```
**Result:** Complete patient picture: all conditions, current medications, lab trends (A1C: 8.2 → 7.4 → 7.1), referrals, visit history, and flagged interactions. One query, full context.

### 3. Side Effect Patterns
```
search_memory("medications that worsened another condition")
```
**Result:** Cross-practice side effect pattern detection — which medications caused problems for which conditions, with visit-level evidence.

### 4. Drug Interaction Flagging
```
search_memory("drug interactions flagged")
```
**Result:** All interaction alerts across the practice: warfarin + NSAID (INR monitoring needed), with outcomes and follow-up notes.

### 5. Diagnostic Chain
```
traverse_path(metformin_id, fatigue_complaint_id)
```
**Result:** Is the fatigue a metformin side effect, or independent? Shows the diagnostic reasoning chain: metformin started → fatigue reported 3 months later → thyroid panel ordered → result pending.

## 💡 The Holy Shit Moment

Semantic radar discovers that a patient's chronic pain is semantically linked to their sleep disorder — but the clinician never connected them. Dragon Brain: *"These conditions are semantically related but not linked. Consider: is the pain causing sleep issues, or vice versa?"*

## Sample Data

| Category | Count | Examples |
|----------|-------|---------|
| Patients | 8 | Synthetic patients with demographics |
| Conditions | 12 | Diabetes, hypertension, depression, chronic pain |
| Medications | 10 | With dosages and interactions |
| Visits | 15 | Visit records across patients |
| Lab Results | 8 | Panels with values and trends |
| Relationships | 55 | DIAGNOSED_WITH, PRESCRIBED, CONTRAINDICATED_WITH, RESPONDED_TO |
