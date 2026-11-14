

# RelayGrid Flask App
import os
import sqlite3
import random
import io
import base64
import secrets
import string
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from captcha.image import ImageCaptcha
from dotenv import load_dotenv
from uuidgen import generate_recovery_uuid

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', '8a0ba8f0ebf595523890df6d3fcc4f2b')
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'profile_pics')
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB max
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
DB_PATH = 'users.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, timeout=10.0, check_same_thread=False)
    # 🚀 Optimize for speed
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA synchronous=NORMAL')  # Faster than FULL
    conn.execute('PRAGMA cache_size=10000')    # Larger cache
    conn.execute('PRAGMA temp_store=MEMORY')   # Store temp in memory
    return conn

def init_db():
	conn = get_db_connection()
	c = conn.cursor()
	c.execute('''CREATE TABLE IF NOT EXISTS users (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		username TEXT NOT NULL,
		email TEXT UNIQUE NOT NULL,
		password TEXT NOT NULL,
		recovery_email TEXT,
		profile_pic TEXT
	)''')
	c.execute('''CREATE TABLE IF NOT EXISTS emails (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		sender_email TEXT NOT NULL,
		receiver_email TEXT NOT NULL,
		subject TEXT NOT NULL,
		body TEXT NOT NULL,
		timestamp TEXT NOT NULL,
		is_read INTEGER DEFAULT 0
	)''')
	c.execute('''CREATE TABLE IF NOT EXISTS recovery_tokens (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		user_id INTEGER NOT NULL,
		token TEXT UNIQUE NOT NULL,
		created_at TEXT NOT NULL
	)''')
	conn.commit()

	# Create default admin and relaymailgrid accounts if not exist
	from dotenv import load_dotenv
	load_dotenv()
	admin_pw = os.environ.get('ADMIN_PASSWORD', 'abbb92c4acaded401ea0a9b5c4adeec9')
	relay_pw = os.environ.get('RELAYMAILGRID_PASSWORD', '3809ff76aed9d461795f93f343b8a1d3')
	admin_email = 'admin@relaymailgrid.com'
	relay_email = 'relaymailgrid@relaymailgrid.com'
	# Check and create admin
	c.execute('SELECT id FROM users WHERE email = ?', (admin_email,))
	if not c.fetchone():
		try:
			c.execute('INSERT INTO users (username, email, password, profile_pic, recovery_email) VALUES (?, ?, ?, ?, ?)',
					  ('admin', admin_email, generate_password_hash(admin_pw), 'relaymailgrid.png', None))
			conn.commit()
		except sqlite3.IntegrityError:
			pass
	# Check and create relaymailgrid
	c.execute('SELECT id FROM users WHERE email = ?', (relay_email,))
	if not c.fetchone():
		try:
			c.execute('INSERT INTO users (username, email, password, profile_pic, recovery_email) VALUES (?, ?, ?, ?, ?)',
					  ('Relay Mail Grid', relay_email, generate_password_hash(relay_pw), 'relaymailgrid.png', admin_email))
			conn.commit()
		except sqlite3.IntegrityError:
			pass

	# Insert hardcoded flag email from relaymailgrid to admin
	flag = os.environ.get('FLAG', 'FLAG_NOT_SET')
	body = f"Dear Players,\nCongratulations! You've managed to find the one thing we were supposed to keep secret:\n{flag}\nIf you're reading this, you're officially smarter than our security system.\nGame on,\nrelaymailgrid"
	# Check if flag email already exists
	c.execute('SELECT id FROM emails WHERE sender_email = ? AND receiver_email = ? AND subject = ?',
			  ('relaymailgrid@relaymailgrid.com', 'admin@relaymailgrid.com', 'Here you go!'))
	if not c.fetchone():
		c.execute('''INSERT INTO emails (sender_email, receiver_email, subject, body, timestamp, is_read)
				 VALUES (?, ?, ?, ?, ?, ?)''',
			  ('relaymailgrid@relaymailgrid.com', 'admin@relaymailgrid.com',
			   'Here you go!',
			   body,
			   datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 0))
	conn.commit()
	conn.close()


