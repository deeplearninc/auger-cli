# -*- coding: utf-8 -*-

import os

DEFAULT_COREAPI_URL = 'https://app.auger.ai'
COREAPI_SCHEMA_PATH = '/api/v1/schema/'
API_POLL_INTERVAL = 2.0

ROOT_PATH = '.auger'
SERVICE_YAML_PATH = os.path.join(ROOT_PATH, 'service.yml')
DOCKERFILE_PATH = os.path.join(ROOT_PATH, 'Dockerfile')
PROJECT_FILES_PATH = os.path.join(ROOT_PATH, 'project-files')
