from flask import Flask, render_template, request, redirect, session, jsonify
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username


class Book(db.Model):
    __tablename__ = "books"
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.Integer)
    title = db.Column(db.String(80))
    author = db.Column(db.String(120))
    year = db.Column(db.Integer)

    def __repr__(self):
        return '<User %r>' % self.username


class Review(db.Model):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True)
    rate = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                          nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'),
                        nullable=False)
    book = db.relationship('Book',
                           backref=db.backref('books', lazy=True))
    user = db.relationship('User',
                               backref=db.backref('users', lazy=True))
    def __repr__(self):
        return '<User %r>' % self.comment


@app.route("/", methods=['GET', 'POST'])
def index():
    if 'username' in session:
        return redirect('/books')

    if request.method == 'GET':
        return render_template("index.html")
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username, password=password).first()
    if user:
        session['username'] = user.username
        session['user_id'] = user.id
        return redirect("/books")
    else:
        return render_template("index.html", error=True)


@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    name = request.form['name']
    password = request.form['password']
    if not username or not name or not password:
        return render_template("register.html", error=True)
    user = User(name=name, username=username, password=password)
    db.session.add(user)
    db.session.commit()
    return redirect('/')


@app.route('/register-page')
def registerpage():
    return render_template("register.html")


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect("/")

@app.route('/books', methods=['GET', 'POST'])
def books():
    if request.method == 'GET':
        return render_template("books.html", username=session['username'])
    else:
        BookName = request.form['name']
        search = "%{}%".format(BookName)
        books = Book.query.filter(Book.title.like(search)).all()
        size = len(books)
        return render_template('books.html', data=books, isData=True, size=size, username=session['username'])

@app.route('/book/<id>')
def book(id):
    if 'username' not in session:
        return redirect('/')
    book = Book.query.get(id)
    reviews = Review.query.filter_by(book_id=id).all()
    size = len(reviews)
    return render_template("book.html", book=book,
                           username=session['username'], reviews=reviews, size=size)


@app.route('/review/<book_id>', methods=['POST'])
def review(book_id):
    url = "/book/" + book_id
    if not request.form['rate'] or not request.form['comment']:
        return redirect(url)
    r = Review(rate=request.form['rate'], comment=request.form['comment'], user_id=session['user_id'], book_id=book_id)
    db.session.add(r)
    db.session.commit()
    return redirect(url)

@app.route('/api/<isbn>', methods=['get'])
def api(isbn):
    book = Book.query.filter_by(isbn=isbn).first()
    book_id = book.id
    reviews_count = Review.query.filter_by(book_id=book_id).count()
    api = jsonify({
        "title": book.title,
        "author": book.author,
        "year": book.year,
        "isbn": book.isbn,
        "review_count": reviews_count,
        "average_score": random.randint(0,5)
    })
    return api