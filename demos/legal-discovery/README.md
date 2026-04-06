# ⚖️ Legal Discovery

> **Find contradictions, trace connections, and surface hidden relationships across case documents.**

## The Scenario

**Meridian Corp v. Apex Holdings** — a corporate fraud investigation with depositions, emails, financial records, and a whistleblower. The kind of case where critical connections are buried across thousands of pages.

## What Dragon Brain Finds

### 1. Contradiction Detection
```
search_memory("contradictions in Thornton's statements")
```
**Result:** James Thornton's March deposition states *"I had no knowledge of the shell companies"* — but an email from Sarah Chen to Thornton dated September 14th reads: *"Jim, the Alpha account is ready for the Q3 transfer."* Dragon Brain surfaces the contradiction automatically.

### 2. Entity Network Mapping
```
get_hologram("Shell Company Alpha")
```
**Result:** Full network visualization — who created it, money flows through it, linked entities, connected individuals, and every document that mentions it. One query, complete picture.

### 3. Connection Tracing
```
traverse_path(thornton_id, shell_alpha_id)
```
**Result:** Traces the hidden chain: Thornton → Chen → First National Bank → Shell Company Alpha. Shows exactly how an executive with "no knowledge" is connected to the entity through two intermediaries.

### 4. Timeline Reconstruction
```
point_in_time_query("what did we know about shell companies", as_of="2026-01-01")
```
**Result:** Shows the investigation's knowledge state BEFORE the whistleblower report — what was known, what was suspected, and what was completely invisible.

### 5. Lead Discovery
```
semantic_radar(thornton_id)
```
**Result:** Discovers that Thornton is semantically similar to **Shell Company Beta** (similarity: 0.78) — but there's NO relationship in the graph connecting them. Dragon Brain flags: *"High semantic similarity but no graph path — potential undiscovered connection."*

## 💡 The Holy Shit Moment

Query 5. Semantic radar discovers a connection the investigator hasn't found yet. Thornton's deposition language, email patterns, and financial references are semantically linked to Shell Company Beta — even though nobody has drawn that line. **Dragon Brain just surfaced a lead that wasn't in any document index.**

## Sample Data

| Category | Count | Examples |
|----------|-------|---------|
| People | 14 | CEO, CFO, whistleblower, board members, lawyers |
| Organizations | 5 | Meridian Corp, Apex Holdings, shell companies, bank |
| Documents | 18 | Depositions, email chains, financial reports, board minutes |
| Events | 4 | Earnings call, board meeting, wire transfer, whistleblower report |
| Relationships | 83 | EMPLOYED_BY, AUTHORED, TRANSFERRED_TO, CONTRADICTS, PRECEDED_BY |
| Observations | 50+ | Deposition quotes, email content, financial data, whistleblower notes |
