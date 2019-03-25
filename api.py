import flask
from flask import request, jsonify
import sqlite3

app = flask.Flask(__name__)
app.config["DEBUG"] = True


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


@app.route('/', methods=['GET'])
def home():
    return '''<h1>Distant Reading Archive</h1>
<p>A prototype API for distant reading of science fiction novels.</p>'''


@app.route('/api/v1/resources/books/all', methods=['GET'])
def api_all():
    conn = sqlite3.connect('books.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    all_books = cur.execute('SELECT * FROM books;').fetchall()
    conn.close()
    return jsonify(all_books)


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>"


@app.route('/api/v1/resources/books', methods=['GET', 'POST'])
def handle_request():
    if request.method == 'GET':
        return do_get()
    if request.method == 'POST':
        return do_post()


def do_get():
    query_parameters = request.args

    id = query_parameters.get('id')
    published = query_parameters.get('published')
    author = query_parameters.get('author')

    query = "SELECT * FROM books WHERE"
    to_filter = []

    if id:
        query += ' id=? AND'
        to_filter.append(id)
    if published:
        query += ' published=? AND'
        to_filter.append(published)
    if author:
        query += ' author=? AND'
        to_filter.append(author)
    if not (id or published or author):
        return page_not_found(404)

    query = query[:-4] + ';'

    conn = sqlite3.connect('books.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()

    results = cur.execute(query, to_filter).fetchall()
    conn.close()
    return jsonify(results)


def do_post():
    results = request.get_json()
    author_value = results.get('author')
    published_value = results.get('published')
    title_value = results.get('title')

    # Connecting to the database file
    conn = sqlite3.connect("books.db")
    cur = conn.cursor()

    insert_statement = "INSERT INTO books (published, author, title, first_sentence) " \
                       "VALUES ('{pv}', '{av}', '{tv}', 'first')".format(pv=published_value,
                                                                         av=author_value, tv=title_value)
    try:
        cur.execute(insert_statement)
    except sqlite3.IntegrityError:
        print('ERROR: insert failed')

    conn.commit()
    conn.close()
    return jsonify(results)


app.run()
