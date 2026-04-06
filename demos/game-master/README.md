# 🎲 Game Master / Worldbuilder

> **Your AI remembers every NPC, every quest, every player decision — across 50+ sessions.**

## The Scenario

**The Shattered Crown** — a D&D campaign spanning 20 sessions. 12 NPCs with secret motivations, 4 competing factions, player decisions that rippled through the world in ways nobody tracked. Campaign continuity that would take hours to reconstruct from session notes.

## What Dragon Brain Finds

### 1. Betrayal Network
```
search_memory("who betrayed whom and why")
```
**Result:** Full betrayal map with context and session references. Who turned, when, the motivations documented across multiple sessions, and which players were present for each reveal.

### 2. NPC Deep Dive
```
get_hologram("Aldric")
```
**Result:** Public alliances + secret rebel funding + the courier interception in Session 12 + the fact that *players still don't know about his connection to the tax policy*. One query reveals both what the GM knows and what the players have discovered.

### 3. Consequence Chains
```
search_memory("consequences of sparing the dragon")
```
**Result:** Traces the ripple effects of a single player decision: spared the dragon → Scalecrest alliance formed → Crown became hostile → 3 new quest opportunities opened → map fragment discovered in the dragon's hoard.

### 4. Knowledge State
```
point_in_time_query("what do the players know about the crown fragments", as_of="session-14")
```
**Result:** At Session 14, players believed there were 3 fragments. The dragon hoard discovery in Session 15 revealed there are actually 5. Perfect for managing dramatic irony.

### 5. Political Web
```
traverse_path(king_maren_id, aldric_id)
```
**Result:** King Maren → oppressive taxes → border town rebellion → Aldric's secret funding → courier intercepted by players. The complete political chain that no player has fully connected yet.

## 💡 The Holy Shit Moment

A player asks *"wait, why did the rebellion start?"* The GM queries Dragon Brain and traces the ENTIRE causal chain from King Maren's tax policy through Aldric's secret funding to the courier the players intercepted 7 sessions ago. **Continuity that no human GM could maintain across 20 sessions.**

## Sample Data

| Category | Count | Examples |
|----------|-------|---------|
| NPCs | 12 | Characters with backstories and hidden motivations |
| Locations | 8 | Towns, dungeons, landmarks |
| Quests | 6 | Active/completed with objectives and outcomes |
| Factions | 4 | Competing groups with agendas |
| Sessions | 8 | Session summaries with key events |
| Relationships | 75 | ALLIED_WITH, HOSTILE_TO, BETRAYED, QUEST_GIVER, EVOLVED_FROM |
