from flask import render_template, request, redirect, url_for

def make_endpoints(app, backend):

    # Flask uses the "app.route" decorator to call methods when users
    # go to a specific route on the project's website.
    @app.route("/")
    def home():
        username = request.args.get('username', default="")
        return render_template('main.html', username=username)

    # TODO(Project 1): Implement additional routes according to the project requirements.
    @app.route("/signup")
    def sign_up():
        return render_template('sign_up.html')

    @app.route("/login", methods=["GET"])
    def log_in():
        return render_template('login.html')

    @app.route("/authenticate", methods=["POST"])
    def authenticate():
        username = request.form['username']
        password = request.form['password']
        result = backend.authenticate_user(username, password)
        if result['success']:
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
