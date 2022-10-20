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
import sys
import os
import subprocess
from io import BytesIO
import streamlit as st
import pandas as pd
# from terminal, popen has different paths, so adding the package path manually
sys.path.append(os.path.dirname(__file__)+'/../')
import pandas_eda


def download(df, excel_name):
    st.write(df)

    output = BytesIO()
    df.to_excel(output, index=False, sheet_name='Sheet1')
    st.download_button(label=f'📥 Download {excel_name}',
                       data=output.getvalue(), file_name=f'{excel_name}.xlsx')


def main():
    st.set_page_config(layout="wide")
    tab_statistics, tab_data, tab_help = st.tabs(['statistics', 'data', 'help'])

    with tab_help:
        st.code('examples for query at the side bar:\n\t60 > age > 32 and firstname.str.lower().str.startswith("a")')
        st.code('tables:\n\tclick column name to sort table by that column')
    df = pd.read_excel(sys.argv[1], index_col=None)

    query = st.sidebar.text_area('query by table content')
    if len(query):
        df = df.query(query)

    # EDA
    eda = pandas_eda.explore.ExploreTable(df)

    with tab_data:
        download(df, 'data')

    with tab_statistics:
        st.subheader('columns statistics:')
        download(eda.get_columns_statistics().reset_index(), 'statistics')

    st.sidebar.header('frequent values per column:')
    freq = eda.get_frequent_values()
    for col in freq.col.unique():
        st.sidebar.info(col)
        show = freq.query(f'col=="{col}"').set_index('value').bar
        show.name = 'percentages'
        show.index = show.index.astype(str)
        st.sidebar.write(show)


if __name__ == '__main__':
    if st._is_running_with_streamlit:
        # this code cannot really work as we dont have sys.argv[1] that contains the table to show...
        main()
    else:
        argv = ["streamlit", "run", sys.argv[0]]
        subprocess.run([f"{sys.executable}", "-m"]+argv)
