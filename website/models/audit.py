# models.py

from .. import db
import datetime
from flask_restx import Namespace, fields


class Audit(db.Model):
    __tablename__ = "audit"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    status_code = db.Column(db.Integer, nullable=False)
    request_origin = db.Column(db.String(255), nullable=False)  # API or UI
    user_public_id = db.Column(db.String(100), nullable=True)
    route = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=True)  # JSON or text data
    request_start_time = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.datetime.now)

    def __init__(self, status_code, request_origin, user_public_id, route, body, request_start_time):
        self.status_code = status_code
        self.request_origin = request_origin
        self.user_public_id = user_public_id
        self.route = route
        self.body = body
        self.request_start_time = request_start_time

    def __repr__(self):
        return f"<Audit {self.id}, User {self.user_public_id}, Status {self.status_code}>"


class AuditDto:
    api = Namespace('audit', description='Audit related operations')
    audit = api.model('Audit', {
        'status_code': fields.Integer(required=True, description='The HTTP status code of the request'),
        'request_origin': fields.String(required=True, description='How the request arrived (API/UI)'),
        'user_public_id': fields.String(required=True, description='Who triggered the request (user public id)'),
        'route': fields.String(required=True, description='Which route was accessed'),
        'body': fields.String(description='The body of the request'),
        'request_start_time': fields.DateTime(description='The time the request was received')
    })
