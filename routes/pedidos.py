from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from models import db, Pedido, ItemPedido, Mesa, Funcionario, Pizza, Bebida, IngredientePizza, Produto, Financeiro
from services.auditoria import registrar

bp = Blueprint("pedidos", __name__, url_prefix="/pedidos")


@bp.route("/")
@login_required
def listar():
    page = request.args.get("page", 1, type=int)
    status = request.args.get("status", "")
    q = Pedido.query
    if status:
        q = q.filter(Pedido.status == status)
    pedidos = q.order_by(Pedido.data.desc()).paginate(page=page, per_page=20)
    return render_template("pedidos.html", pedidos=pedidos, status=status)


@bp.route("/novo", methods=["GET", "POST"])
@login_required
def novo():
    mesas = Mesa.query.order_by(Mesa.numero).all()
    funcionarios = Funcionario.query.filter_by(ativo=True).order_by(Funcionario.nome).all()
    pizzas = Pizza.query.filter_by(ativo=True).order_by(Pizza.nome).all()
    bebidas = Bebida.query.filter_by(ativo=True).order_by(Bebida.nome).all()

    if request.method == "POST":
        mesa_id = request.form.get("mesa_id", type=int)
        func_id = request.form.get("funcionario_id", type=int)
        forma = request.form.get("forma_pagamento")
        obs = request.form.get("observacoes", "").strip()

        pedido = Pedido(mesa_id=mesa_id, funcionario_id=func_id,
                        forma_pagamento=forma, observacoes=obs, status="Em preparo")
        db.session.add(pedido); db.session.flush()

        total = 0.0
        pizza_ids = request.form.getlist("pizza_id")
        pizza_qtds = request.form.getlist("pizza_qtd")
        for pid, q in zip(pizza_ids, pizza_qtds):
            if not pid or not q: continue
            pid = int(pid); q = int(q)
            if q <= 0: continue
            pz = Pizza.query.get(pid)
            if not pz: continue
            item = ItemPedido(pedido_id=pedido.id, pizza_id=pid, quantidade=q, valor_unitario=pz.valor)
            total += pz.valor * q
            db.session.add(item)
            # baixa estoque de ingredientes
            for ing in pz.ingredientes:
                if ing.produto:
                    ing.produto.estoque_atual -= ing.quantidade_utilizada * q

        beb_ids = request.form.getlist("bebida_id")
        beb_qtds = request.form.getlist("bebida_qtd")
        for bid, q in zip(beb_ids, beb_qtds):
            if not bid or not q: continue
            bid = int(bid); q = int(q)
            if q <= 0: continue
            b = Bebida.query.get(bid)
            if not b: continue
            db.session.add(ItemPedido(pedido_id=pedido.id, bebida_id=bid, quantidade=q, valor_unitario=b.valor))
            b.estoque_atual -= q
            total += b.valor * q

        pedido.valor_total = total
        if mesa_id:
            m = Mesa.query.get(mesa_id)
            if m: m.status = "Ocupada"

        # lança no financeiro
        db.session.add(Financeiro(tipo="entrada", descricao=f"Pedido #{pedido.id}",
                                  valor=total, categoria="Vendas"))
        db.session.commit()
        registrar(f"Pedido #{pedido.id} criado, total R${total:.2f}")
        flash("Pedido registrado.", "success")
        return redirect(url_for("pedidos.detalhe", pid=pedido.id))

    return render_template("pedido_form.html", mesas=mesas, funcionarios=funcionarios,
                           pizzas=pizzas, bebidas=bebidas)


@bp.route("/<int:pid>")
@login_required
def detalhe(pid):
    pedido = Pedido.query.get_or_404(pid)
    return render_template("pedido_detalhe.html", pedido=pedido)


@bp.route("/<int:pid>/status", methods=["POST"])
@login_required
def alterar_status(pid):
    pedido = Pedido.query.get_or_404(pid)
    novo = request.form.get("status")
    if novo not in ("Em preparo", "Finalizado", "Entregue", "Cancelado"):
        abort(400)
    pedido.status = novo
    if novo == "Cancelado":
        # estorna financeiro
        db.session.add(Financeiro(tipo="despesa", descricao=f"Cancelamento pedido #{pedido.id}",
                                  valor=pedido.valor_total, categoria="Estorno"))
    if novo in ("Entregue", "Cancelado") and pedido.mesa:
        pedido.mesa.status = "Em limpeza"
    db.session.commit()
    registrar(f"Pedido #{pid} -> {novo}")
    return redirect(url_for("pedidos.detalhe", pid=pid))
