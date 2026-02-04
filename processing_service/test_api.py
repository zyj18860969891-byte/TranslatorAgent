import requests
import json

api_key = 'sk-88bf1bd605544d208c7338cb1989ab3e'
base_url = 'https://dashscope.aliyuncs.com/api/v1'

headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

try:
    # 测试模型列表
    response = requests.get(f'{base_url}/models', headers=headers, timeout=10)
    print(f'Status Code: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print('Models response:')
        print(json.dumps(data, indent=2))
    else:
        print(f'Error: {response.text}')
        
    # 测试兼容模式
    response2 = requests.get(f'{base_url}/compatible-mode/v1/models', headers=headers, timeout=10)
    print(f'Compatible Mode Status Code: {response2.status_code}')
    if response2.status_code == 200:
        data2 = response2.json()
        print('Compatible Mode response:')
        print(json.dumps(data2, indent=2))
    else:
        print(f'Compatible Mode Error: {response2.text}')
        
except Exception as e:
    print(f'Exception: {e}')