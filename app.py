from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///church_website.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'epub', 'txt'}

db = SQLAlchemy(app)

# Model for storing books
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    filename = db.Column(db.String(200), nullable=False)

# Model for storing questions
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String(300), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    book = db.relationship('Book', backref=db.backref('questions', lazy=True))

# Ensure the database is created
with app.app_context():
    db.create_all()

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Home page to display the list of books
@app.route('/')
def index():
    books = Book.query.all()
    return render_template('index.html', books=books)

# Upload book page (Admin only)
@app.route('/upload', methods=['GET', 'POST'])
def upload_book():
    if request.method == 'POST':
        title = request.form['title']
        file = request.files['file']

        if file and allowed_file(file.filename):
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)

            new_book = Book(title=title, filename=filename)
            db.session.add(new_book)
            db.session.commit()

            return redirect(url_for('index'))

    return render_template('upload_book.html')

# View a book and add questions
@app.route('/book/<int:book_id>', methods=['GET', 'POST'])
def book_page(book_id):
    book = Book.query.get_or_404(book_id)
    if request.method == 'POST':
        question_text = request.form['question']
        new_question = Question(question_text=question_text, book_id=book.id)
        db.session.add(new_question)
        db.session.commit()
    
    questions = Question.query.filter_by(book_id=book.id).all()
    return render_template('book_page.html', book=book, questions=questions)

if __name__ == '__main__':
    app.run(debug=True)
