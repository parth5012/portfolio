"""Every word of claim, case and proof on the site lives here.

One file so a new case is a thirty-minute job, not a template hunt.
Each case is the same three beats: the problem, what I built, what I learned.
"""

SITE = {
    "name": "Parth Chawla",
    "claim": "I build AI systems that keep working on messy real data, because I measure them instead of guessing.",
    "proof": (
        "Most AI demos look finished right up until real data arrives. My work is the "
        "unglamorous half: evaluation sets, retries, kill switches, cost logs, and an "
        "honest list of what still breaks."
    ),
    "audience": "A non-technical solo founder whose automation has to survive their inbox.",
    "action_label": "Message me about a pilot",
    "repos": "https://github.com/parth5012/flyrank",
    "github": "https://github.com/parth5012",
    "linkedin": "https://www.linkedin.com/in/parth-chawla-271405324/",
    "email": "parthchawla5012@gmail.com",
}

HEADLINE_STATS = [
    ("8", "cases in the eval set"),
    ("60", "records validated per run"),
    ("6", "prompt versions, measured"),
]

FEATURED_CASE = "classify"

CASES = [
    {
        "slug": "classify",
        "title": "Triage Desk",
        "tagline": "An LLM classifier that is allowed to say it does not know",
        "summary": (
            "A FastAPI service that routes a support message to one of four teams. "
            "It cannot invent a fifth label, it cannot ramble, and when the message is "
            "vague it returns 'other' with low confidence instead of guessing."
        ),
        "problem": (
            "Support messages arrive unstructured and someone has to hand-route every one. "
            "An LLM is fast at this and quietly untrustworthy: it invents labels outside the "
            "list, pads the answer with prose, and will confidently place a message it did "
            "not understand. A demo that only shows the happy path hides exactly the failure "
            "that costs you trust."
        ),
        "built": (
            "I started from a written job card, not a prompt: the exact input, the exact "
            "output shape, the four categories it must never leave, the topics it must never "
            "advise on, and an explicit instruction to answer 'other' when unsure. The prompt "
            "is a versioned file so a change is reviewable. A Pydantic schema rejects anything "
            "off-contract into a quarantine log instead of passing it downstream. Retries fire "
            "only on timeout, 429 and 5xx, with 1s/2s/4s backoff plus jitter and Retry-After "
            "honoured; 400s are never retried. A kill switch returns 503 before spending a "
            "token. Every call writes tokens, duration and whether a repair happened to a cost "
            "log, and swapping the provider is three environment variables."
        ),
        "learned": (
            "The stub mode scored 2/8 on the eval set, and that was the useful result: it "
            "proved the harness measures the prompt rather than the plumbing, because the "
            "plumbing was identical in both runs. The eval set deliberately includes an "
            "ambiguous message and a hostile one, because those are the two that break naive "
            "routing. Urgency is the weak axis I have not fixed: the contract allows three "
            "values but the eval only scores category, so 'right team, wrong priority' is a "
            "failure I cannot currently see. The real-model score is also still unrecorded."
        ),
        "facts": [
            ("Eval cases", "8"),
            ("Stub score", "2/8"),
            ("Retries", "3, jittered"),
            ("Timeout", "30s"),
        ],
        "stack": ["Python", "FastAPI", "Pydantic", "OpenRouter", "Docker"],
        "source_url": "https://github.com/parth5012/flyrank/tree/main/backend/Assignment%206",
        "source_label": "Source, job card and eval set",
        "honest_gap": (
            "The live-model number is not recorded yet, and urgency is unscored. Both are "
            "listed on the reliability page instead of being quietly left out."
        ),
    },
    {
        "slug": "task-api-auth",
        "title": "Task API with real auth",
        "tagline": "Persistence, identity and a one-command run",
        "summary": (
            "A FastAPI task service where data survives a restart and every private route "
            "actually checks a token. The whole stack starts with one command."
        ),
        "problem": (
            "Most CRUD demos skip identity and persistence, so tasks vanish on restart and "
            "every endpoint is public. That is fine for a tutorial and useless the moment "
            "someone else is using it, which is the part I wanted to get right."
        ),
        "built": (
            "FastAPI with SQLModel against Postgres, containerised with Docker Compose, and "
            "Supabase Auth issuing JWTs verified as bearer tokens. Routes are split into a "
            "public set and a protected set, and the protected ones genuinely refuse a bad "
            "token rather than trusting a header. The database is defined in a compose file, "
            "so the only setup command a stranger needs is docker compose up --build -d."
        ),
        "learned": (
            "Moving the database into a compose file deleted an entire category of "
            "\"works on my machine\" bug, and it cost about an hour. Splitting routes by "
            "public and protected made the auth rule visible in the routing table instead "
            "of scattered through handlers, so an unprotected route is now easy to spot in a "
            "diff."
        ),
        "facts": [
            ("Routes", "CRUD + auth"),
            ("Auth", "Supabase JWT"),
            ("Database", "Postgres"),
            ("Setup", "1 command"),
        ],
        "stack": ["Python", "FastAPI", "SQLModel", "Postgres", "Docker", "Supabase"],
        "source_url": "https://github.com/parth5012/flyrank/tree/main/backend/Assignment%204",
        "source_label": "Source and run commands",
    },
    {
        "slug": "prompt-ladder",
        "title": "Prompt ladder V0 to V5",
        "tagline": "Six versions of one prompt, each changing one thing",
        "summary": (
            "The same email-triage prompt rebuilt six times, adding one variable at a time, "
            "with every output kept verbatim so the comparison is honest."
        ),
        "problem": (
            "\"Write backend code for email triage\" returns something plausible. The problem "
            "is that plausible is not a measurement: I had no way to tell whether version 3 "
            "was actually better than version 2, so I kept rewriting the prompt on instinct."
        ),
        "built": (
            "Six versions, each adding exactly one thing: a clearer goal with three labels "
            "and a reason, then real context (Python 3.11, the Gmail API, a messy inbox), "
            "then an output format, then constraints about label-only output and credential "
            "handling, then five messy test inputs and a self-check. Every response is kept "
            "word for word in a single document so a reader can check my conclusion rather "
            "than take it."
        ),
        "learned": (
            "Adding real context changed the output more than adding a clearer goal did. That "
            "is not the change I expected, and I would not have noticed it without keeping "
            "all six outputs side by side. Constraint-late worked better than "
            "constraint-early: telling the model about credentials at V4 beat burying it in "
            "the first prompt."
        ),
        "facts": [
            ("Versions", "6"),
            ("Variable per step", "1"),
            ("Outputs kept", "verbatim"),
        ],
        "stack": ["Python", "Gmail API", "Prompt engineering"],
        "source_url": "https://github.com/parth5012/flyrank/tree/main/ai-fluency/Assignment%203",
        "source_label": "Full ladder, V0 to V5",
    },
    {
        "slug": "workflow-audit",
        "title": "Workflow audit",
        "tagline": "Fourteen recurring tasks in, three actually worth automating",
        "summary": (
            "An audit of my own recurring work, which picked three targets for automation and "
            "killed the rest before anything was built."
        ),
        "problem": (
            "The default advice is add AI to more things. Applied to a real week that "
            "produces a long list of candidates and no way to choose between them, so effort "
            "goes into the most interesting one rather than the most useful one."
        ),
        "built": (
            "I listed fourteen things I actually do repeatedly, scored each on volume, how "
            "predictable the input is, and what a wrong answer costs, and kept three. Then I "
            "set up a project workspace carrying the context, the constraints and the tone, "
            "so the setup survives past the week it was made in."
        ),
        "learned": (
            "The audit was the deliverable, not the automation. Two tasks I was certain were "
            "worth automating failed the predictability test once I saw the real volume, and "
            "killing them early was the highest-value hour in the project. The scoring also "
            "told me which target to build first, which is the part people usually guess."
        ),
        "facts": [
            ("Tasks audited", "14"),
            ("Kept", "3"),
            ("Output", "scored decision"),
        ],
        "stack": ["Workflow audit", "Claude Projects"],
        "source_url": "https://github.com/parth5012/flyrank/tree/main/ai-fluency/FL-01",
        "source_label": "Audit and scoring",
    },
    {
        "slug": "catalogue-scraper",
        "title": "Catalogue scraper",
        "tagline": "Sixty records, validated, cached, and isolated when one breaks",
        "summary": (
            "Three catalogue pages into sixty validated records, with caching, dedup and a "
            "run report that proves exactly what happened on every run."
        ),
        "problem": (
            "Real data is dirty. A scraper that writes malformed rows into its JSON is worse "
            "than no scraper, because the failure shows up later, downstream, as somebody "
            "else's bug."
        ),
        "built": (
            "Three catalogue pages become sixty books through a Pydantic schema where the "
            "canonical product URL is the identity, so re-running never doubles the output. "
            "Pages are cached to disk so a second run makes no requests at all, real requests "
            "are spaced 0.5s apart with a 10s timeout, and retries fire only on timeout or "
            "5xx, never on 403 or 404. Anything invalid is quarantined with a reason instead "
            "of entering the dataset, and each run writes a report with fetched pages, cache "
            "hits, valid, invalid and failed counts."
        ),
        "learned": (
            "I injected a deliberately broken URL to see what happens. One page failed and "
            "the run still returned all sixty valid records, because the failure was isolated "
            "to that page. Before that test, failure isolation was something I believed; now "
            "it is a number in a file I can point at. The real limitation is that the "
            "selectors are coupled to the current markup, and a redesign would break them."
        ),
        "facts": [
            ("Records", "60"),
            ("Politeness delay", "0.5s"),
            ("Cache hits, 2nd run", "63"),
            ("Broken page", "1, still 60 valid"),
        ],
        "stack": ["Python", "BeautifulSoup", "Pydantic", "requests"],
        "source_url": "https://github.com/parth5012/flyrank/tree/main/backend/Assignment%205",
        "source_label": "Source and run report",
        "honest_gap": (
            "Selectors are coupled to the current page markup. There is no headless-browser "
            "fallback, on purpose: this site serves everything in the first response, so a "
            "browser would only add cost."
        ),
    },
]

