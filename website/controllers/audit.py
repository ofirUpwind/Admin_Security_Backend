# controllers/audit_controller.py

from flask import request
from flask_restx import Resource
from ..service.audit_service import log_audit_entry
from ..models.audit import AuditDto

api = AuditDto.api
_audit = AuditDto.audit


@api.route('/')
class AuditList(Resource):
    @api.doc('create_audit_log')
    @api.expect(_audit, validate=True)
    def post(self):
        """Create a new audit log entry"""
        # Here you extract the audit information from the incoming request
        data = request.json
        status_code = data.get('status_code')
        request_origin = data.get('request_origin')
        user_public_id = data.get('user_public_id')
        route = data.get('route')
        body = data.get('body', '')

        # Now you call the service to log the audit entry
        log_audit_entry(status_code, request_origin,
                        user_public_id, route, body)

        return {'message': 'Audit log entry created'}, 201
