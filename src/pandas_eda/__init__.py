import os
import sys
import subprocess
import tempfile
import atexit
import argparse

import pytest
from codetiming import Timer
import pandas as pd
import pandas_eda.streamlit_app
import pandas_eda.explore
import pandas_eda._testing


def eda(df, title='pandas eda'):
    size_mb = df.memory_usage(deep=True).sum() / 1024 ** 2
    if size_mb > 50:
        print(f'warning - table size is {size_mb:.0f}MB. May take some time to analyze the table')
    fp = tempfile.NamedTemporaryFile(prefix='pandas_eda_tool_', suffix='.pkl', delete=False)
    with Timer(text="dumping table to disk: {:.1f} seconds"):
        df.to_pickle(fp)
    args = [sys.executable, "-m", "streamlit", "run", pandas_eda.streamlit_app.__file__,
            "--", fp.name, title
            ]
    process = subprocess.Popen(args)
    atexit.register(eda_exit_handler, process, fp.name)
    return process


def eda_exit_handler(process, temp_file_name):
    process.kill()
    os.remove(temp_file_name)


pd.core.frame.DataFrame.eda = lambda df, cli_mode=False, title='pandas eda': \
    pandas_eda.explore.ExploreTable(df) if cli_mode else pandas_eda.eda(df, title)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='pandas_eda command-line interface')
    parser.add_argument('--test', action='store_true',
                        help='Run tests for pandas_eda: python -m pandas_eda --test')

    args = parser.parse_args()
    if args.test:
        # Determine the path to the current script
        script_path = os.path.abspath(__file__)

        # Determine the path to the tests directory
        tests_dir = os.path.join(os.path.dirname(script_path), '../pandas_eda_tests')

        pytest.main(['-s', tests_dir])
