from time import sleep

import pandas as pd
import numpy as np
import pandas_eda
from faker import Faker


def generate_fake_table():
    samples = 500
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
df.eda()
sleep(600)
