from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, BooleanField
from wtforms.validators import DataRequired, NumberRange, Length
from sqlalchemy import func
from models import db, Funcionario, Pedido

bp = Blueprint("funcionarios", __name__, url_prefix="/funcionarios")


class FuncionarioForm(FlaskForm):
    nome = StringField("Nome", validators=[DataRequired(), Length(max=120)])
    telefone = StringField("Telefone", validators=[Length(max=30)])
    cargo = StringField("Cargo", validators=[Length(max=60)])
    salario = FloatField("Salário", validators=[NumberRange(min=0)], default=0)
    ativo = BooleanField("Ativo", default=True)


@bp.route("/")
@login_required
def listar():
    funcs = Funcionario.query.order_by(Funcionario.nome).all()
    ranking = db.session.query(
        Funcionario.nome, func.coalesce(func.sum(Pedido.valor_total),0).label("total"),
        func.count(Pedido.id).label("qtd")
    ).outerjoin(Pedido, Pedido.funcionario_id==Funcionario.id).group_by(Funcionario.id).order_by(func.sum(Pedido.valor_total).desc()).all()
    return render_template("funcionarios.html", funcs=funcs, ranking=ranking)


@bp.route("/novo", methods=["GET","POST"])
@login_required
def novo():
    form = FuncionarioForm()
    if form.validate_on_submit():
        f = Funcionario(); form.populate_obj(f); db.session.add(f); db.session.commit()
        return redirect(url_for("funcionarios.listar"))
    return render_template("funcionario_form.html", form=form, titulo="Novo Funcionário")


@bp.route("/<int:fid>/editar", methods=["GET","POST"])
@login_required
def editar(fid):
    f = Funcionario.query.get_or_404(fid); form = FuncionarioForm(obj=f)
    if form.validate_on_submit():
        form.populate_obj(f); db.session.commit()
        return redirect(url_for("funcionarios.listar"))
    return render_template("funcionario_form.html", form=form, titulo="Editar Funcionário")
