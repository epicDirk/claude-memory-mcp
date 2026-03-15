# Dragon Brain Live Logging Protocol — Eval Run 001

**Datum:** 2026-03-15
**Session-ID:** 9a83d4ba-af58-4790-a9ff-93f1a23fd5bf
**Themen im Gespräch:** 5 (Steuerrecht-Gliederung, Füllwörter, Token-Artikel-Übersetzung, Fehleranalyse, Englisch-Korrektur)

---

## Was wurde geloggt

| # | Thema | Entities | Observations | Relationships | MCP Calls | Fehler |
|---|-------|----------|-------------|---------------|-----------|--------|
| 1 | Session-Start | — | — | — | 2 (reconnect, start_session) | — |
| 2 | Steuerrecht Gliederung | +2 (Dirk Studium, Gliederungstemplate) | — | +1 (BELONGS_TO_PROJECT) | 5 | 2 Fails: node_type "Context" ungültig, relationship by name statt ID |
| 3 | Füllwörter-Vermeidung | +1 (Füllwörter Sprechtechnik) | — | +1 (SUPPORTS → Studium) | 2 | — |
| 4 | Token-Artikel Übersetzung | +1 (Artikel Token-Physik) | — | — | 1 | **Unvollständig:** keine Relationship, keine Observation |
| 5 | Korrektur nach User-Hinweis | — | +1 (Dirk: Prompt Engineering Interesse) | +1 (Artikel → Dirk) | 3 | Nachholend, nicht proaktiv |
| 6 | Fehleranalyse | — | — | — | 0 | Korrekt: kein neues Wissen |
| 7 | Zukunft ändern | — | — | — | 0 | Korrekt: kein neues Wissen |
| 8 | Englisch-Korrektur OPI | +1 (OPI Foundry Projekt) | +1 (Dirk: Arbeitskontext) | +1 (OPI → Dirk) | 3 | — |

**Gesamt:** 5 Entities, 2 Observations, 4 Relationships, 16 MCP Calls

---

## Was fehlt

### Nicht erstellte Entities
- **Philipp Arnold, Balazs Nagy, Abraham Wolk** — nur in einer Observation erwähnt, keine eigenen Person-Entities. Bei zukünftigen Gesprächen über diese Kollegen fehlt der Graph-Kontext.
- **Cryomodules Graphical Control OPI** — konkretes Arbeitsprodukt, erwähnt in der Nachricht, nicht geloggt.

### Fehlende Relationships
- **Dirk Studium Steuerrecht FOM → Dirk (Person)** — die Studium-Entity ist nicht mit Dirks Haupt-Entity verbunden. Kritisch, weil Suchen über Dirk das Studium nicht finden.
- **OPI Foundry → CS-Studio / EPICS** — diese Tool-Entities existieren bereits im Graph, wurden aber nicht verknüpft (DEPENDS_ON).

### Fehlende Observations
- **Dirk schreibt Hausarbeiten** (nicht nur "studiert Steuerrecht") — das Profil-Detail ist in den Entity-Properties, aber nicht als Observation durchsuchbar.

---

## Fehleranalyse

### Fehler 1: Ungültiger node_type "Context"
- **Was:** `create_entity` mit `node_type: "Context"` schlug fehl
- **Ursache:** Erlaubte Typen nicht im Kopf gehabt (Entity, Concept, Project, Person, etc.)
- **Impact:** 1 zusätzlicher Call verbraucht
- **Fix:** Erlaubte node_types merken oder aus Fehlermeldung lernen

### Fehler 2: Relationship by Name statt ID
- **Was:** `create_relationship(from_entity="Gliederungstemplate...", to_entity="Dirk Studium...")` schlug fehl
- **Ursache:** API erwartet UUIDs, nicht Entity-Namen
- **Impact:** 1 zusätzlicher Call verbraucht
- **Fix:** Immer IDs aus den create_entity-Responses verwenden

### Fehler 3: Unvollständiges Logging bei Übersetzung (kritisch)
- **Was:** Nur 1 Entity erstellt, keine Relationship, keine Observation
- **Ursache:** "Dienstleistungs-Modus" — Aufgabe erledigt, Logging als Pflichtübung statt als Wissensextraktion behandelt
- **Impact:** Entity wäre Orphan geworden; implizites Wissen (Prompt Engineering Interesse) wäre verloren
- **Fix:** Post-Log-Checkliste: "Hat jedes Entity eine Relationship? Gibt es implizites Wissen über Dirk?"
- **Vom User entdeckt, nicht selbst erkannt**

