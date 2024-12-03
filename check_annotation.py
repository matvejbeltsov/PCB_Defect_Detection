import xml.etree.ElementTree as ET
import cv2
import matplotlib.pyplot as plt
#

def load_annotations(xml_path):
    """
    Загрузка аннотаций из XML-файла.
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()
    annotations = []

    for obj in root.findall('object'):
        name = obj.find('name').text
        bndbox = obj.find('bndbox')
        xmin = int(bndbox.find('xmin').text)
        ymin = int(bndbox.find('ymin').text)
        xmax = int(bndbox.find('xmax').text)
        ymax = int(bndbox.find('ymax').text)

        annotations.append({'name': name, 'bbox': (xmin, ymin, xmax, ymax)})

    return annotations


def visualize_annotations(image_path, annotations):
    """
    Визуализация аннотаций поверх изображения.
    """
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    for ann in annotations:
        name = ann['name']
        xmin, ymin, xmax, ymax = ann['bbox']
        cv2.rectangle(image, (xmin, ymin), (xmax, ymax), (255, 0, 0), 2)
        cv2.putText(image, name, (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    plt.figure(figsize=(10, 10))
    plt.imshow(image)
    plt.axis('off')
    plt.show()


def validate_annotations(image_path, xml_path):
    """
    Проверка аннотаций на соответствие изображению.
    """
    # Загрузка аннотаций
    annotations = load_annotations(xml_path)

    # Загрузка изображения
    image = cv2.imread(image_path)
    if image is None:
        print(f"Не удалось загрузить изображение: {image_path}")
        return

    # Проверка координат аннотаций
    image_height, image_width = image.shape[:2]
    valid = True

    for ann in annotations:
        xmin, ymin, xmax, ymax = ann['bbox']
        if xmin < 0 or ymin < 0 or xmax > image_width or ymax > image_height:
            print(f"Аннотация выходит за пределы изображения: {ann}")
            valid = False

    if valid:
        print("Все аннотации корректны.")
    else:
        print("Некоторые аннотации содержат ошибки.")

    # Визуализация аннотаций
    visualize_annotations(image_path, annotations)


if __name__ == "__main__":
    # Путь к изображению и XML-файлу
    image_path = r"C:\Users\Matvej\Desktop\Programm\Python\AI_Project_2\Unified_Dataset\defected\gerber\li-ion_charger-B_Mask_defected_6.png"
    xml_path = r"C:\Users\Matvej\Desktop\Programm\Python\AI_Project_2\Unified_Dataset\annotations\gerber_defected\li-ion_charger-B_Mask_defected_6.xml"

    validate_annotations(image_path, xml_path)