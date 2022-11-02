from time import sleep
import pandas_eda


df = pandas_eda._testing.generate_fake_table(600)
df.eda()
sleep(600)