BREAKS = [
    {
        "what": "The classifier's live-model eval score is not recorded",
        "status": "fix-now",
        "note": "The stub run is logged at 2/8. The real-model run still has to be captured "
                "and pasted into the README before this case can be called measured.",
    },
    {
        "what": "Urgency is returned but never scored",
        "status": "known",
        "note": "The contract allows low/normal/high and the eval only checks category, so a "
                "right-team-wrong-priority answer passes. Naming it beats hiding it.",
    },
    {
        "what": "The scraper's selectors are tied to one page's markup",
        "status": "known",
        "note": "A redesign of books.toscrape.com would break extraction. No headless "
                "fallback is included by design, and the coupling is documented.",
    },
    {
        "what": "Contact form rate limiting is per server instance and in memory",
        "status": "known",
        "note": "The cap is deliberately generous (20 an hour) because carriers and office "
                "Wi-Fi put many real people behind one address, but it is still a single "
                "instance's memory. A real deployment would move it to Redis or the "
                "platform's limiter; it is noted rather than pretended away.",
    },
    {
        "what": "No automated test suite on the web layer",
        "status": "known",
        "note": "The contact endpoint has 26 tests. Every other route is manual QA, which is "
                "the honest state of this site today.",
    },
    {
        "what": "The contact form needs one environment variable to deliver",
        "status": "fix-now",
        "note": "With no webhook configured the endpoint returns a clear error instead of "
                "faking success. Set CONTACT_WEBHOOK and it delivers.",
    },
]

BREAKS_LABEL = {
    "fix-now": ("Fixing now", "amber"),
    "known": ("Known limitation", "slate"),
}