def send_welcome_email(user_email, username):
	welcome_messages = [
		f"Welcome aboard, {username}! We're thrilled to have you here. Just so you know, this email system is so secure, even we can't read your messages... or can we?",
		f"Hey {username}! Welcome to RelayGrid, where your emails travel faster than gossip in a small town. Buckle up and enjoy the ride!",
		f"Greetings, {username}! You've successfully joined RelayGrid. Congratulations on choosing the email service that's definitely not reading your messages.",
		f"Welcome {username}! Your inbox is now officially open for business. We promise to deliver your emails with minimal snooping... just kidding!"
	]
	message = random.choice(welcome_messages)
	
	conn = get_db_connection()
	c = conn.cursor()
	c.execute('''INSERT INTO emails (sender_email, receiver_email, subject, body, timestamp, is_read)
				 VALUES (?, ?, ?, ?, ?, ?)''',
			  ('relaymailgrid@relaymailgrid.com', user_email, 
			   'Welcome to RelayGrid!', message, 
			   datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 0))
	conn.commit()
	conn.close()

init_db()

# Cleanup expired recovery tokens (older than 30 min)
def cleanup_recovery_tokens():
	conn = get_db_connection()
	c = conn.cursor()
	expire_time = (datetime.now() - timedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S')
	c.execute('DELETE FROM recovery_tokens WHERE created_at < ?', (expire_time,))
	conn.commit()
	conn.close()


# Generate CAPTCHA
def generate_captcha_text(length=6):
	chars = ''.join([c for c in (string.ascii_uppercase + string.digits) if c not in ['O', '0', 'I', '1']])
	return ''.join(secrets.choice(chars) for _ in range(length))

@app.route('/captcha')
def get_captcha():
		captcha_text = generate_captcha_text()
		captcha_token = secrets.token_urlsafe(32)
		try:
			image = ImageCaptcha(width=280, height=90, fonts=[
				'/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
				'/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'
			])
		except:
			image = ImageCaptcha(width=280, height=90)
		data = image.generate(captcha_text)
		img_bytes = data.getvalue()
		img_base64 = base64.b64encode(img_bytes).decode('utf-8')
		session[f'captcha_{captcha_token}'] = {
			'text': captcha_text,
			'timestamp': datetime.now().timestamp(),
			'attempts': 0
		}
		return jsonify({
			'captcha': f'data:image/png;base64,{img_base64}',
			'token': captcha_token
		})
# Verify with token and expiration
def verify_captcha(token, user_input):
	captcha_key = f'captcha_{token}'
	if captcha_key not in session:
		return False
	captcha_data = session[captcha_key]
	# Check expiration (5 minutes)
	if datetime.now().timestamp() - captcha_data['timestamp'] > 300:
		session.pop(captcha_key, None)
		return False
	# Check attempts
	if captcha_data['attempts'] >= 3:
		session.pop(captcha_key, None)
		return False
	# Verify
	if user_input.upper() != captcha_data['text'].upper():
		captcha_data['attempts'] += 1
		session[captcha_key] = captcha_data
		return False
	session.pop(captcha_key, None)
	return True


# Home page route
@app.route('/')
def home():
	username = session.get('username')
	return render_template('index.html', username=username)

# Password Recovery Route
@app.route('/recovery', methods=['GET', 'POST'])
def recovery():
	if request.method == 'POST':
		from uuidgen import generate_recovery_uuid
		token = str(generate_recovery_uuid())
		email_local = request.form.get('email', '').strip().lower()
		captcha_input = request.form.get('captcha', '').strip()
		captcha_token = request.form.get('captcha_token', '').strip()
		
		if not email_local:
			flash('Please enter your email address.', 'danger')
			return render_template('recovery.html')
		
		if not captcha_input or not captcha_token:
			flash('Please complete the CAPTCHA.', 'danger')
			return render_template('recovery.html')
		
		if not verify_captcha(captcha_token, captcha_input):
			flash('Invalid or expired CAPTCHA. Please try again.', 'danger')
			return render_template('recovery.html')
		
		email = f'{email_local}@relaymailgrid.com'
		# Generic response, never reveal existence
		try:
			cleanup_recovery_tokens()
			conn = get_db_connection()
			c = conn.cursor()
			c.execute('SELECT id, username, recovery_email FROM users WHERE email = ?', (email,))
			user = c.fetchone()
			if user and user[2]:
				c.execute('INSERT INTO recovery_tokens (user_id, token, created_at) VALUES (?, ?, ?)', (user[0], token, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
				conn.commit()
				recovery_link = url_for('recovery_form', token=token, _external=True)
				message = f"Hey {user[1]},\n\nLooks like the account {email} is trying to recover its password, and you are the chosen one!\nClick the link below to help {email} get back in business:\n\n{recovery_link}\n\nIf you didn't request this, just ignore it. Your password is probably just bored.\n\nStay secure,\nRelayGrid Team"
				# Send email (store in emails table)
				c.execute('''INSERT INTO emails (sender_email, receiver_email, subject, body, timestamp, is_read) VALUES (?, ?, ?, ?, ?, ?)''',
						  ('relaymailgrid@relaymailgrid.com', user[2], 'RelayGrid Password Recovery', message, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 0))
				conn.commit()
			conn.close()
		except Exception:
			pass
		flash('If your account exists and has a recovery email, a recovery link has been sent! If it doesn\'t arrive, check your spam folder or your fridge.', 'success')
		return redirect(url_for('login'))
	return render_template('recovery.html')

# Password Reset Form Route
@app.route('/recoveryForm', methods=['GET', 'POST'])
def recovery_form():
	token = request.args.get('token', '').strip()
	if request.method == 'POST':
		new_password = request.form.get('new_password', '')
		confirm_password = request.form.get('confirm_password', '')
		captcha_input = request.form.get('captcha', '').strip()
		captcha_token = request.form.get('captcha_token', '').strip()
		
		if not new_password or not confirm_password:
			flash('Please fill in all fields.', 'danger')
			return render_template('recoveryForm.html')
		
		if not captcha_input or not captcha_token:
			flash('Please complete the CAPTCHA.', 'danger')
			return render_template('recoveryForm.html')
		
		if not verify_captcha(captcha_token, captcha_input):
			flash('Invalid or expired CAPTCHA. Please try again.', 'danger')
			return render_template('recoveryForm.html')
		
		if new_password != confirm_password:
			flash('Passwords do not match. Try again!', 'danger')
			return render_template('recoveryForm.html')
		if len(new_password) < 6:
			flash('Password must be at least 6 characters long.', 'danger')
			return render_template('recoveryForm.html')
		# Validate token
		conn = get_db_connection()
		c = conn.cursor()
		c.execute('CREATE TABLE IF NOT EXISTS recovery_tokens (user_id INTEGER, token TEXT, created_at TEXT)')
		c.execute('SELECT user_id, created_at FROM recovery_tokens WHERE token = ?', (token,))
		token_row = c.fetchone()
		if not token_row:
			conn.close()
			flash('Invalid or expired recovery link. Please try again.', 'danger')
			return render_template('recoveryForm.html')
		# Check expiration (30 min)
		created_at = datetime.strptime(token_row[1], '%Y-%m-%d %H:%M:%S')
		if (datetime.now() - created_at).total_seconds() > 1800:
			c.execute('DELETE FROM recovery_tokens WHERE token = ?', (token,))
			conn.commit()
			conn.close()
			flash('Recovery link expired. Please request a new one.', 'danger')
			return render_template('recoveryForm.html')
		user_id = token_row[0]
		# Update password
		hashed_pw = generate_password_hash(new_password)
		c.execute('UPDATE users SET password = ? WHERE id = ?', (hashed_pw, user_id))
		# Invalidate token
		c.execute('DELETE FROM recovery_tokens WHERE token = ?', (token,))
		conn.commit()
		conn.close()
		flash('If your account exists, your password has been updated! You may now log in with your new password.', 'success')
		return redirect(url_for('login'))
	return render_template('recoveryForm.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
	if 'user_id' in session:
		return redirect(url_for('dashboard'))
	
	if request.method == 'POST':
		email_local = request.form.get('email', '').strip().lower()
		password = request.form.get('password', '')
		captcha_input = request.form.get('captcha', '').strip()
		captcha_token = request.form.get('captcha_token', '').strip()
		if not email_local or not password or not captcha_input or not captcha_token:
			flash('Please fill in all fields including the CAPTCHA.', 'danger')
			return render_template('login.html')
		if not verify_captcha(captcha_token, captcha_input):
			flash('Invalid or expired CAPTCHA. Please try again.', 'danger')
			return render_template('login.html')
		email = f'{email_local}@relaymailgrid.com'
		conn = get_db_connection()
		c = conn.cursor()
		c.execute('SELECT id, username, password FROM users WHERE email = ?', (email,))
		user = c.fetchone()
		conn.close()
		if user and check_password_hash(user[2], password):
			session['user_id'] = user[0]
			session['username'] = user[1]
			flash(f'Welcome back, {user[1]}!', 'success')
			return redirect(url_for('dashboard'))
		else:
			flash('Invalid credentials. Did you forget your password or your sense of humor?', 'danger')
	return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
	if request.method == 'POST':
		username = request.form.get('username', '').strip()
		email_local = request.form.get('email', '').strip().lower()
		password = request.form.get('password', '')
		captcha_input = request.form.get('captcha', '').strip()
		captcha_token = request.form.get('captcha_token', '').strip()
		if not username or not email_local or not password or not captcha_input or not captcha_token:
			flash('Please fill in all fields including the CAPTCHA.', 'danger')
			return render_template('signup.html')
		if not verify_captcha(captcha_token, captcha_input):
			flash('Invalid or expired CAPTCHA. Please try again.', 'danger')
			return render_template('signup.html')
		if len(password) < 6:
			flash('Password must be at least 6 characters long.', 'danger')
			return render_template('signup.html')
		email = f'{email_local}@relaymailgrid.com'
		if not all(c.isalnum() or c in '._-' for c in email_local):
			flash('Email can only contain letters, numbers, dots, hyphens, and underscores.', 'danger')
			return render_template('signup.html')
		hashed_pw = generate_password_hash(password)
		try:
			conn = get_db_connection()
			c = conn.cursor()
			c.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
					  (username, email, hashed_pw))
			conn.commit()
			conn.close()
			send_welcome_email(email, username)
			flash('Signup successful! You can now log in.', 'success')
			return redirect(url_for('login'))
		except sqlite3.IntegrityError:
			flash('Email already exists. Try a different one!', 'danger')
	return render_template('signup.html')

@app.route('/faq')
def faq():
	username = session.get('username')
	return render_template('faq.html', username=username)

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_profile_pic', methods=['POST'])
def upload_profile_pic():
	if 'user_id' not in session:
		return jsonify({'error': 'Unauthorized'}), 401
	if 'profile_pic' not in request.files:
		return jsonify({'error': 'No file part'}), 400
	file = request.files['profile_pic']
	if file.filename == '':
		return jsonify({'error': 'No selected file'}), 400
	if file and allowed_file(file.filename):
		conn = get_db_connection()
		c = conn.cursor()
		# Get previous profile pic
		c.execute('SELECT profile_pic FROM users WHERE id = ?', (session['user_id'],))
		prev_pic = c.fetchone()
		prev_pic = prev_pic[0] if prev_pic and prev_pic[0] else None
		filename = secure_filename(f"{session['user_id']}_{file.filename}")
		filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
		file.save(filepath)
		# Remove previous pic if not default or admin.svg
		if prev_pic and prev_pic not in ['default.svg', 'admin.svg', 'relaymailgrid.png']:
			try:
				old_path = os.path.join(app.config['UPLOAD_FOLDER'], prev_pic)
				if os.path.exists(old_path):
					os.remove(old_path)
			except Exception:
				pass
		c.execute('UPDATE users SET profile_pic = ? WHERE id = ?', (filename, session['user_id']))
		conn.commit()
		conn.close()
		return jsonify({'success': True, 'filename': filename})
	return jsonify({'error': 'Invalid file type'}), 400

@app.route('/dashboard')
def dashboard():
	if 'user_id' not in session:
		flash('Please log in to access the dashboard.', 'warning')
		return redirect(url_for('login'))
	user_email = session.get('email')
	conn = get_db_connection()
	c = conn.cursor()
	c.execute('SELECT email, profile_pic FROM users WHERE id = ?', (session['user_id'],))
	result = c.fetchone()
	if result:
		user_email = result[0]
		session['email'] = user_email
		profile_pic = result[1] if result[1] else 'default.svg'
	else:
		profile_pic = 'default.svg'
	c.execute('''SELECT id, sender_email, subject, timestamp, is_read 
				 FROM emails 
				 WHERE receiver_email = ? 
				 ORDER BY timestamp DESC''', (user_email,))
	emails = c.fetchall()
	conn.close()
	return render_template('dashboard.html', 
						   username=session.get('username'),
						   emails=emails,
						   user_email=user_email,
						   profile_pic=profile_pic)

@app.route('/email/<int:email_id>')
def view_email(email_id):
	if 'user_id' not in session:
		return jsonify({'error': 'Unauthorized'}), 401
	user_email = session.get('email')
	conn = get_db_connection()
	c = conn.cursor()
	c.execute('''SELECT id, sender_email, receiver_email, subject, body, timestamp, is_read
				 FROM emails 
				 WHERE id = ? AND (receiver_email = ? OR sender_email = ?)''', (email_id, user_email, user_email))
	email = c.fetchone()
	sender_pic = None
	receiver_pic = None
	if email:
		# Get sender profile pic
		c.execute('SELECT profile_pic FROM users WHERE email = ?', (email[1],))
		sender_pic = c.fetchone()
		sender_pic = sender_pic[0] if sender_pic and sender_pic[0] else 'default.svg'
		# Get receiver profile pic
		c.execute('SELECT profile_pic FROM users WHERE email = ?', (email[2],))
		receiver_pic = c.fetchone()
		receiver_pic = receiver_pic[0] if receiver_pic and receiver_pic[0] else 'default.svg'
		if email[2] == user_email:
			c.execute('UPDATE emails SET is_read = 1 WHERE id = ?', (email_id,))
		conn.commit()
		conn.close()
		return jsonify({
			'id': email[0],
			'sender': email[1],
			'receiver': email[2],
			'subject': email[3],
			'body': email[4],
			'timestamp': email[5],
			'is_read': email[6],
			'sender_pic': sender_pic,
			'receiver_pic': receiver_pic
		})
	conn.close()
	return jsonify({'error': 'Email not found'}), 404

@app.route('/send_email', methods=['POST'])
def send_email():
	if 'user_id' not in session:
		return jsonify({'error': 'Unauthorized'}), 401
	data = request.get_json()
	receiver = data.get('receiver', '').strip()
	subject = data.get('subject', '').strip()
	body = data.get('body', '').strip()
	# Length limits
	if not receiver or not subject or not body:
		return jsonify({'error': 'All fields are required'}), 400
	if len(subject) > 120:
		return jsonify({'error': 'Subject too long (max 120 chars)'}), 400
	if len(body) > 2000:
		return jsonify({'error': 'Body too long (max 2000 chars)'}), 400
	if not receiver.endswith('@relaymailgrid.com'):
		receiver = f'{receiver}@relaymailgrid.com'
	sender_email = session.get('email')
	conn = get_db_connection()
	c = conn.cursor()
	c.execute('SELECT id FROM users WHERE email = ?', (receiver,))
	if not c.fetchone():
		conn.close()
		# Do not reveal existence, just return success
		return jsonify({'success': True, 'message': 'Email sent successfully'})
	c.execute('''INSERT INTO emails (sender_email, receiver_email, subject, body, timestamp, is_read)
				 VALUES (?, ?, ?, ?, ?, ?)''',
			  (sender_email, receiver, subject, body, 
			   datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 0))
	conn.commit()
	conn.close()
	return jsonify({'success': True, 'message': 'Email sent successfully'})

@app.route('/delete_email/<int:email_id>', methods=['POST'])
def delete_email(email_id):
	if 'user_id' not in session:
		return jsonify({'error': 'Unauthorized'}), 401
	
	user_email = session.get('email')
	conn = get_db_connection()
	c = conn.cursor()
	
	c.execute('DELETE FROM emails WHERE id = ? AND receiver_email = ?', (email_id, user_email))
	conn.commit()
	conn.close()
	
	return jsonify({'success': True, 'message': 'Email deleted successfully'})

@app.route('/sent_emails')
def sent_emails():
	if 'user_id' not in session:
		return jsonify({'error': 'Unauthorized'}), 401
	
	user_email = session.get('email')
	conn = get_db_connection()
	c = conn.cursor()
	
	c.execute('''SELECT id, receiver_email, subject, timestamp 
				 FROM emails 
				 WHERE sender_email = ? 
				 ORDER BY timestamp DESC''', (user_email,))
	emails = c.fetchall()
	conn.close()
	
	return jsonify([{
		'id': e[0],
		'receiver': e[1],
		'subject': e[2],
		'timestamp': e[3]
	} for e in emails])

@app.route('/logout')
def logout():
	session.clear()
	flash('You have been logged out. See you soon!', 'info')
	return redirect(url_for('login'))

@app.route('/settings')
def settings():
	if 'user_id' not in session:
		flash('Please log in to access settings.', 'warning')
		return redirect(url_for('login'))
	
	conn = get_db_connection()
	c = conn.cursor()
	c.execute('SELECT username, email, recovery_email FROM users WHERE id = ?', (session['user_id'],))
	user = c.fetchone()
	conn.close()
	
	if not user:
		return redirect(url_for('logout'))
	
	return render_template('settings.html', 
						   username=user[0],
						   email=user[1],
						   recovery_email=user[2] or '')

@app.route('/update_username', methods=['POST'])
def update_username():
	if 'user_id' not in session:
		return jsonify({'error': 'Unauthorized'}), 401
	
	data = request.get_json()
	new_username = data.get('username', '').strip()
	
	if not new_username:
		return jsonify({'error': 'Username cannot be empty'}), 400
	
	if len(new_username) < 3:
		return jsonify({'error': 'Username must be at least 3 characters long'}), 400
	
	try:
		conn = get_db_connection()
		c = conn.cursor()
		c.execute('UPDATE users SET username = ? WHERE id = ?', (new_username, session['user_id']))
		conn.commit()
		conn.close()
		
		session['username'] = new_username
		return jsonify({'success': True, 'message': 'Username updated successfully'})
	except sqlite3.IntegrityError:
		return jsonify({'error': 'Username already taken'}), 400

@app.route('/update_password', methods=['POST'])
def update_password():
	if 'user_id' not in session:
		return jsonify({'error': 'Unauthorized'}), 401
	
	data = request.get_json()
	current_password = data.get('current_password', '')
	new_password = data.get('new_password', '')
	
	if not current_password or not new_password:
		return jsonify({'error': 'All fields are required'}), 400
	
	if len(new_password) < 6:
		return jsonify({'error': 'Password must be at least 6 characters long'}), 400
	
	conn = get_db_connection()
	c = conn.cursor()
	c.execute('SELECT password FROM users WHERE id = ?', (session['user_id'],))
	user = c.fetchone()
	
	if not user or not check_password_hash(user[0], current_password):
		conn.close()
		return jsonify({'error': 'Current password is incorrect'}), 400
	
	hashed_pw = generate_password_hash(new_password)
	c.execute('UPDATE users SET password = ? WHERE id = ?', (hashed_pw, session['user_id']))
	conn.commit()
	conn.close()
	
	return jsonify({'success': True, 'message': 'Password updated successfully'})

@app.route('/update_recovery_email', methods=['POST'])
def update_recovery_email():
	if 'user_id' not in session:
		return jsonify({'error': 'Unauthorized'}), 401
	
	data = request.get_json()
	recovery_email_local = data.get('recovery_email', '').strip().lower()
	
	if not recovery_email_local:
		conn = get_db_connection()
		c = conn.cursor()
		c.execute('UPDATE users SET recovery_email = NULL WHERE id = ?', (session['user_id'],))
		conn.commit()
		conn.close()
		return jsonify({'success': True, 'message': 'Recovery email removed'})

	recovery_email = f'{recovery_email_local}@relaymailgrid.com'

	if not all(c.isalnum() or c in '._-' for c in recovery_email_local):
		return jsonify({'error': 'Email can only contain letters, numbers, dots, hyphens, and underscores'}), 400

	conn = get_db_connection()
	c = conn.cursor()

	try:
		c.execute('SELECT username, email FROM users WHERE id = ?', (session['user_id'],))
		user_row = c.fetchone()
		user_email = user_row[1]
		username = user_row[0]
		if recovery_email != user_email:
			c.execute('SELECT id FROM users WHERE email = ?', (recovery_email,))
			if c.fetchone():
				c.execute('UPDATE users SET recovery_email = ? WHERE id = ?', (recovery_email, session['user_id']))
				conn.commit()
				# Send notification email to recovery email
				subject = 'RelayGrid Recovery Email Notification'
				body = f"Hey there!\n\nJust a heads up: {username} ({user_email}) has set your account as their recovery email on RelayGrid.\nIf you feel honored, great! If you feel confused, maybe ask them if they lost their password already.\n\nIf you did not expect this, you can ignore this message or reply with a meme.\n\nStay safe,\nRelayGrid Team"
				c.execute('''INSERT INTO emails (sender_email, receiver_email, subject, body, timestamp, is_read) VALUES (?, ?, ?, ?, ?, ?)''',
						  ('relaymailgrid@relaymailgrid.com', recovery_email, subject, body, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 0))
				conn.commit()
		conn.close()
	except Exception:
		pass
	return jsonify({'success': True, 'message': 'If the account exists, it will be set as your recovery email.'})

if __name__ == '__main__':
	app.run(debug=False, host="0.0.0.0", port=5000)