from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-this-in-production'

# ✅ MySQL connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:system@127.0.0.1:3306/trek_nirvana_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['TEMPLATES_AUTO_RELOAD'] = True

db = SQLAlchemy(app)

# ✅ ADD THIS CONTEXT PROCESSOR - Makes datetime available to all templates
@app.context_processor
def inject_now():
    return {'datetime': datetime}

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
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not first_name or not email or not password:
            flash('First name, email, and password are required!', 'error')
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('register'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return redirect(url_for('register'))
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('An account with this email already exists. Please log in.', 'error')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password)
        
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
    
    return render_template('register.html')


# --- HOME ROUTE ---
@app.route("/")
def home():
    return render_template('index.html')


@app.route("/products")
def products():
    return render_template('products.html')


# --- USER PROFILE VIEW ROUTE ---
@app.route("/user/<int:user_id>")
def user_profile(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('user_profile.html', user=user)


# --- DELETE USER ROUTE ---
@app.route("/user/<int:user_id>/delete", methods=['POST'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    try:
        db.session.delete(user)
        db.session.commit()
        flash(f'User {user.first_name} {user.last_name or ""} has been deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the user.', 'error')
        print(f"Error: {e}")
    
    return redirect(url_for('users_list'))


# --- USERS LIST ROUTE ---
@app.route("/users-list")
def users_list():
    users = User.query.order_by(User.created_at.desc()).all()
    total_users = User.query.count()
    return render_template('users_list.html', users=users, total_users=total_users)


# --- OLD SIMPLE USERS ROUTE ---
@app.route("/users")
def get_users():
    users = User.query.all()
    return "<br>".join([f"{u.id} - {u.first_name} {u.last_name or ''} - {u.email}" for u in users])


# --- TEST ROUTE ---
@app.route("/add-test-user")
def add_test_user():
    test_user = User(
        first_name="Test",
        last_name="User",
        email="test@example.com",
        password=generate_password_hash("password123")
    )
    try:
        db.session.add(test_user)
        db.session.commit()
        return "Test user added successfully!"
    except Exception as e:
        db.session.rollback()
        return f"Error: {e}"


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=8001)