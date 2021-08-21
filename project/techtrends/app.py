import logging, sys
from os import strerror
from re import DEBUG
import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
from werkzeug.wrappers import response

db_connection_count = 0
# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global db_connection_count
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    db_connection_count += 1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    title = post[2]
    logger = logging.getLogger('app')
    logger.info(f'Article "{title}" retrieved!')
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        logger = logging.getLogger('app')
        logger.info('A non-existing article is accessed and a 404 page is returned')
        return render_template('404.html'), 404
    else:
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    logger = logging.getLogger('app')
    logger.info('The "About Us" page is retrieved!')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            logger = logging.getLogger('app')
            logger.info(f'New article "{title}" has been created!')

            return redirect(url_for('index'))

    return render_template('create.html')

# Define the healthcheck endpoint
@app.route('/healthz')
def health_check(): 
    response = app.response_class(
        response=json.dumps({"result":"OK - healthy"}),
        status=200,
        mimetype='application/json'
    )
    return response

# Define the metrics endpoint
@app.route('/metrics')
def app_metrics():
    connection = get_db_connection()
    post_count = len(connection.execute('SELECT * FROM posts').fetchall())
    connection.close()
    response = app.response_class(
        response=json.dumps({"db_connection_count": db_connection_count, "post_count": post_count}),
        status=200,
        mimetype='application/json'
    )
    return response

def init_logger():
    logger = logging.getLogger('app')
    logger.setLevel(logging.DEBUG)
    stdout_h = logging.StreamHandler(sys.stdout)
    stdout_h.setLevel(logging.DEBUG)
    stderr_h = logging.StreamHandler(sys.stderr)
    stderr_h.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s:%(name)s:%(asctime)s, %(message)s', datefmt='%d/%m/%y, %H:%M:%S')
    stdout_h.setFormatter(formatter)
    stderr_h.setFormatter(formatter)
    logger.addHandler(stdout_h)
    logger.addHandler(stderr_h)
    logging.basicConfig(level=logging.DEBUG) # Capture Python logs at DEBUG level

# start the application on port 3111
if __name__ == "__main__":        
    init_logger()
    app.run(host='0.0.0.0', port='3111')
