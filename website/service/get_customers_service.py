from typing import Dict, Tuple
from .query_service import execute_query
import json
import csv
from io import StringIO


def get_customers_service() -> Tuple[Dict[str, str], int]:
    """
    Service function to get a list of customers.
    :return: Tuple of the result as a dictionary and an HTTP status code.
    """
    # Define the SQL query to execute
    sql = "SELECT database() AS orgId, unhealthy.cloudAccountId, unhealthy.clusterName, unhealthy.region, unhealthy.clusterId, unhealthy.type, unhealthy.state, unhealthy.unhealthyCount as count, unhealthy.LastUpdate FROM (SELECT beat.cloudAccountId, beat.clusterId, conn.region, conn.NAME AS clusterName, beat.type, beat.state, beat.version, MAX(beat.updatedAt) as LastUpdate, COUNT(*) AS unhealthyCount FROM cluster_components_heartbeats AS beat INNER JOIN (SELECT DISTINCT k8sClusterId, region, NAME FROM connected_clusters WHERE deletedAt IS NULL AND updatedAt >= NOW() - INTERVAL 15 MINUTE) AS conn ON beat.clusterId = conn.k8sClusterId WHERE beat.state IN ('unhealthy', 'healthy','terminated') AND beat.type IN ('agent', 'scanagent', 'cluster_agent', 'operator') AND beat.deletedAt IS NULL GROUP BY beat.cloudAccountId, beat.clusterId, conn.region, conn.NAME, beat.type, beat.state) AS unhealthy ORDER BY unhealthy.clusterId, unhealthy.LastUpdate DESC"
    cluster_names = ['orgs01']
    output_format = 'csv'

    try:
        # Execute the query
        result = execute_query(sql, cluster_names, output_format)

        # Check if result is a tuple and extract the relevant part
        if isinstance(result, tuple):
            # Assuming the actual data you need is the first element of the tuple
            customers = result[0]
        else:
            customers = result  # If it's not a tuple, use it as it is

        # Format the result
        formatted_result = format_customers(customers)

        return formatted_result, 200
    except Exception as e:
        # Handle any exceptions and return an appropriate error message and status code
        return {'error': 'Failed to fetch customers', 'details': str(e)}, 500


def format_customers(csv_data):
    """
    Parse and reformat CSV data for each organization.
    :param csv_data: CSV formatted string containing organization details.
    :return: A list of formatted organization dictionaries.
    """
    formatted_orgs = []

    # Use StringIO to read the CSV data as a file
    csv_file = StringIO(csv_data)

    # Use csv.DictReader to parse the CSV data
    reader = csv.DictReader(csv_file)

    for row in reader:
        # Extract and reformat the required fields

        if 'Upwind' in row.get('orgName', ''):
            continue
        formatted_org = {
            'orgId': row.get('orgId', ''),
            'orgName': row.get('orgName', ''),
            'cloudAccountId': row.get('cloudAccountId', ''),
            'clusterName': row.get('clusterName', ''),
            'region': row.get('region', ''),
            'clusterId': row.get('clusterId', ''),
            'type': row.get('type', ''),
            'state': row.get('state', ''),
            'count': row.get('count', 0),
            'lastUpdate': row.get('LastUpdate', '')
        }
        formatted_orgs.append(formatted_org)

    return formatted_orgs


# Call the function with your data
