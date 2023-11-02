# service/query_service.py
from typing import Dict, List, Tuple


def execute_query(
    sql: str,
    cluster_names: List[str],
    output_format: str
) -> Tuple[Dict[str, str], int]:
    """
    Execute a SQL query on specified clusters with a given output format.

    :param sql: SQL query string.
    :param cluster_names: List of names of the clusters on which to execute the query.
    :param output_format: Desired format of the query results.
    :return: Tuple of the result as a dictionary and an HTTP status code.
    """
    # Logic to execute the SQL on the clusters will go here

    # For now, return a mock response for demonstration purposes
    mock_response = {
        'result': '1',
        'details': 'Mock response for demonstration'
    }
    return mock_response, 200
