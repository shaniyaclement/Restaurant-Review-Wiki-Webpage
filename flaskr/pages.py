from flask import Flask, render_template, request, redirect, url_for, flash, abort, session, make_response, Response, send_file
import io


def make_endpoints(app, backend):

    @app.route("/")
    def home():
        '''
        Route for Home
        '''
        username = request.args.get('username', default="")
        return render_template('main.html', username=username)

    @app.route("/about")
    def about():
        '''
        Route for About us page
        '''
        username = request.args.get('username', default="")
        image_names = backend.get_images()
        return render_template('about.html',
                               image_names=image_names,
                               username=username)

    @app.route("/image/<string:image_name>")
    def get_image(image_name):
        '''
        Our method of showing/getting images from private bucket to public about_us_page
        '''
        image_data = backend.get_image(image_name)
        if image_data is None:
            return Response(status=404)
        return Response(image_data, mimetype="image/jpeg")

    @app.route("/signup")
    def sign_up():
        '''
        Sign up route
        '''
        return render_template('sign_up.html')

    @app.route("/login", methods=["GET"])
    def log_in():
        '''
        Login route
        '''
        return render_template('login.html')

    @app.route('/upload')
    def upload():
        '''
        Upload route
        '''
        username = request.args.get('username', default="")
        return render_template("upload.html", username=username)

    @app.route("/authenticate", methods=["POST"])
    def authenticate():
        '''
        Route for user auth
        '''
        username = request.form['username']
        password = request.form['password']
        result = backend.authenticate_user(username, password)
        if result['success']:
            session["username"] = username
            return render_template('main.html', username=username)
        else:
            error_message = result['message']
            return render_template('login.html',
                                   error=error_message,
                                   show_popup=True)

    @app.route("/search", methods=["POST"])
    def search():
        '''
        Search route
        '''
        searched = request.form['searched']
        username = request.args.get('username', default="")
        page_names = backend.get_all_page_names()
        for page_name in page_names:
            if (searched.lower() not in (backend.get_wiki_page(page_name)).lower()):
                page_names.remove(page_name)
        return render_template('search.html', searched=searched, page_names=page_names,
                               username=username)

    @app.route("/authenticate_new_user", methods=["POST"])
    def authenticate_new_user():
        '''
        Route for authenticating new user request
        '''
        username = request.form['username']
        password = request.form['password']
        result = backend.authenticate_new_user(username, password)
        if result['success']:
            return render_template('main.html', username=username)
        else:
            error_message = result['message']
            return render_template('sign_up.html',
                                   error=error_message,
                                   show_popup=True)

    @app.route("/logout")
    def logout():
        '''
        Route for logging out
        '''
        res = make_response(render_template('main.html', username=''))
        res.headers[
            'Cache-Control'] = 'no-cache, no-store, must-revalidate'  # for removing cache data of prev. user
        return res

    @app.route('/authenticate_upload', methods=['POST'])
    def authenticate_upload():
        '''
        Route for uploading files as an authenticated user
        '''
        username = request.args.get('username', default="")
        uploaded_file = request.files['file']
        f_name = request.form['upload']
        result = backend.authenticate_upload(uploaded_file, f_name)
        if result['success']:
            return render_template(
                'upload.html',
                error="File uploaded successfully!",
                show_popup=True,
                username=username
            )  # not an error, simply using that param for a pop-message
        elif result['message'] == 'You can only have .txt files':
            return render_template('upload.html',
                                   error="You can Only upload .txt files!",
                                   show_popup=True,
                                   username=username)

        elif result['message'] == 'File is not in UTF-8 encoding!':
            return render_template('upload.html',
                                   error="File is not in UTF-8 encoding!",
                                   show_popup=True,
                                   username=username)  # check encoding

        elif result['message'] == 'File is empty!':
            return render_template('upload.html',
                                   error="File is empty!",
                                   show_popup=True,
                                   username=username)  # check if file is empty

        elif result['message'] == 'Please enter a file name!':
            return render_template(
                'upload.html',
                error="Please enter a name for the submission!",
                show_popup=True,
                username=username)


    @app.route('/pages')
    def pages():
        '''
        Route for pages index
        '''
        username = request.args.get('username', default="")
        page_names = backend.get_all_page_names()
        return render_template('index.html',
                               page_names=page_names,
                               username=username)

    @app.route('/pages/<page_name>')
    def show_page(page_name):
        '''
        Route for param pages
        '''
        username = request.args.get('username', default="")
        text_content = backend.get_wiki_page(page_name)
        if text_content is None:
            abort(404)
        return render_template('page.html',
                               page_name=page_name,
                               text_content=text_content,
                               username=username)


