import requests

url_yd = 'https://cloud-api.yandex.net/v1/disk/resources'

url = 'https://dog.ceo/api/breed/'

inp = input("Введите породу собаки: ")

token_YD = input("Введите токен Яндекс диска: ")

def get_info_doge(inp, token):

     #создаем папку с названием породы в ядекс диске
    requests.put(url_yd, params = {"path": inp}, headers = {'Authorization': f'OAuth {token}'})
    
    # записываем в переменную ссылку на фото переданной породы
    res = requests.get(f'{url}{inp}/images/random')
    data = res.json()
    
    # записываем в файл фото собаки переданной породы

    with open(f'image_dogs/{inp}.jpg', 'wb') as f:
        f.write(requests.get(data['message']).content)

    #  Загружаем на Я.Диск
    params = {"path": f'{inp}/{inp}'}
    headers = {'Authorization': f'OAuth {token}'}
    
    r = requests.get(f'{url_yd}/upload', params=params, headers=headers)
    upload_url = r.json()['href']

    with open(f'image_dogs/{inp}.jpg', 'rb') as f:
        requests.put(upload_url, files={'file': f})
    
    # получаем подпороды
    res1 = requests.get(f'{url}{inp}/list')
    sub_breeds = res1.json()["message"]

    for sub in sub_breeds:
        # Загружаем фото подпороды
        
        # получаем ссылку на фото подпороды
        img_url = requests.get(f'{url}{inp}/{sub}/images/random').json()['message']
        
        #получаем ссылку на загрузку фото в ядекс диске 
        params = {"path": f'{inp}/{inp}_{sub}'}
        headers = {'Authorization': f'OAuth {token}'}
        
        r = requests.get(f'{url_yd}/upload', params=params, headers=headers)
        upload_url = r.json()['href']

        with open(f'image_dogs/{inp}_{sub}.jpg', 'wb') as f:
            f.write(requests.get(img_url).content)
        
        # загружаем подпороду на яндекс диск
        with open(f'image_dogs/{inp}_{sub}.jpg', 'rb') as f:
            requests.put(upload_url, files={'file': f})
    
    return f"Фото собаки данной породы загруженo(ны) на ваш Я.Диск в папке {inp}"
        
print(get_info_doge(inp, token_YD))

