from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, SelectField, TextAreaField, BooleanField, FieldList, FormField
from wtforms.validators import DataRequired, NumberRange, Length
from models import db, Pizza, Bebida, Produto, IngredientePizza
from services.auditoria import registrar

bp = Blueprint("cardapio", __name__, url_prefix="/cardapio")


class PizzaForm(FlaskForm):
    nome = StringField("Nome", validators=[DataRequired(), Length(max=120)])
    descricao = TextAreaField("Descrição")
    tamanho = SelectField("Tamanho", choices=[("Pequena", "Pequena"), ("Média", "Média"), ("Grande", "Grande"), ("Família", "Família")])
    valor = FloatField("Valor", validators=[NumberRange(min=0)])
    ativo = BooleanField("Ativo", default=True)


class BebidaForm(FlaskForm):
    nome = StringField("Nome", validators=[DataRequired(), Length(max=120)])
    categoria = StringField("Categoria", validators=[Length(max=60)])
    valor = FloatField("Valor", validators=[NumberRange(min=0)])
    estoque_atual = IntegerField("Estoque", validators=[NumberRange(min=0)], default=0)
    ativo = BooleanField("Ativo", default=True)


@bp.route("/pizzas")
@login_required
def pizzas():
    page = request.args.get("page", 1, type=int)
    items = Pizza.query.order_by(Pizza.nome).paginate(page=page, per_page=15)
    return render_template("pizzas.html", items=items)


@bp.route("/pizzas/nova", methods=["GET", "POST"])
@login_required
def pizza_nova():
    form = PizzaForm()
    produtos = Produto.query.order_by(Produto.nome).all()
    if form.validate_on_submit():
        p = Pizza()
        form.populate_obj(p)
        db.session.add(p)
        db.session.flush()
        # ingredientes via form-data dinâmico
        ids = request.form.getlist("ingrediente_id")
        qtds = request.form.getlist("ingrediente_qtd")
        for pid, qtd in zip(ids, qtds):
            if pid and qtd:
                db.session.add(IngredientePizza(pizza_id=p.id, produto_id=int(pid), quantidade_utilizada=float(qtd)))
        db.session.commit()
        registrar(f"Pizza cadastrada: {p.nome}")
        flash("Pizza cadastrada.", "success")
        return redirect(url_for("cardapio.pizzas"))
    return render_template("pizza_form.html", form=form, produtos=produtos, pizza=None, titulo="Nova Pizza")


@bp.route("/pizzas/<int:pid>/editar", methods=["GET", "POST"])
@login_required
def pizza_editar(pid):
    p = Pizza.query.get_or_404(pid)
    form = PizzaForm(obj=p)
    produtos = Produto.query.order_by(Produto.nome).all()
    if form.validate_on_submit():
        form.populate_obj(p)
        IngredientePizza.query.filter_by(pizza_id=p.id).delete()
        ids = request.form.getlist("ingrediente_id")
        qtds = request.form.getlist("ingrediente_qtd")
        for iid, qtd in zip(ids, qtds):
            if iid and qtd:
                db.session.add(IngredientePizza(pizza_id=p.id, produto_id=int(iid), quantidade_utilizada=float(qtd)))
        db.session.commit()
        registrar(f"Editou pizza {p.id}")
        flash("Atualizada.", "success")
        return redirect(url_for("cardapio.pizzas"))
    return render_template("pizza_form.html", form=form, produtos=produtos, pizza=p, titulo="Editar Pizza")


@bp.route("/pizzas/<int:pid>/excluir", methods=["POST"])
@login_required
def pizza_excluir(pid):
    p = Pizza.query.get_or_404(pid)
    db.session.delete(p)
    db.session.commit()
    registrar(f"Excluiu pizza {pid}")
    return redirect(url_for("cardapio.pizzas"))


@bp.route("/bebidas")
@login_required
def bebidas():
    page = request.args.get("page", 1, type=int)
    items = Bebida.query.order_by(Bebida.nome).paginate(page=page, per_page=15)
    return render_template("bebidas.html", items=items)


@bp.route("/bebidas/nova", methods=["GET", "POST"])
@login_required
def bebida_nova():
    form = BebidaForm()
    if form.validate_on_submit():
        b = Bebida(); form.populate_obj(b)
        db.session.add(b); db.session.commit()
        registrar(f"Bebida cadastrada: {b.nome}")
        return redirect(url_for("cardapio.bebidas"))
    return render_template("bebida_form.html", form=form, titulo="Nova Bebida")


@bp.route("/bebidas/<int:bid>/editar", methods=["GET", "POST"])
@login_required
def bebida_editar(bid):
    b = Bebida.query.get_or_404(bid)
    form = BebidaForm(obj=b)
    if form.validate_on_submit():
        form.populate_obj(b); db.session.commit()
        return redirect(url_for("cardapio.bebidas"))
    return render_template("bebida_form.html", form=form, titulo="Editar Bebida")


@bp.route("/bebidas/<int:bid>/excluir", methods=["POST"])
@login_required
def bebida_excluir(bid):
    b = Bebida.query.get_or_404(bid)
    db.session.delete(b); db.session.commit()
    return redirect(url_for("cardapio.bebidas"))
