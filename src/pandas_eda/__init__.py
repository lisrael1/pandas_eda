import sys
import subprocess
import tempfile
import atexit

from codetiming import Timer
import pandas as pd
import pandas_eda.streamlit_app
import pandas_eda.explore


def eda(df):
    size_mb = df.memory_usage(deep=True).sum() / 1024 ** 2
    if size_mb > 50:
        print(f'warning - table size is {size_mb:.0f}MB. May take some time to analyze the table')
    fp = tempfile.TemporaryFile(suffix='.pkl', delete=False)  # TODO - delete file at exit
    with Timer(text="dumping table to disk: {:.1f} seconds"):
        df.to_pickle(fp)
    args = [sys.executable, "-m", "streamlit", "run", pandas_eda.streamlit_app.__file__,
            "--", fp.name,
            ]
    process = subprocess.Popen(args)
    atexit.register(eda_exit_handler, process)


def eda_exit_handler(process):
    process.kill()


pd.core.frame.DataFrame.eda = lambda df: pandas_eda.eda(df)
