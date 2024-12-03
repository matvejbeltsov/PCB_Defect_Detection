import os
import zipfile
import subprocess
import shutil


def extract_zip(zip_path, extract_to):
    """
    Извлекает файлы из ZIP-архива.

    :param zip_path: Путь к ZIP-архиву.
    :param extract_to: Директория для извлечения файлов.
    """
    os.makedirs(extract_to, exist_ok=True)
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        print(f"Файлы успешно извлечены в: {extract_to}")
    except Exception as e:
        print(f"Ошибка при извлечении ZIP-архива: {e}")

#
def find_gerber_files(input_dir):
    """
    Рекурсивно ищет все Gerber-файлы в указанной директории и ее поддиректориях.

    :param input_dir: Директория для поиска файлов.
    :return: Список путей к Gerber-файлам.
    """
    gerber_files = []
    for root, _, files in os.walk(input_dir):
        for file_name in files:
            if file_name.lower().endswith(('.gbr', '.gtl', '.gbl', '.gto', '.gbo', '.gts', '.gbs', '.gko', '.drl')):
                gerber_files.append(os.path.join(root, file_name))
    return gerber_files


def convert_gerber_to_png(gerber_files, output_dir, gerbv_path, dpi=600):
    """
    Конвертирует все Gerber-файлы в PNG.

    :param gerber_files: Список путей к Gerber-файлам.
    :param output_dir: Директория для сохранения PNG-файлов.
    :param gerbv_path: Полный путь к исполняемому файлу gerbv.exe.
    :param dpi: Разрешение PNG (точек на дюйм).
    """
    os.makedirs(output_dir, exist_ok=True)
    png_files = []
    for input_path in gerber_files:
        output_path = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(input_path))[0]}.png")
        try:
            subprocess.run([
                gerbv_path,
                '-x', 'png',
                '-D', str(dpi),
                '-o', output_path,
                input_path
            ], check=True)
            png_files.append(output_path)
            print(f"Успешно конвертировано: {input_path} -> {output_path}")
        except subprocess.CalledProcessError as e:
            print(f"Ошибка при конвертации {input_path}: {e}")
    return png_files


def clean_up(directory):
    """
    Удаляет указанную директорию и ее содержимое.

    :param directory: Директория для удаления.
    """
    try:
        shutil.rmtree(directory)
        print(f"Временная папка удалена: {directory}")
    except Exception as e:
        print(f"Ошибка при удалении временной папки {directory}: {e}")


# Пример использования
if __name__ == "__main__":

    zip_path = "GERBERS_top_PCBWayCommunity.zip"
    extracted_dir = "extracted_gerber_files"  # Папка для извлечения файлов
    output_directory = "output_pngs"         # Папка для сохранения PNG

    # Путь к исполняемому файлу gerbv.exe
    gerbv_path = r"C:\Program Files\gerbv\gerbv.exe"


    extract_zip(zip_path, extracted_dir)


    gerber_files = find_gerber_files(extracted_dir)
    if not gerber_files:
        print("Не найдено подходящих Gerber-файлов для конвертации.")
    else:

        convert_gerber_to_png(
            gerber_files,
            output_directory,
            gerbv_path,
            dpi=600
        )

    clean_up(extracted_dir)