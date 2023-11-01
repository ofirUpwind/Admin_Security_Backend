from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models.user import User
from . import db  # Import the auth_helpers module
import json
import http.client
from sqlalchemy import text  # Import the 'text' function
from flask_jwt_extended import jwt_required


premissions = Blueprint('premissions', __name__)


@premissions.route('/edit_note', methods=['GET'])
@login_required
@jwt_required
def protected_route():
    return jsonify(message="This is a protected route!")


# @premissions.route('/check_db_connection')
# def check_db_connection():
#     try:
#         # Explicitly declare the SQL expression as a text object
#         query = text("SELECT 1")
#         result = db.session.execute(query)

#         # Check the result to ensure the query was successful
#         if result.scalar() == 1:
#             return "Database connection is working!"
#         else:
#             return "Database query did not return the expected result."
#     except Exception as e:
#         return f"Database connection failed: {str(e)}"
