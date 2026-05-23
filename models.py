from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class Usuario(db.Model, UserMixin):
    __tablename__ = "usuarios"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    senha_hash = db.Column(db.String(255), nullable=False)
    perfil = db.Column(db.String(20), default="operador")  # admin, gerente, operador
    ativo = db.Column(db.Boolean, default=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def check_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

    @property
    def is_active(self):
        return self.ativo


class Produto(db.Model):
    """Ingredientes e insumos"""
    __tablename__ = "produtos"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    categoria = db.Column(db.String(60))
    unidade_medida = db.Column(db.String(20), default="un")
    preco_custo = db.Column(db.Float, default=0.0)
    estoque_atual = db.Column(db.Float, default=0.0)
    estoque_minimo = db.Column(db.Float, default=0.0)
    fornecedor = db.Column(db.String(120))


class Pizza(db.Model):
    __tablename__ = "pizzas"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    descricao = db.Column(db.Text)
    tamanho = db.Column(db.String(20), default="Média")
    valor = db.Column(db.Float, default=0.0)
    ativo = db.Column(db.Boolean, default=True)
    ingredientes = db.relationship("IngredientePizza", backref="pizza", cascade="all,delete")


class IngredientePizza(db.Model):
    __tablename__ = "ingredientes_pizza"
    id = db.Column(db.Integer, primary_key=True)
    pizza_id = db.Column(db.Integer, db.ForeignKey("pizzas.id"), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey("produtos.id"), nullable=False)
    quantidade_utilizada = db.Column(db.Float, default=0.0)
    produto = db.relationship("Produto")


class Bebida(db.Model):
    __tablename__ = "bebidas"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    categoria = db.Column(db.String(60))
    valor = db.Column(db.Float, default=0.0)
    estoque_atual = db.Column(db.Integer, default=0)
    ativo = db.Column(db.Boolean, default=True)


class Funcionario(db.Model):
    __tablename__ = "funcionarios"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    telefone = db.Column(db.String(30))
    cargo = db.Column(db.String(60))
    salario = db.Column(db.Float, default=0.0)
    ativo = db.Column(db.Boolean, default=True)


class Mesa(db.Model):
    __tablename__ = "mesas"
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.Integer, unique=True, nullable=False)
    capacidade = db.Column(db.Integer, default=4)
    status = db.Column(db.String(20), default="Livre")  # Livre, Ocupada, Reservada, Em limpeza


class Pedido(db.Model):
    __tablename__ = "pedidos"
    id = db.Column(db.Integer, primary_key=True)
    mesa_id = db.Column(db.Integer, db.ForeignKey("mesas.id"))
    funcionario_id = db.Column(db.Integer, db.ForeignKey("funcionarios.id"))
    valor_total = db.Column(db.Float, default=0.0)
    forma_pagamento = db.Column(db.String(30))
    status = db.Column(db.String(20), default="Em preparo")
    observacoes = db.Column(db.Text)
    data = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    mesa = db.relationship("Mesa")
    funcionario = db.relationship("Funcionario")
    itens = db.relationship("ItemPedido", backref="pedido", cascade="all,delete")


class ItemPedido(db.Model):
    __tablename__ = "itens_pedido"
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey("pedidos.id"), nullable=False)
    pizza_id = db.Column(db.Integer, db.ForeignKey("pizzas.id"))
    bebida_id = db.Column(db.Integer, db.ForeignKey("bebidas.id"))
    quantidade = db.Column(db.Integer, default=1)
    valor_unitario = db.Column(db.Float, default=0.0)

    pizza = db.relationship("Pizza")
    bebida = db.relationship("Bebida")


class MovimentacaoEstoque(db.Model):
    __tablename__ = "movimentacoes_estoque"
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey("produtos.id"))
    tipo_movimentacao = db.Column(db.String(20))  # entrada / saida
    quantidade = db.Column(db.Float)
    observacao = db.Column(db.String(255))
    data = db.Column(db.DateTime, default=datetime.utcnow)
    produto = db.relationship("Produto")


class Financeiro(db.Model):
    __tablename__ = "financeiro"
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(20))  # entrada / despesa
    descricao = db.Column(db.String(255))
    valor = db.Column(db.Float, default=0.0)
    categoria = db.Column(db.String(60))
    data = db.Column(db.DateTime, default=datetime.utcnow, index=True)


class LogAuditoria(db.Model):
    __tablename__ = "logs_auditoria"
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"))
    acao = db.Column(db.String(255))
    data = db.Column(db.DateTime, default=datetime.utcnow)
