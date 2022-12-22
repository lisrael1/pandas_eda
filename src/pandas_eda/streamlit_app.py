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
import traceback
from io import BytesIO
import pkg_resources

import pandas as pd
import plotly.express as px

# from terminal, popen has different paths, so adding the package path manually
sys.path.append(os.path.dirname(__file__) + '/../')
import pandas_eda.explore

pd.options.plotting.backend = "plotly"


def download(df: pd.DataFrame, output_name: str):
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


def add_suffix_to_duplicated_columns(columns):
    """
        usage:
            df.columns = add_suffix_to_duplicated_columns(df.columns)
    :param columns:
    :return:
    """
    cols = columns.rename('col_name').to_frame().reset_index(drop=True)
    cols['suffix'] = cols.groupby('col_name').col_name.cumcount().astype(str).radd('_').replace('_0', '')
    return cols.sum(1)


class Main:
    def __init__(self):
        self.number_of_most_frequent_values = None
        self.df = None
        self.eda = None
        self.columns_statistics = None
        self.small_table_to_show = None
        self.mem_size = None
        self.plot_hist = None
        self.preserve_column_order_at_sidebar = None

        st.set_page_config(layout="wide")

        st.header('pandas eda')
        (
            self.tab_data,
            self.tab_statistics,
            self.tab_sizes,
            self.tab_frequent_values,
            self.tab_config,
            self.tab_help) = st.tabs(['data', 'statistics', 'table size', 'frequent values', 'config', 'help'])

        self.read_table()
        self.config()
        self.analyze()
        self.show_data()
        self.show_statistics()
        self.show_sizes()
        self.show_frequent_values_at_main()
        self.show_frequent_values_at_sidebar()
        self.help()

        print('done reading table')

    def read_table(self):
        self.df = pd.read_pickle(sys.argv[1])
        self.df.columns = self.df.columns.astype(str)  # in case one of the columns is integer
        self.df.columns = add_suffix_to_duplicated_columns(self.df.columns)

    def config(self):
        with self.tab_config:
            columns = st.columns(3)
            self.plot_hist = columns[0].checkbox('plot histogram at numeric columns')
            self.preserve_column_order_at_sidebar = columns[0].checkbox('preserve column order at sidebar')
            self.number_of_most_frequent_values = columns[0] \
                .slider('number of most frequent values to display', 2, 10, 6)
            columns_to_drop = columns[0].multiselect('select columns to ignore', self.df.columns.tolist())
            if len(columns_to_drop):
                self.df = self.df.drop(columns=columns_to_drop)

            columns = st.columns([2, 1])
            query = columns[0].text_area('filter content with pandas query')
            if len(query):
                try:
                    self.df = self.df.query(query)
                    if self.df.empty:
                        st.sidebar.error('filtering data, at config tab, left empty table!!')
                        st.stop()
                    st.sidebar.warning('showing filtered data by the query at the config tab!')
                except (pd.errors.UndefinedVariableError, ValueError, SyntaxError):
                    st.error('query has errors:')
                    st.code(traceback.format_exc())
                    st.stop()

    def help(self):
        with self.tab_help:
            st.code(
                'examples for query at the config tab:'
                '\n\t60 > age > 32 and firstname.str.lower().str.startswith("a")'
                '\nat the "table size" tab, the size will be after filleting.')
            st.code('tables:\n\tclick column name to sort table by that column.')
            st.code(f'table at this session is temporary saved at\n\t{sys.argv[1]}')

    def analyze(self):
        # EDA
        self.eda = pandas_eda.explore.ExploreTable(self.df,
                                                   number_of_most_frequent_values=self.number_of_most_frequent_values)
        self.columns_statistics = self.eda.get_columns_statistics().reset_index()
        self.small_table_to_show = self.df.copy()
        self.mem_size = self.df.memory_usage(deep=True).div(1024 ** 2).rename('MB')

        # now trying to avoid this error:
        # MessageSizeError: Data of size 234.2 MB exceeds the message size limit of 200.0 MB.
        while True:
            display_table_mem_size = self.small_table_to_show.memory_usage(deep=True).div(1024 ** 2).sum()
            if display_table_mem_size < 200:
                break
            rows = int(self.small_table_to_show.shape[0] * 200 / display_table_mem_size) - 1
            rows = pd.Series(self.small_table_to_show.index).sample(rows).sort_index()
            self.small_table_to_show = self.small_table_to_show.loc[rows]
        print('done analyzing data')

    def show_data(self):
        with self.tab_data:
            if self.small_table_to_show.shape != self.df.shape:
                st.warning(
                    f'table is too big! showing only {self.small_table_to_show.shape[0]:,} rows out of {self.df.shape[0]:,}')
            download(self.small_table_to_show, 'data')

    def show_statistics(self):
        with self.tab_statistics:
            st.subheader('columns statistics:')
            download(self.columns_statistics, 'statistics')

    def show_sizes(self):
        with self.tab_sizes:
            st.subheader('table statistics:')
            st.code(f'{self.mem_size.sum():.3f} MB\n{self.df.shape[0]:,} rows\n{self.df.shape[1]:,} columns')

            st.subheader('size of each column:')
            columns = st.columns([1, 2])
            columns[0].table(self.mem_size.to_frame().style.bar(color='#ead9ff').format('{:.3f}'))
            fig = px.pie(self.mem_size.to_frame().reset_index(), names='index', values='MB', hole=0.4)
            fig.update_traces(texttemplate="%{label}:<br>%{value:,.3f}MB<br>%{percent:.0%}", )
            if columns[1].checkbox('remove labels from pie chart', value=self.mem_size.shape[0]>10):
                fig.update_traces(texttemplate='', textinfo="none", )
            columns[1].plotly_chart(fig)

    def show_frequent_values_at_main(self):
        with self.tab_frequent_values:
            st.subheader('frequent values:')
            frequent = self.eda.get_frequent_values()
            frequent.value = frequent.value.astype(str)  # streamlit issue
            download(frequent, 'frequent_values')

    def show_frequent_values_at_sidebar(self):
        st.sidebar.header('frequent values per column:')
        freq = self.eda.get_frequent_values()
        columns = freq.col.unique()
        if self.preserve_column_order_at_sidebar:
            columns = self.df.columns[self.df.columns.isin(columns)].values
        for col in columns:
            single_col_statistics = self.columns_statistics.astype(dict(col=str))
            single_col_statistics = single_col_statistics.query(f'col=="{col}"').iloc[0]
            show = freq.query(f'col=="{col}"').set_index('value')

            # column name, uniques and nans
            st.sidebar.info(f'{col} [{single_col_statistics.uniques:,} uniques, {single_col_statistics.nans:,} nans]')

            # histogram
            if self.plot_hist:
                if pd.api.types.is_numeric_dtype(self.df[col]) and single_col_statistics.uniques > show.shape[0]:
                    bins = st.sidebar.slider('number of bins',
                                             0,
                                             min(self.df[col].nunique(), 300),
                                             0,
                                             key=f'nbins {col}')
                    bins = bins if bins > 1 else None
                    st.sidebar.plotly_chart(self.df.plot.hist(x=col, height=300, nbins=bins),
                                            use_container_width=True)
            # frequent values
            for index, row in show.iterrows():
                st.sidebar.write(f'{index}: [#{row.counts:,}, {row.counts / self.df.shape[0]:.2%}]')
                st.sidebar.progress(row.percentages)


if __name__ == '__main__':
    # importing streamlit is a bit slow, so moving it to here
    import streamlit as st

    if pkg_resources.parse_version(st.__version__).release > (1, 13, 0):
        already_running = st.runtime.exists()
    else:
        already_running = st._is_running_with_streamlit
    if already_running:
        Main()
    else:
        argv = ["streamlit", "run", sys.argv[0]]
        subprocess.run([f"{sys.executable}", "-m"] + argv)
