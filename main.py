# using: python 3.8.5

import os
import cv2
import bs4
import numpy as np
import requests


URL = "http://translit-online.ru/"

images_in = os.path.normpath("/home/roman/Изображения/Блюда")
RESOLUTIONS = [(340, 226), (600, 400)]


def get_images_path_and_text(path: str) -> tuple:
    """
    Собирает исходные пути до фотографий,
    объединяет имена файлов в единую строку.

    input: путь до папки с фотографиями.

    output 1: список, содержащий полный путь до каждой картинки.
    Пример: ["/home/roman/images/my photo.jpg", ...]

    output 2: строка, содержащая имена файлов без расширения через запятую. Пробелы заменяются на дефис.
    Пример: "my-photo, my-photo-2, my-photo-3, ..."
    """
    default_images_path = []
    text = ""
    for root, *_, images in os.walk(path):
        if root == path:
            for image in images:
                path = os.path.join(root, image)
                default_images_path.append(path)

                default_image_name = image.split(".jpg")[0].replace(" ", "-").lower()
                text += default_image_name + ", "

    return default_images_path, text[:-2]


def get_transliterated_text(text: str) -> str:
    """
    Преобразует русский текст в английскую транслитерацию.
    input: строка, содержащая имена файлов через запятую без расширения.

    output: строка в транслитерированном виде.
    Пример: Казань -> kazan, речка -> rechka, ...
    """
    data = {
        "in": f"{text}",
        "translate": "перевести",
        "n6": "e",
        "n7": "yo",
        "n8": "zh",
        "n11": "j",
        "n23": "cehksz",
        "n24": "c",
        "n27": "shch",
        "n28": "\"",
        "n29": "y",
        "n30": "",
        "n31": "e",
        "n32": "yu",
        "n33": "ya"
    }
    response = requests.post(url=URL, data=data)
    if response.status_code == 200:
        r_text = response.text
        html = bs4.BeautifulSoup(r_text, "lxml")
        return html.find(attrs={"id": "out"}).text.split(", ")


default_images_path, text = get_images_path_and_text(images_in)
transliterated_text = get_transliterated_text(text)


def resize_image(image: str, resolution: tuple) -> np.ndarray:
    return cv2.resize(
        src=cv2.imread(image),
        dsize=resolution,
    )


def save_image(image: np.ndarray, image_name: str, user_wants_overwrite_file: bool = None):
    if not isinstance(image, np.ndarray):
        raise ValueError(f"Картинка должна быть экземпляром {np.ndarray}")

    cv2.imwrite(image_name, image)

    if user_wants_overwrite_file:
        print(f"{image_name} успешно перезаписан!")


def _overwrite_file(image_name: str) -> bool:
    print(f"{image_name} уже существует! Хотите перезаписать его?")

    while True:
        answer = input("Введите y/n: ")
        if answer.lower() == "n":
            return False
        elif answer.lower() == "y":
            return True


for i, image in enumerate(default_images_path):  # выбрать картинку
    text = transliterated_text[i]                # выбрать транслитированный текст
    for resolution in RESOLUTIONS:               # выбрать разрешение
        prefix = str(resolution[0])              # выбрать префикс, например: 340 или 600

        image_name = os.path.join(images_in, prefix, f"{text}-{prefix}.jpg")
        dir_for_save = os.path.join(images_in, prefix)

        user_wants_overwrite_file = False

        if not os.path.exists(dir_for_save):
            os.mkdir(dir_for_save)

        if os.path.isfile(image_name):
            user_wants_overwrite_file = _overwrite_file(image_name)
            if user_wants_overwrite_file is False:
                continue

        img = resize_image(image, resolution)
        save_image(img, image_name, user_wants_overwrite_file)

if __name__ == '__main__':
    pass
