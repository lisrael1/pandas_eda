import pandas as pd
import numpy as np
import pandas_eda
from faker import Faker

pd.options.display.expand_frame_repr = False
pd.options.display.max_colwidth = 40
pd.options.display.max_columns = 0
pd.options.display.max_rows = 100
pd.options.display.min_rows = 20


def generate_fake_table(samples=500):
    fake = Faker()
    df = pd.DataFrame()
    df['firstname'] = [fake.first_name_nonbinary() for _ in range(samples)]
    df['phone'] = [fake.phone_number() for _ in range(samples)]
    countries = [fake.country() for _ in range(3)] + [None]
    df['country'] = np.random.choice(countries, samples, p=[0.1, 0.1, 0.3, 0.5])
    df['age'] = np.random.randint(30, 60, samples)
    df['agree'] = np.random.choice([True, False], samples)
    return df


df = generate_fake_table()
eda = pandas_eda.explore.ExploreTable(df)

print('\n\n *** column statistics *** ')
print(eda.get_columns_statistics())
print('\n\n *** frequent values *** ')
print(eda.get_frequent_values())
