import os
from datetime import datetime, timezone
from flask import Flask, render_template, redirect, abort, flash

import contact
import content

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-change-in-production')
contact.init_app(app)


# ── context processor: inject `now` into every template ──────────────────────
@app.context_processor
def inject_now():
    return {'now': datetime.now(timezone.utc), 'site': content.SITE}


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route('/')
def home():
    return render_template('index.html', cases=content.CASES,
                           stats=content.HEADLINE_STATS,
                           featured=content.FEATURED_CASE)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/projects')
def projects():
    return render_template('projects.html', cases=content.CASES,
                           featured=content.FEATURED_CASE)


@app.route('/projects/<slug>')
def project_detail(slug):
    case = next((c for c in content.CASES if c['slug'] == slug), None)
    if case is None:
        abort(404)
    others = [c for c in content.CASES if c['slug'] != slug]
    return render_template('project_details.html', case=case, others=others)


@app.route('/reliability')
def reliability():
    return render_template('reliability.html', breaks=content.BREAKS,
                           labels=content.BREAKS_LABEL)


@app.route('/contact')
def contact_page():
    return render_template('contact.html')


@app.route('/blog')
def blog():
    return render_template('blog.html')


@app.route('/skills')
def skills():
    """Redirect /skills to the about page where the skill matrix lives."""
    return redirect('/about')


@app.route('/resume')
def resume():
    flash("Redirecting you to the resume download link!", "info")
    return redirect("https://drive.google.com/file/d/1rcqw895KCUNjJ_-UOVGxEbJAgBO4PWrm/view?usp=sharing")


# ── Error handlers ────────────────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == '__main__':
    app.run(debug=True)
