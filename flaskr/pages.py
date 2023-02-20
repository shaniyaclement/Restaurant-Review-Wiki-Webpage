from flask import render_template, request, redirect, url_for

def make_endpoints(app, backend):

    # Flask uses the "app.route" decorator to call methods when users
    # go to a specific route on the project's website.
    @app.route("/")
    def home():
        return render_template('main.html')

    # TODO(Project 1): Implement additional routes according to the project requirements.
    @app.route("/sign_up")
    def sign_up():
        return render_template('sign_up.html')

    @app.route("/log_in", methods=["GET"])
    def log_in():
        return render_template('login.html')

    @app.route("/authenticate", methods=["POST"])
    def authenticate():
        username = request.form['username']
        password = request.form['password']
        result = backend.authenticate_user(username, password)
        #print(result)
        if result['success']:
            return redirect(url_for('dashboard'))
        else:
            error_message = result['message']
            return render_template('login.html', error=error_message, show_popup=True)

    @app.route("/dashboard")
    def dashboard():
        return render_template('dashboard.html')
