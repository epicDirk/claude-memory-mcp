# 🐉 Dragon Brain — Showcase Demos

> **Same Dragon Brain, different story.** No custom features, no vertical code — just your data, your queries, and connections you didn't know existed.

Pick a demo that matches your world. Each one shows Dragon Brain solving real problems in a specific domain — with sample data, example queries, and the "holy shit" moment where the AI finds something a human would miss.

## The Demos

| # | Demo | Who It's For | The Hook |
|---|------|-------------|----------|
| 1 | [Legal Discovery](legal-discovery/) | Lawyers, compliance teams | Find contradictions across depositions |
| 2 | [Research Lab](research-lab/) | Academics, ML researchers | Track your lab's evolving understanding |
| 3 | [Startup CTO](startup-cto/) | Engineers, founders | Never lose a design decision again |
| 4 | [Investigative Journalist](investigative-journalist/) | Journalists, OSINT analysts | Connect the dots across sources |
| 5 | [Game Master](game-master/) | D&D players, worldbuilders | Remember 50 sessions of campaign history |
| 6 | [Personal Knowledge](personal-knowledge/) | Zettelkasten, PKM enthusiasts | Cross-domain connections you'd never find manually |
| 7 | [Cybersecurity SOC](cybersecurity-soc/) | Security analysts, threat intel | Threat intel that actually links up |
| 8 | [Open Source Maintainer](open-source-maintainer/) | OSS maintainers, contributors | 3 years of project history, instantly searchable |
| 9 | [Portfolio Manager](portfolio-manager/) | Traders, quant analysts | Trading brain that never forgets a regime change |
| 10 | [Medical Practice](medical-practice/) | Clinicians, health tech | Patient connections your EHR buries |
| 11 | [Engineering R&D](engineering-rnd/) | Hardware engineers, EE/ME teams | Failure modes that connect across subsystems |
| 12 | [Teacher](teacher/) | Educators, course designers | Teaching that adapts from every student interaction |
| 13 | [University Student](university-student/) | Students, grad researchers | Cross-course connections no textbook makes |

## How It Works

Every demo uses the **exact same Dragon Brain** — no plugins, no customization. The magic is in how knowledge graphs + vector search + temporal awareness combine to surface connections that flat note-taking systems miss.

```
You store entities → observations → relationships
Dragon Brain finds → contradictions → hidden links → evolving patterns
```

## Quick Start

```bash
# 1. Start Dragon Brain
docker compose up -d

# 2. Pick a demo and load its sample data
python demos/legal-discovery/load_data.py

# 3. Run the example queries
python demos/legal-discovery/run_queries.py
```

## What Makes Dragon Brain Different

| Feature | What It Does | Why It Matters |
|---------|-------------|----------------|
| **Semantic Radar** | Finds entities that are semantically similar but not connected in your graph | Discovers leads, connections, and patterns you haven't explicitly noted |
| **Time Travel** | Query your knowledge as it existed at any point in time | Replay your understanding before a breakthrough changed everything |
| **Hologram** | Full 360° context for any entity — neighbors, observations, connections | Never ask "what do we know about X?" and get a partial answer |
| **Path Tracing** | Find the shortest connection chain between any two entities | "How is A connected to B?" — through entities you didn't realize were bridges |
| **Knowledge Gaps** | Automatically detect semantically related entities with no graph link | "You should investigate this — it's related but you haven't connected it" |
