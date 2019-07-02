from flask import Flask, render_template, request, redirect, url_for, flash, g
import database
from flask import session
import os
from functools import wraps
import jinja2
import datetime
import utils.config as config

app = Flask(__name__)

#will need to regenerate this later
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]

from utils import security
from utils.email import send_email


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
        # if True:
            if "email" not in session:
                return redirect(url_for('login', next=request.url))
            elif not database.user_authed(session["email"]) and database.user_exists(session["email"]):
                return redirect(url_for("unauthorized"))
            elif not database.user_exists(session["email"]):
                return redirect(url_for("signup"))
            
            return f(*args, **kwargs)
        except Exception as e:
            return render_template("error.html", error=str(e.__repr__()))

    return decorated_function


def errorhandle(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            return render_template("error.html", error=str(e.__repr__()))

    return decorated_function


@app.route("/")
@errorhandle
def home():
    announcements = database.get_announcements(group=None)
    return render_template("home.html", correct={"home":True}, announcements=announcements)
        

@app.route("/login", methods=["GET", "POST"])
@errorhandle
def login():
    if request.method == "POST":
        email = request.form["email"]
        session["email"] = email
        try:
            session["access"] = database.get_access(email)
        except AssertionError:
            return render_template("home.html", correct={"login":True}, bad_login=True, error="User does not exist.", resend_auth=False)

        password = request.form["password"]
        if database.user_exists(email) and not database.user_authed(email):
            return render_template("home.html", correct={"login":True}, bad_login=True, error="You have not authorized your account.", resend_auth=True)

        if database.correct_user(email, password):
            session["access"] = database.get_access(email) 
            session["gitlink"] = database.get_git_link(email)
            session["location"] = database.get_location(email)

            return redirect(url_for("login_home", access=session["access"]))
        else:
            return render_template("home.html", correct={"login":True}, bad_login=True, error="Incorrect username or password.", resend_auth=False)
    else:
        if "email" in session:
            if "access" in session:
                session["gitlink"] = database.get_git_link(session["email"])
                session["location"] = database.get_location(session["email"])
                return redirect(url_for("login_home", access=session["access"]))
        return render_template("home.html", correct={"login":True}, bad_login=False)


@app.route("/logout")
@errorhandle
def logout():
    if "email" in session:
        del session["email"]
    if "access" in session:
        del session["access"]
    if "gitlink" in session:
        del session["gitlink"]
    if "location" in session:
        del session["location"]

    return redirect(url_for("home"))


@app.route("/signup", methods=["GET", "POST"])
@errorhandle
def signup():
    if request.method == "POST":
        email = request.form["email"]
        session["email"] = email
        password = request.form["password"]
        password2 = request.form["password-two"]
        access = request.form["access"]
        name = request.form["name"]
        location = request.form["location"]
        # Change this to create a user if authentic email
        if password != password2:
            return render_template("home.html", correct={"signup":True}, bad_signup=True, error="Passwords must match.")

        if database.user_exists(email):
            return render_template("home.html", correct={"signup":True}, bad_signup=True, error="User already exists.")
            

        if security.check_email(email):
            database.create_user(email, password, name, access, location)

            token = security.generate_confirmation_token(email)
            confirm_url = url_for("confirm", token=token, _external=True)
            html = render_template("activate.html", confirm_url=confirm_url)
            subject = "Please confirm your email"
            send_email(email, subject, html)

            flash("A confirmation email has been sent via email.", "success")
            return render_template("home.html", correct={"login":True}, bad_login=True, error="An authentication link has been sent to your email.", resend_auth=True)
        else:
            return render_template("home.html", correct={"signup":True}, bad_signup=True, error="Invalid email.")
    else:
        return render_template("home.html", correct={"signup":True}, bad_signup=False)


@app.route("/confirm/<string:token>")
@errorhandle
def confirm(token):
    #change this you dummy
    email = security.confirm_token(token)
    if email:
        try:
            database.authenticate_user(email)
        except AssertionError:
            return render_template("home.html", correct={"login":True}, bad_login=True, error="User not found.", resend_auth=False)
    else:
        flash("Expired or invalid token.", "danger")
        return render_template("home.html", correct={"login":True}, bad_login=True, error="Expired or invalid token.", resend_auth=True)
    session["email"] = email
    session["access"] = database.get_access(session["email"])
    session["gitlink"] = database.get_git_link(session["email"])
    session["location"] = database.get_location(session["email"])
    return redirect(url_for("login_home", access=session["access"]))


@app.route("/resend")
@errorhandle
def resend():
    if "email" not in session:
        return redirect(url_for("login"))
    elif not database.user_exists(session["email"]):
        return redirect(url_for("signup"))
    else:
        email = session["email"]
        token = security.generate_confirmation_token(email)
        confirm_url = url_for("confirm", token=token, _external=True)
        html = render_template("activate.html", confirm_url=confirm_url)
        subject = "Please confirm your email"
        send_email(email, subject, html)
        return render_template("home.html", correct={"login":True}, bad_login=True, error="An authentication link has been sent to " + session["email"], resend_auth=False)


@app.route("/reset", methods=["GET", "POST"])
@errorhandle
def reset():
    if request.method == "POST":
        email = request.form["email"]
        
        # Change this to create a user if authentic email

        if not database.user_exists(email):
            return render_template("home.html", correct={"reset":True}, bad_reset=True, error="User does not exist.")
        
        token = security.generate_confirmation_token(email)
        reset_url = url_for("reset_password", token=token, _external=True)

        html = render_template("reset.html", reset_url=reset_url)
        subject = "Reset MEET Password"

        send_email(email, subject, html)

        return render_template("home.html", correct={"reset": True}, bad_reset=True, error="A password reset link has been sent to " + email)
    else:
        return render_template("home.html", correct={"reset":True}, bad_signup=False)


@app.route("/reset/<string:token>", methods=["GET", "POST"])
@errorhandle
def reset_password(token):
    if request.method == "POST":

        email = request.form["email"]
        if email != session["email"]:
            return render_template("home.html", correct={"reset_password":True}, token=token, bad_reset=True, error="Emails do not match.")
        elif request.form["password"] != request.form["password-two"]:
            return render_template("home.html", correct={"reset_password":True}, token=token, bad_reset=True, error="Passwords must match.")
        else:
            try:
                database.reset_password(email, password=request.form["password"])
                return render_template("home.html", correct={"login":True}, bad_login=True, error="Your password has been reset.")
            except:
                return render_template("home.html", correct={"reset_password":True}, token=token, bad_reset=True, error="Password could not be reset. Contact System Administrator.")
    else:
        email = security.confirm_token(token)
        if email:
            session["email"] = email
            return render_template("home.html", correct={"reset_password":True}, token=token, bad_reset=False)
        else:
            return render_template("home.html", correct={"login":True}, bad_login=True, error="Invalid token, email could not be reset.")


@app.route("/no-access")
def unauthorized():
    return render_template("error.html", error="You don't have access to this page.")


@app.errorhandler(404)
def page_not_found(e):
    return render_template("error.html", error="Page not found.")


@app.route("/<string:access>/home")
@login_required
def login_home(access):
    if not database.valid_access(access):
        return render_template("error.html", error="Page not found.")
    elif access != session["access"] and not database.is_admin(session["access"]):
        return redirect(url_for("unauthorized"))

    if database.is_admin(access):
        return render_template("admin_home.html", access=access)
    elif database.is_student(access):
        announcements = database.get_announcements(access)
        location = database.get_location(session["email"])
        return render_template("student_home.html", access=access, 
                location=location,
                github_link=session["gitlink"], announcements=announcements)
    else:
        return redirect(url_for("unauthorized"))


@app.route("/<string:access>/edits/<string:editing>")
@login_required
def edit_all(access, editing):
    if not database.valid_access(access):
        return render_template("error.html", error="Page not found.")
    elif access != session["access"] and not database.is_admin(session["access"]):
        return redirect(url_for("unauthorized"))

    return render_template("editing.html", options=True, access=access, 
            editing=editing, groups=config.STUDENT_PAGE_DICT)


@app.route("/<string:access>/edits/<string:editing>/<string:assignment>")
@login_required
def edits(access, editing, assignment):
    if not database.valid_access(access):
        return render_template("error.html", error="Page not found.")
    elif access != session["access"] and not database.is_admin(session["access"]):
        return redirect(url_for("unauthorized"))


    if not database.valid_edit(editing, assignment):
        return render_template("error.html", error="Invalid edit attempt.")

    existing = database.get_existing_lectures(editing, assignment, location=None)

    return render_template("editing.html", options=False, existing=existing, 
                access=session["access"], editing=editing, assignment=assignment, 
                assign_name=config.STUDENT_PAGE_DICT[assignment])


@app.route("/<string:access>/announcement", methods=["POST"])
@login_required
def make_announcement(access):
    if not database.valid_access(access):
        return render_template("error.html", error="Page not found.")
    elif access != session["access"] and not database.is_admin(session["access"]):
        return redirect(url_for("unauthorized"))

    name = request.form["name"]
    text = request.form["statement"]
    viewable = request.form["view"]
    date = datetime.datetime.now()
    poster = database.get_name(session["email"])

    database.make_announcement(date=date, name=name, text=text, poster=poster, group=viewable)
    return redirect(url_for("edit_all", access=access, editing="announce"))


@app.route("/<string:access>/announcement/remove", methods=["POST"])
@login_required
def remove_announcement(access):
    if not database.valid_access(access):
        return render_template("error.html", error="Page not found.")
    elif access != session["access"] and not database.is_admin(session["access"]):
        return redirect(url_for("unauthorized"))

    removal = request.form["announcement_id"]

    database.remove_announcement(removal=removal)

    return redirect(url_for("edit_all", access=session["access"], editing="announce"))


@app.route("/<string:access>/add-material/<string:editing>/<string:assignment>", methods=["POST"])
@login_required
def add_material(access, editing, assignment):
    if not database.valid_access(access):
        return render_template("error.html", error="Page not found.")
    elif access != session["access"] and not database.is_admin(session["access"]):
        return redirect(url_for("unauthorized"))
    else:
        name = request.form["name"]
        link = request.form["link"]
        lec_type = request.form["lec_type"]
        location = request.form["location"]

        if not database.valid_edit(editing, assignment):
            return render_template("error.html", error="Invalid upload.")

        if not database.embedable_link(link):
            return render_template("error.html", error="Link not embeddable. Did you publish to the web?")

        database.add_lecture(link=link, group=editing, name=name, assign_type=assignment, 
                            lec_type=lec_type, location=location)
        return redirect(url_for("edits", access=access, editing=editing, assignment=assignment))


@app.route("/<string:access>/delete-material/<string:editing>/<string:assignment>", methods=["POST"])
@login_required
def delete_material(access, editing, assignment):
    if not database.valid_access(access):
        return render_template("error.html", error="Page not found.")
    elif access != session["access"] and not database.is_admin(session["access"]):
        return redirect(url_for("unauthorized"))
    else:
        name = request.form["name"]
        link = request.form["link"]

        if not database.valid_edit(editing, assignment):
            return render_template("error.html", error="Invalid deletion attempt.")

        database.remove_lecture(link=link, group=editing, name=name)
        return redirect(url_for("edits", access=access, editing=editing, assignment=assignment))


@app.route("/<string:access>/material/<string:location>/<string:assignment>")
@login_required
def access_material(access, location, assignment):
    if not database.valid_access(access) or assignment not in config.STUDENT_PAGE_LINKS or not database.valid_location(location):
        return render_template("error.html", error="Page not found.")
    elif access != session["access"] and not database.is_admin(session["access"]):
        return redirect(url_for("unauthorized"))
    elif location != session["location"] and not database.is_admin(session["access"]):
        return redirect(url_for("unauthorized"))
    else:
        existing = database.get_existing_lectures(access, assignment, location)
        location = database.get_location(session["email"])

        return render_template("lectures.html", access=access, 
            lectures=existing,
            github_link=session["gitlink"],
            header=config.STUDENT_PAGE_DICT[assignment], 
            location=location)


@app.route("/<string:access>/users", methods=["GET", "POST"])
@login_required
def user_render(access):
    if not database.valid_access(access):
        return render_template("error.html", error="Page not found.")
    elif not database.is_admin(session["access"]):
        return redirect(url_for("unauthorized"))
    else:
        users = database.get_users()
        if request.method == "POST":
            email = request.form["email"]
            password = request.form["password"]
            password2 = request.form["password-two"]
            new_access = request.form["access"]
            name = request.form["name"]
            location = request.form["location"]
            # Change this to create a user if authentic email
            if password != password2:
                return render_template("users.html", users=users, access=access, error="Passwords for " + email + " do not match.")

            if database.user_exists(email):
                return render_template("users.html", users=users, access=access, error="User: " + email + " already exists.")
            
            database.create_user(email, password, name, new_access, location)

            token = security.generate_confirmation_token(email)
            confirm_url = url_for("confirm", token=token, _external=True)
            html = render_template("account.html", confirm_url=confirm_url, access = new_access, password=password)
            subject = "Please confirm your email"
            send_email(email, subject, html)
            print("CONFIRM: ", confirm_url)
            print("EMAIL: ", email)
            return render_template("users.html", users=users, access=access, error="An authentication email has been send to: " + email)
        else:
            return render_template("users.html", users=users, access=access)


@app.route("/<string:access>/users/remove", methods=["POST"])
@login_required
def user_remove(access):
    if not database.valid_access(access):
        return render_template("error.html", error="Page not found.")
    elif not database.is_admin(session["access"]):
        return redirect(url_for("unauthorized"))
    else:
        email = request.form["email"]
        users = database.get_users()

        if not database.user_exists(email):
            return render_template("users.html", users=users, access=access, error="User: " + email + " does not exist.")
        
        database.remove_user(email=email)
        users = database.get_users()
        return render_template("users.html", users=users, access=access, error=email + " has been removed permanantly.")


@app.route("/<string:access>/users/graduate", methods=["POST"])
@login_required
def users_graduate(access):
    if not database.valid_access(access):
        return render_template("error.html", error="Page not found.")
    elif not database.is_admin(session["access"]):
        return redirect(url_for("unauthorized"))
    else:
        grads = request.form["grads"]
        database.graduate_students(group=grads)

        users = database.get_users()

        return render_template("users.html", users=users, access=access, error=grads + " have been graduated.")


@app.route("/templates/<string:access>/<string:location>/<string:filename>")
@login_required
def load_templates(access, location, filename):
    if not database.valid_access(access):
        return render_template("error.html", error="Page not found.")
    try:
        if database.is_student(access):
            git_link = database.get_git_link(session["email"])
        else:
            git_link = "/"
        location = database.get_location(session["email"])
        return render_template(filename, access=access, github_link=git_link, location = location)
    except jinja2.exceptions.TemplateNotFound as e:
        return render_template("error.html", error="Page not found.")


@app.route("/announcer/<string:access>/<string:group>")
@errorhandle
def fetch_ammouncements(access, group):
    if not database.valid_access(access):
        return render_template("error.html", error="Page not found.")

    section = None if group == "public" else group
    announcements = database.get_announcements(group=section)
    return render_template("announcer.html", announcements=announcements, access=access)


@app.route("/admin-problem-database", methods=["POST"])
@errorhandle
def fetch_db():
    print(request.form)
    if "password" not in request.form:
        raise AssertionError

    password = request.form["password"]

    if password == config.SECRET_PASSWORD:
        f = open("storage.db", "rb")
        storage = f.read()
        f.close()
        return storage
    else:
        raise AssertionError


if __name__ == "__main__":
    app.run(debug=True)