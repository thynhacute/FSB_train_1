from flask import session, redirect, url_for, flash,request,render_template,Blueprint
from functools import wraps
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Vui lòng đăng nhập để truy cập!', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function
auth = Blueprint('auth', __name__)  # Blueprint để nhóm các route liên quan đến đăng nhập

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    Route xử lý đăng nhập.
    """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Kiểm tra thông tin đăng nhập
        if username == 'admin' and password == 'password':  # Thay bằng logic thực tế
            session['logged_in'] = True
            flash('Đăng nhập thành công!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Sai tên đăng nhập hoặc mật khẩu!', 'danger')
    
    return render_template('login.html')

@auth.route('/logout')
def logout():
    """
    Route xử lý đăng xuất.
    """
    session.pop('logged_in', None)
    flash('Bạn đã đăng xuất.', 'info')
    return redirect(url_for('auth.login'))