from flask_login import current_user
from models import db, LogAuditoria


def registrar(acao: str):
    try:
        uid = current_user.id if current_user.is_authenticated else None
        db.session.add(LogAuditoria(usuario_id=uid, acao=acao))
        db.session.commit()
    except Exception:
        db.session.rollback()
