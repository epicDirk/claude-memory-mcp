# Dragon Brain - Windows Installation Guide

Installationsanleitung basierend auf den Learnings der Erstinstallation auf Windows 11 Pro.
Dieses Dokument dokumentiert alle Abweichungen vom Standard-Setup und bekannte Fixes.

## Voraussetzungen

- **Windows 11** (getestet mit Pro 10.0.26200)
- **Python 3.12+** (getestet mit 3.14.2)
- **Docker Desktop 4.64+** mit WSL 2 Backend
- **VS Code** mit offizieller Claude Extension
- **Git**

## Schritt 1: Docker Desktop installieren

1. Download: https://www.docker.com/products/docker-desktop/
2. Bei der Konfiguration:
   - **WSL 2 instead of Hyper-V**: JA (angehakt lassen)
   - **Windows Containers**: NEIN (nicht nötig, Projekt nutzt Linux-Container)
   - **Desktop Shortcut**: optional
3. Nach Installation: **Neustart erforderlich**
4. Nach Neustart: Docker Desktop starten und warten bis es "running" zeigt

## Schritt 2: Repository klonen

```bash
git clone https://github.com/iikarus/claude-memory-mcp.git "C:/Users/DEIN_USER/Documents/Dragon Brain"
```

## Schritt 3: Zwei Bugs im Repo fixen (vor dem ersten Build!)

### Fix 1: .dockerignore blockiert README.md

Das Dockerfile braucht `README.md` im Build-Context, aber `.dockerignore` schliesst alle `*.md` aus.

**Datei:** `.dockerignore`
**Zeile:** `*.md` ersetzen durch `CONTRIBUTING.md`

```diff
 # Documentation
 docs/
-*.md
+CONTRIBUTING.md
 LICENSE
```

### Fix 2: Dashboard fehlt nest_asyncio

Der Dashboard-Container crasht mit `ModuleNotFoundError: No module named 'nest_asyncio'`.

**Datei:** `Dockerfile`
**Zeile ~35:** `nest_asyncio` zur pip install Zeile hinzufuegen:

```diff
-RUN pip install --no-cache-dir torch==2.9.1 sentence-transformers qdrant-client redis fastapi uvicorn httpx
+RUN pip install --no-cache-dir torch==2.9.1 sentence-transformers qdrant-client redis fastapi uvicorn httpx nest_asyncio
```

## Schritt 4: Docker-Container starten

```bash
cd "C:/Users/DEIN_USER/Documents/Dragon Brain"
docker compose up -d
```

Das dauert beim ersten Mal **10-20 Minuten** (Images werden gebaut, Modelle heruntergeladen).

Danach pruefen:

```bash
docker compose ps
```

Alle 4 Container muessen "healthy" sein:

| Container | Port | Funktion |
|-----------|------|----------|
| dragonbrain-graphdb | 6379 | FalkorDB (Knowledge Graph) |
| dragonbrain-qdrant | 6333 | Qdrant (Vector Search) |
| dragonbrain-embeddings | 8001 | BGE-M3 Embedding API |
| dragonbrain-dashboard | 8501 | Streamlit Dashboard |

Dashboard erreichbar unter: http://localhost:8501

## Schritt 5: Python-Dependencies lokal installieren

Der MCP-Server laeuft als lokaler Python-Prozess (nicht im Docker).

```bash
cd "C:/Users/DEIN_USER/Documents/Dragon Brain"
pip install -e .
```

**Hinweis:** Es kommen Warnungen dass Scripts nicht im PATH sind. Das ist okay, der MCP-Server wird ueber `python -m claude_memory.server` gestartet, nicht ueber ein Script.

## Schritt 6: MCP-Server in Claude Code registrieren

Es gibt zwei Methoden. **Methode B (mcp.json)** ist empfohlen — sie ist einfacher, zuverlaessiger, und braucht kein PowerShell-Script.

Datei erstellen: `C:/Users/DEIN_USER/.claude/mcp.json`

