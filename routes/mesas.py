from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField
from wtforms.validators import DataRequired, NumberRange
from models import db, Mesa

bp = Blueprint("mesas", __name__, url_prefix="/mesas")


class MesaForm(FlaskForm):
    numero = IntegerField("Número", validators=[DataRequired(), NumberRange(min=1)])
    capacidade = IntegerField("Capacidade", validators=[NumberRange(min=1)], default=4)
    status = SelectField("Status", choices=[("Livre","Livre"),("Ocupada","Ocupada"),("Reservada","Reservada"),("Em limpeza","Em limpeza")])


@bp.route("/")
@login_required
def listar():
    mesas = Mesa.query.order_by(Mesa.numero).all()
    return render_template("mesas.html", mesas=mesas)


@bp.route("/nova", methods=["GET","POST"])
@login_required
def nova():
    form = MesaForm()
    if form.validate_on_submit():
        m = Mesa(); form.populate_obj(m); db.session.add(m); db.session.commit()
        return redirect(url_for("mesas.listar"))
    return render_template("mesa_form.html", form=form, titulo="Nova Mesa")


@bp.route("/<int:mid>/editar", methods=["GET","POST"])
@login_required
def editar(mid):
    m = Mesa.query.get_or_404(mid); form = MesaForm(obj=m)
    if form.validate_on_submit():
        form.populate_obj(m); db.session.commit()
        return redirect(url_for("mesas.listar"))
    return render_template("mesa_form.html", form=form, titulo="Editar Mesa")


@bp.route("/<int:mid>/status/<status>", methods=["POST"])
@login_required
def status(mid, status):
    m = Mesa.query.get_or_404(mid)
    if status in ("Livre","Ocupada","Reservada","Em limpeza"):
        m.status = status; db.session.commit()
    return redirect(url_for("mesas.listar"))
