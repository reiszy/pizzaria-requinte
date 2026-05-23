# 🍕 PIZZARIA REQUINTE — Mini-ERP

Sistema web em **Python/Flask** para controle administrativo, operacional e comercial de pizzaria.

## Funcionalidades
- Autenticação multiusuário (Flask-Login) com hash de senha (Werkzeug) e CSRF (Flask-WTF)
- Dashboard com KPIs, gráficos (Chart.js), status de mesas e estoque baixo
- Cadastro de **Produtos (ingredientes)**, **Pizzas** (com ingredientes), **Bebidas**
- **Pedidos** com baixa automática de estoque, vínculo a mesa/funcionário, status workflow
- **Mesas** (Livre / Ocupada / Reservada / Em limpeza)
- **Funcionários** com ranking de vendas
- **Financeiro** (entradas / despesas / saldo)
- **Relatórios** + Exportação **XLSX** e **CSV** (pandas + openpyxl)
- API REST básica em `/api/...`
- Tema **dark mode**, sidebar, paginação, busca, logs e auditoria
- Backup do banco SQLite (utilitário em `services/backup.py`)

## Como executar

```bash
python -m venv venv
source venv/bin/activate         # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Acesse: http://localhost:5000

**Login padrão:** `admin@requinte.com` / `admin123`

> O banco SQLite e dados de exemplo (10 mesas, 7 ingredientes, 5 pizzas, 4 bebidas, 3 funcionários) são criados automaticamente no primeiro start em `database/pizzaria.db`.

## Estrutura
```
pizzaria_requinte/
├── app.py              # Bootstrap Flask + seed inicial
├── config.py           # Configurações
├── models.py           # SQLAlchemy ORM
├── routes/             # Blueprints (auth, dashboard, estoque, cardápio, pedidos, mesas, funcionarios, financeiro, relatorios, api)
├── services/           # Auditoria, backup, exportador
├── templates/          # Jinja2 + Bootstrap 5
├── static/             # CSS / JS
├── database/           # SQLite
├── exports/            # Planilhas geradas
├── backups/            # Backups SQLite
├── logs/               # app.log
└── requirements.txt
```

## Segurança
- Senhas com `werkzeug.security` (PBKDF2)
- CSRF habilitado em todos os forms WTForms
- Sessões HttpOnly + SameSite Lax
- Rotas protegidas por `@login_required` e decorator `perfil_requerido`
- Validação e sanitização via WTForms (`Length`, `NumberRange`, `Email`)
- Logs rotativos + tabela `logs_auditoria`

## Expansão futura
- Sistema de impressão térmica de comandas
- API REST completa com tokens
- Multi-loja
- Integração delivery (iFood, Rappi)
