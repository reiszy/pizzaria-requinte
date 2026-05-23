"""
PIZZARIA REQUINTE - Mini-ERP em Flask
Execução: python app.py
Login padrão: admin@requinte.com / admin123
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, redirect, url_for
from flask_login import LoginManager
from config import Config
from models import db, Usuario, Mesa, Produto, Pizza, Bebida, Funcionario, IngredientePizza
print("APP INICIANDO...")

def criar_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    for d in [Config.DATABASE_DIR, Config.EXPORTS_DIR, Config.BACKUPS_DIR, Config.LOGS_DIR]:
        os.makedirs(d, exist_ok=True)

    db.init_app(app)

    login_manager = LoginManager(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Faça login para acessar."

    @login_manager.user_loader
    def load_user(uid):
        return Usuario.query.get(int(uid))

    # logging
    handler = RotatingFileHandler(os.path.join(Config.LOGS_DIR, "app.log"),
                                  maxBytes=1_000_000, backupCount=3)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)

    # blueprints
    from routes.auth import bp as auth_bp
    from routes.dashboard import bp as dashboard_bp
    from routes.estoque import bp as estoque_bp
    from routes.cardapio import bp as cardapio_bp
    from routes.pedidos import bp as pedidos_bp
    from routes.mesas import bp as mesas_bp
    from routes.funcionarios import bp as funcionarios_bp
    from routes.financeiro import bp as financeiro_bp
    from routes.relatorios import bp as relatorios_bp
    from routes.api import bp as api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(estoque_bp)
    app.register_blueprint(cardapio_bp)
    app.register_blueprint(pedidos_bp)
    app.register_blueprint(mesas_bp)
    app.register_blueprint(funcionarios_bp)
    app.register_blueprint(financeiro_bp)
    app.register_blueprint(relatorios_bp)
    app.register_blueprint(api_bp)

    @app.route("/")
    def root():
        return redirect(url_for("dashboard.index"))

    @app.errorhandler(404)
    def e404(e): return "Página não encontrada", 404

    @app.errorhandler(403)
    def e403(e): return "Acesso negado", 403

    with app.app_context():
        db.create_all()
        seed_initial()

    return app


def seed_initial():
    """Cria usuário admin e dados de exemplo se vazio."""
    if not Usuario.query.first():
        admin = Usuario(nome="Administrador", email="admin@requinte.com", perfil="admin")
        admin.set_senha("admin123")
        db.session.add(admin)

    if not Mesa.query.first():
        for n in range(1, 11):
            db.session.add(Mesa(numero=n, capacidade=4, status="Livre"))

    if not Produto.query.first():
        for nome, un, est, mn, custo in [
            ("Farinha de Trigo", "kg", 50, 10, 5.0),
            ("Molho de Tomate", "L", 20, 5, 8.0),
            ("Mussarela", "kg", 15, 3, 35.0),
            ("Calabresa", "kg", 10, 2, 28.0),
            ("Catupiry", "kg", 5, 1, 40.0),
            ("Frango Desfiado", "kg", 8, 2, 25.0),
            ("Manjericão", "un", 30, 5, 1.5),
        ]:
            db.session.add(Produto(nome=nome, categoria="Ingrediente", unidade_medida=un,
                                   estoque_atual=est, estoque_minimo=mn, preco_custo=custo))

    if not Pizza.query.first():
        for nome, desc, valor in [
            ("Mussarela", "Molho, mussarela e orégano", 49.90),
            ("Calabresa", "Calabresa, cebola e azeitona", 54.90),
            ("Portuguesa", "Presunto, ovo, cebola, ervilha", 59.90),
            ("Frango com Catupiry", "Frango desfiado e catupiry", 62.90),
            ("Marguerita", "Mussarela, tomate e manjericão", 57.90),
        ]:
            db.session.add(Pizza(nome=nome, descricao=desc, tamanho="Média", valor=valor, ativo=True))

    if not Bebida.query.first():
        for nome, cat, val, est in [
            ("Coca-Cola 2L", "Refrigerante", 14.0, 20),
            ("Guaraná 2L", "Refrigerante", 12.0, 20),
            ("Água Mineral", "Sem gás", 4.0, 50),
            ("Suco de Laranja", "Natural", 9.0, 15),
        ]:
            db.session.add(Bebida(nome=nome, categoria=cat, valor=val, estoque_atual=est, ativo=True))

    if not Funcionario.query.first():
        for nome, cargo, sal in [
            ("João Pizzaiolo", "Pizzaiolo", 2500),
            ("Maria Atendente", "Atendente", 1800),
            ("Carlos Caixa", "Caixa", 2000),
        ]:
            db.session.add(Funcionario(nome=nome, cargo=cargo, salario=sal, ativo=True))

    db.session.commit()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
