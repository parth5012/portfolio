from flask import Flask, render_template, flash, redirect, url_for


app = Flask(__name__)
app.secret_key = 'a-super-secret-key-that-should-be-changed'


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/projects')
def projects():
    return render_template('projects.html')


@app.route('/resume')
def resume():
    flash("Redirecting you to the download link!!")
    return redirect("https://drive.google.com/file/d/18wDQQyzVUJF5xzhxYksk1bkdkqTtgNGB/view?usp=sharing")


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

# @app.route('project/{id}')
# def project_details(id):

#     # extracting project details from db
#     return render_template('project_details.html')








if __name__ == "__main__":
    app.run(debug=True)
