# using: python 3.8.5

import os
import cv2
import bs4
import numpy as np
import requests


url = "http://translit-online.ru/"

images_in = os.path.normpath("/home/roman/Изображения/Блюда")
RESOLUTIONS = [(340, 226), (600, 400)]


def get_default_images_path_and_text(path: str):
    default_images_path = []
    text = ""
    for root, *_, images in os.walk(path):
        if root == path:
            for image in images:
                # добавить путь исходной картинки в список
                path = os.path.join(root, image)
                default_images_path.append(path)

                # запомнить имя исходной картинки
                default_image_name = image.split(".jpg")[0].replace(" ", "-").lower()
                text += default_image_name + ", "

    return default_images_path, text[:-2]


def get_transliterated_text(text: str, url: str) -> str:
    """
    Приводит текст к транслиту.
    Например:
        Казань -> kazan,
        Речка -> rechka
        и т.д.
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
    response = requests.post(url=url, data=data)
    if response.status_code == 200:
        r_text = response.text
        html = bs4.BeautifulSoup(r_text, "lxml")
        return html.find(attrs={"id": "out"}).text


default_images_path, text = get_default_images_path_and_text(images_in)
transliterated_text = get_transliterated_text(text, url).split(", ")


def resize_image(image: str, resolution: tuple) -> np.ndarray:
    return cv2.resize(
        src=cv2.imread(image),
        dsize=resolution,
    )


def save_image(image: np.ndarray, image_name: str, user_wants_overwrite_file: bool):
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
