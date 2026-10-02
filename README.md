# parthchawla.dev — portfolio

The live site. One claim, five cases, and an honest list of what breaks.

**The claim:** I build AI systems that keep working on messy real data, because I measure them
instead of guessing.

## Run it

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m flask --app app run --port 5000
```

Open http://localhost:5000.

## Configuration

| Variable | Required | What it does |
|---|---|---|
| `SECRET_KEY` | in production | Signs the session cookie. |
| `CONTACT_WEBHOOK` | for the contact form | Where a validated message is POSTed. **Without it the form returns an honest error instead of pretending to send.** |
| `CONTACT_RATE_LIMIT` | no | Submits per IP per window. Defaults to `20`. |
| `CONTACT_RATE_WINDOW` | no | Window in seconds. Defaults to `3600`. |

The contact form is deliberately incapable of lying: if `CONTACT_WEBHOOK` is unset, or the
webhook fails or is unreachable, the endpoint returns a real error and the UI shows it. An
earlier version faked a success message and dropped every message.

## Layout

```
app.py               routes; injects `site` and `now` into every template
content.py           ALL claim, case and proof copy. One file, one dict per case.
contact.py           contact endpoint: validation, honeypot, rate limit, delivery
templates/
  base.html          head, nav, footer, the FlyRank badge block
  index.html         the claim, the method, the featured case, the one action
  projects.html      case index, loops over content.CASES
  project_details.html   one case: problem / built / learned / where it breaks
  reliability.html   the fix-now vs known-limitation list
  contact.html       the working form + a plain-words explainer of how it works
  blog.html          the build-in-public story
src/input.css        Tailwind entry: base layer + the site's custom components
static/tailwind.css  built and committed (35KB), so no build step on the server
tools/og-card.html   the share-preview card
tools/make-og.mjs    renders it to static/og.png
tests/               26 tests, mostly the contact endpoint
```

## Adding a case in about thirty minutes

1. Append one dict to `CASES` in `content.py`. Required keys: `slug`, `title`, `tagline`,
   `summary`, `problem`, `built`, `learned`, `facts` (list of label/value pairs), `stack`,
   `source_url`, `source_label`. Optional: `honest_gap`.
2. Nothing else. The index, the detail page and the links all pick it up automatically.
3. Commit. Deploy.

## Styles

Tailwind is compiled, not run in the browser. The earlier version loaded the Tailwind Play CDN
and ran a compiler plus a config block on every page load; this ships one cached CSS file
instead. If you edit a template's classes, rebuild:

```bash
npm install
npm run build:css     # or: npm run watch:css
```

## Tests

```bash
.venv/bin/python -m pytest tests/ -q
```

Covers email and length validation, the honeypot, the rate limiter, and every failure the
contact endpoint can hit. The rest of the web layer is manual QA, which is listed as a known
limitation on `/reliability` rather than glossed over.

## Deploying to Vercel

`app.py` and `requirements.txt` at the repo root are enough for Vercel's Flask preset. Add
`SECRET_KEY` and `CONTACT_WEBHOOK` as environment variables in the project settings. There is no
build step: the compiled CSS is committed.

## Built with

Flask, Jinja, Tailwind CSS, and a lot of help from AI — see `/blog` for the honest version.