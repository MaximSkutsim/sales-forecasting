from typing import Dict

def get_config() -> Dict:
    """
    Возвращает конфигурацию для модели прогнозирования продаж.
    
    Returns:
        Dict: Словарь с параметрами конфигурации
    """
    config = {
        # Количество дней для тестового периода
        'test_days': 30,
        
        # Признаки для модели
        'features': {
            # Формат: 'название_признака': ('колонка', период_дней, 'метрика', квантиль)
            'qty_7d_avg': ('qty', 7, 'avg', None),
            'qty_7d_q10': ('qty', 7, 'quantile', 10),
            'qty_7d_q50': ('qty', 7, 'quantile', 50),
            'qty_7d_q90': ('qty', 7, 'quantile', 90),
            'qty_14d_avg': ('qty', 14, 'avg', None),
            'qty_14d_q10': ('qty', 14, 'quantile', 10),
            'qty_14d_q50': ('qty', 14, 'quantile', 50),
            'qty_14d_q90': ('qty', 14, 'quantile', 90),
            'qty_21d_avg': ('qty', 21, 'avg', None),
            'qty_21d_q10': ('qty', 21, 'quantile', 10),
            'qty_21d_q50': ('qty', 21, 'quantile', 50),
            'qty_21d_q90': ('qty', 21, 'quantile', 90),
        },
        
        # Целевые переменные для прогнозирования
        'targets': {
            # Формат: 'название_цели': ('колонка', горизонт_прогноза)
            'next_7d': ('qty', 7),
            'next_14d': ('qty', 14),
            'next_21d': ('qty', 21),
        },
        
        # Квантили для прогнозирования
        'quantiles': [0.1, 0.5, 0.9],
        
        # Горизонты прогнозирования (в днях)
        'horizons': [7, 14, 21],
        
        # Параметры модели
        'model_params': {
            'random_state': 42,
            'verbose': True,
        },
        
        # Параметры обучения
        'training_params': {
            'early_stopping_rounds': 50,
            'eval_metric': 'quantile',
        }
    }
    
    return config

