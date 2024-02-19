import pandas as pd
import numpy as np
from faker import Faker
from tqdm import tqdm


def _random_birth_timestamp(min_age, max_age):
    current_timestamp = pd.Timestamp.now(tz='UTC')
    min_birth_timestamp = current_timestamp - pd.DateOffset(years=max_age)
    max_birth_timestamp = current_timestamp - pd.DateOffset(years=min_age)
    random_timestamp = pd.to_datetime(np.random.uniform(min_birth_timestamp.value, max_birth_timestamp.value))
    random_date = random_timestamp.date()  # Convert timestamp to date
    return random_date


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
    df['birth_date'] = df.apply(lambda row: _random_birth_timestamp(age_min, age_max), axis=1)
    df['age'] = (pd.to_datetime('today').date() - df.birth_date) \
        .apply(lambda x: x.total_seconds()).div(60 * 60 * 24 * 365).astype(int)
    df.birth_date = pd.to_datetime(df.birth_date)
    while True:
        index = df.age.isin([age_min, age_max])
        if not index.sum():
            break
        df.loc[index, 'age'] = np.clip(np.random.normal(50, 20, index.sum()), age_min, age_max)

    # dummy value
    df['agree'] = np.random.choice([True, False], samples)

    return df
