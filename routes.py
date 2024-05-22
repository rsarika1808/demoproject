from flask import render_template, redirect, request, flash, session, url_for
import os
from datetime import datetime

from flask import render_template, redirect, request, flash, session, url_for
from flask_login import logout_user, current_user, login_user, login_required
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from werkzeug.utils import secure_filename

from app import app, db
from app.doctotext import extract_text_from_docx
from app.entity_recognizer import extract_skills
from app.models import User, JobDescription, MyUpload, Contact
from app.pdf2text import extract_text_from_pdf


@app.route('/')
@app.route('/index')
@login_required
def index():
    jobs = JobDescription.query.all()
    # todo add pagination
    return render_template('index.html', title='home', jobs=jobs)


##########################################################
#########################JOBS#############################
##########################################################

@app.route('/input', methods=['GET', 'POST'])
def input_page():
    if request.method == 'POST':

        msg = request.form.get('msg')
        title = request.form.get('title')
        category = request.form.get('category')
        keywords = request.form.get('keywords')

        if msg and keywords:  # not none
            keywords = [word.strip().lower() for word in keywords.split(',')]
            if len(msg) >= 150 and len(title) > 4:  # just some validation
                msgObj = JobDescription(details=msg, title=title, keywords=str(keywords),
                                        category=category)  # add data to model object
                db.session.add(msgObj)  # save data in database
                db.session.commit()  # update database
                flash('we have saved the job description detail, please visit the dashboard to view the job card',
                      'success')
                return redirect(url_for('input_page'))
            else:
                flash('description smaller than 150 characters cannot be allowed', 'danger')
        else:
            flash('please fill the job description, the data in the box is just placeholder')
    if os.path.exists('app/sample_job_description.txt'):
        ptext = open('app/sample_job_description.txt').read()
    else:
        ptext = ""
    return render_template('input.html', title="Job Description", pholder=ptext)


@app.route('/job/<jobid>')
@login_required
def view_job(jobid):
    job = JobDescription.query.get(jobid)
    if job is None:
        return redirect(url_for('index'))
    keywords = [word.replace("'", "") for word in job.keywords[1:-1].split(',')]
    return render_template('job_detail.html', title='home', job=job, keywords=keywords)


@app.route('/job/edit/<jobid>', methods=['GET', 'POST'])
@login_required
def edit_job(jobid):
    job = JobDescription.query.get(jobid)
    if job is None:
        return redirect(url_for('index'))

    if request.method == 'POST':

        msg = request.form.get('msg')
        title = request.form.get('title')
        category = request.form.get('category')
        keywords = request.form.get('keywords')

        if msg and keywords:  # not none
            keywords = [word.strip().lower() for word in keywords.split(',')]
            if len(msg) >= 150 and len(title) > 4:  # just some validation
                job = JobDescription.query.get(jobid)
                job.details = msg
                job.title = title
                job.keywords = str(keywords)
                job.category = category  # add data to model object
                db.session.commit()  # update database
                # prediction logic
                flash('we have saved the job description', 'success')
                return redirect(f'/job/{jobid}')
            else:
                flash('description smaller than 150 characters cannot be allowed', 'danger')
        else:
            flash('please fill the job description, the data in the box is just placeholder')
    if os.path.exists('app/sample_job_description.txt'):
        ptext = open('app/sample_job_description.txt').read()
    else:
        ptext = ""
    keywords = [word.replace("'", "") for word in job.keywords[1:-1].split(',')]
    return render_template('job_edit.html', title='edit job', pholder=ptext, job=job, keywords=keywords)


@app.route('/job/delete/<jobid>')
@login_required
def delete_job(jobid):
    try:
        JobDescription.query.filter(JobDescription.id == jobid).delete()
        db.session.commit()
        flash('Job delete successfully', 'info')
    except:
        flash('Job not found', 'danger')
    return redirect(url_for('index'))


###################################################################
#######################AUTHENTICATION##############################
###################################################################

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username and password:
            user = User.query.filter_by(username=username).first()
            if user is None or not user.check_password(password):
                flash('Invalid username or password', 'danger')
                return redirect(url_for('login'))
            login_user(user, remember=True)
            return redirect(url_for('index'))
        else:
            flash('fill your credentials to login', 'danger')
    return render_template('login.html', title='Sign In')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        cpassword = request.form.get('cpassword')
        password = request.form.get('password')
        # print(cpassword, password, cpassword==password)
        if username and password and cpassword and email:
            if cpassword != password:
                flash('Password do not match', 'danger')
                return redirect('/register')
            else:
                if User.query.filter_by(email=email).first() is not None:
                    flash('Please use a different email address', 'danger')
                    return redirect('/register')
                elif User.query.filter_by(username=username).first() is not None:
                    flash('Please use a different username', 'danger')
                    return redirect('/register')
                else:
                    user = User(username=username, email=email)
                    user.set_password(password)
                    db.session.add(user)
                    db.session.commit()
                    flash('Congratulations, you are now a registered user!', 'success')
                    return redirect(url_for('login'))
        else:
            flash('Fill all the fields', 'danger')
            return redirect('/register')

    return render_template('register.html', title='Sign Up page')


@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    if request.method == 'POST':
        email = request.form.get('email')
        if email:
            pass
    return render_template('forgot.html', title='Password reset page')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@login_required
@app.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('profile.html', user=user, title=f'{user.username} profile')


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        current_user.username = request.form.get('username')
        current_user.about_me = request.form.get('aboutme')
        db.session.commit()
        flash('Your changes have been saved.', 'success')
        return redirect(url_for('edit_profile'))
    return render_template('edit_profile.html', title='Edit Profile', user=user)


##########################################################
###################UPLOADING##############################
##########################################################

