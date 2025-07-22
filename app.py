import os
from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask import abort # You might need to import abort if not already

# Initialize Flask app
app = Flask(__name__)

# --- Database Configuration ---
# Get the database URL from Replit Secrets
DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    # This will immediately stop the app if the secret isn't found
    raise RuntimeError("DATABASE_URL not found in environment variables. Please set it in Replit Secrets.")

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # To suppress a warning and save memory/CPU

# Initialize SQLAlchemy with the Flask app
db = SQLAlchemy(app)

# --- Define your Database Model ---
# This matches your 'jobs' table structure
class Job(db.Model):
    __tablename__ = 'jobs' # Explicitly define table name
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    salary = db.Column(db.Integer)
    currency = db.Column(db.String(10))
    responsibilities = db.Column(db.String(2000))
    requirements = db.Column(db.String(2000))

    def __repr__(self):
        # A helpful representation for debugging
        return f"<Job {self.id}: {self.title}>"

    def to_dict(self):
        # Converts a Job object to a dictionary, useful for JSON or template rendering
        return {
            'id': self.id,
            'title': self.title,
            'location': self.location,
            'salary': self.salary,
            'currency': self.currency,
            'responsibilities': self.responsibilities,
            'requirements': self.requirements
        }

# --- Flask Routes ---
@app.route('/')
def home():
    jobs_data = [] # Initialize as empty list in case of DB connection issues
    try:
        # Fetch all jobs from the database using SQLAlchemy ORM
        jobs = Job.query.all()
        # Convert list of Job objects to list of dictionaries for rendering
        print(f"DEBUG: Fetched jobs (SQLAlchemy objects): {jobs}")
        jobs_data = [job.to_dict() for job in jobs]
        print(f"DEBUG: Jobs data for template (dictionaries): {jobs_data}")
    except Exception as e:
        # Print error to Replit console for debugging
        print(f"Error fetching jobs from database: {e}")
        # You might want to show a user-friendly error on the page as well
        # For now, it will just show an empty list of jobs

    return render_template('home.html', jobs=jobs_data)

@app.route('/api/jobs')
def list_jobs_api():
    jobs_data = []
    try:
        jobs = Job.query.all()
        jobs_data = [job.to_dict() for job in jobs]
    except Exception as e:
        print(f"Error fetching jobs for API: {e}")
        return jsonify({"error": "Failed to retrieve job data"}), 500 # Return an error for API
    return jsonify(jobs_data)
    


@app.route('/job/<id>')
def job_detail(id):
    # Fetch the job from the database using its ID
    # db.session.get() directly fetches by primary key
    job = db.session.get(Job, id)

    # Now, explicitly check if the job was found, and if not, abort with a 404
    if job is None:
        abort(404) # This will raise an HTTP 404 Not Found error

    return render_template('job.html', job=job.to_dict())


# --- Run the app ---
if __name__ == '__main__':
    # This block is for initial setup like creating tables if they don't exist.
    # Since you've already created and populated your 'jobs' table via TiDB Cloud console,
    # you typically don't need db.create_all() here unless your model changes
    # and you want to ensure the schema matches.
    # If you *do* use it, put it inside app.app_context()
    # with app.app_context():
    #     db.create_all()

    app.run(host='0.0.0.0', port=8080, debug=True) # Replit uses 0.0.0.0 and a specific port
