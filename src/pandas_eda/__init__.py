import pandas_eda.streamlit_app
import pandas_eda.explore
import subprocess
import tempfile
import pandas as pd
import atexit


def eda(df):
    fp = tempfile.TemporaryFile(suffix='.xlsx', delete=False)
    df.to_excel(fp, index=None)
    args = ["streamlit", "run", pandas_eda.streamlit_app.__file__,
            "--", fp.name,
            ]
    process = subprocess.Popen(args)
    atexit.register(eda_exit_handler, process)


def eda_exit_handler(process):
    process.kill()


pd.core.frame.DataFrame.eda = lambda df: eda(df)
