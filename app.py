import sqlite3
import string
import random
import io
from flask import Flask, render_template, request, redirect, url_for, send_file, abort
from datetime import datetime, timedelta, timezone
app = Flask(__name__)
DB_FILE = "urls.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            short_code TEXT UNIQUE,
            original_url TEXT
        )
    ''')
    try:
        c.execute('ALTER TABLE urls ADD COLUMN name TEXT')
    except sqlite3.OperationalError:
        pass
    try:
        c.execute('ALTER TABLE urls ADD COLUMN is_favorite INTEGER DEFAULT 0')
    except sqlite3.OperationalError:
        pass
    try:
        c.execute('ALTER TABLE urls ADD COLUMN is_saved INTEGER DEFAULT 1')
    except sqlite3.OperationalError:
        pass
    try:
        c.execute('ALTER TABLE urls ADD COLUMN expires_at TEXT')
    except sqlite3.OperationalError:
        pass
    try:
        c.execute('ALTER TABLE urls ADD COLUMN clicks INTEGER DEFAULT 0')
    except sqlite3.OperationalError:
        pass

    c.execute('''
        CREATE TABLE IF NOT EXISTS visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            short_code TEXT,
            clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            referrer TEXT,
            browser TEXT,
            platform TEXT
        )
    ''')
    conn.commit()
    conn.close()

def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/', methods=['GET', 'POST'])
def index():
    short_url = None
    short_code = None

    if request.method == 'POST':
        original_url = request.form['url']
        name = request.form.get('name', '')
        action = request.form.get('action', 'save')
        ttl_hours = request.form.get('ttl')

        expires_at = None
        if ttl_hours and ttl_hours.isdigit():
            expires_at = (datetime.now(timezone.utc) + timedelta(hours=int(ttl_hours))).isoformat()

        is_saved = 1 if action == 'save' else 0
        if not is_saved:
            name = ''

        conn = get_db_connection()
        c = conn.cursor()

        existing_url = c.execute('SELECT * FROM urls WHERE original_url = ?', (original_url,)).fetchone()

        if existing_url:
            short_code = existing_url['short_code']
            new_name = name if name else existing_url['name']
            new_expires = expires_at if expires_at else existing_url['expires_at']
            new_is_saved = 1 if is_saved else existing_url['is_saved']

            c.execute('UPDATE urls SET is_saved = ?, name = ?, expires_at = ? WHERE id = ?',
                      (new_is_saved, new_name, new_expires, existing_url['id']))
            conn.commit()
        else:
            while True:
                short_code = generate_short_code()
                try:
                    c.execute('INSERT INTO urls (short_code, original_url, name, is_saved, is_favorite, expires_at) VALUES (?, ?, ?, ?, 0, ?)', (short_code, original_url, name, is_saved, expires_at))
                    conn.commit()
                    break
                except sqlite3.IntegrityError:
                    continue

        conn.close()
        short_url = request.host_url + short_code

    conn = get_db_connection()
    saved_urls = conn.execute('SELECT * FROM urls WHERE is_saved = 1 ORDER BY is_favorite DESC, id DESC').fetchall()
    conn.close()

    return render_template('index.html', short_url=short_url, short_code=short_code, saved_urls=saved_urls, host_url=request.host_url)

@app.route('/delete/<int:id>', methods=['POST'])
def delete_link(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM urls WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/favorite/<int:id>', methods=['POST'])
def toggle_favorite(id):
    conn = get_db_connection()
    url_data = conn.execute('SELECT is_favorite FROM urls WHERE id = ?', (id,)).fetchone()
    if url_data:
        new_status = 0 if url_data['is_favorite'] else 1
        conn.execute('UPDATE urls SET is_favorite = ? WHERE id = ?', (new_status, id))
        conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/<short_code>')
def redirect_to_url(short_code):
    conn = get_db_connection()
    url_data = conn.execute('SELECT * FROM urls WHERE short_code = ?', (short_code,)).fetchone()

    if url_data:
        expires_at_str = url_data['expires_at']
        if expires_at_str:
            expires_at = datetime.fromisoformat(expires_at_str)
            if datetime.now(timezone.utc) > expires_at:
                conn.close()
                abort(410)

        referrer = request.referrer or 'Direct'
        browser = request.user_agent.browser or 'Unknown'
        platform = request.user_agent.platform or 'Unknown'

        conn.execute('UPDATE urls SET clicks = clicks + 1 WHERE short_code = ?', (short_code,))
        conn.execute('INSERT INTO visits (short_code, referrer, browser, platform) VALUES (?, ?, ?, ?)',
                     (short_code, referrer, browser, platform))
        conn.commit()
        conn.close()

        return redirect(url_data['original_url'])
    else:
        conn.close()
        abort(404)

@app.route('/qr/<short_code>')
def generate_qr(short_code):
    conn = get_db_connection()
    url_data = conn.execute('SELECT * FROM urls WHERE short_code = ?', (short_code,)).fetchone()
    conn.close()

    if url_data:
        expires_at_str = url_data['expires_at']
        if expires_at_str:
            expires_at = datetime.fromisoformat(expires_at_str)
            if datetime.now(timezone.utc) > expires_at:
                abort(410)

        import segno
        short_url = request.host_url + short_code

        qr = segno.make(short_url)

        img_io = io.BytesIO()
        qr.save(img_io, kind='svg', scale=10)
        img_io.seek(0)

        return send_file(img_io, mimetype='image/svg+xml')
    else:
        abort(404)

@app.route('/db_management')
def db_management():
    search = request.args.get('search', '')
    conn = get_db_connection()
    if search:
        query = f"%{search}%"
        urls = conn.execute('SELECT * FROM urls WHERE short_code LIKE ? OR original_url LIKE ? ORDER BY id DESC', (query, query)).fetchall()
    else:
        urls = conn.execute('SELECT * FROM urls ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('db_management.html', urls=urls, search=search, host_url=request.host_url)

@app.route('/analytics')
def analytics():
    conn = get_db_connection()

    total_clicks = conn.execute('SELECT SUM(clicks) as s FROM urls').fetchone()['s'] or 0
    total_links = conn.execute('SELECT COUNT(*) as c FROM urls').fetchone()['c'] or 0

    top_links = conn.execute('SELECT * FROM urls ORDER BY clicks DESC LIMIT 5').fetchall()
    top_link_clicks = top_links[0]['clicks'] if top_links else 0

    visits = conn.execute("SELECT date(clicked_at) as d, COUNT(*) as c FROM visits WHERE clicked_at >= date('now', '-7 days') GROUP BY d").fetchall()

    today = datetime.now().date()
    labels = []
    data_points = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        labels.append(day.strftime('%a'))

        count = next((v['c'] for v in visits if v['d'] == day.strftime('%Y-%m-%d')), 0)
        data_points.append(count)


    referrers = conn.execute("SELECT referrer, COUNT(*) as c FROM visits GROUP BY referrer ORDER BY c DESC LIMIT 5").fetchall()


    browsers = conn.execute("SELECT browser, COUNT(*) as c FROM visits GROUP BY browser ORDER BY c DESC LIMIT 4").fetchall()

    platforms = conn.execute("SELECT platform, COUNT(*) as c FROM visits GROUP BY platform ORDER BY c DESC LIMIT 3").fetchall()

    conn.close()

    return render_template('analytics.html',
        total_clicks=total_clicks,
        total_links=total_links,
        top_link_clicks=top_link_clicks,
        top_links=top_links,
        labels=labels,
        data_points=data_points,
        referrers=referrers,
        browsers=browsers,
        platforms=platforms,
        host_url=request.host_url
    )

if __name__ == '__main__':
    init_db()
    app.run(debug=True)

