from cs50 import SQL
from flask import *
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import pytz
from helpers import login_required

app = Flask(__name__)

app.config["SESSION_TYPE"] = "filesystem"

Session(app)

db = SQL("sqlite:///project.db")

@app.route("/", methods=['GET', 'POST'])
@login_required
def index():
    if "contact" not in session:
        session['contact'] = {"id_person": None, "id_chat": None, "username": None}
    
    if request.method == 'POST':
        lista1 = db.execute('SELECT id_1 FROM contacts WHERE id_2=?', session["user_id"])
        lista2 = db.execute('SELECT id_2 FROM contacts WHERE id_1=?', session["user_id"])
        lista3 = []
        for i in range(len(lista1)):
            lista3.append(lista1[i]['id_1'])
        for j in range(len(lista2)):
            lista3.append(lista2[j]['id_2'])
        leng = len(lista3)
        lista4 = []
        for i in range(leng):
            a = db.execute('SELECT username FROM users WHERE id=?', lista3[i])
            lista4.append(a[0]['username'])
        
        # if chat selected
        if request.form.get('id'):
            session['contact'] = {"id_person": None, "id_chat": None, "username": None}
            try:
                id = int(request.form.get('id'))
                username = request.form.get('username')
            except ValueError:
                return render_template('index.html', error='invalid contact', lista3=lista3, lista4=lista4, leng=leng)
            if id in lista3:
                if db.execute("SELECT id_chat FROM contacts WHERE id_1=? AND id_2=?", session["user_id"], id):
                    id_chat = db.execute("SELECT id_chat FROM contacts WHERE id_1=? AND id_2=?", session["user_id"], id)
                    id_chat = id_chat[0]['id_chat']
                    session['contact'] = {"id_person": id, "id_chat": id_chat, "username": username}
                    return redirect("/")
                else:
                    id_chat = db.execute("SELECT id_chat FROM contacts WHERE id_1=? AND id_2=?", id, session["user_id"])
                    id_chat = id_chat[0]['id_chat']
                    session['contact'] = {"id_person": id, "id_chat": id_chat, "username": username}
                    return redirect("/")
            else:
                return render_template('index.html', error='invalid contact', lista3=lista3, lista4=lista4, leng=leng)
            
        # if sent message
        if request.form.get('message'):
            if request.form.get('id2'):
                try:
                    id = int(request.form.get('id2'))
                    username = request.form.get('uname')
                except ValueError:
                    return render_template('index.html', error='invalid contact', lista3=lista3, lista4=lista4, leng=leng)
                if id in lista3:
                    if db.execute("SELECT id_chat FROM contacts WHERE id_1=? AND id_2=?", session["user_id"], id):
                        id_chat = db.execute("SELECT id_chat FROM contacts WHERE id_1=? AND id_2=?", session["user_id"], id)
                        id_chat = id_chat[0]['id_chat']
                        db.execute(f"INSERT INTO messages{id_chat} (message, id_who_sent) VALUES (?, ?)", request.form.get("message"), session["user_id"])
                        session['contact'] = {"id_person": id, "id_chat": id_chat, "username": username}
                        return redirect("/")
                    else:
                        id_chat = db.execute("SELECT id_chat FROM contacts WHERE id_1=? AND id_2=?", id, session["user_id"])
                        id_chat = id_chat[0]['id_chat']
                        db.execute(f"INSERT INTO messages{id_chat} (message, id_who_sent) VALUES (?, ?)", request.form.get("message"), session["user_id"])
                        session['contact'] = {"id_person": id, "id_chat": id_chat, "username": username}
                        return redirect("/")
                else:
                    return render_template('index.html', error='invalid contact', lista3=lista3, lista4=lista4, leng=leng)
            else:
                return render_template('index.html', error='invalid contact', lista3=lista3, lista4=lista4, leng=leng)
        return render_template('index.html', error='error', lista3=lista3, lista4=lista4, leng=leng)
    else:
        lista1 = db.execute('SELECT id_1 FROM contacts WHERE id_2=?', session["user_id"])
        lista2 = db.execute('SELECT id_2 FROM contacts WHERE id_1=?', session["user_id"])
        lista3 = []
        for i in range(len(lista1)):
            lista3.append(lista1[i]['id_1'])
        for j in range(len(lista2)):
            lista3.append(lista2[j]['id_2'])
        leng = len(lista3)
        lista4 = []
        for i in range(leng):
            a = db.execute('SELECT username FROM users WHERE id=?', lista3[i])
            lista4.append(a[0]['username'])

        #this path allows me to avoid resending message when refreshing the page
        if session['contact']['id_person']:
            id_chat = session['contact']['id_chat']
            id = session['contact']['id_person']
            listm = db.execute(f"SELECT * FROM messages{id_chat}")
            lengt = len(listm)
            return render_template('index.html', lista3=lista3, lista4=lista4, leng=leng, lengt=lengt, listm=listm, id1=session["user_id"], id2=id, on=1, username=session['contact']['username'])
        else:
            return render_template("index.html", lista3=lista3, lista4=lista4, leng=leng)

