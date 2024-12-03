from ultralytics import YOLO

def main():
    # Путь к конфигурации набора данных
    DATASET_PATH = r"C:\Users\Matvej\Desktop\Programm\Python\AI_Project_2\dataset_config.yaml"
#
    model = YOLO("yolov8l.pt")

    # Обучение модели
    model.train(
        data=DATASET_PATH,
        epochs=200,
        batch=8,
        imgsz=640,
        workers=4,
        project="PCB_Defect_Detection",
        name="yolov8l_training",
        device=0,
        optimizer="AdamW",
        patience=20,
        save_period=10,
        val=True,
    )

if __name__ == "__main__":
    main()