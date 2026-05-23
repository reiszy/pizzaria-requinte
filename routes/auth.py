from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email, Length
from models import db, Usuario
from services.auditoria import registrar

bp = Blueprint("auth", __name__)


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    senha = PasswordField("Senha", validators=[DataRequired(), Length(min=4, max=120)])


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    form = LoginForm()
    if form.validate_on_submit():
        u = Usuario.query.filter_by(email=form.email.data.strip().lower()).first()
        if u and u.ativo and u.check_senha(form.senha.data):
            login_user(u)
            registrar(f"Login: {u.email}")
            return redirect(url_for("dashboard.index"))
        flash("Credenciais inválidas.", "danger")
    return render_template("login.html", form=form)


@bp.route("/logout")
@login_required
def logout():
    registrar(f"Logout: {current_user.email}")
    logout_user()
    return redirect(url_for("auth.login"))
