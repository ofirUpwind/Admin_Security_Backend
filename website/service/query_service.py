import requests
from typing import Dict, List, Tuple
import csv
from io import StringIO
from flask import Flask, request, jsonify
from flask_cors import CORS


def execute_query(
    sql: str,
    cluster_names: List[str],
    output_format: str
) -> Tuple[Dict[str, str], int]:
    """
    Execute a SQL query on specified clusters with a given output format.

    :param sql: SQL query string.
    :param cluster_names: List of names of the clusters on which to execute the query.
    :param output_format: Desired format of the query results ('json' or 'csv').
    :return: Tuple of the result as a dictionary and an HTTP status code.
    """
    print(output_format, cluster_names, sql)
    # Define the URL for the API endpoint
    api_url = 'http://monitoring-receiver.prod.internal:5000/query/'

    # Prepare the headers
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }

    # Prepare the payload
    payload = {
        'sql': sql,
        'clusterNames': cluster_names,
        'format': output_format
    }

    try:
        # Make the POST request to the API
        response = requests.post(api_url, headers=headers, json=payload)
        print("response", response)

        # Check if the response status code is OK
        if response.status_code == 200:
            if output_format == 'csv':
                # Check the content type of the response
                content_type = response.headers.get('Content-Type', '')
                print("content_type", content_type)
                if content_type.startswith('text/csv'):
                    # Return the response content as CSV
                    csv_data = response.text
                    return csv_data, 200
                else:
                    return {'error': 'Unexpected content type in response'}, 500
            else:
                return response.json(), 200
        else:
            # If response is not OK, handle it appropriately
            return {'error': 'API request failed', 'details': response.text}, response.status_code

    except requests.exceptions.RequestException as e:
        # Handle any exceptions during the API call
        return {'error': 'API request exception', 'details': str(e)}, 500
