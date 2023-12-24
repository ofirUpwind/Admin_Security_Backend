from typing import Dict, Tuple, List
from typing import Dict, Tuple
from .query_service import execute_query
import json
import csv
from io import StringIO
from collections import defaultdict
import json
from packaging import version
import re


def get_Cluster() -> Tuple[Dict[str, str], int]:

    sql = """
SELECT DISTINCT
    connected_clusters.cloudProvider, 
    connected_clusters.cloudAccountId, 
    connected_clusters.k8sClusterId, 
    connected_clusters.region, 
    connected_clusters.name, 
    agent_monitored_resource_groups.cloudProvider AS agent_monitored_resource_groups_cloudProvider,
    agent_monitored_resource_groups.cloudAccountId AS agent_monitored_resource_groups_cloudAccountId,
    agent_monitored_resource_groups.type,
    agent_monitored_resource_groups.data AS agent_monitored_resource_groups_data,
    COALESCE(
        TRIM('"' FROM JSON_EXTRACT(aws_eks_clusters.awsEntity, '$.version')),
        TRIM('"' FROM JSON_EXTRACT(gcp_gke_clusters.gcpEntity, '$.version')),
        TRIM('"' FROM JSON_EXTRACT(azure_aks_clusters.azureEntity, '$.version'))
    ) AS K8SVersion
FROM 
    connected_clusters
LEFT JOIN
    aws_eks_clusters ON 
        connected_clusters.name = aws_eks_clusters.name
        AND connected_clusters.region = aws_eks_clusters.region
        AND connected_clusters.cloudAccountId = aws_eks_clusters.cloudAccountId
LEFT JOIN
    gcp_gke_clusters ON 
        connected_clusters.name = gcp_gke_clusters.name
        AND connected_clusters.region = gcp_gke_clusters.location
        AND connected_clusters.cloudAccountId = gcp_gke_clusters.projectId
LEFT JOIN
    azure_aks_clusters ON 
        connected_clusters.name = azure_aks_clusters.name
        AND connected_clusters.region = azure_aks_clusters.location
        AND connected_clusters.cloudAccountId = azure_aks_clusters.subscriptionId
JOIN
    agent_monitored_resource_groups ON
        connected_clusters.cloudProvider = agent_monitored_resource_groups.cloudProvider
        AND connected_clusters.cloudAccountId = agent_monitored_resource_groups.cloudAccountId
        AND connected_clusters.k8sClusterId = agent_monitored_resource_groups.refId
        AND agent_monitored_resource_groups.type = "cluster"
WHERE
    agent_monitored_resource_groups.deletedAt IS NULL AND connected_clusters.deletedAt IS NULL
"""
    cluster_names = ['orgs01']
    output_format = 'csv'

    try:
        result = execute_query(sql, cluster_names, output_format)

        # Assuming result is obtained as before
        customers_csv = result[0] if isinstance(result, tuple) else result
        orgs_data = parse_csv_to_aggregated_json(customers_csv)

        # Parse the JSON string into a list
        orgs_data_list = json.loads(orgs_data)

        return orgs_data_list, 200
    except Exception as e:
        return {'error': 'Failed to fetch cluster data', 'details': str(e)}, 500


def parse_csv_to_aggregated_json(csv_content: str) -> str:
    csv_file = StringIO(csv_content)
    reader = csv.DictReader(csv_file)

    orgs = defaultdict(lambda: {'orgId': '', 'orgName': '', 'clouds': []})
    for row in reader:
        if "upwind" not in row['orgName'].lower():
            org_id = row['orgId']
            org_name = row['orgName']
            orgs[org_id]['orgId'] = org_id
            orgs[org_id]['orgName'] = org_name

            try:
                agent_monitored_data = json.loads(
                    row['agent_monitored_resource_groups_data'])
            except json.JSONDecodeError:
                agent_monitored_data = {}  # or some default value

            cloud_data = {
                'k8sClusterId': row['k8sClusterId'],
                'clusterRegion': row['region'],
                'clusterName': row['name'],
                'K8SVersion': row.get('K8SVersion', ''),
                'agentMonitoredResourceGroupsData': agent_monitored_data,
                'cloudAccountId': row['cloudAccountId'],
                'cloudProvider': row['cloudProvider']
            }
            orgs[org_id]['clouds'].append(cloud_data)

    orgs_list = list(orgs.values())
    return json.dumps(orgs_list, indent=4)


def is_standard_version(version_str):
    """Check if the version string follows standard semantic versioning."""
    try:
        # Attempt to parse it as a standard version
        version.parse(version_str)
        return True
    except version.InvalidVersion:
        return False


def parse_version(version_str):
    # Remove 'v' prefix from version string if present
    cleaned_version_str = version_str.lstrip('v')

    if is_standard_version(cleaned_version_str):
        return version.parse(cleaned_version_str)
    else:
        # If the version string is non-standard, use a custom handling approach
        # For example, return a very low version number to ensure it is considered 'lower'
        # than any standard version number, or handle it based on your specific needs
        return version.parse("0.0.0")


def is_standard_version(version_str):
    # Regular expression for standard semantic versioning (e.g., 1.2.3, 1.2.3-alpha1)
    pattern = r'^\d+\.\d+\.\d+(-[a-zA-Z0-9]+)?$'
    return bool(re.match(pattern, version_str))


def parse_version(version_str):
    # Remove 'v' prefix from version string if present
    cleaned_version_str = version_str.lstrip('v')

    if is_standard_version(cleaned_version_str):
        return version.parse(cleaned_version_str)
    else:
        # Non-standard version strings are ignored (or treated as lower priority)
        return version.parse("0.0.0")


