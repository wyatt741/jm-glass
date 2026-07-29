# Site AI chat Worker

A tiny Cloudflare Worker that lets the website's chat bot talk to Claude, **without ever
putting the Anthropic API key in the public website**. The key lives as a Worker secret.

## Free vs hybrid (what this Worker is for)

The site's `chat.js` runs in one of two modes, chosen by `WORKER_URL` at the top of `chat.js`:

- **Free (WORKER_URL empty):** free-text hits the built-in deterministic `ANSWERS`. No backend,
  no API key, no cost. The site works fully without this Worker.
- **Hybrid AI (WORKER_URL set):** free-text POSTs to this Worker's `/chat`, which calls Claude.
  The canned `ANSWERS` stay as the **fallback on any error**, so the bot never dies to a
  "couldn't connect." This Worker is only needed for hybrid mode.

- `worker.js` — the proxy. Origin allowlist, native per-IP rate limit (`env.RL`), turn/length caps, a
  business system prompt, and a regex backstop that drops any price/guarantee.
- `wrangler.jsonc` — config. No secrets in it.

## What it costs
- **Cloudflare Worker:** free tier (100k requests/day) — free.
- **Claude API:** ~1-3¢ per conversation (model: Claude Haiku 4.5). Needs an Anthropic
  API account with prepaid credits. **Set a monthly spend cap** in the Anthropic Console.

## Before you deploy
Edit `worker.js`:
- `ALLOWED` — the site origins allowed to call the Worker (replace the PLACEHOLDER domains).
- `SYSTEM` — fill in the business facts (search for `TODO:`). Keep the HOW TO TALK / HARD RULES
  guardrails as-is; they're what make the bot safe.
- `PHONE` — the real number.

Edit `wrangler.jsonc`: rename `"name"` (e.g. `"acme-chat"`).

## Deploy (one time, ~10 min)

You need: an Anthropic API key (console.anthropic.com → API keys) with a few dollars of
credit, and Node installed.

```bash
cd worker
npm i -g wrangler            # or: npx wrangler ...
wrangler login              # opens Cloudflare in your browser (use the account that owns the domain)
wrangler secret put ANTHROPIC_API_KEY   # paste your Anthropic key when prompted (never goes in git)
wrangler deploy             # prints the Worker URL, e.g. https://acme-chat.<sub>.workers.dev
```

Then in the **Anthropic Console → Limits**, set a monthly **spend cap** (e.g. $10) so a
bad day can never surprise-bill you.

## Turn it on
Set `WORKER_URL` at the top of `chat.js` to the Worker's base URL (no `/chat` suffix), then
bump `CHATV` in `build.py`, `python3 build.py`, and push. Until `WORKER_URL` is set, the bot
stays on its free deterministic answers.

## Custom domain (recommended)
Serve the bot on the site's **own** domain, not the `*.workers.dev` URL. Once the domain's DNS
is on this Cloudflare account, uncomment the `routes` block in `wrangler.jsonc`, set the
pattern to `chat.<domain>`, and `wrangler deploy` again. **Adding the route disables the
workers.dev URL**, so set `WORKER_URL = "https://chat.<domain>"` in `chat.js` and rebuild.

## Rate limiting (already ON)
Per-IP rate limiting ships enabled — a native `[[ratelimits]]` binding (`RL`, 20 req / 60s)
in `wrangler.jsonc`; `worker.js` gates on `env.RL`. **No KV namespace to create** and no
per-request cost.

Know what it is: Cloudflare documents the limiter as **permissive and eventually
consistent** — "intentionally designed to not be used as an accurate accounting system."
Measured in practice, a fresh limit can take several calls on one colo before it first
refuses. That's fine: it is an abuse cap, and a monthly spend cap in the Anthropic Console
remains the hard backstop.

Before the FIRST deploy, set `namespace_id`. Two rules, both enforced the hard way:
- it must be a **string** ("1001"); wrangler rejects a bare number with
  `"ratelimits[0]" bindings must have a string "namespace_id" field`
- it must be **unique across your whole Cloudflare account**, not per worker. Sites spun up
  from this template share one account, so each new worker takes the next number
  (anderson-chat="1001", jm-glass-chat="1002", ...). A duplicate id makes two workers share
  one counter — requests to either eat the other's budget, and nothing warns you.

To tune: edit `limit` in `wrangler.jsonc` (`period` must be 10 or 60).

## Test
```bash
curl -s https://<your-worker-url>/chat \
  -H 'content-type: application/json' -H 'origin: https://<your-domain>' \
  -d '{"messages":[{"role":"user","content":"what are your hours?"}]}'
```
Should return `{"reply":"..."}`. A request with no/other `origin` returns 403 (that's the gate).

## Guardrails baked in
- **Origin allowlist** — only the domains in `ALLOWED` may call it.
- **Price/guarantee backstop** — any reply with a dollar figure or "guarantee" is replaced
  with a "call for pricing" line, even if the model is jailbroken.
- **System prompt** — stays on-topic, no invented stock/reviews, no em/en dashes,
  prompt-injection resistant.
- **Caps** — 16 turns, 1000 chars/message, optional 20 msgs/10min per IP.
