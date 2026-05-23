from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField
from wtforms.validators import DataRequired, NumberRange, Length
from sqlalchemy import func
from models import db, Financeiro

bp = Blueprint("financeiro", __name__, url_prefix="/financeiro")


class LancamentoForm(FlaskForm):
    tipo = SelectField("Tipo", choices=[("entrada","Entrada"),("despesa","Despesa")])
    descricao = StringField("Descrição", validators=[DataRequired(), Length(max=255)])
    valor = FloatField("Valor", validators=[DataRequired(), NumberRange(min=0.01)])
    categoria = StringField("Categoria", validators=[Length(max=60)])


@bp.route("/", methods=["GET","POST"])
@login_required
def index():
    form = LancamentoForm()
    if form.validate_on_submit():
        f = Financeiro(); form.populate_obj(f); db.session.add(f); db.session.commit()
        return redirect(url_for("financeiro.index"))

    page = request.args.get("page", 1, type=int)
    lancs = Financeiro.query.order_by(Financeiro.data.desc()).paginate(page=page, per_page=20)

    entradas = db.session.query(func.coalesce(func.sum(Financeiro.valor),0)).filter(Financeiro.tipo=="entrada").scalar()
    despesas = db.session.query(func.coalesce(func.sum(Financeiro.valor),0)).filter(Financeiro.tipo=="despesa").scalar()
    saldo = entradas - despesas

    return render_template("financeiro.html", form=form, lancs=lancs,
                           entradas=entradas, despesas=despesas, saldo=saldo)
