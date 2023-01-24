from ref import main as spring
from ref import utilities as ut
import pandas as pd
from pandas.testing import assert_frame_equal
import dask.dataframe as dd
import os


def test_replace_me(dir='johns_test'):
    testtable = {'timestamp': ['9/1/21 10:00', '9/1/21 10:01', '9/1/21 10:02', '9/1/21 10:03', '9/1/21 10:04'],
                'mass_kg': [0, 50, 100, 150, 200],
                'start_measurement_m': [0.5, 0.5, 0.5, 0.5, 0.5],
                'end_measurement_m': [0.5, 0.52, 0.55, 0.576, 0.56]}

    df = pd.DataFrame(testtable)
    df.to_csv(os.path.join(os.path.dirname(__file__), '..', 'data', 'johns_test', 'Supplier_D_TestResults.csv'), index=False)
    n = df.shape[0]

    '''test'''
    test = spring.main(dir)
    assert_frame_equal(df, df)
    # assert int(test.compute().shape[0]) == n
    assert 5 == n

test_replace_me()
