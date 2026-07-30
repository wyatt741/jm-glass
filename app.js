// BASE BEHAVIOUR. Mechanics only — no component wiring.
//
// The old app.js drove a specific mobile menu, a specific lightbox, a specific gallery
// filter and a specific sun/moon toggle. Each assumed particular markup, so every derived
// site inherited the same interactions and the same silhouette. Gone.
//
// What is left is the theme MECHANISM (persist a choice, otherwise follow the OS) and a
// reduced-motion helper. Both are face-neutral. Wire your own controls to them.

(() => {
  'use strict';

  const KEY = 'theme';
  const root = document.documentElement;

  const osDark = () => matchMedia('(prefers-color-scheme: dark)').matches;
  const stored = () => { try { return localStorage.getItem(KEY); } catch { return null; } };

  // An explicit choice if one was made, otherwise whatever the OS says.
  const current = () => root.getAttribute('data-theme') || (osDark() ? 'dark' : 'light');

  function setTheme(next) {
    root.setAttribute('data-theme', next);
    try { localStorage.setItem(KEY, next); } catch { /* private mode: this page only */ }
    root.dispatchEvent(new CustomEvent('themechange', { detail: { theme: next } }));
  }

  // Keep following the OS until the visitor makes an explicit choice.
  matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
    if (!stored()) root.removeAttribute('data-theme');
  });

  // Public surface. Build whatever control you like:
  //   <button data-theme-toggle aria-pressed="false">…</button>  is wired automatically
  //   site.setTheme('dark') / site.toggleTheme() / site.theme() / site.prefersReducedMotion()
  window.site = {
    setTheme,
    theme: current,
    toggleTheme: () => setTheme(current() === 'dark' ? 'light' : 'dark'),
    prefersReducedMotion: () => matchMedia('(prefers-reduced-motion: reduce)').matches,
  };

  document.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-theme-toggle]');
    if (!btn) return;
    window.site.toggleTheme();
    btn.setAttribute('aria-pressed', String(current() === 'dark'));
  });
})();

/* ============================================================================
   J&M GLASS — SITE BEHAVIOUR
   Authored for this site. Three things: the daylight control's label, the project
   filter, and the bid assistant.

   The assistant's LOGIC is ported from the retired chat.js
   (git show 60db2db:chat.js): the quote-wizard state machine, the XSS-safe
   linkifier, the AI-primary-with-canned-fallback path, the once-per-session
   nudge, and the soft follow-up capture. NONE of its markup or class names came
   with it, and one thing was deliberately fixed on the way: the old nudge used
   window.addEventListener('scroll'), which runs on every scroll frame. This uses
   an IntersectionObserver.
   ============================================================================ */
