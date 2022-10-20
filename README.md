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
# or your data...
# df = pd.read_excel('whatever.xlsx')

# show original data
df.eda()  # can use this at debug mode too!

# manipulation #1
df.A += 10
df.eda()  # yes, you can open multiple EDA windows!

# manipulation #2
df.loc[df.B==1, 'A'] -= 30
df.eda()

sleep(600)  # just that ending script will end the eda too, so delaying the exit. no need at jupyter
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