def getMaxClusterVersion():
    sql = """
    SELECT TRIM('"' FROM JSON_EXTRACT(data, '$.installedComponents[*].componentType')) AS t,
    TRIM('"' FROM JSON_EXTRACT(data, '$.installedComponents[*].version')) AS v
    FROM agent_monitored_resource_groups
    WHERE type = 'cluster'
    """
    cluster_names = ['orgs01']
    output_format = 'csv'

    try:
        result = execute_query(sql, cluster_names, output_format)
        # Initialize maximum versions
        max_versions = {"cluster_agent": version.parse("0.0.0"),
                        "operator": version.parse("0.0.0"),
                        "agent": version.parse("0.0.0")}

        # Assuming the first element of the result tuple is the CSV data
        csv_data = result[0]
        csv_reader = csv.reader(csv_data.strip().split('\n'))

        # Skip header
        next(csv_reader)

        for row in csv_reader:
            # Extract component types and versions from the row
            # Adjust the indices [3] and [4] based on your CSV data structure
            component_types = json.loads(row[3])
            component_versions = json.loads(row[4])

            for comp_type, comp_version in zip(component_types, component_versions):
                if comp_type == 'agent':
                    cleaned_version_str = comp_version.lstrip('v')
                comp_version_parsed = parse_version(comp_version)
                if comp_version_parsed > max_versions.get(comp_type, version.parse("0.0.0")):
                    max_versions[comp_type] = comp_version_parsed

        # Convert Version objects to strings for JSON serialization
        max_versions_str = {key: str(value)
                            for key, value in max_versions.items()}

        return max_versions_str, 200

    except Exception as e:
        return {'error': 'Failed to fetch cluster data', 'details': str(e)}, 500


def getPinnedVersion() -> Tuple[Dict[str, str], int]:
    sql = """
   SELECT 
    orgId,
    cloudProvider,
    cloudAccountId,
    clusterId,
    JSON_EXTRACT(config, '$.agent.version') as pinnedAgentChartVersion,
    JSON_EXTRACT(config, '$.clusterAgent.version') as pinnedClusterAgentChartVersion,
    JSON_EXTRACT(config, '$.agent.values.image.tag') as pinnedAgentImageVersion,
    JSON_EXTRACT(config, '$.clusterAgent.values.image.tag') as pinnedClusterAgentImageVersion
    FROM upwind.cluster_components_configurations
    WHERE deletedAt IS NULL HAVING     pinnedAgentChartVersion IS NOT NULL OR
    pinnedClusterAgentChartVersion IS NOT NULL OR
    pinnedAgentImageVersion IS NOT NULL OR
    pinnedClusterAgentImageVersion IS NOT NULL
    """
    cluster_names = ['coredb']
    output_format = 'json'

    try:
        result = execute_query(sql, cluster_names, output_format)
        # This is the first element of the tuple, a dictionary
        data_dict = result[0]
        # Accessing the 'coreDb' key of the nested dictionary
        core_db_data = data_dict['result']['coreDb']

        # core_db_data is now a list of dictionaries
        return core_db_data, 200  # Returning the list and the HTTP status code
        # Initialize maximum versions
    except Exception as e:
        return {'error': 'Failed to fetch cluster data', 'details': str(e)}, 500


def getFeatures() -> Tuple[Dict[str, str], int]:
    sql = """
    select orgId, cloudProvider, CloudAccountId, ClusterId, config
     from cluster_components_configurations
     where deletedAt IS NULL
     """
    cluster_names = ['coredb']
    output_format = 'json'

    try:
        result, status_code = execute_query(sql, cluster_names, output_format)
        cluster_data = result['result']['coreDb']

        for item in cluster_data:
            if 'config' in item and isinstance(item['config'], str):
                try:
                    config = json.loads(item['config'])
                    transform_extra_args(config)
                    item['config'] = config
                except json.JSONDecodeError:
                    item['config'] = {'error': 'Invalid JSON format'}

        return cluster_data, status_code
    except Exception as e:
        return [{'error': 'Failed to fetch cluster data', 'details': str(e)}], 500


def transform_extra_args(config):
    # Initialize the new config structure with existing keys if present
    new_config = {
        'agent': config.get('agent', {}).get('values', {}).get('agent', {}),
        'scanAgent': config.get('agent', {}).get('values', {}).get('scanAgent', {}),
        'clusterAgent': config.get('clusterAgent', {}).get('values', {})
    }

    # Process extraArgs for agent
    if 'extraArgs' in new_config['agent']:
        new_config['agent']['extraArgs'] = transform_args(
            new_config['agent']['extraArgs'])

    # Process extraArgs for scanAgent
    if 'extraArgs' in new_config['scanAgent']:
        new_config['scanAgent']['extraArgs'] = transform_args(
            new_config['scanAgent']['extraArgs'])

    # Process extraArgs for clusterAgent
    if 'extraArgs' in new_config['clusterAgent']:
        new_config['clusterAgent']['extraArgs'] = transform_args(
            new_config['clusterAgent']['extraArgs'])

    return new_config


def transform_args(extra_args):
    new_extra_args = []
    for arg in extra_args:
        if '=' in arg:
            name, val = arg.split('=', 1)
        else:
            name, val = arg, None
        new_extra_args.append({'name': name, 'value': val})
    return new_extra_args

# This function should be called within your existing getFeatures function
# after you load the JSON from the '
