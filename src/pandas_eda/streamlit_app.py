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
sys.path.append(os.path.dirname(__file__) + '/../')
import pandas_eda


def download(df, output_name):
    st.write(df)

    size_mb = df.memory_usage(deep=True).sum() / 1024 ** 2
    output = BytesIO()
    if size_mb < 10:
        print('dumping into excel format')
        df.to_excel(output, index=False, sheet_name='Sheet1')
        st.download_button(label=f'📥 Download {output_name}',
                           data=output.getvalue(), file_name=f'{output_name}.xlsx')
    else:
        print('dumping into csv format')
        df.to_csv(output, index=False)
        st.download_button(label=f'📥 Download {output_name}',
                           data=output.getvalue(), file_name=f'{output_name}.csv')


def main():
    st.set_page_config(layout="wide")
    tab_statistics, tab_frequent_values, tab_data, tab_help = st.tabs(['statistics', 'frequent values', 'data', 'help'])

    with tab_help:
        st.code('examples for query at the side bar:\n\t60 > age > 32 and firstname.str.lower().str.startswith("a")')
        st.code('tables:\n\tclick column name to sort table by that column')
    df = pd.read_pickle(sys.argv[1])
    print('done reading table')

    query = st.sidebar.text_area('query by table content')
    if len(query):
        df = df.query(query)

    # EDA
    eda = pandas_eda.explore.ExploreTable(df)
    columns_statistics = eda.get_columns_statistics().reset_index()
    small_table_to_show = df.copy()
    # now trying to avoid this error:
    # MessageSizeError: Data of size 234.2 MB exceeds the message size limit of 200.0 MB.
    while True:
        mem_size = small_table_to_show.memory_usage(deep=True).div(1024 ** 2).sum()
        if mem_size < 200:
            break
        rows = int(small_table_to_show.shape[0] * 200 / mem_size) - 1
        rows = pd.Series(small_table_to_show.index).sample(rows).sort_index()
        small_table_to_show = small_table_to_show.iloc[rows]
    print('done analyzing data')

    with tab_data:
        if small_table_to_show.shape != df.shape:
            st.warning(f'table is too big! showing only {small_table_to_show.shape[0]:,} rows out of {df.shape[0]:,}')
        download(small_table_to_show, 'data')

    with tab_statistics:
        st.subheader('columns statistics:')
        download(columns_statistics, 'statistics')

        mem_size = df.memory_usage(deep=True).div(1024 ** 2).rename('MB')
        st.info(f'total table size is: {mem_size.sum():.3f} MB')
        st.subheader('size of each column')
        st.columns(4)[0].table(mem_size.to_frame().style.bar(color='#ead9ff').format('{:.3f}'))

    with tab_frequent_values:
        st.subheader('frequent values:')
        frequent = eda.get_frequent_values()
        frequent.value = frequent.value.astype(str)  # streamlit issue
        download(frequent, 'frequent_values')

    st.sidebar.header('frequent values per column:')
    st.sidebar.code(f'table contains {df.shape[0]:,} rows')
    freq = eda.get_frequent_values()
    for col in freq.col.unique():
        single_col_statistics = columns_statistics.astype(dict(col=str))
        single_col_statistics = single_col_statistics.query(f'col=="{col}"').iloc[0]

        st.sidebar.info(f'{col} [{single_col_statistics.uniques:,} uniques, {single_col_statistics.nans:,} nans]')
        show = freq.query(f'col=="{col}"').set_index('value')
        for index, row in show.iterrows():
            st.sidebar.write(f'{index}: [#{row.counts:,}]')
            st.sidebar.progress(row.percentages)


if __name__ == '__main__':
    if st._is_running_with_streamlit:
        # this code cannot really work as we dont have sys.argv[1] that contains the table to show...
        main()
    else:
        argv = ["streamlit", "run", sys.argv[0]]
        subprocess.run([f"{sys.executable}", "-m"] + argv)