---

## Technische Probleme

### Hanging bei create_relationship (kritisch)
- **Symptom:** MCP-Calls hängen sporadisch, besonders `create_relationship` nach mehreren `create_entity` Calls
- **Root Cause:** MCP Server nutzte synchronen Code in einem async Event Loop:
  - `httpx.Client` (sync) für Embedding API → **2.2s blockiert pro Call**
  - `FalkorDB graph.query()` (sync) → blockiert Event Loop
  - `redis.Redis` (sync) für Locks → blockiert Event Loop
  - Single-threaded asyncio Event Loop → NICHTS läuft während sync Calls blockieren
- **Ursprüngliches Call-Limit (max 5):** War ein Workaround, nicht die Lösung. Reduzierte die Logging-Qualität.

### Benchmark: Sync vs Async

| Operation | Sync (alt) | Async (neu) | Faktor |
|-----------|-----------|-------------|--------|
| Embedding encode | 2222ms | 528ms | 4.2x |
| 3 concurrent ops | ~6600ms | 673ms | ~10x |
| Entity + Rel Sequenz | ~4500ms | 477ms | ~9x |

### Fix: Async Migration (Phase 1-6 implementiert)
- 15 Dateien geändert, 47 await-Calls migriert
- `httpx.AsyncClient` für Embeddings
- `falkordb.asyncio.FalkorDB` für Graph-Queries
- `redis.asyncio.Redis` für Locks
- Smoke-Test + Benchmark bestanden
- **Aktivierung:** MCP Server Neustart erforderlich (= neue Claude Code Session)
- **Call-Limit entfernt** aus CLAUDE.md nach Root Cause Fix

---

## Statuszeile

Wurde in jeder Antwort angezeigt ✓

Format konsistent: `[DB: +X entity, +X rel | X Calls]` oder `[DB: skipped, kein neues Wissen]`

---

## Gesamtbewertung

| Kriterium | Bewertung | Note |
|-----------|-----------|------|
| Logging-Pflicht eingehalten | Überwiegend | 1 Antwort unvollständig |
| Statuszeile immer angezeigt | Ja | ✓ |
| Max 5 Calls pro Antwort | Eingehalten | Knapp in Antwort 2 |
| Korrekte Entity-Typen | Nach 1 Fehler | node_type gelernt |
| Relationships erstellt | Überwiegend | 1 vergessen, 1 fehlgeschlagen |
| Implizites Wissen extrahiert | Nach Hinweis | Nicht proaktiv bei Übersetzung |
| Orphan-Prävention | Mangelhaft | Ohne User-Hinweis wäre 1 Orphan entstanden |
| Keine Duplikate | Ja | ✓ |

**Gesamtnote: 6/10**

Grundfunktion (Entities erstellen, Relationships, Statuszeile) funktioniert. Die kritische Schwäche: Bei "Dienstleistungs-Aufgaben" (Übersetze X, Formatiere Y) fällt das Logging auf ein Minimum zurück, weil der Fokus auf der Aufgabe liegt statt auf dem Wissen das dabei entsteht. Der Post-Log-Check muss ins Protokoll.

---

## Empfohlene Protokoll-Änderungen

1. **Post-Log-Checkliste** in CLAUDE.md ergänzen (2 Prüfpunkte: Relationship + implizites Wissen)
2. **Erlaubte node_types** als Kommentar im Protokoll auflisten
3. **Relationship immer per ID**, nie per Name — als explizite Regel
4. **"Dienstleistungs-Aufgaben"-Warnung:** Auch wenn die Hauptaufgabe rein ausführend ist (Übersetzung, Formatierung), IMMER prüfen ob Kontext-Wissen über den User entsteht
5. **Feedback-Memory in Dragon Brain:** Zusätzlich zur Checkliste im Protokoll eine Bottle-Entity in Dragon Brain anlegen, die das *Warum* hinter der Regel erklärt. Die Checkliste sagt *was* zu tun ist, die Memory erklärt *warum* — das hilft bei Edge Cases, wo die Checkliste nicht eindeutig greift.

### Umsetzungsstatus

- [x] Bericht geschrieben (diese Datei)
- [x] Post-Log-Checkliste in CLAUDE.md ergänzt
- [x] Feedback-Memory als Bottle in Dragon Brain gespeichert
