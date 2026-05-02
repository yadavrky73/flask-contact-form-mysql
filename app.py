from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-this-in-production'  # Required for flash messages

# ✅ MySQL connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:system@127.0.0.1:3306/trek_nirvana_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['TEMPLATES_AUTO_RELOAD'] = True  # Helps with template debugging


db = SQLAlchemy(app)

# Model
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.BigInteger, primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255))
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"{self.first_name}-{self.email}"


# --- REGISTRATION ROUTE ---
@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Basic validation
        if not first_name or not email or not password:
            flash('First name, email, and password are required!', 'error')
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('register'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return redirect(url_for('register'))
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('An account with this email already exists. Please log in.', 'error')
            return redirect(url_for('register'))
        
        # Hash the password for security
        hashed_password = generate_password_hash(password)
        
        # Create new user
        new_user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=hashed_password
        )
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash(f'Account created successfully! Welcome, {first_name}!', 'success')
            return redirect(url_for('home'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'error')
            print(f"Error: {e}")
            return redirect(url_for('register'))
    
    # For GET request, show the registration form
    return render_template('register.html')


# --- FIXED HOME ROUTE (no more automatic user creation!) ---
@app.route("/")
def home():
    # ✅ Removed the buggy user creation code
    # Just render the homepage template
    return render_template('index.html')


@app.route("/products")
def products():
    return "Hare Krishna, All Glories to Sri Guru and Gauranga"


@app.route("/users")
def get_users():
    users = User.query.all()
    return "<br>".join([f"{u.id} - {u.first_name} {u.last_name or ''} - {u.email}" for u in users])


# --- TEST ROUTE (only for development, remove in production) ---
@app.route("/add-test-user")
def add_test_user():
    """Only use this for testing - creates a user with proper password"""
    test_user = User(
        first_name="Test",
        last_name="User",
        email="test@example.com",
        password=generate_password_hash("password123")  # ✅ Password is provided and hashed
    )
    try:
        db.session.add(test_user)
        db.session.commit()
        return "Test user added successfully!"
    except Exception as e:
        db.session.rollback()
        return f"Error: {e}"


# Run + create DB
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=8001)