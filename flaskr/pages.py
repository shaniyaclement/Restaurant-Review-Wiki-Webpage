from flask import Flask, render_template, request, redirect, url_for, flash, abort, session, make_response, Response

def make_endpoints(app, backend):
    @app.route("/")
    def home():
        username = request.args.get('username', default="")
        return render_template('main.html', username=username)
    
    @app.route("/about")
    def about():
        username = request.args.get('username', default="")
        image_names = backend.get_images()
        answ = backend.get_image('Prof.png')
        print(answ)
        return render_template('about.html',image_names = image_names, username=username, answ=answ)

    @app.route("/signup")
    def sign_up():
        return render_template('sign_up.html')

    @app.route("/login", methods=["GET"])
    def log_in():
        return render_template('login.html')
    
    @app.route('/upload')  
    def upload():
        username = request.args.get('username', default="")  
        return render_template("upload.html", username=username)    

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
    def logout():
        #return render_template('main.html', username='')
        res = make_response(render_template('main.html', username=''))
        res.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return res

    @app.route('/authenticate_upload', methods = ['POST'])  
    def authenticate_upload():  
        username = request.args.get('username', default="") 
        uploaded_file = request.files['file']
        if not uploaded_file.filename.endswith('.txt'):
            return render_template('upload.html', error="You can Only upload .txt files!", show_popup=True, username=username)
        file_contents = uploaded_file.read()
        # check if file is empty
        try:
            decoded_contents = file_contents.decode('utf-8')
        except UnicodeDecodeError:
            return render_template('upload.html', error="File is not in UTF-8 encoding!", show_popup=True, username=username)
        if not decoded_contents.strip():
            return render_template('upload.html', error="File is empty!", show_popup=True, username=username)
        f_name = request.form['upload']
        if len(f_name)<1:
            return render_template('upload.html', error="Please enter a name for the submission!", show_popup=True, username=username)
        backend.upload(file_contents, f_name)
        return render_template('upload.html', error="File uploaded successfully!", show_popup=True, username=username)  # not an error, simply using that param for a pop-message
        
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
