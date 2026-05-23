from datetime import datetime, timedelta
from flask import Blueprint, render_template
from flask_login import login_required
from sqlalchemy import func
from models import db, Pedido, Produto, Pizza, ItemPedido, Mesa, Financeiro

bp = Blueprint("dashboard", __name__)


@bp.route("/")
@login_required
def index():
    hoje = datetime.utcnow().date()
    inicio_mes = hoje.replace(day=1)

    fat_dia = db.session.query(func.coalesce(func.sum(Pedido.valor_total), 0)).filter(
        func.date(Pedido.data) == hoje, Pedido.status != "Cancelado"
    ).scalar()
    fat_mes = db.session.query(func.coalesce(func.sum(Pedido.valor_total), 0)).filter(
        Pedido.data >= inicio_mes, Pedido.status != "Cancelado"
    ).scalar()
    pedidos_dia = Pedido.query.filter(func.date(Pedido.data) == hoje).count()

    estoque_baixo = Produto.query.filter(Produto.estoque_atual <= Produto.estoque_minimo).all()

    top_pizzas = db.session.query(
        Pizza.nome, func.sum(ItemPedido.quantidade).label("qtd")
    ).join(ItemPedido, ItemPedido.pizza_id == Pizza.id).group_by(Pizza.id).order_by(
        func.sum(ItemPedido.quantidade).desc()
    ).limit(5).all()

    mesas = Mesa.query.order_by(Mesa.numero).all()

    # série diária dos últimos 14 dias
    inicio = hoje - timedelta(days=13)
    serie = db.session.query(
        func.date(Pedido.data), func.coalesce(func.sum(Pedido.valor_total), 0)
    ).filter(Pedido.data >= inicio, Pedido.status != "Cancelado").group_by(func.date(Pedido.data)).all()
    serie_map = {str(d): float(v) for d, v in serie}
    labels = [(inicio + timedelta(days=i)).isoformat() for i in range(14)]
    valores = [serie_map.get(l, 0) for l in labels]

    entradas = db.session.query(func.coalesce(func.sum(Financeiro.valor), 0)).filter(
        Financeiro.tipo == "entrada", Financeiro.data >= inicio_mes
    ).scalar()
    despesas = db.session.query(func.coalesce(func.sum(Financeiro.valor), 0)).filter(
        Financeiro.tipo == "despesa", Financeiro.data >= inicio_mes
    ).scalar()

    return render_template(
        "dashboard.html",
        fat_dia=fat_dia, fat_mes=fat_mes, pedidos_dia=pedidos_dia,
        estoque_baixo=estoque_baixo, top_pizzas=top_pizzas, mesas=mesas,
        labels=labels, valores=valores,
        entradas=entradas, despesas=despesas, lucro=(entradas - despesas + fat_mes),
    )
