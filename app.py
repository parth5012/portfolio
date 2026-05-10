import os
from datetime import datetime
from flask import Flask, render_template, redirect, flash


app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-change-in-production')


# ── context processor: inject `now` into every template ──────────────────────
@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/projects')
def projects():
    return render_template('projects.html')


@app.route('/contact')
def contact():
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
    return redirect("https://drive.google.com/file/d/18wDQQyzVUJF5xzhxYksk1bkdkqTtgNGB/view?usp=sharing")


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
