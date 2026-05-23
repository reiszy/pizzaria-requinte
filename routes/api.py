from flask import Blueprint, jsonify
from flask_login import login_required
from models import Pedido, Produto, Mesa, Pizza

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.get("/pedidos")
@login_required
def pedidos():
    return jsonify([{"id": p.id, "status": p.status, "total": p.valor_total,
                     "data": p.data.isoformat()} for p in Pedido.query.limit(100)])


@bp.get("/estoque")
@login_required
def estoque():
    return jsonify([{"id": p.id, "nome": p.nome, "estoque": p.estoque_atual,
                     "minimo": p.estoque_minimo} for p in Produto.query.all()])


@bp.get("/mesas")
@login_required
def mesas():
    return jsonify([{"id": m.id, "numero": m.numero, "status": m.status} for m in Mesa.query.all()])
