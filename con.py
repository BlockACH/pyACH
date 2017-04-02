from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

def fetch(url, timeout):
    r = requests.get(url, timeout=timeout)
    data = r.json()['args']
    return data

# for i in range(42):
#     url = 'https://httpbin.org/get?i={0}'.format(i)
#     print(fetch(url, 60))

with ThreadPoolExecutor(max_workers=10) as executor:
    futures = {}
    for i in range(42):
        url = 'https://httpbin.org/get?i={0}'.format(i)
        future = executor.submit(fetch, url, 60)
        futures[future] = url

    for future in as_completed(futures):
        url = futures[future]
        try:
            data = future.result()
        except Exception as exc:
            print(exc)
        else:
            print('fetch {0}, get {1}'.format(url, data))
