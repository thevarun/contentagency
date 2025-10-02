# Vision

Create a personal, web‑based **agentic content agency** that turns a seed idea into high‑quality, multi‑platform posts (LinkedIn, Twitter/X, and  Medium), with **human‑in‑the‑loop review**, **draft storage**, and **scheduled publishing**. The system should feel like a capable junior team (strategist → writer → editor → publisher) that learns my voice, respects platform norms, and ships consistently while keeping me in control.

---

# Product Outcomes (What “good” looks like)

- **Clarity & speed:** From idea → ready‑to‑publish draft in ≤5 minutes of my input.
- **Consistency:** 3–5 posts/week across platforms without burnout (customisable).
- **Quality:** Posts meet a defined style guide, avoid hallucinations, and include optional citations when claims are made.
- **Learning:** System adapts to my tone and preferences over time via feedback loops.
- **Control:** Nothing publishes without explicit approval (unless I enable auto‑publish rules).

---

# Users & Roles

- **Owner (me):** sole primary user with full access.
- **System Agents:** brainstorm, strategy, research, writer, editor, publisher (described below).

---

# Primary Use Cases

1. **Brainstorm**: Suggest ideas I could post about based on my drafts, latest news & trending topics. 
2. **Idea to Draft:** I drop a seed (topic, link, or bullet list) → platform‑specific drafts are generated.
3. **Repurpose Content:** Take an existing post/article and adapt it to other platforms (thread → post → article, and vice‑versa).
4. **Iterate & Review:** Inline suggestions, tone tweaks, length changes, fact checks, and safety checks before approval.
5. **Schedule & Publish:** Queue posts per platform; handle time zones.
6. **Library & Search:** Store drafts, templates, snippets, and examples; full‑text search.
7. **Track costs** : Maintains a token count and costs incurred by the usage of LLMs

---

# V1 Scope (MVP)

**Platforms:** LinkedIn, Twitter/X, Medium&#x20;

&#x20;**Core Flow:** Brainstorm → Select Seed → Research  → Drafts (per platform) → Edit/Approve → Schedule/Publish.&#x20;

**Human‑in‑loop:** Mandatory approval gate before anything posts.

**Hosting:** Single‑tenant, secure web app with sign‑in.

---


# V2+ Nice-to-Haves (Backlog)

- Asset generation (images, cover art) and captioning.
- Engagement assistant (reply suggestions post-publish).
- Multi-account support.
- Analytics (CTR, impressions, saves, follows) and learning loops.
- Versioning.
- **Platform Constraint Packs:** per-platform rules (character limits, thread/paragraph limits, mentions/links/tag counts) via a configurable rules engine and UI.
- **Platform Policy Linting:** pre-publish enforcement with actionable fix-ups.
- **Advanced QC & Safety:** retrieval-backed fact checks with citations, plagiarism scan, robust link checker/redirect handling, and “news mode” risk scoring.
- **Budgets & Alerts:** monthly spend caps, threshold alerts, and weekly cost digest.



---
# System Agents (conceptual)

1. **Brainstorm Agent** – Suggests seeds from my Topics, past content, and optional **News mode** (opt-in). Outputs 3–5 de-duplicated ideas with a one-line rationale, links, and confidence; respects safety gates; citations persist to the draft’s context.
2. **Strategy Agent** – Interprets seed; proposes angles, hooks, and outcomes; surfaces 3 outlines.
3. **Research Agent** – Gathers supporting points, quotes, links; flags unverifiable claims.
4. **Medium Writer Agent** – Produces platform-aware drafts for Medium (no hard constraints enforced in V1).
5. **Twitter/X Writer Agent** – Produces platform-aware drafts for X (no hard constraints enforced in V1).
6. **LinkedIn Writer Agent** – Produces platform-aware drafts for LinkedIn (no hard constraints enforced in V1).
7. **Editor Agent** – Checks clarity, tone match, grammar, style-guide compliance; runs hallucination and safety checks; proposes revisions; checks semantic consistency across platforms.
8. **Publisher Agent** – Manages queue; schedules posts; retries on transient errors; records canonical post URLs.

