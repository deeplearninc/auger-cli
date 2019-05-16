from collections import OrderedDict
from datetime import datetime

from auger_cli.api import projects
from auger_cli.utils import list_dict_fillna

display_attributes = ['created_at', 'cpu', 'memory', 'slave_data', 'pods_data']

def read(client, cluster_id=None):
    if not cluster_id:
        project = projects.get_or_create(client)
        cluster_id = project.get('cluster_id')
        
    if not cluster_id:
        raise Exception("Run experiment to see cluster information.")

    return client.call_hub_api('get_cluster_statuses', {'cluster_id': cluster_id})

def read_ex(client, cluster_id=None):
    result_raw = read(client, cluster_id)

    result = {'cpu': [], 'memory': []}
    dt_format = '%Y-%m-%dT%H:%M:%S.%fZ'
    all_columns = {}
    for item in result_raw:
        worker_pods = []
        for pod in item.get('pods_data', []):
            if 'worker' in pod.get('name', ''):
                worker_pods.append(pod)

        if not worker_pods:
            continue

        item_time = datetime.strptime(item.get('created_at'), dt_format).time().replace(microsecond=0)
        item_cpu = item.get('cpu')
        if not item_cpu:
            item_cpu = 0

        cpu_res = OrderedDict({'Time': item_time,'CPU total %': item_cpu})
        memory_res = OrderedDict({'Time': item_time, 'Memory total %': item.get('memory')})
        worker_pods = sorted(worker_pods, key=lambda k: k['name'])
        for idx, pod in enumerate(worker_pods):
            if 'optimizer' in pod['name']:
                cpu_res['opt'] = "%.1f"%pod.get('cpu')
                memory_res['opt'] = "%.1f"%pod.get('memory')
                all_columns['opt'] = 1
            else:    
                cpu_res[str(idx)] = "%.1f"%pod.get('cpu')
                memory_res[str(idx)] = "%.1f"%pod.get('memory')
                all_columns[str(idx)] = 1

        result['cpu'].append(cpu_res)    
        result['memory'].append(memory_res)    

    result['cpu'] = sorted(result['cpu'], key=lambda k: k['Time'])
    result['memory'] = sorted(result['memory'], key=lambda k: k['Time'])

    list_dict_fillna(result['cpu'], all_columns.keys(), 0)
    list_dict_fillna(result['memory'], all_columns.keys(), 0)

    #print(result['memory'])
    return result
