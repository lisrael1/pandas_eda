import numpy as np
import pandas as pd
import scipy.stats
from tqdm import tqdm


def bar(percentages: int):
    """
        percentages - 0 to 100
        return string bar like this |#####_____|
    """
    p = str(tqdm(initial=round(percentages / 10),
                 total=10,
                 gui=True,
                 ncols=12,
                 bar_format='|{bar}|', ascii=True)) \
        .replace(" ", "_")
    return p


def entropy(labels: list, base: int = 2):
    value, counts = np.unique(labels, return_counts=True)
    # if it's pd.Series you can use: counts = labels.value_counts(normalize=True, sort=False),
    # but it's 20x times slower
    counts = counts / counts.sum()
    return scipy.stats.entropy(counts, base=base)


def add_suffix_to_duplicated_columns(columns):
    """
        usage:
            df.columns = add_suffix_to_duplicated_columns(df.columns)
    :param columns:
    :return:
    """
    cols = columns.rename('col_name').to_frame().reset_index(drop=True)
    cols['suffix'] = cols.groupby('col_name').col_name.cumcount().astype(str).radd('_').replace('_0', '')
    cols = cols.astype(str)  # in case one of the columns is integer / float
    return cols.sum(axis=1)


class ExploreTable:
    """

    2 output table
        statistics_of_columns
            each column at the original table is a row at this output table
        frequent_values_per_column
            taking number_of_most_frequent_values most frequent values
            each frequent value for each column will be a row at this output table

    usage example:
        eda = ExploreTable(df)
        eda.get_columns_statistics()
        eda.get_frequent_values()
    """

    def __init__(self, df: pd.DataFrame, number_of_most_frequent_values: int = 6):
        self.number_of_most_frequent_values = number_of_most_frequent_values

        # original table
        self.df = df
        # statistics summary. each df column will be a row here
        self.statistics_of_columns = pd.DataFrame
        # each df column will have self.number_of_most_frequent_values rows here
        self.frequent_values_per_column = pd.DataFrame

        self._number_of_rows = df.shape[0]
        self._value_counts_per_column = dict()

        self.df.columns = add_suffix_to_duplicated_columns(self.df.columns)
        self._value_counts()
        self._columns_statistics()
        self._most_frequent_statistics()

    def _value_counts(self):
        for col in tqdm(self.df.columns, desc='value count per column'):
            self._value_counts_per_column[col] = self.df[col].value_counts(dropna=False)

    def _calc_average_length(self, col):
        """
            converting content to string, then calculating length of each cell, then average on all column.
            for example ['abab', 'aba'] has average length of 3.5
        """
        # like calculating
        # self.df[col].astype(str).apply(len).mean()
        if self._number_of_rows == 0:
            return 0
        counts = self._value_counts_per_column[col]
        counts = counts.to_frame('counts')
        counts['value_length'] = counts.index.to_series().astype(str).apply(len)
        return counts.value_length.mul(counts.counts).sum() / self._number_of_rows

    def _calc_entropy(self, col, base=2, dropna=True):
        counts = self._value_counts_per_column[col].copy()
        if dropna and counts.index.isna().sum():
            counts = counts[counts.index.notnull()]
        counts /= counts.sum()
        return scipy.stats.entropy(counts, base=base)

    def _columns_statistics(self):
        """
        extract statistics on table, like counting nans, duplications, uniques and more
        :return:
        """
        results = []
        for col, values in tqdm(self._value_counts_per_column.items(), desc='statistics per column'):
            statistics = dict()
            statistics['col'] = col
            statistics['uniques'] = values.shape[0]
            statistics['duplications'] = self._number_of_rows - statistics['uniques']
            statistics['nans'] = values[values.index.isna()].values[0] if values.index.isna().sum() else 0
            if self._number_of_rows > 0:
                statistics['nan_perc'] = int(100 * statistics['nans'] / self._number_of_rows)
            else:
                statistics['nan_perc'] = 100
            statistics['avg_length'] = self._calc_average_length(col)
            statistics['entropy'] = self._calc_entropy(col)
            # diversity is normalized entropy. it's a randomness index
            if self._number_of_rows > 0:
                statistics['diversity_inx'] = (2 ** statistics['entropy']) / (self._number_of_rows / 100)
            else:
                statistics['diversity_inx'] = 0
            statistics['diversity_inx'] = round(statistics['diversity_inx'])
            results.append(statistics)
        self.statistics_of_columns = pd.DataFrame(results)
        if not self.statistics_of_columns.empty:
            self.statistics_of_columns = self.statistics_of_columns.sort_values('entropy', ascending=False)

    def _most_frequent_statistics(self):
        if self.statistics_of_columns.empty:
            self.frequent_values_per_column = pd.DataFrame(
                columns=['col', 'value', 'frequent_inx', 'counts', 'percentages', 'bar'])
            return

        frequents = pd.DataFrame()
        for col in self.statistics_of_columns.col[::-1]:
            values = self._value_counts_per_column[col]
            values = values.to_frame('counts')
            values = values.head(self.number_of_most_frequent_values)
            values.index.name = 'value'
            values = values.reset_index(drop=False)
            values['col'] = col
            frequents = pd.concat([frequents, values], axis=0)

        frequents.index.name = 'frequent_inx'
        frequents = frequents.reset_index(drop=False)
        frequents['percentages'] = frequents.counts.div(self._number_of_rows).mul(100).round().astype(int)
        frequents['bar'] = frequents.percentages.apply(bar)

        self.frequent_values_per_column = frequents[['col', 'value', 'frequent_inx', 'counts', 'percentages', 'bar']]

    def get_columns_statistics(self):
        return self.statistics_of_columns.copy()

    def get_frequent_values(self):
        return self.frequent_values_per_column.copy()