```json
{
  "mcpServers": {
    "claude-memory": {
      "command": "python",
      "args": ["-m", "claude_memory.server"],
      "cwd": "C:\\Users\\DEIN_USER\\Documents\\Dragon Brain",
      "env": {
        "PYTHONPATH": "C:\\Users\\DEIN_USER\\Documents\\Dragon Brain\\src",
        "FALKORDB_HOST": "localhost",
        "FALKORDB_PORT": "6379",
        "FALKORDB_PASSWORD": "",
        "QDRANT_HOST": "localhost",
        "QDRANT_PORT": "6333",
        "EMBEDDING_API_URL": "http://localhost:8001"
      }
    }
  }
}
```

**Wichtig — Python direkt, NICHT PowerShell:**

Das Repo liefert ein `mcp_config.example.json` mit `powershell.exe` als Launcher. Das funktioniert **nicht zuverlaessig** mit Claude Code in VS Code — der stdio-Handshake scheitert wegen PowerShell-Startup-Latenz, und die MCP-Tools erscheinen nicht.

Der Fix: `python -m claude_memory.server` direkt aufrufen (wie oben gezeigt). Das `cwd`-Feld setzt das Arbeitsverzeichnis, damit Python den Code findet.

**Hinweise:**
- Datei liegt in `~/.claude/` und gilt global fuer alle Projekte
- Die CLI-Methode (`claude mcp add`) funktioniert auch, schreibt aber in dieselbe `mcp.json` — manuelles Editieren ist einfacher
- Falls sowohl `claude mcp add` als auch manuell editierte `mcp.json` existieren, kann es zu Doppel-Registrierungen kommen

## Schritt 7: VS Code neu starten

Claude Code muss neu gestartet werden, damit der MCP-Server geladen wird. Danach sollten ~30 Memory-Tools verfuegbar sein (create_entity, search_memory, etc.).

## Verifizierung

Nach dem Neustart testen:

