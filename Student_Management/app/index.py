
from flask import render_template
from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/login", methods=['get', 'post'])
def login_process():
    # if request.method.__eq__('POST'):
    #     username = request.form.get('username')
    #     password = request.form.get('password')
    #
    #     user = dao.auth_user(username=username, password=password)
    #     if user:
    #         login_user(user)
    #
    #         next=request.args.get('next')
    #         return redirect('/' if next is None else next)

    return render_template('login.html')

if __name__ == "__main__":
    app.run(debug=True)