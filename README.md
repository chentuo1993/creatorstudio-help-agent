# Apple Creator Studio Help Agent

An English-language Q&A chatbot for Apple Creator Studio (Final Cut Pro, Logic Pro, Pixelmator Pro, Motion, Compressor, MainStage, Keynote, Pages, Numbers, Freeform). Answers are grounded in Apple's official user guides and always cite sources.

See [`PRD.md`](./PRD.md) for the one-page product spec and architecture rationale.

## Architecture (TL;DR)
- **Storage:** single SQLite file with FTS5 (BM25) + [`sqlite-vec`](https://github.com/asg017/sqlite-vec) (vectors). Fits a 256 MB Koyeb instance.
- **Retrieve:** hybrid (BM25 + vector) → RRF fusion → top-K (default K=**40** when rerank is on, **20** when off).
- **Rerank:** LLM-as-reranker (`deepseek` by default). **On** by default (`ENABLE_RERANK=true`); set `false` for lowest latency on tiny corpora.
- **Generate:** `grok-4-fast` with grounded prompt, optional **RECENT CONVERSATION** block for follow-ups (multi-turn).
- **API:** `POST /api/chat` with `{ "question": "…", "history": [{ "role": "user"|"assistant", "content": "…" }, …] }`.
- **Embeddings & LLM:** AI Builders Space OpenAI-compatible API, single `AI_BUILDER_TOKEN`.

### Measured Phase 0 latencies (30 FCP pages, 86 chunks, rerank off)
| Stage | p50 |
|---|---|
| Hybrid retrieve | 0.6–0.7s |
| Answer (`grok-4-fast`) | 2.0–2.5s |
| **Total e2e** | **~3s** |

```
ingest/   offline crawl → extract → chunk → embed → SQLite
app/      FastAPI online service (single process, single port)
data/     index.db (committed; built locally and pushed)
```

## Local development

### 1. Setup
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# fill AI_BUILDER_TOKEN in .env (or `set -a; source ~/.config/ai-builders-coach/.env; set +a`)
```

### 2. Build the index
```bash
# single app for testing
python -m ingest.run --app final-cut-pro --max-pages 30

# full build (all 10 apps, ~30–60 min crawl, ~$0.50 embeddings)
python -m ingest.run --all --max-pages 800
```
Crawls Apple Support guide pages → extracts clean text → chunks → embeds → writes `data/index.db`.

### 3. Run the server
```bash
uvicorn app.main:app --reload --port 8000
```
Open http://localhost:8000 and ask a question.

Health check: `curl http://localhost:8000/healthz`

## Deployment to ai-builders.space

1. Push this repo (with `data/index.db.gz`; the Dockerfile gunzips at build) to a public GitHub repo.
2. Confirm `Dockerfile` is at the root and uses `${PORT:-8000}` (it does).
3. From Cursor, ask the AI Builders deployment agent to deploy, providing:
   - GitHub URL
   - Service name (e.g. `creatorstudio-help`)
   - Branch (`main`)
4. The platform injects `AI_BUILDER_TOKEN` automatically.
5. Wait 5–10 min, then visit `https://creatorstudio-help.ai-builders.space`.

Optional non-secret env vars (already in `deploy-config.json`):
`EMBEDDING_MODEL`, `RERANK_MODEL`, `ANSWER_MODEL`, `DB_PATH`, `LOG_LEVEL`.

## Cost ceiling
Designed to stay **under $5** for the MVP demo:
- One-time index build: ~$0.13
- Per query: ~$0.0014 (embed + rerank + answer)
- $5 → ~3,400 queries

## Golden-set evaluation
```bash
# server running locally on :8000
python eval/run_golden.py --base http://127.0.0.1:8000
```
`eval/golden_set.json` holds 50 items (in-doc questions + a few out-of-scope refusals). For optional RAGAS faithfulness metrics, see `eval/run_ragas_optional.py` (install `ragas` first).

## What's intentionally NOT in MVP
- **Server-persisted** chat history (client sends `history` each turn; no DB of users)
- Non-English languages
- Real cross-encoder reranker (LLM-as-reranker is the 256 MB-friendly substitute)
- Authentication / per-user history
- Apple Communities forum data (high noise; V1 candidate)

## Repo map
```
PRD.md                 ← one-page product spec
Dockerfile             ← deployable to ai-builders.space
requirements.txt
deploy-config.json     ← non-secret deploy params
.env.example
ingest/
  config.py            ← list of apps + URL roots
  crawl.py             ← BFS over support.apple.com/guide/{slug}/...
  extract.py           ← trafilatura HTML→Markdown
  chunk.py             ← H2/H3-aware ~400-token chunks
  index.py             ← SQLite schema + embed + insert
  run.py               ← `python -m ingest.run`
app/
  main.py              ← FastAPI: /, /api/chat, /healthz
  config.py            ← env-driven Settings
  llm.py               ← AI Builders OpenAI client
  router.py            ← rule-based app classifier
  retrieval.py         ← hybrid: BM25 + vec → RRF
  rerank.py            ← LLM-as-reranker
  answer.py            ← grounded prompt + citations
  static/concept-a.html  ← Liquid Glass UI
eval/
  golden_set.json      ← 50-question set
  run_golden.py          ← p50 / pass-fail
data/
  index.db             ← built by ingest pipeline (committed)
```

## Roadmap
- **Phase 0** ✅ scaffold + ingest 30 FCP pages + e2e validated (~3s p50, accurate answers, refuses out-of-scope)
- **Phase 1** ✅ ingest all 10 apps (~thousands of pages) + Apple-style Liquid Glass UI + deploy to ai-builders.space
- **Phase 2**: turn rerank back on (now justified at this corpus size); 50-Q golden set + RAGAS eval CI; feedback loop
- **Phase 3**: multilingual, multi-turn, in-product embed, real cross-encoder rerank when memory budget allows