1. Claude fragen: "Starte eine Dragon Brain Session"
2. Claude sollte `start_session()` aufrufen koennen
3. Im Dashboard (http://localhost:8501) sollten neue Nodes erscheinen

## Bekannte Probleme

### Haenger bei Bulk-Entity-Erstellung
Bei vielen aufeinanderfolgenden Entity/Relationship-Erstellungen (~2.5s pro Call) kann VS Code traege werden. Kein Datenverlust, aber VS Code Neustart kann noetig sein.

### Entity-Typen sind beschraenkt
Erlaubte `node_type` Werte: `Entity`, `Concept`, `Project`, `Person`, `Decision`, `Session`, `Breakthrough`, `Analogy`, `Observation`, `Tool`, `Issue`, `Bottle`, `Procedure`. Fuer Organisationen, Hardware etc. den Typ `Entity` verwenden und den spezifischen Typ in `properties` ablegen.

### Ghost Graph `memory_graph` in FalkorDB

FalkorDB kann neben dem eigentlichen Graphen `claude_memory` einen leeren Ghost Graph namens `memory_graph` enthalten. Dieser entsteht vermutlich durch einen initialen Verbindungstest oder Default-Konfiguration.

**Problem:** Tools oder Abfragen die den falschen Graph-Namen verwenden, bekommen 0 Ergebnisse zurueck obwohl Daten vorhanden sind.

**Diagnose:**

```bash
docker exec dragonbrain-graphdb-1 redis-cli GRAPH.LIST
```

Wenn dort sowohl `claude_memory` als auch `memory_graph` erscheinen:

```bash
# Pruefen ob memory_graph leer ist (sollte 0 sein)
docker exec dragonbrain-graphdb-1 redis-cli GRAPH.QUERY memory_graph "MATCH (n) RETURN count(n)"

# Ghost Graph loeschen
docker exec dragonbrain-graphdb-1 redis-cli GRAPH.DELETE memory_graph
```

**Erwarteter Zustand:** `GRAPH.LIST` zeigt nur `claude_memory`.

### MCP-Tools nicht verfuegbar trotz laufender Container

Wenn Claude die Dragon Brain MCP-Tools (create_entity, search_memory, etc.) nicht findet, obwohl alle Docker Container "healthy" sind:

1. **MCP-Server separat pruefen** — der MCP-Server laeuft als lokaler Python-Prozess, nicht im Docker. Die Container allein reichen nicht.
2. **Pruefen ob `mcp.json` korrekt ist** — der Server MUSS mit `python -m claude_memory.server` gestartet werden, NICHT ueber `powershell.exe` (siehe Schritt 6).
3. **Import testen:**
   ```bash
   cd "C:/Users/DEIN_USER/Documents/Dragon Brain"
   PYTHONPATH="src" python -c "from claude_memory.server import mcp; print('Import OK')"
   ```
   Falls das fehlschlaegt: `pip install -e .` wiederholen.
4. **Verwaiste Python-Prozesse pruefen** — nach mehreren Neustarts koennen alte MCP-Server-Prozesse haengen:
   ```bash
   # Laufende Python-Prozesse anzeigen
   tasklist | grep python
   # Falls alte Prozesse da sind: VS Code schliessen, Prozesse beenden, VS Code neu starten
   taskkill /F /PID <PID>
   ```
5. **VS Code komplett neu starten** (nicht nur das Terminal) — der MCP-Server wird beim Start von Claude Code geladen.
6. **Fallback:** Daten koennen direkt via `docker exec` abgefragt werden:

```bash
# Alle Entities auflisten
docker exec dragonbrain-graphdb-1 redis-cli GRAPH.QUERY claude_memory "MATCH (n) WHERE n.name IS NOT NULL RETURN n.name, n.entity_type ORDER BY n.name"

# Observations einer Entity lesen
docker exec dragonbrain-graphdb-1 redis-cli GRAPH.QUERY claude_memory "MATCH (n {name: 'ENTITY_NAME'})-[:HAS_OBSERVATION]->(o) RETURN o.content, o.certainty"

# Relationships einer Entity lesen
docker exec dragonbrain-graphdb-1 redis-cli GRAPH.QUERY claude_memory "MATCH (n {name: 'ENTITY_NAME'})-[r]-(m) RETURN type(r), m.name, m.entity_type"
```

### Docker Container nach Neustart
Docker Desktop startet Container nicht automatisch nach Windows-Neustart (abhaengig von Einstellungen). Pruefen mit:

```bash
docker compose -f "C:/Users/DEIN_USER/Documents/Dragon Brain/docker-compose.yml" ps
```

Falls nicht laufend:

```bash
cd "C:/Users/DEIN_USER/Documents/Dragon Brain"
docker compose up -d
```

## Schritt 8: Anthropic Skills installieren (optional)

Anthropic stellt offizielle Skills bereit, die Claude Code um Dokumenten-Verarbeitung und Skill-Erstellung erweitern. Skills werden global in `~/.claude/skills/<skill-name>/SKILL.md` installiert und stehen damit in allen VS Code Projekten zur Verfuegung.

**Quelle:** https://github.com/anthropics/skills/tree/main/skills

### Empfohlene Skills

| Skill | Funktion |
|-------|----------|
| `docx` | Word-Dokumente (.docx) lesen, erstellen, bearbeiten |
| `pptx` | PowerPoint-Dateien (.pptx) lesen, erstellen, bearbeiten |
| `skill-creator` | Neue Skills erstellen, testen, benchmarken |

### Installation

```bash
# Skills-Verzeichnis anlegen (falls nicht vorhanden)
mkdir -p ~/.claude/skills

# Repo klonen (temporaer)
git clone https://github.com/anthropics/skills.git /tmp/anthropic-skills

# Skills kopieren
cp -r /tmp/anthropic-skills/skills/docx ~/.claude/skills/
cp -r /tmp/anthropic-skills/skills/pptx ~/.claude/skills/
cp -r /tmp/anthropic-skills/skills/skill-creator ~/.claude/skills/

# Temp-Repo aufraeumen
rm -rf /tmp/anthropic-skills
```

### Dependencies installieren

Die Skills brauchen externe Tools fuer Datei-Verarbeitung:

```bash
# Python-Packages (fuer docx + pptx lesen/bearbeiten)
pip install markitdown python-docx

# Pandoc (fuer docx lesen — alternativer Parser)
# Download: https://pandoc.org/installing.html
# Oder via winget:
winget install --id JohnMacFarlane.Pandoc

# Node.js Package (fuer pptx erstellen)
npm install -g pptxgenjs
```

**Installierte Versionen (Referenz):**

| Dependency | Version | Verwendet von |
|------------|---------|---------------|
| markitdown | 0.1.5 | docx, pptx (Text-Extraktion) |
| python-docx | 1.2.0 | docx (Word-Dateien bearbeiten) |
| pandoc | (system) | docx (alternativer Parser) |
| pptxgenjs | 4.0.1 | pptx (Praesentationen erstellen) |

### Verifizierung

Nach Installation VS Code neu starten. Claude sollte die Skills automatisch erkennen. Testen:

```
User: "Lies bitte die Datei test.docx"
→ Claude nutzt den docx-Skill
```

Skills erscheinen in der VS Code Claude-Sidebar und werden als verfuegbare Slash-Commands gelistet.

## Schritt 9: CLAUDE.md konfigurieren

Die Datei `~/.claude/CLAUDE.md` steuert Claudes Verhalten global. Fuer Dragon Brain muss das **Live Logging Protocol** enthalten sein, damit Claude automatisch Wissen in den Knowledge Graph speichert.

### CLAUDE.md fuer Dragon Brain

Die Datei `~/.claude/CLAUDE.md` steuert Claudes Verhalten global. Erstelle sie unter `C:/Users/DEIN_USER/.claude/CLAUDE.md` mit folgendem Inhalt:

```markdown
# Persoenliche Notizen fuer Claude

## Dragon Brain (Memory MCP)

Pruefe zu Beginn jeder Session ob Dragon Brain erreichbar ist:

docker compose -f "C:/Users/DEIN_USER/Documents/Dragon Brain/docker-compose.yml" ps --format "table {{.Name}}\t{{.Status}}"

Melde dem User kurz den Status (laeuft / laeuft nicht). Starte die Container NICHT automatisch — falls sie nicht laufen, weise den User darauf hin.

### Live Logging Protocol

**Oberste Regel:** Alles Logging passiert still im Hintergrund. Keine Meldungen an den User — nur bei Fehlern.

#### Session-Management
- Bei Gespraechsbeginn: `reconnect()` aufrufen, `start_session(project_id, focus)` starten
- **project_id themen-basiert** waehlen: `coding`, `gesundheit`, `persoenlich`, `lernen`, `finanzen`, `kreativ` (oder passend)
- `reconnect()`-Ergebnisse nur teilen wenn der User danach fragt
- **Wichtig:** `end_session()` erfordert die `session_id` als Parameter. Merke dir die Session-ID beim Start.
- Bei **Themenwechsel**:
  1. Ein Themenwechsel liegt vor wenn sich das **Fachgebiet** aendert (z.B. Arbeit -> Privat, Projekt A -> Projekt B). **Kein** Themenwechsel: Zwei persoenliche Themen hintereinander (z.B. E-Mail fuer Jean-Pascal -> CV von Dirk) bleiben in derselben Session, solange die project_id gleich bleibt.
  2. Mehrere Nachrichten zum selben Fachgebiet (z.B. verschiedene Slack-Messages ueber ESS-Arbeit) sind KEIN Themenwechsel
  3. **project_id** richtet sich nach dem Inhalt, nicht nach dem Format (eine Slack-Nachricht ueber Code-Arbeit = `coding`, nicht `persoenlich`)
  4. `search_memory()` mit Stichworten des bisherigen Themas — ist alles gespeichert?
  5. Fehlende Observations/Relationships nachholen
  6. `end_session(session_id, summary)` mit kurzer Summary
  7. Neue Session mit passender project_id starten

#### Kontinuierliches Logging

**Grundregel:** Speichere alles, was in einer zukuenftigen Konversation nuetzlich sein koennte. Sofort speichern, nicht sammeln, nicht warten.

**Vor dem Speichern:** Immer erst `search_memory()` nutzen um zu pruefen ob die Entity bereits existiert. Keine Duplikate erstellen — stattdessen bestehende Entity mit `add_observation()` ergaenzen.

**Nach dem Erstellen:** Jede neue Entity MUSS mindestens eine Relationship erhalten. Erstelle die Relationship im selben Tool-Call-Block wie die Entity. Entities ohne Relationships werden zu Orphans und verlieren ihren Kontext.

**Wie speichern — das richtige Tool waehlen:**
- Neue Sache (Person, Ort, Projekt, Idee, Tool, Problem, Gewohnheit, Ziel...) -> `create_entity()` mit passendem `node_type` (Person, Concept, Project, Decision, Tool, Issue, Breakthrough, Analogy, Bottle, Procedure — oder neuen Typ via `create_memory_type()`)
- Neues Detail ueber bestehende Sache -> `add_observation()` an die passende Entity
- Verbindung zwischen zwei Sachen -> `create_relationship()` — RELATED_TO nur als letzter Ausweg. Bevorzuge spezifische Typen: PART_OF, CREATED_BY, DEPENDS_ON, BELONGS_TO_PROJECT, ENABLES, SUPPORTS, ANALOGOUS_TO, TAUGHT_THROUGH. Wenn kein passender Typ existiert, nutze die `properties` der Relationship fuer Kontext (z.B. `{"role": "Student-Dozent"}`) statt auf RELATED_TO zurueckzufallen.
- Aha-Moment / Durchbruch -> `record_breakthrough()`
- Notiz fuer die Zukunft -> `create_entity(node_type="Bottle")`

**Beispiele:**
- "Ich bin Steuerberater" -> Entity(name="Dirk", type="Person") + Observation("Ist Steuerberater", certainty="confirmed")
- "React finde ich besser als Vue" -> Observation an bestehende Entity: "Bevorzugt React gegenueber Vue"
- "Mein Knie macht mir Probleme" -> Entity(name="Knie-Problem", type="Issue") + Relationship(Dirk -> Knie-Problem)
- "Naechsten Monat ziehe ich um" -> Entity(name="Umzug", type="Concept") + Observation mit Zeitangabe
- "Ach so, DESHALB funktioniert das!" -> `record_breakthrough()`
- "Nicht so, mach es lieber mit TypeScript" -> Observation("Korrektur: bevorzugt TypeScript-Loesungen")
- E-Mail mit CC-Liste -> Alle genannten Personen als Entities anlegen, nicht nur Absender/Empfaenger
- Erwaehnte Personen in Nachrichtentext (z.B. "@Horus Cardona") -> ebenfalls als Entity mit Relationship anlegen

**Implizite Entities:** Wenn aus dem Kontext klar wird, dass ein Projekt, Vorhaben oder Thema existiert (z.B. "Bachelorarbeit", "Umzug", "Jobwechsel"), erstelle dafuer eine eigene Entity (typ Project/Concept), auch wenn der User es nicht als eigenstaendiges Ding benennt. Verbinde sie sofort mit den beteiligten Personen.

**Personen-Kontext:** Wenn der User ueber/fuer andere Personen spricht, klaere (oder spekuliere mit `speculative`) die Beziehung zum User. Erstelle eine Relationship zwischen User und der Person mit Kontext in den Properties (z.B. `{"role": "Sohn"}`, `{"role": "Kollege"}`).

**Dokumente:** Wenn der User ein Dokument teilt (CV, Brief, Vertrag), logge die Kern-Fakten als Observations an die relevante Entity. Logge auch Meta-Beobachtungen (z.B. "CV endet 2016, aktuelle Taetigkeit fehlt") als Observation mit `speculative`.

**Certainty:** User sagt es explizit -> `confirmed` · Claude schliesst aus Kontext -> `speculative` · Brainstorming -> `spitballing`
*(Gueltige Werte: confirmed, speculative, spitballing, rejected, revisited)*

**Atomicity:** Ein Fakt pro Observation. Nie buendeln.

#### Orphan-Check (alle ~10 Interaktionen)
- `list_orphans()` aufrufen
- Fuer gefundene Orphans passende Relationships erstellen

#### Was NICHT gespeichert wird
- Rohe Chat-Transkripte
- Einmalige/temporaere Details ("oeffne mal Datei X")
- Passwoerter, Secrets, API-Keys
```

**Nach dem Kopieren:** Alle Vorkommen von `DEIN_USER` durch den tatsaechlichen Windows-Benutzernamen ersetzen.

## Pfade-Uebersicht

| Was | Pfad |
|-----|------|
| Repo | `C:/Users/DEIN_USER/Documents/Dragon Brain/` |
| MCP Config (empfohlen) | `C:/Users/DEIN_USER/.claude/mcp.json` |
| MCP Config (alternativ) | `C:/Users/DEIN_USER/.claude.json` (unter `mcpServers`, via CLI) |
| Docker Volumes | Managed by Docker Desktop |
| Dashboard | http://localhost:8501 |
| Embedding API | http://localhost:8001 |
| FalkorDB | localhost:6379 |
| Qdrant | localhost:6333 |
