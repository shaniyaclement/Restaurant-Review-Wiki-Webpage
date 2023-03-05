from flask import Flask, render_template, request, redirect, url_for, flash, abort, session

def make_endpoints(app, backend):
    @app.route("/")
    def home():
        username = request.args.get('username', default="")
        return render_template('main.html', username=username)
    
    @app.route("/about")
    def about():
        username = request.args.get('username', default="")
        image_names = backend.get_all_image_names()
        return render_template('about.html',image_names = image_names, username=username)

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
            file.save(file.filename)
            return home()
    @app.route('/pages')
    def pages():
        username = request.args.get('username', default="")
        page_names = backend.get_all_page_names()
        return render_template('index.html', page_names=page_names,username =username)
        
    @app.route('/pages/<page_name>')
    def show_page(page_name):
        username = request.args.get('username', default="")
        # Fetch the text content from the GCS content bucket using the page name
        text_content = backend.get_wiki_page(page_name)
        if text_content is None:
            abort(404)
        return render_template('page.html', page_name=page_name, text_content=text_content,username = username)