> All agents log decisions and expose a transparent trace for auditability.


---

# Functional Requirements

## 1) Input & Ideation

- Accept seed as: **free text**, **bullet list**, or **one/more URLs**.
- Auto-extract from URLs: title, author, summary, and key points.
- **Suggest (opt-in):**
  - **Sources (V1):** my Topics taxonomy, my approved/published posts, saved ideas/snippets.
  - **Optional “News mode” (off by default):** pulls from a configurable set of feeds/lists I provide (e.g., newsletters, blogs, X Lists). Each suggestion includes a short rationale and links.
  - **Recency window:** last **7 days** by default (configurable).
  - **Output:** **3–5** candidate seeds with *(title, 1–2 line rationale, links, confidence)*.
  - **Quality gates:** de-duplicate against my past posts; drop low-quality/paywalled links unless explicitly allowed.
- Maintain **Topics** taxonomy (e.g., “building apps with AI using AI”) to bias brainstorming, drafting, and repurposing.



## 2) Style & Voice

- **StyleGuide (versioned):**
  - **Tone sliders:** practical ↔ playful; concise ↔ detailed; opinionated ↔ neutral.
  - **Voice & POV:** first-person (“I”), second-person (“you”), or mixed; avoid passive voice.
  - **Register & reading level:** target grade band (e.g., 8–10).
  - **Structure preferences:** hook → insight → example → CTA; bullets preferred for lists; code snippets allowed when helpful.
  - **Formatting policy:** emoji usage (never/limited/allowed); hashtag policy (none/limited); link policy (inline vs end).
  - **Banned/avoid list:** phrases, clichés, buzzwords.
  - **Positive exemplars:** 5–10 approved posts for few-shot conditioning.
- **Learning loop:**
  - Feedback signals (approve, minor edit, major edit, reject) update a per-feature weight vector.
  - **Style score** (0–100) computed by Editor Agent; drafts below threshold trigger an auto “match my voice” revision.
  - Drift control via periodic exploration variants to avoid overfitting.
- **Enforcement:** Editor Agent can block publishing if style score < threshold (Owner override allowed); **safety overrides style**.

## 3) Draft Generation

- **Platform-aware patterns (V1):** generate drafts tailored to each platform’s *typical* reading pattern (e.g., strong hook, scannable body, clear CTA) **without** enforcing hard platform rules in V1.
- **Variants:** generate **2–3** alternatives per selected platform.
- Alt-text prompts only when an image is attached (no image generation in V1).

> Detailed platform constraints (exact character limits, thread steps, mention/tag/link rules) are deferred to **V2**.

## 4) Quality Control & Safety

### V1 (baseline)
- **Approval Gate:** Nothing publishes without explicit Owner approval.
- **Claim highlighting:** Identify factual claims; prompt for sources; mark confidence.
- **Link sanity:** Validate that provided links resolve (no deep web verification).
- **Duplicate check:** Compare against my past content; flag near-duplicates.
- **Toxicity/PII screening:** Red-flag and require confirmation (names, emails, phone, secrets).
- **Basic sanity checks:** approximate length and link count checks (platform-agnostic).
- **QC report:** style score, safety flags, claims needing sources, and duplicate risk.

### V2 (advanced)
- Retrieval-backed fact checks with inline citations and confidence.
- Plagiarism scan across web sources.
- **Platform Policy Packs** (rules engine): per-platform hard limits and policy linting.
- Link checker (status, redirects, archive fallback); media alt-text enforcement.
- “News mode” risk checks (rumor/low-credibility source down-weights).

## 5) Editing & Collaboration

- Rich text and markdown editor for user to modify the content if they want.
- Quick actions: “shorter/longer,” “more technical,” “friendlier,” “first‑person,” “add example,” “remove jargon.”

## 6) Drafts, Library & Search

- Save drafts with status: *Idea, Outlined, Ready for Review, Approved, Scheduled, Published, Archived*.
- Global search across titles, bodies, tags, and links.

