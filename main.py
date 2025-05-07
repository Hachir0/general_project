import requests
import json
import os
from tqdm import tqdm

DOG_API_URL = "https://dog.ceo/api/breed/"
YANDEX_API_URL = "https://cloud-api.yandex.net/v1/disk/resources/upload"

def upload_to_yandex(file_name, file_url, folder, token):
    try:
        img_data = requests.get(file_url).content
        
        upload_response = requests.get(
            YANDEX_API_URL,
            params={"path": f"{folder}/{file_name}", "overwrite": "true"},
            headers={"Authorization": f"OAuth {token}"}
        )
        
        if upload_response.status_code != 200:
            return None
        
        upload_url = upload_response.json().get("href")
        
        headers = {
            "Authorization": f"OAuth {token}",
            "Content-Type": "image/jpeg"
        }
        
        requests.put(upload_url, data=img_data, headers=headers)
        return file_name
        
    except Exception as e:
        print(f"Ошибка загрузки {file_name}: {e}")
        return None

def get_dog_images(breed):
    try:
        sub_breeds = requests.get(f"{DOG_API_URL}{breed}/list").json().get("message", [])
        main_image = requests.get(f"{DOG_API_URL}{breed}/images/random").json().get("message")
        sub_images = [requests.get(f"{DOG_API_URL}{breed}/{sub}/images/random").json().get("message") 
                     for sub in sub_breeds if sub]
        return [img for img in ([main_image] + sub_images) if img]
    except Exception as e:
        print(f"Ошибка получения изображений: {e}")
        return []

def backup_dogs():
    breed = input("Введите породу собаки: ").strip().lower()
    token = input("Введите ваш токен Яндекс.Диска: ").strip()
    
    requests.put(
        "https://cloud-api.yandex.net/v1/disk/resources",
        params={"path": breed},
        headers={"Authorization": f"OAuth {token}"}
    )
    
    images = get_dog_images(breed)
    if not images:
        print(f"Не найдено изображений для породы {breed}")
        return
    
    uploaded_files = []
    
    print(f"\nНайдено {len(images)} изображений для загрузки:")
    for i, img_url in enumerate(tqdm(images, desc="Загрузка")):
        file_name = f"{breed}_{i+1}.jpg"
        if uploaded_name := upload_to_yandex(file_name, img_url, breed, token):
            uploaded_files.append({"file_name": uploaded_name})
    
    # Сохраняем информацию в JSON
    json_filename = f"{breed}_uploaded_files.json"
    with open(json_filename, 'w') as f:
        json.dump(uploaded_files, f, indent=2)
    
    print(f"\nГотово! Загружено {len(uploaded_files)} изображений.")
    print(f"Список файлов сохранен в {json_filename}")

if __name__ == "__main__":
    backup_dogs()
    