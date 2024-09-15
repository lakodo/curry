import pandas as pd
from faker import Faker


# 1. Generate a fake dataset using pandas
def generate_fake_data(num_rows: int = 1000) -> pd.DataFrame:
    fake = Faker()
    data = []
    for _ in range(num_rows):
        date = fake.date_between(start_date="-50y", end_date="today")
        author = fake.name()
        tags = ", ".join(fake.words(nb=3))
        sentence = fake.sentence(nb_words=10)
        data.append({"date": date, "author": author, "tags": tags, "sentence": sentence})
    df = pd.DataFrame(data)
    return df
