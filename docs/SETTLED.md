# SETTLED — J&M Glass LLC

The grill (RUN.md phase 2). Answers below freeze the work list. The four contract lines come
first, before any prose, because `ship.py: parse_settled()` takes the first match per field.

- domain: none
- preview: https://wyatt741.github.io/jm-glass/
- repo: jm-glass
- chatbot: hybrid
- rights: project photos cleared, 2023 team photo cleared, GC partner logos cleared by owner instruction; the four leadership headshots are NOT cleared and do not ship
- hosting: github

## Answered at the grill, 2026-07-29

| # | Question | Answer | Effect on the build |
|---|---|---|---|
| 1 | Prequalification block (EMR, ISNetworld/Avetta, bonding capacity, insurance limits) | **Omit entirely** | No prequal section anywhere. The site is a portfolio and credential record, not a prequal packet. The ROC/BBB/bond facts still appear because they are checkable on a .gov page; nothing SAMPLE-marked is invented to fill a gap |
| 2 | 23 GC and developer partner logos | **Show the logos** | A named partner section ships using the 23 recovered marks. Each gets real alt text naming the company (their current site ships all 23 with empty alt) |
| 3 | Chatbot tier | **Hybrid AI Worker** | Site-authored widget, `worker/` deployed, canned answers as automatic fallback. Costs roughly 1 to 3 cents per conversation. `wrangler deploy` runs from ship.py only because this tier is hybrid |
| 4 | Services scope list | **All 12 evidenced scopes** | Scope page claims only what a named photograph shows. Curtain wall and glass guard panels included; both are absent from their current site |

Not asked, defaulted, and recorded so the default is visible:

- **Careers page: cut.** No evidence they are hiring; a careers page with nothing behind it is filler.
- **Reviews: cut.** Settled in KICKOFF and confirmed by research: no usable positive public review exists. Never invent one.
- **Pricing: cut.** Commercial glazing is bid work.
- **Leadership headshots: cut.** Rights not cleared.

## Frozen work list

Page set, four pages. Derived from research §8 (the site's job is to survive the ten seconds
between a GC pulling this company off a bid list and deciding whether to send the invitation),
not from a default five.

| Page | Job |
|---|---|
| `index.html` | The whole case in one screen-and-a-bit: what they self-perform, the credential that is checkable, proof of work, and the bid path |
| `scope.html` | The 12 scopes, each tied to a real photograph. This page is the single biggest content gain over their current site, which describes the entire offering in two words |
| `projects.html` | The project record: 22 named projects, 55 usable photographs, split Commercial Shell and Tenant Improvement |
| `contact.html` | The bid path: inbox, phone, hours, address, and what to send with an invitation |

Modules kept: scope grid, project record, partner list, ROC credential block, contact form,
hybrid chat widget, light/dark control.
Modules cut: reviews, testimonials, pricing, careers, prequalification, leadership headshots,
employee count, years-of-experience claim.

## Content that must never ship as fact

Carried from the brief so the authoring phase cannot forget:

- Employee count. Four sources, four numbers.
- "Over 60 years experience". Their own Facebook says over 75.
- "A leader in the commercial glass industry". Pure superlative, no citation.
- "Since 2016". Wrong; ROC and BBB both say **2015-11-09**. The site says licensed since 2015.
- Both testimonials on the current site. One is affiliated to the literal word "Unknown"; the
  other claims a 10-year relationship against a 2015 founding.
- `lifetime_peoria.jpg` is an architectural **rendering**, not a photograph. It does not ship.
- `cfc_1-5` are the best curtain-wall photographs on their server and belong to no project page.
  They ship as capability photographs with generic captions, never captioned as a named project.

## Accepted exposure: the FormSubmit address is in page source, 2026-07-30

A PII sweep of the public repo found `wyatt741@gmail.com` live in the contact form's `action`,
in `app.js`'s `LEAD_URL`, and across 8 tracked files and 7 commits. **KICKOFF says that address
is "never displayed", and a form action IS page source, so the two disagree.**

**Wyatt's call: leave it. It is a throwaway address.** Do not "fix" this in a later pass. The
options were offered and declined: pointing the form at `jmglassllc@gmail.com`, activating
FormSubmit and swapping to the hashed endpoint, or scrubbing history with a force-push.

If it ever does need removing, the cheapest route is FormSubmit's hashed endpoint, which
requires activating the form first (one real submission plus the confirmation click).

Everything else in the sweep was clean: **0 of 178 published photographs carry EXIF or GPS**,
no keys or tokens, `.git/gate.key` untracked, the client's four staff emails absent, and the
competitor research absent from every commit.

## Hosting note — shipping to a PREVIEW URL first, 2026-07-30

Amended after the grill. J&M have not seen the site yet and their DNS has not moved, so
there is a demo step between build and cutover that the original plan did not have.

`- domain: none` plus `- preview: https://wyatt741.github.io/jm-glass/` is the sanctioned
third state (`ship.py`): a project repo may ship to its Pages project URL with **no CNAME**,
and `engine.Site(preview=True)` makes every page `noindex,nofollow` with a `Disallow: /`
robots.txt, so the staging copy can never compete with jmglassllc.com in search.

**At cutover, in ONE motion** (standing rule, RUN.md phase 7): change `- domain:` here to
`jmglassllc.com` and drop the `- preview:` line, flip `PREVIEW_BASE`/`preview=True` in
`build.py`, `printf 'jmglassllc.com\n' > CNAME`, move the DNS, then `gate.py --ship` and
`ship.py`.

## Original hosting note — CNAME is deliberately absent this run

`ship.py` ruling 6 requires that a settled custom domain ALREADY have a matching `CNAME` file at
ship time, and it refuses a project-page repo that settles no custom domain. KICKOFF is equally
explicit the other way: DNS still points at their WordPress host, so adding `CNAME` now would
make GitHub 301 the working preview URL to a domain GitHub does not serve.

Both are satisfied because **this run stops at the §12.8 verdict and does not ship** (RUN.md
stop d, KICKOFF gate c). Creating `CNAME` is a cutover-time action: write it, re-run
`gate.py --ship`, then `ship.py`. Until then no `CNAME` exists and nothing is public.