## 7) Scheduling & Publishing

- Connect social accounts via OAuth; per‑platform permissions stored securely.
- Schedule by **date/time** (with my timezone default).
- Publish now / schedule / unschedule; retry logic on API errors; idempotency keys.

## 8) Authentication & Security

- Passwordless email sign‑in or OAuth (Google) for the web app.
- Role: Owner; (future: Collaborator with restricted scopes).
- Secure storage of social tokens (server‑side, encrypted at rest; short‑lived tokens refreshed via OAuth).
- Audit log of publishes/edits.



---

# Non‑Functional Requirements

- **Scalability:** Single user now; codebase designed for multi‑tenant later.
- **Portability:** Deployable to common PaaS (Vercel) with managed DB.
- **Observability:** Structured logs, request tracing, error tracking, and prompt/agent run telemetry.
- **Privacy:** No training on my private data outside configured models; redact secrets in logs.

---
# UX Requirements

- **Home:** Next publishes; “Start from seed” CTA; recent drafts; recent publishes.
- **Composer:** Left: seed & controls. Middle: drafts/variants. Right: QC checklist & facts panel.
- **Calendar:** Drag-drop posts across days/platforms.
- **Library:** Drafts, snippets, saved hooks, past posts.
- **Trace:** Agent run timeline with inputs/outputs, **token counts, $ cost per run and per-draft total, latency, errors, retries**, and decision notes.


---

# Content Lifecycle & States

`Idea → Outlined → Drafted → Edited → Approved → Scheduled → Published`

- Transitions logged with actor (me/agent) and timestamp.

---

# Guardrails & Style Guide (Initial)

- Prioritize clarity over cleverness; avoid buzzword soup.
- Include concrete examples/code when useful; cite sources for facts.
- Be audience‑aware (builders/PMs/founders learning AI apps).
- Avoid confidential/project‑internal details and vendor NDAs.

---

# Integrations (V1 targets)

- **LinkedIn API:** share text posts.
- **Twitter/X API:** tweet & threads.
- **Medium API:** create drafts but don’t auto‑publish.
- **Email (SendGrid/SES):** notifications.
- **Auth (Auth provider):** Google OAuth or passwordless magic links.
- **Storage:** Postgres for data; object store for assets.

---

# Data Model (Conceptual)

- **User**(id, email, auth_provider)
- **Account**(platform, handle, oauth_credentials, status)
- **Idea**(id, seed_text, source_url, topic_tags, created_by)
- **Draft**(id, idea_id, platform, variant_no, body, status, qc_score, warnings, created_at)
- **Schedule**(draft_id, platform, scheduled_at, timezone, publish_status)
- **Post**(id, platform_post_id, url, published_at, account_id)
- **Feedback**(draft_id, label, note, created_at)
- **StyleGuide**(tone, voice_rules, banned_phrases, emoji_policy, hashtag_rules)
- **AuditLog**(actor, action, target, timestamp, metadata)
- **AgentRun**(id, draft_id, agent_type, model, prompt_tokens, completion_tokens, cost_usd, latency_ms, started_at, finished_at, status, notes)


---

# Acceptance Criteria (MVP)

1. I can sign in securely and connect LI/X accounts.
2. I can submit a seed (text, bullet list, or URL) **or** use **Suggest** to get **3–5** candidate seeds with a rationale and links within **5 mins**.
3. For each selected platform, I receive at least **two** draft variants.
4. Each draft shows a QC report (style score, claims flagged, duplicate risk, safety flags).
5. The **Trace** shows per-agent token counts and **$ cost** for the draft.
6. I can edit drafts and mark **Approved**.
7. I can schedule an approved draft for a future time and see it in the calendar/queue.
8. Posts do **not** publish without explicit approval.
9. After publish, I can see the canonical URL.
10. “News mode” is **opt-in** and clearly indicates sources when used.

---

# Glossary

- **QC:** Quality Control (automated checks + editor agent report).
- **Variant:** Alternative drafts from the same seed.
- **Trace:** Timeline of steps and agent outputs for a run.

