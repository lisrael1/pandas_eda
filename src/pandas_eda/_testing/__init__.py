import pandas as pd
import numpy as np
from faker import Faker
from tqdm import tqdm


def generate_fake_table(samples=500):
    fake = Faker()
    df = pd.DataFrame()
    df['firstname'] = [fake.first_name_nonbinary() for _ in tqdm(range(samples), desc='generating fake names')]
    df['phone'] = [fake.phone_number() for _ in tqdm(range(samples), desc='generating phone numbers')]

    # random country
    countries = [fake.country() for _ in range(3)] + [None]
    df['country'] = np.random.choice(countries, samples, p=[0.1, 0.1, 0.3, 0.5])
    # df.country = df.country.astype("category")

    # random age
    age_min, age_max = 10, 90
    df['age'] = np.clip(np.random.normal(50, 20, samples), age_min, age_max)
    while True:
        index = df.age.isin([age_min, age_max])
        if not index.sum():
            break
        df.loc[index, 'age'] = np.clip(np.random.normal(50, 20, index.sum()), age_min, age_max)

    # dummy value
    df['agree'] = np.random.choice([True, False], samples)
    col = df.columns.tolist()
    col[-2] = 'agree'
    df.columns = col

    return df
