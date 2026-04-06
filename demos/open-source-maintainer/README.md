# 📦 Open Source Maintainer

> **Your AI remembers every issue, every design decision, every contributor interaction — across years of project history.**

## The Scenario

**FastQueue** — a popular open-source message queue with 3 years of history. 10 significant issues, 8 notable PRs, 6 design decisions, 3 RFCs with community feedback, and the kind of institutional knowledge that usually lives only in maintainer's heads.

## What Dragon Brain Finds

### 1. Bug Pattern Recognition
```
search_memory("message loss bugs")
```
**Result:** Links Issue #247 (message loss under high concurrency) to Issue #89 from 2 years ago — same subsystem, similar root cause (race condition in partition assignment), different code path. Pattern recognition across years.

### 2. Design Decision History
```
search_memory("why did we make consumer groups immutable")
```
**Result:** Returns RFC-003 with full rationale, the community vote (67% in favor), the main concern (migration path), and the person who championed the change. Complete decision context.

### 3. Contributor Expertise
```
search_memory("who should review replication changes")
```
**Result:** Alice (deep networking expertise) and Bob (storage engine owner) — with context about WHY they're the right reviewers and what they've touched before.

### 4. Cross-Issue Connections
```
traverse_path(issue_247_id, issue_89_id)
```
**Result:** Same subsystem, similar root cause, different code path. Shows the architectural connection between two bugs filed 2 years apart.

### 5. Failure Mode Discovery
```
semantic_radar(partition_assignment_id)
```
**Result:** *"Partition assignment semantically similar to leader election — no graph link. Shared failure modes?"* A systems insight that could prevent the next bug.

## 💡 The Holy Shit Moment

New contributor asks about consumer rebalance. Dragon Brain surfaces Issue #89 from 2 years ago, the RFC that redesigned it, the community vote, AND the related ongoing Issue #247 — context that would take hours to dig through GitHub history. **Institutional knowledge, instantly searchable.**

## Sample Data

| Category | Count | Examples |
|----------|-------|---------|
| Issues | 10 | Significant bugs with resolution history |
| PRs | 8 | Notable pull requests with review context |
| Decisions | 6 | API changes, breaking changes, deprecations |
| Contributors | 8 | With expertise areas and review history |
| Releases | 5 | Major releases with changelogs |
| Relationships | 55 | FIXES, INTRODUCED_BY, SUPERSEDES, BLOCKED_BY, BREAKING_CHANGE_IN |
