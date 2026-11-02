from flask import Flask, render_template, request , redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.config["SECRET_KEY"] = "chave-de-exemplo-troque-antes-de-publicar"

def conectar_banco():
    conexao = sqlite3.connect("usuarios.db")
    conexao.row_factory = sqlite3.Row
    return conexao

def criar_tabela():
    conexao = conectar_banco()
    conexao.execute("""
        CREATE TABLE IF NOT EXISTS usuarios(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL ,
            email TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL    
        )
    """)
    conexao.commit()
    conexao.close()

@app.route("/")
def home():
    if "usuario_id" not in session:
        return redirect(url_for("login"))
    return render_template("home.html",nome=session["usuario_nome"])

@app.route("/cadastro", methods=["GET","POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form["nome"].strip()
        email = request.form["email"].strip().lower()
        senha = request.form["senha"]

        if not nome or not email or not senha:
            return "Preencha todos os campos.", 400

        senha_hash = generate_password_hash(senha)
        conexao = conectar_banco()

        try:
            conexao.execute(
                "INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)",
                (nome,email,senha_hash)
            )
            conexao.commit()
        except sqlite3.IntegrityError:
            return "Este e-mail ja esta cadastrado.", 409
        finally:
            conexao.close()
        return redirect(url_for("login"))
    return render_template("cadastro.html")

@app.route("/login",methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        senha = request.form["senha"]

        conexao = conectar_banco()
        usuario = conexao.execute(
            "SELECT * FROM usuarios WHERE email = ?", (email,)
        ).fetchone()
        conexao.close()

        if usuario and check_password_hash(usuario["senha"],senha):
            session.clear()
            session["usuario_id"] = usuario["id"]
            session["usuario_nome"] = usuario["nome"]
        return redirect(url_for("home"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    criar_tabela()
    app.run(debug=True)