from time import sleep
import pandas_eda


df = pandas_eda._testing.generate_fake_table(6_000)
print(df.head(10))
df.eda()
sleep(600)
