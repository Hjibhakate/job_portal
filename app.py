import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from werkzeug.utils import secure_filename
from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a real secret key!

# MongoDB setup
MONGO_URI = 'mongodb://localhost:27017'  # Change if needed
client = MongoClient(MONGO_URI)
db = client['jobportal']
users_collection = db['users']
jobs_collection = db['jobs']  # <-- New jobs collection

# Upload config
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    role = request.form.get('role')
    name = request.form.get('name')
    email = request.form.get('email').lower()
    password = request.form.get('password')

    if not all([role, name, email, password]):
        flash("All fields are required!", 'error')
        return redirect(url_for('index'))

    if users_collection.find_one({'email': email}):
        flash("User already exists!", 'error')
        return redirect(url_for('index'))

    hashed_password = generate_password_hash(password)

    user_doc = {
        'role': role,
        'name': name,
        'email': email,
        'password': hashed_password,
        'profile': {}
    }
    users_collection.insert_one(user_doc)
    flash("Registration successful! Please log in.", 'success')
    return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email').lower()
    password = request.form.get('password')

    user = users_collection.find_one({'email': email})
    if user and check_password_hash(user['password'], password):
        session['user'] = {
            'id': str(user['_id']),
            'email': user['email'],
            'name': user['name'],
            'role': user['role']
        }
        flash(f"Welcome, {user['name']}!", 'success')
        return redirect(url_for('index'))
    else:
        flash("Invalid email or password!", 'error')
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("You have been logged out.", 'success')
    return redirect(url_for('index'))

@app.route('/jobseeker_profile', methods=['POST'])
def jobseeker_profile():
    if 'user' not in session or session['user']['role'] != 'jobseeker':
        flash("Unauthorized access.", 'error')
        return redirect(url_for('index'))

    resume = request.files.get('resume')
    skills = request.form.get('skills')
    experience = request.form.get('experience')
    education = request.form.get('education')

    if not all([resume, skills, experience, education]):
        flash("Please fill all profile fields.", 'error')
        return redirect(url_for('index'))

    if resume and allowed_file(resume.filename):
        filename = secure_filename(resume.filename)
        resume_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        resume.save(resume_path)
    else:
        flash("Invalid resume file.", 'error')
        return redirect(url_for('index'))

    users_collection.update_one(
        {'_id': ObjectId(session['user']['id'])},
        {'$set': {
            'profile.resume': filename,
            'profile.skills': skills,
            'profile.experience': experience,
            'profile.education': education
        }}
    )
    flash("Profile updated successfully!", 'success')
    return redirect(url_for('index'))

@app.route('/employer_profile', methods=['POST'])
def employer_profile():
    if 'user' not in session or session['user']['role'] != 'employer':
        flash("Unauthorized access.", 'error')
        return redirect(url_for('index'))

    company_name = request.form.get('company_name')
    company_description = request.form.get('company_description')
    company_logo = request.files.get('company_logo')

    if not all([company_name, company_description]):
        flash("Please fill all company profile fields.", 'error')
        return redirect(url_for('index'))

    logo_filename = None
    if company_logo and company_logo.filename != '':
        if allowed_file(company_logo.filename):
            logo_filename = secure_filename(company_logo.filename)
            logo_path = os.path.join(app.config['UPLOAD_FOLDER'], logo_filename)
            company_logo.save(logo_path)
        else:
            flash("Invalid company logo file.", 'error')
            return redirect(url_for('index'))

    update_data = {
        'profile.company_name': company_name,
        'profile.company_description': company_description,
    }
    if logo_filename:
        update_data['profile.company_logo'] = logo_filename

    users_collection.update_one(
        {'_id': ObjectId(session['user']['id'])},
        {'$set': update_data}
    )
    flash("Company profile updated successfully!", 'success')
    return redirect(url_for('index'))


@app.route('/post_job', methods=['POST'])
def post_job():
    # Only logged in employers can post jobs
    if 'user' not in session or session['user']['role'] != 'employer':
        flash("Unauthorized access.", 'error')
        return redirect(url_for('index'))
    
    job_title = request.form.get('job_title')
    job_description = request.form.get('job_description')
    location = request.form.get('location')
    salary = request.form.get('salary')
    deadline = request.form.get('deadline')

    # Basic validation
    if not all([job_title, job_description, location, deadline]):
        flash("Please fill all required job fields.", 'error')
        return redirect(url_for('index'))

    job_doc = {
        'employer_id': ObjectId(session['user']['id']),
        'job_title': job_title,
        'job_description': job_description,
        'location': location,
        'salary': salary,
        'deadline': deadline,
        'posted_at':  datetime.utcnow()
    }

    jobs_collection.insert_one(job_doc)
    flash("Job posted successfully!", 'success')
    return redirect(url_for('index'))


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