def allowed_files(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def uploadResume():
    if request.method == 'POST':

        if 'file' not in request.files:
            flash('No file uploaded', 'danger')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('no file selected', 'danger')
            return redirect(request.url)
        if file and allowed_files(file.filename):
            # print(file.filename)
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            upload = MyUpload(file=filename, path=f"/static/uploads/{filename}",
                              extension=os.path.splitext(file.filename)[1], user_id=current_user.id)
            db.session.add(upload)
            db.session.commit()
            flash('file uploaded and saved', 'success')
            session['uploaded_file'] = f"/static/uploads/{filename}"
            return redirect(request.url)
        else:
            flash('wrong file selected, only DOC and PDF images allowed', 'danger')
            return redirect(request.url)
    uploads = MyUpload.query.filter(MyUpload.user_id == current_user.id)

    return render_template('upload.html', title='upload resume', resumes=uploads)


@app.route('/resume/delete/<id>')
@login_required
def delete_resume(id):
    try:
        upload = MyUpload.query.get(id)
        os.unlink(os.path.join('app', 'static', 'uploads', upload.file))
        MyUpload.query.filter(MyUpload.id == id).delete()
        db.session.commit()
        flash('Resume delete successfully', 'success')
    except Exception as e:
        flash(f'Resume not found {e}', 'danger')
    return redirect(url_for('uploadResume'))


@app.route('/resume/view/<id>')
@login_required
def view_resume(id):
    upload = MyUpload.query.get(id)
    return render_template('view.html', upload=upload)


@app.route('/resume/admin')
@login_required
def view_all_resume():
    uploads = MyUpload.query.all()
    return render_template('view_all_uploads.html', resumes=uploads)


######################################################
#####################CONTACTS#########################
######################################################

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        message = request.form.get('message')
        if name and message and email:
            msgObj = Contact(name=name, email=email, message=message)  # add data to model object
            db.session.add(msgObj)  # save data in database
            db.session.commit()  # update database
            flash('we have recieved your message, we will respond ASAP', 'success')
            return redirect(url_for('index'))
        else:
            flash('your have some invalid entries, please fill correctly', 'danger')

    return render_template('contact.html')


@app.route('/contact/admin')
@login_required
def view_all_contacts():
    contacts = Contact.query.all()
    return render_template('view_all_contact.html', contacts=contacts)


@app.route('/contact/delete/<id>')
@login_required
def delete_contact(id):
    Contact.query.filter(Contact.id == id).delete()
    db.session.commit()
    flash('message deleted', 'success')
    return redirect(url_for('view_all_contacts'))


###################################################################
##############################AI###################################
###################################################################


@app.route('/recommend/<jobid>', methods=['GET', 'POST'])
@login_required
def recommend(jobid):
    try:
        session.pop('rePercent')
        session.pop('msg')
        session.pop('skillPercent')
        session.pop('jobid')
        session.pop('resumeid')
    except:
        pass
    job = JobDescription.query.get(jobid)
    resume_text = None
    resumes = MyUpload.query.filter(MyUpload.user_id == current_user.id)
    if job is None:
        return redirect(url_for('index'))
    keywords = [word.replace("'", "") for word in job.keywords[1:-1].split(',')]
    if request.method == 'POST':
        resume_id = request.form.get('resume_id')
        if resume_id:
            selected_resume = MyUpload.query.get(resume_id)
            ext = os.path.splitext(selected_resume.file)[1]
            # print('ext',ext)
            try:
                if ext == '.pdf':
                    resume_text = extract_text_from_pdf("app" + selected_resume.path)
                elif ext == '.doc':
                    resume_text = extract_text_from_docx("app" + selected_resume.path)

                data = [resume_text, job.details]
                cv = CountVectorizer()
                count_matrix = cv.fit_transform(data)
                cosine_similarity(count_matrix)
                matchPercentage = cosine_similarity(count_matrix)[0][1] * 100
                recommendMatchPercentage = round(matchPercentage, 2)
                recommend = "Your resume matches about <b>" + str(
                    recommendMatchPercentage) + "%</b> of the job description."
                session['rePercent'] = recommendMatchPercentage
                session['msg'] = recommend

                user_skills = extract_skills(resume_text, keywords)
                if user_skills is not None:
                    print(" ".join(keywords), " ".join(user_skills))
                    keydata = [" ".join(keywords), " ".join(user_skills)]
                    cv = CountVectorizer()
                    count_matrix = cv.fit_transform(keydata)
                    cosine_similarity(count_matrix)
                    matchPercentage = cosine_similarity(count_matrix)[0][1] * 100
                    skillsMatchPercentage = round(matchPercentage, 2)
                    session['skillPercent'] = skillsMatchPercentage
                session['jobid'] = jobid
                session['resumeid'] = resume_id
                flash("AI results generated successfully", 'success')
                return redirect(url_for('result_ai'))
            except Exception as e:
                flash(f"some error occurred {e}", 'danger')
        else:
            flash(f"No resume found, please upload resume/cv", 'danger')

    return render_template('recommend.html', title='home', job=job, keywords=keywords, resumes=resumes)


@app.route('/results')
@login_required
def result_ai():
    if 'rePercent' in session:
        rp = session.get('rePercent')
        msg = session.get('msg')
        sp = session.get('skillPercent', 'N/A')
        jid = session.get('jobid')
        rid = session.get('resumeid')
        resume = MyUpload.query.get(rid)
        job = JobDescription.query.get(jid)
        output = {
            'rp': rp, 'msg': msg, 'sp': sp, 'resume': resume, 'job': job
        }
        return render_template('results.html', title='result', output=output)
    else:
        flash("select a job for recommender", 'warning')
    return redirect('index')