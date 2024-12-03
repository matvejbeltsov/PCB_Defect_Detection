import os
import xml.etree.ElementTree as ET
from pathlib import Path
#
# Пути к аннотациям
PHOTOS_ANNOTATIONS_PATH = r"C:\Users\Matvej\Desktop\Programm\Python\AI_Project_2\Unified_Dataset\annotations\photos"
GERBER_ANNOTATIONS_PATH = r"C:\Users\Matvej\Desktop\Programm\Python\AI_Project_2\Unified_Dataset\annotations\gerber_defected"
YOLO_LABELS_PATH = r"C:\Users\Matvej\Desktop\Programm\Python\AI_Project_2\Unified_Dataset\yolo_labels"

# Создаем папку для YOLO аннотаций, если ее нет
os.makedirs(YOLO_LABELS_PATH, exist_ok=True)

# Список классов (будет автоматически обновляться)
classes = []


# Функция для обработки аннотаций в формате XML
def convert_to_yolo(xml_file, yolo_folder):
    global classes
    tree = ET.parse(xml_file)
    root = tree.getroot()


    size = root.find("size")
    width = int(size.find("width").text)
    height = int(size.find("height").text)

    # Путь к YOLO-файлу
    yolo_file = os.path.join(yolo_folder, Path(xml_file).stem + ".txt")
    with open(yolo_file, "w") as yolo:
        for obj in root.findall("object"):
            class_name = obj.find("name").text

            # Проверяем, есть ли класс в списке, если нет, добавляем
            if class_name not in classes:
                classes.append(class_name)

            class_id = classes.index(class_name)

            # Получаем координаты bounding box
            bndbox = obj.find("bndbox")
            xmin = int(bndbox.find("xmin").text)
            ymin = int(bndbox.find("ymin").text)
            xmax = int(bndbox.find("xmax").text)
            ymax = int(bndbox.find("ymax").text)

            # Конвертируем в YOLO формат
            x_center = (xmin + xmax) / 2 / width
            y_center = (ymin + ymax) / 2 / height
            bbox_width = (xmax - xmin) / width
            bbox_height = (ymax - ymin) / height

            yolo.write(f"{class_id} {x_center:.6f} {y_center:.6f} {bbox_width:.6f} {bbox_height:.6f}\n")



def process_annotations(annotation_path):
    processed_files = 0
    for root_dir, dirs, files in os.walk(annotation_path):
        for file in files:
            if file.endswith(".xml"):
                xml_path = os.path.join(root_dir, file)
                convert_to_yolo(xml_path, YOLO_LABELS_PATH)
                processed_files += 1
    return processed_files


# Обработка аннотаций для фото и гербер-файлов
processed_photo_files = process_annotations(PHOTOS_ANNOTATIONS_PATH)
processed_gerber_files = process_annotations(GERBER_ANNOTATIONS_PATH)

# Сохранение классов в файл classes.txt
classes_file = os.path.join(YOLO_LABELS_PATH, "classes.txt")
with open(classes_file, "w") as f:
    for class_name in classes:
        f.write(class_name + "\n")

print(f"Конвертация завершена!")
print(f"Обработано файлов из папки фото: {processed_photo_files}")
print(f"Обработано файлов из папки гербер: {processed_gerber_files}")
print(f"Найденные классы: {classes}")