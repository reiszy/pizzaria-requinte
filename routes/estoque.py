from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, SelectField
from wtforms.validators import DataRequired, NumberRange, Length
from models import db, Produto, MovimentacaoEstoque
from services.auditoria import registrar

bp = Blueprint("estoque", __name__, url_prefix="/estoque")


class ProdutoForm(FlaskForm):
    nome = StringField("Nome", validators=[DataRequired(), Length(max=120)])
    categoria = StringField("Categoria", validators=[Length(max=60)])
    unidade_medida = StringField("Unidade", validators=[Length(max=20)])
    preco_custo = FloatField("Preço Custo", validators=[NumberRange(min=0)], default=0)
    estoque_atual = FloatField("Estoque", validators=[NumberRange(min=0)], default=0)
    estoque_minimo = FloatField("Estoque Mínimo", validators=[NumberRange(min=0)], default=0)
    fornecedor = StringField("Fornecedor", validators=[Length(max=120)])


class MovimentacaoForm(FlaskForm):
    produto_id = SelectField("Produto", coerce=int, validators=[DataRequired()])
    tipo_movimentacao = SelectField("Tipo", choices=[("entrada", "Entrada"), ("saida", "Saída")])
    quantidade = FloatField("Quantidade", validators=[DataRequired(), NumberRange(min=0.01)])
    observacao = StringField("Observação", validators=[Length(max=255)])


@bp.route("/")
@login_required
def listar():
    page = request.args.get("page", 1, type=int)
    q = request.args.get("q", "").strip()
    query = Produto.query
    if q:
        query = query.filter(Produto.nome.ilike(f"%{q}%"))
    produtos = query.order_by(Produto.nome).paginate(page=page, per_page=15)
    return render_template("estoque.html", produtos=produtos, q=q)


@bp.route("/novo", methods=["GET", "POST"])
@login_required
def novo():
    form = ProdutoForm()
    if form.validate_on_submit():
        p = Produto()
        form.populate_obj(p)
        db.session.add(p)
        db.session.commit()
        registrar(f"Novo produto: {p.nome}")
        flash("Produto cadastrado.", "success")
        return redirect(url_for("estoque.listar"))
    return render_template("produtos.html", form=form, titulo="Novo Produto")


@bp.route("/<int:pid>/editar", methods=["GET", "POST"])
@login_required
def editar(pid):
    p = Produto.query.get_or_404(pid)
    form = ProdutoForm(obj=p)
    if form.validate_on_submit():
        form.populate_obj(p)
        db.session.commit()
        registrar(f"Editou produto {p.id}")
        flash("Atualizado.", "success")
        return redirect(url_for("estoque.listar"))
    return render_template("produtos.html", form=form, titulo="Editar Produto")


@bp.route("/<int:pid>/excluir", methods=["POST"])
@login_required
def excluir(pid):
    p = Produto.query.get_or_404(pid)
    db.session.delete(p)
    db.session.commit()
    registrar(f"Excluiu produto {pid}")
    flash("Excluído.", "info")
    return redirect(url_for("estoque.listar"))


@bp.route("/movimentar", methods=["GET", "POST"])
@login_required
def movimentar():
    form = MovimentacaoForm()
    form.produto_id.choices = [(p.id, p.nome) for p in Produto.query.order_by(Produto.nome).all()]
    if form.validate_on_submit():
        p = Produto.query.get(form.produto_id.data)
        qtd = form.quantidade.data
        if form.tipo_movimentacao.data == "entrada":
            p.estoque_atual += qtd
        else:
            p.estoque_atual -= qtd
        db.session.add(MovimentacaoEstoque(
            produto_id=p.id, tipo_movimentacao=form.tipo_movimentacao.data,
            quantidade=qtd, observacao=form.observacao.data
        ))
        db.session.commit()
        registrar(f"Mov. estoque {form.tipo_movimentacao.data} {qtd} - {p.nome}")
        flash("Movimentação registrada.", "success")
        return redirect(url_for("estoque.movimentar"))
    movs = MovimentacaoEstoque.query.order_by(MovimentacaoEstoque.data.desc()).limit(50).all()
    return render_template("movimentacoes.html", form=form, movs=movs)
