# audit_service.py
from typing import Any, Optional, Dict, Tuple
from datetime import datetime
from .. import db
from ..models.audit import Audit
import json


def log_audit_entry(
    status_code: int,
    request_origin: str,
    user_public_id: Optional[str],
    route: str,
    body: Any,
    request_start_time: datetime
) -> None:
    """
    Create an audit log entry in the database.

    :param status_code: HTTP status code of the request
    :param request_origin: Origin of the request (API or UI)
    :param user_public_id: The public ID of the user who made the request
    :param route: The route that was accessed
    :param body: The request body
    :param request_start_time: The start time of the request
    """
    # Create an instance of the Audit model
    # check if in the body there is a password
    if isinstance(body, dict) and 'password' in body:
        # Replace the actual password with asterisks
        body['password'] = '******'

    # Convert body to a JSON string for logging
    body_json = json.dumps(body) if isinstance(body, dict) else str(body)

    new_audit_entry = Audit(
        status_code=status_code,
        request_origin=request_origin,
        user_public_id=user_public_id,
        route=route,
        body=body_json,
        request_start_time=request_start_time
    )

    # Add to the database session and commit
    try:
        db.session.add(new_audit_entry)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise
