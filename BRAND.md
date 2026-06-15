# SQLI Brand Guide — For the Interview Tracker UI

> Use this to make the app look and feel like a real SQLI internal tool.
> Logo files: download manually from the URLs below into `frontend/public/assets/`.

---

## Brand identity

| Attribute | Value |
|-----------|-------|
| **Company** | SQLI SA |
| **Tagline** | *We Elevate. Digitally.* |
| **French tagline** | *Nous créons des expériences digitales qui élèvent les performances* |
| **Founded** | 1990, Levallois-Perret, France |
| **Stock** | Euronext Paris — SQI.PA |
| **Website** | https://www.sqli.com |
| **Rebrand** | 2025 — "Radical Simplicity" by CDLX |
| **Typeface** | **Everett** (Nolan Paparelli / WK Type Foundry) — fallback: `Inter`, `system-ui` |

---

## Color palette

SQLI uses **three blues + cream** — technology balanced with humanity.

```css
:root {
  /* Primary blues */
  --sqli-sky-blue:     #6EC4E8;   /* Warm sky — accents, highlights, links */
  --sqli-cobalt-blue:  #0047BB;   /* Vibrant digital — primary buttons, active states */
  --sqli-midnight-blue:#1A1F4E;   /* Deep volume — sidebar, headers, dark mode base */

  /* Neutrals */
  --sqli-cream:        #FAF7F2;   /* Page background */
  --sqli-white:        #FFFFFF;   /* Cards, modals */
  --sqli-gray-100:     #F0EDE8;   /* Borders, dividers */
  --sqli-gray-500:     #6B7280;   /* Secondary text */
  --sqli-gray-900:     #111827;   /* Body text */

  /* Semantic */
  --sqli-success:      #10B981;
  --sqli-warning:      #F59E0B;
  --sqli-error:        #EF4444;
  --sqli-info:         #6EC4E8;
}
```

### Usage rules

| Element | Color |
|---------|-------|
| App sidebar / top nav (dark) | `--sqli-midnight-blue` |
| Page background | `--sqli-cream` |
| Primary CTA buttons | `--sqli-cobalt-blue` |
| Hover on primary | `#003399` (darker cobalt) |
| Links & active nav | `--sqli-sky-blue` |
| Cards | `--sqli-white` with subtle shadow |
| AI feature badges | Gradient `sky-blue → cobalt-blue` |

---

## Logo assets (download these)

> ⚠️ Logos are SQLI property. Use only for this training project.

| Asset | URL | Save as |
|-------|-----|---------|
| Full logo (PNG) | https://companieslogo.com/img/orig/SQI.PA.png | `frontend/public/assets/sqli-logo.png` |
| Full logo (SVG) | https://companieslogo.com/img/orig/SQI.PA.svg | `frontend/public/assets/sqli-logo.svg` |
| Icon/symbol (PNG) | https://companieslogo.com/img/icon/SQI.PA.png | `frontend/public/assets/sqli-icon.png` |
| Favicon | https://www.sqli.com/favicon.ico | `frontend/public/favicon.ico` |

### Logo placement in app

1. **Login page** — centered logo + tagline "We Elevate. Digitally."
2. **Sidebar** — compact icon when collapsed, full wordmark when expanded
3. **Email templates** (if built) — header logo
4. **PDF export** (scorecard) — footer "Powered by SQLI Interview Tracker"

### Ascender signet (optional decorative element)

SQLI's 2025 rebrand uses two offset vertical bars as a signet (representing "elevation"). Use as a subtle watermark on empty states:

```
│
 │   ← two vertical bars, offset, in sky-blue at 15% opacity
```

---

## Typography scale

```css
/* If Everett is unavailable, use Inter from Google Fonts */
--font-display: 'Everett', 'Inter', system-ui, sans-serif;
--font-body:    'Inter', system-ui, sans-serif;
--font-mono:    'JetBrains Mono', monospace;

--text-xs:   0.75rem;   /* 12px — badges */
--text-sm:   0.875rem;  /* 14px — labels */
--text-base: 1rem;      /* 16px — body */
--text-lg:   1.125rem;  /* 18px — card titles */
--text-xl:   1.25rem;   /* 20px — section headers */
--text-2xl:  1.5rem;    /* 24px — page titles */
--text-3xl:  1.875rem;  /* 30px — dashboard hero */
```

---

## UI component style

- **Border radius:** `8px` cards, `6px` buttons, `12px` modals
- **Shadows:** `0 1px 3px rgba(26, 31, 78, 0.08)` — subtle, not Material Design heavy
- **Spacing:** 4px grid (4, 8, 12, 16, 24, 32, 48)
- **Icons:** [Lucide Vue](https://lucide.dev) or [Heroicons](https://heroicons.com)
- **Animations:** Subtle — 200ms ease transitions, no bounce

### Pipeline stage colors

| Stage | Color | Label |
|-------|-------|-------|
| Applied | `#6B7280` gray | Applied |
| Screening | `#6EC4E8` sky | Screening |
| Technical | `#0047BB` cobalt | Technical Interview |
| Culture Fit | `#8B5CF6` purple | Culture Fit |
| Offer | `#10B981` green | Offer |
| Hired | `#059669` dark green | Hired |
| Rejected | `#EF4444` red | Rejected |

---

## Copy & tone

SQLI voice is **professional, human, straightforward** — not corporate jargon.

| ❌ Avoid | ✅ Use |
|----------|--------|
| "Leverage synergies" | "Combine technology and creativity" |
| "Submit candidate" | "Add candidate" |
| "Terminate process" | "Reject candidate" |
| "AI-powered insights engine" | "AI interview assistant" |

**Empty state example:**
> *No candidates yet. Add your first candidate to start elevating your hiring process.*

---

## Screens to brand (checklist)

- [ ] Login / Register
- [ ] Dashboard (pipeline overview)
- [ ] Candidate list (table + kanban toggle)
- [ ] Candidate detail (timeline, notes, scorecards)
- [ ] Job openings list & form
- [ ] Interview scheduler (calendar view)
- [ ] Scorecard form
- [ ] AI Question Generator panel
- [ ] AI Mock Interview chat
- [ ] Settings / Profile
- [ ] 404 & error pages
