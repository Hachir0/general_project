import requests
import json
import os
from tqdm import tqdm 

DOG_API_URL = "https://dog.ceo/api/breed/"
YANDEX_DISK_API_URL = "https://cloud-api.yandex.net/v1/disk/resources"
YANDEX_UPLOAD_API_URL = "https://cloud-api.yandex.net/v1/disk/resources/upload"

def create_folder_on_yandex_disk(folder_name, token):
    """Создаёт папку на Яндекс.Диске, если её нет."""
    response = requests.put(
        YANDEX_DISK_API_URL,
        params={"path": folder_name},
        headers={"Authorization": f"OAuth {token}"},
    )
    if response.status_code not in (201, 409):  # 409 = папка уже существует
        raise Exception(f"Ошибка при создании папки: {response.json()}")

def upload_to_yandex_disk(file_name, file_url, folder_name, token):
    # Получаем ссылку для загрузки
    upload_response = requests.get(
        YANDEX_UPLOAD_API_URL,params={"path": f"{folder_name}/{file_name}","url": file_url,},
        headers={"Authorization": f"OAuth {token}"},)
    
    upload_url = upload_response.json().get("href")  # Ссылка для загрузки на Яндекс.Диск
    if not upload_url:
        raise Exception("Не удалось получить ссылку для загрузки на Яндекс.Диск")
    
    # Загружаем файл по полученному URL
    file_response = requests.put(upload_url, headers={"Authorization": f"OAuth {token}"})
    
    if file_response.status_code == 201:
        print(f"Изображение {file_name} успешно загружено на Яндекс.Диск.")
    else:
        raise Exception(f"Ошибка при загрузке изображения {file_name}: {file_response.status_code} - {file_response.text}")

def get_breed_images(breed):
    images = []
    
    # Проверяем, есть ли подпороды
    sub_breeds_response = requests.get(f"{DOG_API_URL}{breed}/list")
    sub_breeds = sub_breeds_response.json().get("message", [])
    
    if sub_breeds:
        # Если есть подпороды, загружаем их изображения
        for sub_breed in sub_breeds:
            sub_images_response = requests.get(f"{DOG_API_URL}{breed}/{sub_breed}/images")
            sub_images = sub_images_response.json().get("message", [])
            images.extend([(f"{breed}_{sub_breed}", img) for img in sub_images])
    else:
        # Если подпород нет, загружаем изображения основной породы
        images_response = requests.get(f"{DOG_API_URL}{breed}/images")
        images = [(breed, img) for img in images_response.json().get("message", [])]
    
    return images

def backup_dog_images(breed, token):
    # Получаем все изображения породы
    images = get_breed_images(breed)
    if not images:
        print(f"Нет изображений для породы {breed}.")
        return
    
    # Создаём папку на Яндекс.Диске
    create_folder_on_yandex_disk(breed, token)
    
    # Загружаем каждое изображение
    uploaded_files = []
    for breed_name, image_url in tqdm(images, desc="Загрузка изображений"):
        file_name = f"{breed_name}_{os.path.basename(image_url)}"
        try:
            upload_to_yandex_disk(file_name, image_url, breed, token)
            uploaded_files.append({"file_name": file_name})
        except Exception as e:
            print(f"Ошибка при загрузке {file_name}: {e}")
    
    # Сохраняем информацию в JSON
    with open(f"{breed}_backup.json", "w") as f:
        json.dump(uploaded_files, f, indent=2)
    
    print(f"Готово! Загружено {len(uploaded_files)} изображений.")

if __name__ == "__main__":
    breed = input("Введите породу собаки: ")
    token = input("Введите токен Яндекс.Диска: ")
    backup_dog_images(breed, token)
