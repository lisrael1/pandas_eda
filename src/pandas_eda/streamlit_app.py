r"""
to run this

import sys
from streamlit import cli as stcli
import pandas as pd

df = pd.read_excel(r"C:\Users\israelil\Downloads\tmp\a.xlsx", index_col=None)
output = df.to_string(index=False)

sys.argv = ["streamlit", "run",
            read_db.eda.__file__,
            "--",
            # r"C:\Users\israelil\Downloads\tmp\local_data\reshaped_data\hcp\doctor_summary.csv",
            # r"C:\Users\israelil\Downloads\tmp\a.xlsx",
            output,
            ]

# https://stackoverflow.com/questions/62760929/how-can-i-run-a-streamlit-app-from-within-a-python-script
if 1:
    # without thread, but it will take over your debug session, and you will not be able to use the terminal.
    # it will read sys.argv
    sys.exit(stcli.main())
    # or just:
    stcli.main()

if 0:
    # ValueError: signal only works in main thread
    from threading import Thread
    thread = Thread(target=stcli.main, args=[])
    thread.start()

if 0:
    # _pickle.PicklingError: Can't pickle <function main at 0x0000014818610280>:
    # it's not the same object as streamlit.cli.main
    import multiprocessing
    thread = multiprocessing.Process(target=stcli.main, args=[])
    thread.start()

if 1:
    # can run, and you will have the prompt at the terminal,
    # but here specifically, it cannot use "output" as it's too long
    # FileNotFoundError: [WinError 206] The filename or extension is too long
    import subprocess
    process = subprocess.Popen(sys.argv)

"""
import io
import os
import sys
import streamlit as st
import pandas as pd
import pandas_eda
from streamlit import cli as stcli


def main():
    st.set_page_config(layout="wide")

    if sys.argv[1].endswith('.xlsx'):
        df = pd.read_excel(sys.argv[1], index_col=None)
    elif sys.argv[1].endswith('.csv'):
        df = pd.read_csv(sys.argv[1], index_col=None)
    # os.remove(sys.argv[1])
    # else:
    #     try:
    #         df = pd.read_excel(sys.argv[1], index_col=None)
    #     except:
    #         df = pd.read_csv(io.StringIO(sys.argv[1]), index_col=None, sep=r'\s+')

    query = st.sidebar.text_area('query')
    if len(query):
        df = df.query(query)

    # EDA
    eda = pandas_eda.explore.ExploreTable(df)
    st.info('data')
    st.write(df)
    st.info('columns statistics')
    st.write(eda.get_columns_statistics())
    freq = eda.get_frequent_values_long().reset_index()
    for col in freq.col.unique():
        st.sidebar.info(col)
        st.sidebar.write(freq.query('col==@col')[['nans', 'entropy_inx']].iloc[0].rename('bar'))
        st.sidebar.write(freq.query('col==@col').set_index('val').bar)


if __name__ == '__main__':
    # this code cannot really work as we dont have sys.argv[1] that contains the table to show...
    if st._is_running_with_streamlit:
        main()
    else:
        sys.argv = ["streamlit", "run", sys.argv[0]]
        sys.exit(stcli.main())
