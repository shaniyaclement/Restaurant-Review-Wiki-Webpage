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
        length = len(image_names)
        return render_template('about.html', length=length,
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
        page_names = backend.filter_search(searched)
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
        result = backend.authenticate_upload(uploaded_file, f_name, username)
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


    @app.route('/edit_pages')
    def list_user_pages():
        '''
        Route for listing all the pages the user previously uploaded
        '''
        username = request.args.get('username', default="")
        page_names = backend.get_all_page_names_for_user(username)
        return render_template('edit_pages_index.html',
                               page_names=page_names,
                               username=username,
                               instructions=True)

    @app.route('/edit_pages_content/<page_name>')
    def edit_user_pages(page_name):
        '''
        Route for listing all the pages the user previously uploaded
        '''
        username = request.args.get('username', default="")
        return render_template('edit_pages.html',
                               page_name=page_name,
                               username=username)

    @app.route('/authenticate_edit', methods=['POST'])
    def authenticate_edit():
        '''
        Route for editing files as an authenticated user
        '''
        username = request.args.get('username', default="")
        og_fn = request.args.get('og_fn', default="")
        uploaded_file = request.files['file']
        f_name = request.form['upload']
        result = backend.authenticate_edit(uploaded_file, f_name, og_fn,
                                           username)
        if result['success']:
            return render_template(
                'edit_pages.html',
                error="Page updated successfully!",
                show_popup=True,
                username=username,
                page_name=f_name
            )  # not an error, simply using that param for a pop-message
        elif result['message'] == 'You can only have .txt files':
            return render_template('edit_pages.html',
                                   error="You can Only upload .txt files!",
                                   show_popup=True,
                                   username=username,
                                   page_name=og_fn)

        elif result['message'] == 'File is not in UTF-8 encoding!':
            return render_template('edit_pages.html',
                                   error="File is not in UTF-8 encoding!",
                                   show_popup=True,
                                   username=username,
                                   page_name=og_fn)  # check encoding

        elif result['message'] == 'File is empty!':
            return render_template('edit_pages.html',
                                   error="File is empty!",
                                   show_popup=True,
                                   username=username,
                                   page_name=og_fn)  # check if file is empty

        elif result[
                'message'] == 'Please enter a file name or use previous page title!':
            return render_template(
                'edit_pages.html',
                error="Please enter a page title name for the submission!",
                show_popup=True,
                username=username,
                page_name=og_fn)

    @app.route('/del_page/<page_name>')
    def del_page(page_name):
        '''
        Route for deleting a page the user previously uploaded
        '''
        username = request.args.get('username', default="")
        backend.del_page(page_name)
        return render_template('edit_pages_index.html',
                               error="Page deleted successfully!",
                               show_popup=True,
                               username=username,
                               instructions=False)
    @app.route('/pages/<page_name>')
    def show_page(page_name):
        '''
        Route for param pages
        '''
        username = request.args.get('username', default="")
        text_content = backend.get_wiki_page(page_name)
        if text_content is None:
            abort(404)
        average_rating = backend.get_average_rating(page_name)
        reviews = backend.get_reviews(page_name)
        user_review = next(
            (review for review in reviews if review["username"] == username),
            None)
        reviewed = user_review is not None
        return render_template('page.html',
                               page_name=page_name,
                               text_content=text_content,
                               username=username,
                               average_rating=average_rating,
                               reviews=reviews,
                               reviewed=reviewed)

    @app.route('/pages/<page_name>/submit_review', methods=['POST'])
    def submit_review(page_name):
        username = request.args.get('username', default="")
        if not username:
            return redirect(url_for('log_in'))
        rating = request.form['rating']
        backend.add_review(page_name, username, rating)
        return redirect(
            url_for('show_page', page_name=page_name, username=username))

    @app.route('/ratings', methods=['GET'])
    def view_ratings():
        '''
        Route for veiwing the Ratings html UI Dagi made, 
        left to Thomas as to how to incorporate with the rest of his reqs 
        '''
        username = request.args.get('username', default="")
        return render_template('ratings.html', username=username)
