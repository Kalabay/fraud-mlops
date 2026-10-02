import os
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
os.chdir(root / 'fraud_detector')
sys.path.insert(0, str(Path.cwd() / 'src'))

import pandas as pd
from preprocessing import load_train_data, run_preproc
from scorer import make_pred

if not Path('train_data/train.csv').exists() or not (root / 'data/test.csv').exists():
    raise SystemExit('check csv files: fraud_detector/train_data/train.csv and data/test.csv')

print('loading data...', flush=True)
train = load_train_data()
data = pd.read_csv(root / 'data/test.csv', nrows=10)
result = make_pred(run_preproc(train, data))
assert len(result) == len(data)
assert result['score'].between(0, 1).all()
assert result['fraud_flag'].isin([0, 1]).all()
print(result)
print('model check ok')
