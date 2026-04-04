from flask import Flask, render_template, request, redirect, url_for, session
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key_here_change_in_production'

# Demo users database (in production, use a real database)
USERS = {
    'admin': 'password123',
    'user': 'user123',
    'demo': 'demo123'
}

# Fixed images for demo
NATURE_IMAGE = "https://images.unsplash.com/photo-1501785888041-af3ef285b470"
ANIMAL_IMAGE = "https://images.unsplash.com/photo-1518791841217-8f162f1e1131"
CITY_IMAGE = "https://images.unsplash.com/photo-1467269204594-9661b134dd2b"
CAT_SUNGLASSES_IMAGE = "https://images.unsplash.com/photo-1517849845537-4d257902454a"
DEFAULT_IMAGE = "https://picsum.photos/512"

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/login", methods=["GET", "POST"])
def login():
    error_message = None
    success_message = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        # Validate input
        if not username or not password:
            error_message = "Username and password are required."
        elif username in USERS and USERS[username] == password:
            session['username'] = username
            success_message = f"Welcome, {username}! Redirecting..."
            return redirect(url_for('index'))
        else:
            error_message = "Invalid username or password. Please try again."

    return render_template("login.html", error_message=error_message, success_message=success_message)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    error_message = None
    success_message = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not username or not password or not confirm_password:
            error_message = "All fields are required."
        elif len(password) < 6:
            error_message = "Password must be at least 6 characters."
        elif password != confirm_password:
            error_message = "Passwords do not match."
        elif username in USERS:
            error_message = "Username already exists. Try a different one."
        else:
            USERS[username] = password
            session['username'] = username
            success_message = f"Account created successfully! Welcome, {username}!"
            return redirect(url_for('index'))

    return render_template("signup.html", error_message=error_message, success_message=success_message)

@app.route("/register", methods=["GET", "POST"])
def register():
    # Register is the same as signup, just redirect
    return redirect(url_for('signup'))

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    image_url = None
    prompt = ""
    username = session.get('username', 'User')

    if request.method == "POST":
        prompt = request.form.get("prompt").lower()

        # Special fixed prompt
        if "cute cat wearing sunglasses" in prompt:
            image_url = CAT_SUNGLASSES_IMAGE

        # Nature-related prompts
        elif any(word in prompt for word in ["nature", "mountain", "forest", "river", "sunset"]):
            image_url = NATURE_IMAGE

        # Animal-related prompts
        elif any(word in prompt for word in ["animal", "dog", "cat", "lion", "tiger"]):
            image_url = ANIMAL_IMAGE

        # City-related prompts
        elif any(word in prompt for word in ["city", "building", "street", "urban", "night city"]):
            image_url = CITY_IMAGE

        # Default fallback
        else:
            image_url = DEFAULT_IMAGE

    return render_template("index.html", image_url=image_url, prompt=prompt, username=username)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.before_request
def before_request():
    # Redirect to login if not authenticated and trying to access protected pages
    if request.endpoint not in ['login', 'signup', 'register', 'static'] and 'username' not in session:
        return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)