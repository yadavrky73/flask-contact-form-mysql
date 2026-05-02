# flask-contact-form-mysql
# Setup
python -m venv env
source env/bin/activate  # or env\Scripts\activate on Windows
pip install flask flask-sqlalchemy pymysql werkzeug

# Database Setup (MySQL)
mysql -u root -p
CREATE DATABASE trek_nirvana_db;
EXIT;

# Run Application
python app.py

# Visit http://127.0.0.1:8001


## Additional File: **requirements.txt**

Create this file to make dependency installation easier:

```txt
Flask==2.3.3
Flask-SQLAlchemy==3.1.1
PyMySQL==1.1.0
Werkzeug==2.3.7