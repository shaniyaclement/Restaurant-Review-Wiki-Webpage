from flask import Flask, render_template, request, redirect, url_for, flash, abort, session
from google.cloud import storage

def make_endpoints(app, backend):
    # Flask uses the "app.route" decorator to call methods when users
    # go to a specific route on the project's website.
    @app.route("/")
    def home():
        username = request.args.get('username', default="")
        return render_template('main.html', username=username)
    
    @app.route("/about")
    def about():
        username = ""
        if "username" in session:
            username = session["username"]
        image_names = backend.get_all_image_names()
        print(len(image_names))
        return render_template('about.html',image_names = image_names,username=username)

    # TODO(Project 1): Implement additional routes according to the project requirements.
    @app.route("/pages")
    def pages():
        return render_template("pages.html")

    @app.route("/signup")
    def sign_up():
        return render_template('sign_up.html')

    @app.route("/login", methods=["GET"])
    def log_in():
        return render_template('login.html')
    
    @app.route('/upload')  
    def upload(): 

        return render_template("upload.html")    

    @app.route("/authenticate", methods=["POST"])
    def authenticate():
        username = request.form['username']
        password = request.form['password']
        result = backend.authenticate_user(username, password)
        if result['success']:
            session["username"] = username
            return render_template('main.html', username=username)
        else:
            error_message = result['message']
            return render_template('login.html', error=error_message, show_popup=True)

    @app.route("/authenticate_new_user", methods=["POST"])
    def authenticate_new_user():
        username = request.form['username']
        password = request.form['password']
        result = backend.authenticate_new_user(username, password)
        if result['success']:
            return render_template('main.html', username=username)
        else:
            error_message = result['message']
            return render_template('sign_up.html', error=error_message, show_popup=True)

    @app.route("/logout")
    def dashboard():
        return render_template('main.html', username='')

    @app.route('/authenticate_upload', methods = ['POST'])  
    def authenticate_upload():  
        if request.method == 'POST':
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)  
            file = request.files['file']
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)

        storage_client = storage.Client()
        bucket = storage_client.bucket("wiki_contents_groupx/images")
        blob = bucket.blob(file.filename)

        generation_match_precondition = 0

        blob.upload_from_filename(file.filename, if_generation_match=generation_match_precondition)
        return home()
 