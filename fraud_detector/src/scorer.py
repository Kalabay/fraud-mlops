import pandas as pd
import logging
from catboost import CatBoostClassifier

# Настройка логгера
logger = logging.getLogger(__name__)

logger.info('Importing pretrained model...')

# Import model
model = CatBoostClassifier()
model.load_model('./models/my_catboost.cbm')

# Define optimal threshold
model_th = 0.98
logger.info('Pretrained model imported successfully...')


def make_pred(dt, source_info="kafka"):

    dt = dt.copy()

    # Меняем формат категориальных фичей на string перед скорингом
    expected_categorical = ['hour',
                            'year',
                            'month',
                            'day_of_month',
                            'day_of_week',
                            'gender_cat',
                            'merch_cat',
                            'cat_id_cat',
                            'one_city_cat',
                            'us_state_cat',
                            'jobs_cat']
    for col in expected_categorical:
        if col in dt.columns:
            dt[col] = dt[col].astype(str)

    # Calculate score
    scores = model.predict_proba(dt, thread_count=2)[:, 1]
    submission = pd.DataFrame({
        'score':  scores,
        'fraud_flag': (scores > model_th) * 1
    })
    logger.info(f'Prediction complete for data from {source_info}')

    # Return proba for positive class
    return submission