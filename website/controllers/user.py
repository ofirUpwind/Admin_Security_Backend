from flask import request
from flask_restx import Resource

from ..util.decorator import token_required, admin_token_required
from ..models.user import UserDto
from ..service.user_service import save_new_user, get_all_users, get_a_user
from typing import Dict, Tuple
from ..models.user import QueryDto
from ..service.query_service import execute_query
from ..service.get_customers_service import get_customers_service
from ..service.cluster_version import get_Cluster
from ..service.cluster_version import getMaxClusterVersion
from ..service.cluster_version import getPinnedVersion
from ..service.cluster_version import getFeatures


api1 = QueryDto.api
_query = QueryDto.query

CREATE_USER_KEY: str = "hiOFIR33"

api = UserDto.api
_user = UserDto.user
_user_out = UserDto.user_out


@api.route('/')
class UserList(Resource):
    @api.doc('list_of_registered_users')
    @token_required
    @api.marshal_list_with(_user, envelope='data')
    def get(self):
        """List all registered users"""
        # decode the token to get the organization_id
        organization_id = request.args.get('organization_id')
        return get_all_users(organization_id=organization_id)

    @api.expect(_user, validate=True)
    @api.response(201, 'User successfully created.')
    @api.doc('create a new user')
    @api.param(name="create_user_key", type="string", description="Key to create user")
    def post(self) -> Tuple[Dict[str, str], int]:
        """Creates a new User """
        user_key = request.args.get("create_user_key")
        if user_key != CREATE_USER_KEY:
            api.abort(400, 'Invalid create_user_key')

        data = request.json
        new_user = save_new_user(data=data)
        if not new_user:
            api.abort(400, 'Error creating user')
        return new_user, 201


@api.route('/<public_id>')
@api.param('public_id', 'The User identifier')
@api.response(404, 'User not found.')
class User(Resource):
    @api.doc('get a user')
    @token_required
    @api.marshal_with(_user)
    def get(self, public_id):
        """get a user given its identifier"""
        user = get_a_user(public_id)
        if not user:
            api.abort(404, 'User not found')
        else:
            return user

# Add additional routes and methods as needed.


@api.route('/admin/test')
class AdminTest(Resource):
    @api.doc('admin_test')
    @admin_token_required
    def get(self):
        """Test endpoint that requires an admin token"""
        return {
            'status': 'success',
            'message': 'Admin token has been verified.'
        }, 200


@api1.route('/query/')
class QueryExecute(Resource):
    @api1.doc('execute_query')
    @token_required
    @api1.expect(_query, validate=True)
    def post(self) -> Tuple[Dict[str, str], int]:
        """Execute a SQL query."""
        data = request.json
        sql_query = data.get('sql')
        cluster_names = data.get('clusterNames')
        response_format = data.get('format')

        # Call the service function to execute the SQL query
        response, status_code = execute_query(
            sql_query, cluster_names, response_format)

        return response, status_code


@api1.route('/submit-report/')
class SubmitReport(Resource):
    @api1.doc('submit_report')
    @token_required
    def post(self) -> Tuple[Dict[str, str], int]:
        """Submit a report."""
        data = request.json
        # Extract relevant data from request
        report_data = data.get('reportData')

        # Call a service function to handle the report submission
        response, status_code = submit_report_service(report_data)

        return response, status_code


@api1.route('/get-customers/')
class GetCustomers(Resource):
    @api1.doc('get_customers')
    @token_required
    def get(self) -> Tuple[Dict[str, str], int]:
        """Get a list of customers."""
        # Call a service function to get the list of customers
        response, status_code = get_Cluster()

        return response, status_code


@api1.route('/get-clusterVersion/')
class GetClusterVersion(Resource):
    @api1.doc('get_clusterVersion')
    @token_required
    def get(self) -> Tuple[Dict[str, str], int]:
        """Get a list of customers."""
        # Call a service function to get the list of customers
        response, status_code = getMaxClusterVersion()

        return response, status_code


@api1.route('/get-pinnedVersions/')
class GetCustomers(Resource):
    @api1.doc('get_pinnedVersions')
    @token_required
    def get(self) -> Tuple[Dict[str, str], int]:
        """Get a list of customers."""
        # Call a service function to get the list of customers
        response, status_code = getPinnedVersion()

        return response, status_code


@api1.route('/get-features/')
class GetFeatures(Resource):
    @api1.doc('GetFeatures')
    @token_required
    def get(self) -> Tuple[Dict[str, str], int]:
        """Get a list of features"""
        # Call a service function to get the list of customers
        response, status_code = getFeatures()

        return response, status_code
