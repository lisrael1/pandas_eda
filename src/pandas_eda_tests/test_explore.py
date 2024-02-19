import pandas as pd
import numpy as np
import pandas_eda
from faker import Faker
import unittest


class TestExploreTable(unittest.TestCase):
    def test_nans(self):
        def generate_fake_table():
            samples = 1000
            fake = Faker()
            df = pd.DataFrame()
            countries = [fake.country() for _ in range(3)] + [None]
            df['country'] = np.random.choice(countries, samples, p=[0.1, 0.1, 0.3, 0.5])
            return df

        df = generate_fake_table()
        eda = pandas_eda.explore.ExploreTable(df)
        self.assertTrue(55 > eda.get_columns_statistics().nan_perc[0] > 45, 'error with nan detection')

    def test_uniques(self):
        def generate_fake_table(samples):
            df = pd.DataFrame()
            df['uniq'] = range(samples)
            return df

        tests = 10
        for samples in np.random.randint(1, 100, tests).tolist() + [1]:
            df = generate_fake_table(samples)
            eda = pandas_eda.explore.ExploreTable(df)
            self.assertTrue(eda.get_columns_statistics().uniques[0] == samples, 'error with nan detection')

    def test_empty_table(self):
        df = pd.DataFrame()
        eda = pandas_eda.explore.ExploreTable(df)
        df = pd.DataFrame(columns=list('abc'))
        eda = pandas_eda.explore.ExploreTable(df)
        df = pd.DataFrame(index=list('abc'))
        eda = pandas_eda.explore.ExploreTable(df)

    def test_columns_with_bad_names(self):
        df = pd.DataFrame(columns=[1, None, 'hi', 'hi', '!~()'])
        eda = pandas_eda.explore.ExploreTable(df)
