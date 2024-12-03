from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import uvicorn
import os
import zipfile
import cv2
import torch
from ultralytics import YOLO
from pathlib import Path
from gerber_convert_to_png import convert_gerber_to_png
#
# Инициализация FastAPI
app = FastAPI()

# Добавление CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Устройство для вычислений
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Загрузка модели YOLOv8
model_path = r"C:\Users\Matvej\Desktop\Programm\Python\AI_Project_2\PCB_Defect_Detection\yolov8l_training\weights\best.pt"
try:
    model = YOLO(model_path)
    model.to(DEVICE)
except Exception as e:
    raise RuntimeError(f"Ошибка загрузки модели YOLOv8: {e}")

# Эндпоинт проверки сервера
@app.get("/")
async def root():
    return {"message": "Сервер работает. Используйте /upload/ для загрузки файлов."}


# Эндпоинт для загрузки и обработки изображений
@app.post("/upload/")
async def upload_files(gerber: UploadFile = File(...), photo: UploadFile = File(...)):
    try:
        # Сохранение загруженных файлов
        gerber_path = f"temp_{gerber.filename}"
        photo_path = f"temp_{photo.filename}"

        with open(gerber_path, "wb") as f:
            f.write(await gerber.read())
        with open(photo_path, "wb") as f:
            f.write(await photo.read())

        # Проверяем, является ли Gerber архивом
        gerber_images = []
        if gerber.filename.endswith(".zip"):
            with zipfile.ZipFile(gerber_path, "r") as zip_ref:
                zip_ref.extractall("temp_gerber_files")

            # Преобразование всех Gerber файлов в PNG
            gerber_folder = "temp_gerber_files"
            for gerber_file in Path(gerber_folder).glob("*"):
                if gerber_file.suffix in [".gbr", ".drd"]:  # Расширения Gerber файлов
                    png_path = convert_gerber_to_png(str(gerber_file))
                    gerber_images.append(png_path)
        else:
            # Если не архив, предполагаем, что это PNG
            gerber_images.append(gerber_path)

        # Обработка фото платы
        photo_results = model.predict(source=photo_path, device=DEVICE)
        photo_boxes = photo_results[0].boxes.xyxy.cpu().numpy()
        photo_image = cv2.imread(photo_path)

        # Вычисление различий для каждого Gerber файла
        for gerber_image_path in gerber_images:
            gerber_results = model.predict(source=gerber_image_path, device=DEVICE)
            gerber_boxes = gerber_results[0].boxes.xyxy.cpu().numpy()
            gerber_image = cv2.imread(gerber_image_path)

            # Сравнение рамок Gerber и фото платы
            differences = []
            for g_box in gerber_boxes:
                match_found = False
                for p_box in photo_boxes:
                    iou = calculate_iou(g_box, p_box)
                    if iou > 0.5:  # Порог IoU для совпадений
                        match_found = True
                        break
                if not match_found:
                    differences.append(g_box)

            # Отрисовка рамок дефектов на изображении платы
            for diff in differences:
                x1, y1, x2, y2 = map(int, diff[:4])
                cv2.rectangle(photo_image, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.putText(photo_image, "Defect", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

            # Сравнение Gerber с фото платы
            for box in photo_boxes:
                x1, y1, x2, y2 = map(int, box[:4])
                cv2.rectangle(photo_image, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Сохранение итогового изображения
        diff_image_path = "output_diff.png"
        cv2.imwrite(diff_image_path, photo_image)

        return JSONResponse({"message": "Обработка завершена", "diff_image": "/diff/"})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка обработки: {e}")


# Эндпоинт для получения изображения с различиями
@app.get("/diff/")
async def get_diff_image():
    diff_image_path = "output_diff.png"
    if os.path.exists(diff_image_path):
        return FileResponse(diff_image_path, media_type="image/png", filename="output_diff.png")
    return JSONResponse({"error": "Файл не найден или отсутствуют различия"}, status_code=404)


# Функция вычисления IoU (Intersection over Union)
def calculate_iou(box1, box2):
    x1, y1, x2, y2 = box1[:4]
    x1_p, y1_p, x2_p, y2_p = box2[:4]

    inter_x1 = max(x1, x1_p)
    inter_y1 = max(y1, y1_p)
    inter_x2 = min(x2, x2_p)
    inter_y2 = min(y2, y2_p)

    inter_area = max(0, inter_x2 - inter_x1 + 1) * max(0, inter_y2 - inter_y1 + 1)
    box1_area = (x2 - x1 + 1) * (y2 - y1 + 1)
    box2_area = (x2_p - x1_p + 1) * (y2_p - y1_p + 1)

    union_area = box1_area + box2_area - inter_area
    iou = inter_area / union_area if union_area > 0 else 0

    return iou


# Запуск сервера
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)