## pandas EDA

Big Data? Machine Learning?

You work with your data -<br>
Manipulating it, merging, pivot and more.

But what happened in between? Did you get a lot of nans? Maybe duplicated values?<br>
You constantly need to check your data status, <br>
But you cannot do values_counts, isna and all those stuffs every second...

pandas_eda will show you status and frequent values for each column!<br>
You will be focused on what you have on the spot.

Demo is the best way to understand:<br>
[![demo](https://github.com/lisrael1/pandas_eda/blob/master/front.jpg)](https://youtu.be/kHT6MshXb04)

install:

```shell
pip install pandas_eda
```

usage:
```python
import pandas as pd
import pandas_eda
from time import sleep


df = pd.read_excel('whatever.xlsx')

df = manipulation_1(df)
df.eda()  # can use this at debug mode too!

df = manipulation_2(df)
df.eda()  # yes, you can open multiple EDA windows!

df = manipulation_3(df)
df.eda()

sleep(600)  # just that ending script will end the eda too, so delaying the exit

```

note:

if you're running on remote machine, the eda will be opened on the remote...