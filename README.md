## pandas EDA

Big Data? Machine Learning?

You work with your data -  
Manipulating it, merging, pivot and more.

But what happened in between? Did you get a lot of nans? Maybe duplicated values?  
You constantly need to check your data status,  
But you cannot do values_counts, isna and all those stuffs every second...

**pandas_eda** is an **Exploratory Data Analysis** tool that will show you status and frequent values for each column!  
You will be focused on what you have on the spot.

**Demo** is the best way to understand:  
[![demo](https://github.com/lisrael1/pandas_eda/blob/master/front.jpg?raw=True)](https://youtu.be/kHT6MshXb04)

**install:**

```shell
pip install pandas_eda
```

**usage:**
```python
import pandas as pd
import pandas_eda
from time import sleep


# dummy data
df = pd._testing.makeMixedDataFrame()
# or load your data with pd.read_excel('whatever.xlsx')


# show original data. will pop up a web application
df.eda()  # can use this at debug mode too!


# manipulation #1
df.A += 10
df.eda()  # yes, you can open multiple EDA windows!


# manipulation #2
df.loc[df.B==1, 'A'] -= 30
df.eda()


# no need at jupyter or debug mode...
# just that ending script will end the eda too, so delaying the exit. 
sleep(600)  
```

**cli mode**
```python
# disabling the wrapping of a long table at the print...
pd.options.display.expand_frame_repr = False
pd.options.display.max_columns = 0
pd.options.display.min_rows = 20


eda = pandas_eda.explore.ExploreTable(df)

print('\n\n *** column statistics *** ')
print(eda.get_columns_statistics())
print('\n\n *** frequent values, long format *** ')
print(eda.get_frequent_values_long())
print('\n\n *** frequent values, wide format *** ')
print(eda.get_frequent_values_wide())
```

**note:**  
If you're running on remote machine, the eda will be opened on the remote...

**alternatives:**  
After starting this tool I've found 2 cool alternatives:
* [sweetviz](https://pypi.org/project/sweetviz)
    <ul>Has a nice interactive report.</ul>
* [mito](https://www.trymito.io/) 
    <ul>Great for new table that needs also cleaning.<br>
    Works only at jupyter.</ul> 