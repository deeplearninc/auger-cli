# -*- coding: utf-8 -*-

DEFAULT_COREAPI_URL = "https://app.auger.ai"
COREAPI_SCHEMA_PATH = "/api/v1/schema/"

CMD_ALIASES = {
    "audit": "cluster_audit_items",
    "configs": "amazon_configs",
    "jobs": "cluster_jobs",
    "logs": "clusters logs",
    "orgs": "organizations",
    "provisioning_jobs": "cluster_provisioning_jobs",
    "statuses": "cluster_statuses",
    "types": "instance_types",
}

RESOURCES = {
    "amazon_configs",
    "cluster_audit_items",
    "cluster_jobs",
    "cluster_provisioning_jobs",
    "provisioning_cluster_logs",
    "cluster_statuses",
    "clusters",
    "instance_types",
    "organizations",
}
