from app import app
from flask import request, jsonify
from flask_login import current_user, login_user

@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if current_user.is_authenticated:
#         return redirect(url_for('index'))
#     form = LoginForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(username=form.username.data).first()
#         if user is None or not user.check_password(form.password.data):
#             flash('Invalid username or password')
#             return redirect(url_for('login'))
#         login_user(user, remember=form.remember_me.data)
#         return redirect(url_for('index'))
#     return render_template('login.html', title='Sign In', form=form)

@app.route('/register', methods=['POST'])
def register():
    content = request.json
    print(content)
    return content or "No Content!"
