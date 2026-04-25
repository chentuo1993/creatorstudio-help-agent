# Help Agent for Apple Creator Studio — MVP PRD

> **Owner:** Tuochen · **Status:** Draft v0.1 · **Target launch:** ~3 weeks · **Budget:** ≤ $5 (LLM/embedding)

## 1. Problem & Goal
Apple Creator Studio bundles 11+ creative apps (Final Cut Pro, Logic Pro, Pixelmator Pro, Motion, Compressor, MainStage, Keynote, Pages, Numbers, Freeform, Final Cut Camera). New users frequently ask "how do I use feature X?" and have to dig through long user guides. We will build an English-language Q&A chatbot that answers feature usage questions grounded in Apple's official documentation, with citations.

**MVP success = a user can ask a feature question in English and get a correct, cited answer in < 5 seconds.**

## 2. Non-goals (MVP)
- Multi-language (Chinese, etc.) — V2
- Multi-turn conversation memory — V2
- Troubleshooting that requires telemetry / device state — out of scope
- Billing / account questions — out of scope
- Image / video understanding — out of scope

## 3. Target Users & Jobs-to-be-Done
| User | JTBD |
|---|---|
| New subscriber exploring an app | "What does Beat Detection do and how do I turn it on?" |
| Existing user stuck on a workflow | "How do I export a Final Cut Pro project for YouTube?" |
| Educator / student | "Which iPads support Pixelmator Pro?" |

## 4. Scope: Apps in MVP knowledge base
Final Cut Pro · Motion · Compressor · Logic Pro · MainStage · Pixelmator Pro · Keynote · Pages · Numbers · Freeform · (Final Cut Camera deferred to V1 if doc coverage is thin)

Data source = `support.apple.com/guide/{app}/...` (official user guides) + `support.apple.com/en-us/125029` (Creator Studio support hub).

## 5. UX (MVP)
- Single-page web UI hosted at `https://creatorstudio-help.ai-builders.space/`
- Input box → answer area → up to 3 cited source links (deep-linked into Apple guides)
- "Was this helpful?" 👍/👎 button writing to local SQLite for later eval
- No login, no history, no settings

## 6. Architecture (one diagram)
```
            ┌────────────────────────────────────────────────────┐
            │  ai-builders.space  (256 MB RAM, Dockerfile)       │
            │                                                     │
   user ──► │  FastAPI (single process)                          │
            │   ├─ /            → static SPA (HTML+JS)            │
            │   ├─ /api/chat    → answer pipeline                 │
            │   └─ /api/feedback                                  │
            │                                                     │
            │   pipeline:                                         │
            │     1. classify app (rule + 1 small LLM call)       │
            │     2. hybrid retrieve (FTS5 BM25 + sqlite-vec)     │
            │        → RRF fusion → top-50                        │
            │     3. LLM-as-reranker (deepseek) → top-5           │
            │     4. answer LLM (grok-4-fast) with citations      │
            │                                                     │
            │   storage: SQLite file (~50MB), checked into repo   │
            │   external: AI Builders Space /v1/{embeddings,chat} │
            └────────────────────────────────────────────────────┘
```

## 7. Tech Stack
- **Lang:** Python 3.11
- **Server:** FastAPI + uvicorn
- **Storage:** SQLite with [`sqlite-vec`](https://github.com/asg017/sqlite-vec) (vectors) + FTS5 (BM25). Single ~50 MB file committed at `data/index.db`.
- **Embedding:** `text-embedding-3-small` via `https://space.ai-builders.com/backend/v1/embeddings`
- **LLM:** `deepseek` (rerank, cheap) and `grok-4-fast` (final answer) via the same endpoint
- **Crawl & extract:** `httpx` + `trafilatura`
- **Frontend:** vanilla HTML + JS (no build step — keeps Docker image small)
- **Deployment:** Docker → `ai-builders.space` (free 12 mo, public GitHub repo)

## 8. Data pipeline (offline, runs locally on dev machine)
1. **Discover** — for each app, enumerate URLs from the guide's `welcome` page TOC (BFS, restrict to `support.apple.com/guide/{app}/.../mac` or `/ipad` or `/iphone`).
2. **Fetch** — `httpx` with 1 req/s rate limit, polite UA.
3. **Extract** — `trafilatura.extract()` keeps clean prose + heading hierarchy.
4. **Chunk** — split along H2/H3, target 400 tokens, 80-token overlap.
5. **Embed** — batch 96 chunks/request to `text-embedding-3-small`.
6. **Index** — write to SQLite: `chunks(id, app, platform, breadcrumbs, url, text)` + FTS5 virtual table + `sqlite-vec` vector table.

The resulting `data/index.db` is committed to the repo so the deployed container needs **zero build-time embedding**.

## 9. Online query pipeline
1. **Classify app** — regex match on app names; if zero hits, single deepseek call returns app(s).
2. **Hybrid retrieve** — `WHERE app IN (...)` filter + FTS5 BM25 top-50 + sqlite-vec top-50, then **RRF** fusion → 50 candidates.
3. **Rerank** — one deepseek call: prompt = "score each chunk's relevance to the query 0–10", parse → keep top 5.
4. **Generate** — grok-4-fast with grounded prompt: "Answer only from CONTEXT. If not found, say 'I couldn't find this in the docs.' Always cite source URLs."
5. Return `{answer, citations[], retrieved_chunk_ids[]}`.

## 10. Cost ceiling
| Item | Calc | Cost |
|---|---|---|
| Build index (one-time) | ~6.6M tok @ $0.02/M | $0.13 |
| Per query | 1× embed + 1× rerank + 1× generate | ~$0.0014 |
| MVP demo budget | 3,400 queries | < $5 |

## 11. Evaluation (gating MVP launch)
- **Golden set:** 50 hand-written Q+expected-answer pairs spanning all 11 apps.
- **Auto metrics:** RAGAS `faithfulness`, `answer_relevancy`, `context_precision`.
- **Bar:** faithfulness ≥ 0.85, answer_relevancy ≥ 0.80, p95 latency ≤ 5s.

## 12. Risks & mitigations
| Risk | Mitigation |
|---|---|
| 256 MB RAM blows up at peak | SQLite is memory-mapped, ~30 MB working set; cap concurrent requests at 4 in uvicorn |
| Apple changes doc URLs | Re-run ingest weekly via GitHub Action; commit fresh `index.db` |
| Hallucination | Grounded prompt + "I don't know" fallback + citation requirement |
| Cost overrun | `lifetime_cost` ceiling check via AI Builders cost API every 100 queries |

## 13. Roadmap
- **Phase 0 (week 1):** scaffold + ingest 1 app (Final Cut Pro) e2e
- **Phase 1 (week 2):** ingest all 11 apps, golden set, deploy
- **Phase 2 (post-MVP):** real cross-encoder rerank, multi-turn, eval CI, feedback loop
- **Phase 3:** multilingual, conversational memory, embed in product
