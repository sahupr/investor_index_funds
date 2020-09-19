from flask import Flask, render_template, url_for, g
from flask_sqlalchemy import SQLAlchemy 
import sqlite3

app = Flask(__name__)
app.config['SQLALCHMEY_DATABASE_URI'] = 'sqlite:///'
db = SQLAlchemy(app)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)