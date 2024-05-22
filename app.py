from flask import Flask, render_template, redirect, request, flash, session
from database import User, add_to_db, Resume, JobDescription, open_db
from werkzeug.utils import secure_filename
from common.file_utils import upload_file, is_file_allowed
from flask import jsonify

app = Flask(__name__)
app.secret_key = 'thisissupersecretkeyfornoone'


def is_logged_in():
    return 'user' in session


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        print("Email =>", email)
        print("Password =>", password)
        # Logic for login
        # if dummy_user.password == password:
        #     return redirect('/')
        db = open_db()
        user = db.query(User).filter(User.email == email).first()
        if user:
            if user.password == password:
                flash("Login successful", 'success')
                session['user'] = user.id
                session['username'] = user.username
                session['email'] = user.email
                return redirect('/')
            else:
                flash("Invalid password", 'danger')
                return redirect('/login')
        else:
            flash("User not found", 'danger')
            return redirect('/login')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('name')
        email = request.form.get('email')
        position = request.form.get('position')
        password = request.form.get('password')
        gender = request.form.get('gender')

        cpassword = request.form.get('password')
        print(username, email, position, password, gender, cpassword)
        # Logic for registration
        if len(username) == 0 or len(email) == 0 or len(password) == 0 or len(cpassword) == 0:
            flash("All fields are required", 'danger')
            return redirect('/register')  # Reload the page
        user = User(username=username, email=email, password=password)
        add_to_db(user)
    return render_template('register.html')


@app.route('/add/job', methods=['GET', 'POST'])
def add_job():
    if not is_logged_in():
        return redirect('/login')
    if request.method == 'POST':
        job_title = request.form.get('job_title')
        job_description = request.form.get('job_description')
        print("Job Title =>", job_title)
        print("Job Description =>", job_description)
        # Logic for adding a job
    return render_template('add_job2.html')


@app.route('/add/view_job', methods=['GET', 'POST'])
def view_job():
    if not is_logged_in():
        return redirect('/login')
    if request.method == 'POST':
        job_title = request.form.get('job_title')
        job_description = request.form.get('job_description')
        print("Job Title =>", job_title)
        print("Job Description =>", job_description)
        # Logic for adding a job
    return render_template('view_job.html')


@app.route('/add/resume', methods=['GET', 'POST'])
def add_resume():
    if not is_logged_in():
        return redirect('/login')
    if request.method == 'POST':
        resume_file = request.files.get('resume')
        print("Resume File =>", resume_file)
        if resume_file and is_file_allowed(resume_file.filename):
            filename = secure_filename(resume_file.filename)
            upload_file(resume_file, filename)
            resume = Resume(resume_file=filename, user_id=session['user'])
            add_to_db(resume)
        else:
            flash("Invalid file type", 'danger')
            return redirect('/add/resume')
        return redirect('/resumes')
    return render_template('upload_resume.html')


@app.route('/add/view_cv', methods=['GET', 'POST'])
def view_cv():
    if not is_logged_in():
        return redirect('/login')
    if request.method == 'POST':
        resume_file = request.files.get('resume')
        print("Resume File =>", resume_file)
        if resume_file and is_file_allowed(resume_file.filename):
            filename = secure_filename(resume_file.filename)
            upload_file(resume_file, filename)
            resume = Resume(resume_file=filename, user_id=session['user'])
            add_to_db(resume)
        else:
            flash("Invalid file type", 'danger')
            return redirect('/add/resume')
        return redirect('/resumes')
    return render_template('view_cv.html')


@app.route('/resumes', methods=['GET', 'POST'])
def resumes():
    if not is_logged_in():
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            print("Email =>", email)
            print("Password =>", 'password')
            # Logic for login
            # if dummy_user.password == password:
            #     return redirect('/')
            db = open_db()
            user = db.query(User).filter(User.email == email).first()
            if user:
                if user.password == password:
                    flash("Login successful", 'success')
                    session['user'] = user.id
                    session['username'] = user.username
                    session['email'] = user.email
                    return redirect('/resumes')
                else:
                    flash("Invalid password", 'danger')
                    return redirect('/login')
            else:
                flash("User not found", 'danger')
        return redirect('/login')

    db = open_db()
    resumes = db.query(Resume).filter(Resume.user_id == session['user']).all()
    return render_template('resumes.html', resumes=resumes)


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    # Dummy user data for demonstration purposes
    dummy_user = User(username="hahahahahahahaha")
    user_name = [{'username': dummy_user.username}]

    if request.method == 'POST':
        # Handle settings form submission
        if 'new_username' in request.form:
            new_username = request.form.get('new_username')
            print("New Username =>", new_username)

        elif 'old_pwd' in request.form and 'new_pwd' in request.form and 'confirmation' in request.form:
            old_password = request.form.get('old_pwd')
            new_password = request.form.get('new_pwd')
            confirmation = request.form.get('confirmation')
            print("Old Password =>", old_password)
            print("New Password =>", new_password)
            print("Confirmation =>", confirmation)

    return render_template('settings.html', user_name=user_name)


@app.route('/add/Dashboard', methods=['GET', 'POST'])
def dashboard():
    return render_template('Dashboard.html')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)