# 🛡️ Cybersecurity SOC / Threat Intel

> **Connect IOCs, TTPs, and actor profiles across incidents — threat intel that actually links up.**

## The Scenario

A SOC tracking APT activity across **6 incidents over 12 months**. Three threat actor groups, five malware families, shared infrastructure, and evolving TTPs. The kind of analysis where connecting two IOCs changes the entire attribution picture.

## What Dragon Brain Finds

### 1. Infrastructure Sharing
```
search_memory("shared infrastructure between threat groups")
```
**Result:** APT Group 1 and APT Group 2 share C2 infrastructure at the same hosting provider, registered through the same privacy registrar. Possible operational relationship — or shared tooling supplier.

### 2. Malware Lineage
```
get_hologram("BlackMist malware")
```
**Result:** Full context — which actors deploy it, which incidents involved it, IOCs associated with each variant, and the 73% code overlap with RedDust suggesting shared developer or code theft.

### 3. TTP Correlation
```
search_memory("incidents using the same spearphishing template")
```
**Result:** Incidents 1, 3, and 5 all used the same macro template (T1566.001) with different payloads. Escalating sophistication across the campaign — same operator learning from each engagement.

### 4. Temporal Clustering
```
query_timeline(start="2025-03-01", end="2025-04-01")
```
**Result:** 3 incidents in 4 weeks, same TTP chain, different targets. Burst activity suggesting an active campaign window.

### 5. Emerging Campaign Detection
```
semantic_radar(apt_group_1_id)
```
**Result:** *"APT Group 1 semantically similar to a new IOC cluster — no graph attribution yet. Emerging campaign?"* Dragon Brain flagged a connection before the SOC formally attributed it.

## 💡 The Holy Shit Moment

Semantic radar finds that a cluster of new, unattributed IOCs is semantically similar to a known APT group's infrastructure pattern — before any analyst has manually connected them. **Early warning for an emerging campaign.**

## Sample Data

| Category | Count | Examples |
|----------|-------|---------|
| Threat Actors | 3 | APT groups with aliases and attributions |
| Malware | 5 | Families with capabilities and code relationships |
| IOCs | 10 | IPs, domains, hashes, mutex names |
| TTPs | 8 | MITRE ATT&CK techniques |
| Incidents | 6 | Security incidents with timelines |
| Relationships | 65 | USES, ATTRIBUTED_TO, VARIANT_OF, SHARED_INFRA, SAME_TTP_AS |
