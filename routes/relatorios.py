from datetime import datetime
from flask import Blueprint, render_template, request, send_file, current_app
from flask_login import login_required
from sqlalchemy import func
from models import db, Pedido, ItemPedido, Pizza, Bebida, Produto, Mesa, Financeiro
from services.exportador import exportar_xlsx, exportar_csv

bp = Blueprint("relatorios", __name__, url_prefix="/relatorios")


def _parse_periodo():
    inicio = request.args.get("inicio")
    fim = request.args.get("fim")
    try:
        inicio = datetime.fromisoformat(inicio) if inicio else None
        fim = datetime.fromisoformat(fim) if fim else None
    except ValueError:
        inicio = fim = None
    return inicio, fim


@bp.route("/")
@login_required
def index():
    inicio, fim = _parse_periodo()
    q = Pedido.query
    if inicio: q = q.filter(Pedido.data >= inicio)
    if fim: q = q.filter(Pedido.data <= fim)
    faturamento = q.with_entities(func.coalesce(func.sum(Pedido.valor_total),0)).filter(Pedido.status!="Cancelado").scalar()
    qtd_pedidos = q.count()

    top_pizzas = db.session.query(Pizza.nome, func.sum(ItemPedido.quantidade).label("qtd"))\
        .join(ItemPedido, ItemPedido.pizza_id==Pizza.id)\
        .join(Pedido, Pedido.id==ItemPedido.pedido_id)
    if inicio: top_pizzas = top_pizzas.filter(Pedido.data >= inicio)
    if fim: top_pizzas = top_pizzas.filter(Pedido.data <= fim)
    top_pizzas = top_pizzas.group_by(Pizza.id).order_by(func.sum(ItemPedido.quantidade).desc()).limit(10).all()

    top_bebidas = db.session.query(Bebida.nome, func.sum(ItemPedido.quantidade).label("qtd"))\
        .join(ItemPedido, ItemPedido.bebida_id==Bebida.id)\
        .group_by(Bebida.id).order_by(func.sum(ItemPedido.quantidade).desc()).limit(10).all()

    top_mesas = db.session.query(Mesa.numero, func.count(Pedido.id).label("qtd"))\
        .join(Pedido, Pedido.mesa_id==Mesa.id).group_by(Mesa.id)\
        .order_by(func.count(Pedido.id).desc()).limit(10).all()

    entradas = db.session.query(func.coalesce(func.sum(Financeiro.valor),0)).filter(Financeiro.tipo=="entrada").scalar()
    despesas = db.session.query(func.coalesce(func.sum(Financeiro.valor),0)).filter(Financeiro.tipo=="despesa").scalar()

    return render_template("relatorios.html",
        faturamento=faturamento, qtd_pedidos=qtd_pedidos,
        top_pizzas=top_pizzas, top_bebidas=top_bebidas, top_mesas=top_mesas,
        entradas=entradas, despesas=despesas, lucro=entradas-despesas,
        inicio=request.args.get("inicio",""), fim=request.args.get("fim",""))


@bp.route("/exportar/<formato>/<tipo>")
@login_required
def exportar(formato, tipo):
    if tipo == "pedidos":
        rows = [(p.id, p.data.strftime("%d/%m/%Y %H:%M"), p.status,
                 p.forma_pagamento or "", p.valor_total) for p in Pedido.query.all()]
        cols = ["ID","Data","Status","Pagamento","Valor"]
        name = "pedidos"
    elif tipo == "estoque":
        rows = [(p.nome, p.categoria or "", p.unidade_medida, p.estoque_atual, p.estoque_minimo, p.preco_custo)
                for p in Produto.query.all()]
        cols = ["Produto","Categoria","Unid","Estoque","Mínimo","Custo"]
        name = "estoque"
    elif tipo == "financeiro":
        rows = [(f.data.strftime("%d/%m/%Y"), f.tipo, f.descricao, f.categoria or "", f.valor)
                for f in Financeiro.query.all()]
        cols = ["Data","Tipo","Descrição","Categoria","Valor"]
        name = "financeiro"
    else:
        return "Tipo inválido", 400

    exports = current_app.config["EXPORTS_DIR"]
    if formato == "xlsx":
        path = exportar_xlsx(rows, cols, f"{name}.xlsx", exports)
    elif formato == "csv":
        path = exportar_csv(rows, cols, f"{name}.csv", exports)
    else:
        return "Formato inválido", 400
    return send_file(path, as_attachment=True)
