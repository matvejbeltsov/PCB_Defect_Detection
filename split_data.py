import os
import shutil
from sklearn.model_selection import train_test_split
#
# Пути к изображениям и меткам
photos_images_path = r"C:\Users\Matvej\Desktop\Programm\Python\AI_Project_2\Unified_Dataset\defected\photos"
gerber_images_path = r"C:\Users\Matvej\Desktop\Programm\Python\AI_Project_2\Unified_Dataset\defected\gerber"
labels_path = r"C:\Users\Matvej\Desktop\Programm\Python\AI_Project_2\Unified_Dataset\yolo_labels"
output_path = r"C:\Users\Matvej\Desktop\Programm\Python\AI_Project_2\dataset"

# Проверяем и создаем структуру выходных директорий
for split in ["train", "val", "test"]:
    for subfolder in ["images", "labels"]:
        os.makedirs(os.path.join(output_path, split, subfolder), exist_ok=True)

# Функция для сбора изображений из указанного пути
def collect_images_from_path(images_path):
    image_files = []
    for root, _, files in os.walk(images_path):
        for file in files:
            if file.endswith(".png") or file.endswith(".jpg"):
                image_files.append(os.path.join(root, file))
    return image_files

# Собираем изображения из обоих путей
photos_image_files = collect_images_from_path(photos_images_path)
gerber_image_files = collect_images_from_path(gerber_images_path)

# Объединяем все изображения
all_image_files = photos_image_files + gerber_image_files

# Проверка соответствующих меток
valid_images = []
valid_labels = []

for image_file in all_image_files:
    image_name = os.path.basename(image_file)
    label_file = os.path.join(labels_path, image_name.replace(".png", ".txt").replace(".jpg", ".txt"))

    if os.path.exists(label_file):
        valid_images.append(image_file)
        valid_labels.append(label_file)
    else:
        print(f"Метка отсутствует для изображения: {image_file}")

# Разделение на train, val, test
train_imgs, test_imgs, train_labels, test_labels = train_test_split(
    valid_images, valid_labels, test_size=0.2, random_state=42
)
train_imgs, val_imgs, train_labels, val_labels = train_test_split(
    train_imgs, train_labels, test_size=0.25, random_state=42  # 0.25 x 0.8 = 0.2
)

# Функция для копирования файлов
def copy_files(image_list, label_list, split):
    for img, lbl in zip(image_list, label_list):
        # Копируем изображения
        shutil.copy(img, os.path.join(output_path, split, "images", os.path.basename(img)))
        # Копируем метки
        shutil.copy(lbl, os.path.join(output_path, split, "labels", os.path.basename(lbl)))

# Копирование файлов в соответствующие папки
copy_files(train_imgs, train_labels, "train")
copy_files(val_imgs, val_labels, "val")
copy_files(test_imgs, test_labels, "test")

print(f"Разделение завершено.")
print(f"Тренировочный набор: {len(train_imgs)} изображений")
print(f"Валидационный набор: {len(val_imgs)} изображений")
print(f"Тестовый набор: {len(test_imgs)} изображений")