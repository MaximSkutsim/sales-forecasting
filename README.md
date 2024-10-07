# Система управления запасами

Система машинного обучения для прогнозирования спроса и управления запасами. Система предоставляет квантильные прогнозы будущего спроса, помогая оптимизировать уровни запасов и снизить как дефицит, так и избыток товаров.

## Основные возможности

### Анализ и прогнозирование
* Квантильная регрессия для прогнозирования спроса
* Множественные горизонты прогнозирования (7, 14, 21, 28 дней)
* Различные уровни доверительных интервалов (5%, 10%, 25%, 50%, 75%, 90%, 95%)
* Автоматизированная генерация признаков с гибкой конфигурацией
* Расчёт ключевых метрик эффективности (KPI) для оценки качества прогнозов

### Метрики и аналитика
* Расчет GMV (Gross Merchandise Value)
* Анализ валовой маржи и процента маржинальности
* Оценка GMROI (Gross Margin Return on Investment)
* Расчет оборачиваемости запасов и периода оборота
* Мониторинг среднего уровня запасов

### Оптимизация запасов
* Линейное программирование для оптимального распределения бюджета
* Учет рисков out-of-stock при планировании закупок
* Оптимизация по прибыли или выручке
* Анализ storage score для оптимизации складских запасов
* Рекомендации по объемам пополнения для каждого SKU

### ML Pipeline
* Интеграция с ClearML для оркестрации ML пайплайнов
* Автоматическая валидация качества моделей
* Раздельные пайплайны для обучения и инференса
* Кэширование промежуточных результатов для ускорения разработки
* Мониторинг метрик качества модели

## API Сервис

FastAPI веб-сервис предоставляет следующие эндпоинты:
* `/api/predictions/upload` - Загрузка новых прогнозов в систему
* `/api/how_much_to_order` - Рекомендации по объему заказа для конкретного SKU
* `/api/stock_level_forecast` - Прогноз уровня запасов с учетом текущего стока
* `/api/low_stock_sku_list` - Выявление SKU с риском дефицита

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/MaximSkutsim/sales-forecasting.git
cd stock-management-system
```

2. Создайте виртуальное окружение и активируйте его:
```bash
python -m venv venv
source venv/bin/activate  # Для Linux/MacOS
# или
venv\Scripts\activate     # Для Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

## Использование

### Обучение модели
```bash
python training.py --orders_url <url> --model_path model.pkl
```

Параметры:
* `orders_url`: URL с данными о заказах на Яндекс.Диске
* `model_path`: Путь для сохранения обученной модели
* `test_days`: Количество дней для тестового периода (по умолчанию 30)
* `debug`: Флаг для запуска в режиме отладки

### Получение прогнозов
```bash
python inference.py --orders_url <url> --model_path model.pkl
```

### Запуск веб-сервиса
```bash
python app.py
```
API будет доступен по адресу: http://localhost:5000

## Технологии
*![Python 3.8+](https://img.shields.io/badge/Python%203.8%2B-090909?style=flat-square&logo=python)
*![FastAPI](https://img.shields.io/badge/FastAPI-090909?style=flat-square&logo=fastapi) 

![pandas](https://img.shields.io/badge/pandas-090909?style=flat-square&logo=pandas)

![numpy](https://img.shields.io/badge/numpy-090909?style=flat-square&logo=numpy)

![scikit-learn](https://img.shields.io/badge/scikit--learn-090909?style=flat-square&logo=scikit-learn)

![ClearML](https://img.shields.io/badge/ClearML-090909?style=flat-square&logo=clearml) 

![PuLP](https://img.shields.io/badge/PuLP-090909?style=flat-square)

![uvicorn](https://img.shields.io/badge/uvicorn-090909?style=flat-square)


## Лицензия
MIT