(() => {
  'use strict';

  /* ---- the daylight control says which mode it switches TO ---- */
  const label = document.querySelector('[data-daylight-label]');
  if (label) {
    const paint = () => {
      const dark = window.site.theme() === 'dark';
      label.textContent = dark ? 'Light' : 'Dark';
      const btn = label.closest('[data-theme-toggle]');
      if (btn) {
        btn.setAttribute('aria-label', dark ? 'Switch to the light sheet'
                                            : 'Switch to the dark sheet');
        // the markup ships aria-pressed="false", which is a lie for an OS-dark
        // visitor who has chosen nothing. Derive it from the live theme instead.
        btn.setAttribute('aria-pressed', String(dark));
      }
    };
    paint();
    document.documentElement.addEventListener('themechange', paint);
    matchMedia('(prefers-color-scheme: dark)').addEventListener('change', paint);
  }

  /* ---- publish the title block's height so the assistant panel and its nudge can
     hang off the trigger rather than off a screen corner. The masthead is three
     rows on a phone and one on desktop, so this cannot be a constant. ---- */
  const tblock = document.querySelector('.tblock');
  if (tblock) {
    const publish = () => {
      document.documentElement.style.setProperty(
        '--tb-h', Math.round(tblock.getBoundingClientRect().height) + 'px');
    };
    publish();
    if ('ResizeObserver' in window) new ResizeObserver(publish).observe(tblock);
    else addEventListener('resize', publish);
  }

  /* ---- project filter. Hidden until JS runs, so no-JS shows every record. ---- */
  const bar = document.querySelector('[data-filterbar]');
  const recordHost = document.querySelector('[data-records]');
  if (bar && recordHost) {
    bar.hidden = false;
    const records = [...recordHost.querySelectorAll('[data-kinds]')];
    const buttons = [...bar.querySelectorAll('[data-kind]')];
    buttons.forEach((btn) => btn.addEventListener('click', () => {
      const kind = btn.dataset.kind;
      buttons.forEach((b) => b.setAttribute('aria-pressed', String(b === btn)));
      records.forEach((r) => {
        r.hidden = kind !== 'all' && !r.dataset.kinds.split(' ').includes(kind);
      });
    }));
  }

  /* ======================= the bid assistant ======================= */
  const root = document.querySelector('[data-ask]');
  if (!root) return;
  const openBtn = root.querySelector('[data-ask-open]');
  const panel = root.querySelector('[data-ask-panel]');
  const shutBtn = root.querySelector('[data-ask-shut]');
  const log = root.querySelector('[data-ask-log]');
  const form = root.querySelector('[data-ask-form]');
  const input = root.querySelector('[data-ask-input]');
  const sendBtn = root.querySelector('[data-ask-send]');

  // ---------------- config ----------------
  const PHONE = '623-243-5538';
  const ADDR = '1502 N 29th Ave, Phoenix, AZ 85009';
  const MAPS = 'https://maps.google.com/?q=1502+N+29th+Ave,+Phoenix,+AZ+85009';
  const ADDR_RE = ADDR.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  // where a captured lead goes. Same FormSubmit inbox as the bid form.
  const LEAD_URL = 'https://formsubmit.co/ajax/wyatt741@gmail.com';
  // HYBRID tier (docs/SETTLED.md). Until DNS cutover this host does not resolve
  // and every message falls back to the canned answers below, which is the
  // designed behaviour, not a failure. AI_TIMEOUT keeps that fallback quick.
  const WORKER_URL = 'https://chat.jmglassllc.com';
  const AI_TIMEOUT = 6000;

  const GREETING = 'Ask about scope, our license, or send a bid invitation. '
    + 'I can also take the invitation details here.';

  // Every answer below is a fact from docs/RESEARCH_BRIEF.md. No prices, ever:
  // commercial glazing is bid work and a quoted number would be fabricated.
  const ANSWERS = {
    scope: 'We do storefront, curtain wall, window wall, aluminum and '
      + 'all-glass entrances, automatic sliding entrances, frameless office fronts, '
      + 'sliding glass doors, blinds-between-glass partitions, mirror, glass guard '
      + 'panels and sunshades. The scope sheet shows a photograph of each one.',
    license: 'Arizona ROC 302375, Specialty Dual CR-65 Glazing. Active and renewed '
      + 'through 2027-11-30, first issued 9 November 2015. Bonded, no claim ever paid, '
      + 'and no ROC or BBB complaints. All of it is public at roc.az.gov.',
    residential: 'We take commercial work only. We do not do residential glass.',
    hours: 'The office is open Mon-Fri 6am-2pm. We are at ' + ADDR + '. Call '
      + PHONE + '.',
    price: 'Commercial glazing is bid work, so there is no price list. Send the '
      + 'drawings and the bid date and we will tell you quickly whether we are '
      + 'bidding. Call ' + PHONE + ' if it is urgent.',
    projects: 'The project record has our Arizona projects in two categories, '
      + 'commercial shell and tenant improvement, with our own job photographs. '
      + 'Retail, medical, office, fitness, restaurant and travel centre.',
    contact: 'Call or text ' + PHONE + ', or email jmglassllc@gmail.com. I can also '
      + 'take the bid details right here.',
    thanks: 'Anytime. Want me to take the bid details, or is there anything else?',
    fallback: 'The office can get you a precise answer on that. Want me to take the '
      + 'bid details, or call ' + PHONE + '.',
  };

  function cannedFor(text) {
    const q = text.toLowerCase();
    const has = (words) => words.some((w) => q.indexOf(w) !== -1);
    if (has(['bid', 'invitation', 'invite', 'quote', 'estimate', 'itb', 'tender'])) return startWizard;
    if (has(['residential', 'house', 'home', 'shower', 'window at my', 'apartment'])) return ANSWERS.residential;
    if (has(['licen', 'roc', 'bond', 'insur', 'complaint', 'certif'])) return ANSWERS.license;
    if (has(['price', 'cost', 'how much', 'pricing', 'rate', '$'])) return ANSWERS.price;
    if (has(['hour', 'open', 'where', 'location', 'address', 'directions', 'shop'])) return ANSWERS.hours;
    if (has(['project', 'portfolio', 'work', 'reference', 'past', 'experience'])) return ANSWERS.projects;
    if (has(['contact', 'call', 'text', 'phone', 'email', 'reach'])) return ANSWERS.contact;
    if (has(['scope', 'curtain', 'storefront', 'window wall', 'glaz', 'mirror', 'door', 'do you', 'offer'])) return ANSWERS.scope;
    if (has(['thank', 'thanks', 'great', 'perfect'])) return ANSWERS.thanks;
    return ANSWERS.fallback;
  }

  const STEPS = [
    { key: 'scope', q: 'What scope is the bid for?',
      opts: ['Storefront', 'Curtain wall', 'Interior glass', 'Mixed or not sure'] },
    { key: 'stage', q: 'What stage is it at?',
      opts: ['Bidding now', 'Budget pricing', 'Already awarded'] },
    { key: 'bid_date', q: 'When is the bid due? Type a date, or skip.', text: true, optional: true },
    { key: 'project', q: 'Project name and address?', text: true },
    { key: 'name', q: 'Your name and company?', text: true },
    { key: 'contact', q: 'Best email or phone for the invitation?', text: true },
  ];

  // ---------------- plumbing ----------------
  let mode = 'chat';
  let started = false;
  let convo = [];
  let asked = 0;

  const el = (tag, cls, text) => {
    const n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  };
  const toBottom = () => { log.scrollTop = log.scrollHeight; };
  const setInput = (on, ph) => {
    // disabling the element that currently has focus drops activeElement to
    // <body>. Hand focus to Close first, which stays reachable either way.
    if (!on && (document.activeElement === input || document.activeElement === sendBtn)) {
      shutBtn.focus({ preventScroll: true });
    }
    input.disabled = !on;
    sendBtn.disabled = !on;
    input.placeholder = ph || 'Ask about scope or a bid';
  };

  /* XSS-safe linkifier, ported. Builds text nodes and anchors, never innerHTML. */
  function linkify(box, text) {
    const re = new RegExp('(https?:\\/\\/[^\\s)]+)|(\\d{3}-\\d{3}-\\d{4})|('
      + ADDR_RE + ')|([\\w.-]+@[\\w.-]+\\.\\w+)', 'g');
    let last = 0;
    let m;
    while ((m = re.exec(text))) {
      if (m.index > last) box.appendChild(document.createTextNode(text.slice(last, m.index)));
      const a = document.createElement('a');
      if (m[1]) {
        a.href = m[1]; a.target = '_blank'; a.rel = 'noopener';
        a.textContent = m[1].replace(/^https?:\/\//, '').replace(/\/$/, '');
      } else if (m[2]) {
        a.href = 'tel:+1' + m[2].replace(/\D/g, ''); a.textContent = m[2];
      } else if (m[3]) {
        a.href = MAPS; a.target = '_blank'; a.rel = 'noopener'; a.textContent = m[3];
      } else {
        a.href = 'mailto:' + m[4]; a.textContent = m[4];
      }
      box.appendChild(a);
      last = m.index + m[0].length;
    }
    if (last < text.length) box.appendChild(document.createTextNode(text.slice(last)));
  }

  function say(role, text) {
    const d = el('div', 'ask-line ask-line--' + (role === 'me' ? 'me' : 'bot'));
    linkify(d, text);
    log.appendChild(d);
    toBottom();
    convo.push((role === 'me' ? 'Visitor: ' : 'Assistant: ') + text);
    return d;
  }
  function waiting() {
    const w = el('div', 'ask-wait');
    w.appendChild(el('span')); w.appendChild(el('span')); w.appendChild(el('span'));
    log.appendChild(w);
    toBottom();
    return w;
  }
  function botSay(text, then) {
    const w = waiting();
    setTimeout(() => { w.remove(); say('bot', text); if (then) then(); },
      window.site.prefersReducedMotion() ? 0 : 260);
  }
  function options(items) {
    const wrap = el('div', 'ask-opts');
    items.forEach((it) => {
      const b = el('button', 'ask-opt' + (it.quiet ? ' ask-opt--quiet' : ''), it.label);
      b.type = 'button';
      // Removing the focused button sends activeElement to <body>, which loses a
      // keyboard user's place at every wizard step (WCAG 2.4.3). Park focus on a
      // stable anchor first; the next render then claims it.
      b.addEventListener('click', () => {
        const hadFocus = document.activeElement === b;
        wrap.remove();
        if (hadFocus) input.disabled ? shutBtn.focus() : input.focus();
        it.act();
      });
      wrap.appendChild(b);
    });
    log.appendChild(wrap);
    toBottom();
    // a fresh set of choices takes focus, so Tab order follows the conversation
    if (!panel.hidden && wrap.firstChild) wrap.firstChild.focus({ preventScroll: true });
    return wrap;
  }
  const transcript = () => convo.join('\n');

  /* ---- HYBRID path: AI primary, canned answer as the fallback on ANY error ---- */
  let aiHistory = [];
  function renderAI(box, text) {
    text = text.replace(/\s*—\s*/g, ', ').replace(/–/g, '-');
    text.split('\n').forEach((line, i) => {
      if (i) box.appendChild(el('br'));
      line = line.replace(/^[ \t]*[-*]\s+/, '• ');
      line.split(/\*\*([^*\n]+)\*\*/).forEach((seg, j) => {
        if (!seg) return;
        if (j % 2) { const b = el('strong'); linkify(b, seg); box.appendChild(b); }
        else linkify(box, seg);
      });
    });
  }
  function aiReply(text, fallbackText) {
    const w = waiting();
    const msgs = aiHistory.concat([{ role: 'user', content: text }]).slice(-16);
    const ctl = new AbortController();
    const timer = setTimeout(() => ctl.abort(), AI_TIMEOUT);
    fetch(WORKER_URL.replace(/\/+$/, '') + '/chat', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ messages: msgs }),
      signal: ctl.signal,
    })
      .then((r) => (r.ok ? r.json() : Promise.reject(r.status)))
      .then((d) => {
        const reply = d && d.reply ? String(d.reply) : '';
        if (!reply) return Promise.reject('empty');
        w.remove();
        aiHistory.push({ role: 'user', content: text },
                       { role: 'assistant', content: reply });
        aiHistory = aiHistory.slice(-16);
        const box = el('div', 'ask-line ask-line--bot');
        renderAI(box, reply);
        log.appendChild(box);
        toBottom();
        convo.push('Assistant: ' + reply);
        offerFollowup();
        return null;
      })
      .catch(() => { w.remove(); say('bot', fallbackText); offerFollowup(); })
      .finally(() => clearTimeout(timer));
  }

  /* ---- lead sender: the wizard and the follow-up both route here ---- */
  function sendLead(fields, okMsg) {
    setInput(false, 'Sending');
    const payload = {
      _subject: 'Bid assistant lead from jmglassllc.com',
      _template: 'table',
      _captcha: 'false',
      transcript: transcript(),
    };
    Object.keys(fields).forEach((k) => { payload[k] = fields[k]; });
    fetch(LEAD_URL, {
      method: 'POST',
      headers: { 'content-type': 'application/json', accept: 'application/json' },
      body: JSON.stringify(payload),
    })
      .then((r) => r.json())
      .then((d) => {
        const ok = d && (d.ok || d.success === 'true' || d.success === true);
        botSay(ok ? okMsg
          : 'I could not send that just now. Please email jmglassllc@gmail.com or call '
            + PHONE + '.', () => setInput(true, 'Anything else'));
      })
      .catch(() => botSay('I could not connect to send that. Please call ' + PHONE + '.',
        () => setInput(true, 'Anything else')));
  }

  /* ---- open and close ---- */
  let lastFocus = null;
  function open() {
    lastFocus = document.activeElement;
    panel.hidden = false;
    openBtn.setAttribute('aria-expanded', 'true');
    if (!started) { started = true; menu(); }
    setTimeout(() => { (input.disabled ? shutBtn : input).focus(); }, 40);
  }
  function shut() {
    panel.hidden = true;
    openBtn.setAttribute('aria-expanded', 'false');
    (lastFocus && lastFocus.isConnected ? lastFocus : openBtn).focus();
  }
  openBtn.addEventListener('click', () => (panel.hidden ? open() : shut()));
  shutBtn.addEventListener('click', shut);
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && !panel.hidden) { shut(); return; }
    if (e.key !== 'Tab' || panel.hidden) return;
    // The panel overlays page content that stays focusable behind it, so tabbing
    // past Send used to land on controls the sheet completely hides (SC 2.4.11).
    // Keep the loop inside the panel while it is open.
    const stops = [...panel.querySelectorAll('button, input, textarea, a[href]')]
      .filter((n) => !n.disabled && n.offsetParent !== null);
    if (!stops.length) return;
    const first = stops[0];
    const last = stops[stops.length - 1];
    if (!panel.contains(document.activeElement)) {
      e.preventDefault();
      (e.shiftKey ? last : first).focus();
    } else if (e.shiftKey && document.activeElement === first) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault();
      first.focus();
    }
  });
  document.querySelectorAll('[data-open-ask]').forEach((t) => {
    t.addEventListener('click', (e) => { e.preventDefault(); open(); });
  });

  function menu() {
    mode = 'chat';
    say('bot', GREETING);
    options([
      { label: 'Send a bid invitation', act: startWizard },
      { label: 'What you self-perform', act: () => { say('me', 'What do you self-perform?'); botSay(ANSWERS.scope); } },
      { label: 'License and bonding', act: () => { say('me', 'What is your license?'); botSay(ANSWERS.license); } },
    ]);
    setInput(true, 'Or type your question');
  }

  /* ---- the quote wizard, ported state machine ---- */
  let answers = {};
  let step = 0;
  let skipRow = null;
  function startWizard() {
    mode = 'wizard'; answers = {}; step = 0;
    say('me', 'I have a bid invitation');
    botSay(STEPS[0].q, renderStep);
  }
  function runStep() {
    if (step >= STEPS.length) { submitWizard(); return; }
    botSay(STEPS[step].q, renderStep);
  }
  function renderStep() {
    const s = STEPS[step];
    if (s.opts) {
      setInput(false, 'Pick one above');
      options(s.opts.map((o) => ({
        label: o,
        act: () => { say('me', o); answers[s.key] = o; step += 1; runStep(); },
      })));
    } else {
      setInput(true, s.optional ? 'Type, or press Skip' : 'Type your answer');
      skipRow = s.optional
        ? options([{ label: 'Skip', quiet: true,
            act: () => { skipRow = null; answers[s.key] = ''; step += 1; runStep(); } }])
        : null;
      input.focus();
    }
  }
  function wizardText(text) {
    if (skipRow) { skipRow.remove(); skipRow = null; }
    say('me', text);
    answers[STEPS[step].key] = text;
    step += 1;
    runStep();
  }
  function submitWizard() {
    mode = 'chat';
    sendLead(answers, 'That is everything. The office has it with the full thread, '
      + 'and will come back to you on whether we are bidding.');
  }

  /* ---- soft follow-up capture, during the chat, never on close ---- */
  let followOffered = false;
  let fu = {};
  let fuStep = 0;
  const FU = [
    { key: 'name', q: 'Sure. Your name and company?' },
    { key: 'contact', q: 'Best email or phone to reach you?' },
  ];
  function offerFollowup() {
    if (followOffered || asked < 2 || mode !== 'chat') return;
    followOffered = true;
    say('bot', 'Want the office to follow up? I can pass along what you have asked.');
    options([
      { label: 'Yes, follow up', act: startFollowup },
      { label: 'No thanks', quiet: true,
        act: () => botSay('No problem. You can always reach us at ' + PHONE + '.') },
    ]);
  }
  function startFollowup() { mode = 'followup'; fu = {}; fuStep = 0; runFu(); }
  function runFu() {
    if (fuStep >= FU.length) { submitFollowup(); return; }
    botSay(FU[fuStep].q, () => { setInput(true, 'Type your answer'); input.focus(); });
  }
  function fuText(text) {
    say('me', text);
    fu[FU[fuStep].key] = text;
    fuStep += 1;
    runFu();
  }
  function submitFollowup() {
    mode = 'chat';
    sendLead({ name: fu.name, contact: fu.contact,
      needs: 'Chat follow-up, did not start the bid wizard' },
      'Got it. The office will be in touch.');
  }

  /* ---- one nudge per session. IntersectionObserver, never a scroll listener. ---- */
  function nudge() {
    if (started || !panel.hidden) return;
    // Not on phones. Anchored under the title block it lands on top of the h1,
    // and the opener is already a thumb's reach away in the masthead. Moving it
    // to the bottom instead would just rebuild the floating bubble this design
    // deliberately does not have.
    if (!matchMedia('(min-width: 700px)').matches) return;
    try {
      if (sessionStorage.getItem('ask-nudged')) return;
      sessionStorage.setItem('ask-nudged', '1');
    } catch (e) { /* private mode: nudge once this page only */ }
    const n = el('div', 'ask-hint');
    const msg = el('button', 'ask-hint-msg', 'Sending a bid invitation?');
    msg.type = 'button';
    const x = el('button', 'ask-hint-x', '×');
    x.type = 'button';
    x.setAttribute('aria-label', 'Dismiss');
    n.appendChild(msg); n.appendChild(x);
    root.appendChild(n);
    requestAnimationFrame(() => n.classList.add('ask-hint--shown'));
    const kill = () => {
      n.classList.remove('ask-hint--shown');
      setTimeout(() => n.remove(), 300);
    };
    msg.addEventListener('click', () => { kill(); open(); });
    x.addEventListener('click', (e) => { e.stopPropagation(); kill(); });
    setTimeout(() => { if (panel.hidden) kill(); }, 9000);
  }
  const sentinel = document.querySelector('main > section:nth-of-type(3)');
  if (sentinel && 'IntersectionObserver' in window) {
    const io = new IntersectionObserver((entries) => {
      if (entries.some((en) => en.isIntersecting)) { io.disconnect(); nudge(); }
    }, { rootMargin: '0px' });
    io.observe(sentinel);
  }

  /* ---- input routes by mode ---- */
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const text = input.value.trim();
    if (!text) return;
    input.value = '';
    if (mode === 'followup') { fuText(text); return; }
    if (mode === 'wizard' && STEPS[step] && STEPS[step].text) { wizardText(text); return; }
    say('me', text);
    asked += 1;
    const res = cannedFor(text);
    if (typeof res === 'function') { res(); return; }
    if (WORKER_URL) aiReply(text, res);
    else botSay(res, offerFollowup);
  });
})();
