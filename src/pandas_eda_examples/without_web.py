import pandas as pd
import pandas_eda

pd.options.display.expand_frame_repr = False
pd.options.display.max_colwidth = 40
pd.options.display.max_columns = 0
pd.options.display.max_rows = 100
pd.options.display.min_rows = 20
display = print

df = pandas_eda._testing.generate_fake_table()
eda = df.eda(True)

print('\n\n *** column statistics *** ')
display(eda.get_columns_statistics())
print('\n\n *** frequent values *** ')
display(eda.get_frequent_values())