@app.route("/register", methods=["GET","POST"])
def register():
    session.clear()
    session['contact'] = {"id_person": None, "id_chat": None, "username": None}
    if request.method == "POST":
        user = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        if not user:
            error = "invalid username"
            return render_template("register.html",error=error)
        select_user = db.execute("SELECT username FROM users WHERE username=?", user)
        if select_user:
            error = "username already in use"
            return render_template("register.html",error=error)
        if not password or not confirm:
            error = "invalid password"
            return render_template("register.html",error=error)
        if password != confirm:
            error = "passwords don´t match"
            return render_template("register.html",error=error)
        if len(password) < 8 or ('0' not in password and '1' not in password and '2' not in password and '3' not in password and '4' not in password and '5' not in password and '6' not in password and '7' not in password and '8' not in password and '9' not in password):
            error = "invalid password"
            return render_template("register.html",error=error)
        password = generate_password_hash(password)
        db.execute("INSERT INTO users (username, hashed_password) VALUES (?,?)", user, password)
        select = db.execute("SELECT id FROM users WHERE username=?", user)
        session["user_id"] = select[0]["id"]
        flash("registered succesfully")
        return redirect("/")
    else:
        return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    session.clear()
    session['contact'] = {"id_person": None, "id_chat": None, "username": None}
    if request.method == "POST":
        user = request.form.get("username")
        password = request.form.get("password")
        if not user:
            error = "invalid username"
            return render_template("login.html",error=error)
        if not password:
            error = "invalid password"
            return render_template("login.html",error=error)
        select = db.execute("SELECT * FROM users WHERE username=?", user)
        if len(select) != 1 or not check_password_hash(select[0]["hashed_password"], password):
            error = "invalid username or password"
            return render_template("login.html",error=error)
        session["user_id"] = select[0]["id"]
        flash("logged in succesfully")
        return redirect("/")
    else:
        return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    session.clear()
    session['contact'] = {"id_person": None, "id_chat": None, "username": None}
    return redirect("/login")

@app.route("/addcontacts",  methods=["GET","POST"])
@login_required
def addcontacts():
    session['contact'] = {"id_person": None, "id_chat": None, "username": None}
    if request.method == "POST":
        if request.form.get("select") == "ID":
            form = request.form.get("username")
            list = db.execute("Select username, id FROM users WHERE id LIKE ?", "%" + form + "%")
            leng = len(list)
            if leng > 0:
                return render_template("addcontacts.html", found=1, leng=leng,list=list)
            else:
                return render_template("addcontacts.html", found=0)
        elif request.form.get("select") == "Username":
            form = request.form.get("username")
            list = db.execute("SELECT username,id FROM users WHERE username LIKE ?", "%" + form + "%")
            leng = len(list)
            if leng > 0:
                return render_template("addcontacts.html", found=1, leng=leng,list=list)
            else:
                return render_template("addcontacts.html", found=0)
        if request.form.get("id") and not int(request.form.get("id")) == session["user_id"]:
            lista1 = db.execute('SELECT id_1 FROM contacts WHERE id_2=?', session["user_id"])
            lista2 = db.execute('SELECT id_2 FROM contacts WHERE id_1=?', session["user_id"])
            lista3 = []
            for i in range(len(lista1)):
                lista3.append(lista1[i]['id_1'])
            for j in range(len(lista2)):
                lista3.append(lista2[j]['id_2'])
            lista4 = db.execute('SELECT id FROM users WHERE id=?', request.form.get("id"))
            if int(request.form.get('id')) not in lista3 and lista4:
                db.execute("INSERT INTO contacts (id_1, id_2) VALUES (?,?)", session["user_id"], request.form.get("id"))
                id_chat = db.execute("SELECT id_chat FROM contacts WHERE id_1=? AND id_2=?", session["user_id"], request.form.get("id"))
                id_chat = id_chat[0]['id_chat']
                db.execute(f"CREATE TABLE messages{id_chat} (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, message TEXT, id_who_sent INTEGER NOT NULL)")
                list2 = db.execute("SELECT username FROM users WHERE id=?", request.form.get("id"))
                username = list2[0]["username"]
                return render_template("addcontacts.html", added=1, username=username)
        return render_template("addcontacts.html", error="invalid request")
    else:
        return render_template("addcontacts.html")
