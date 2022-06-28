import numpy as np
import pandas as pd
import scipy.stats
from tqdm import tqdm


def bar(percentages):
    """
        percentages - 0 to 100
        return string bar like this |#####_____|
    """
    p = str(tqdm(initial=round(percentages / 10),
                 total=10,
                 gui=True,
                 ncols=12,
                 bar_format='|{bar}|', ascii=True))\
        .replace(" ", "_")
    return p


def entropy(labels, base=2):
    value, counts = np.unique(labels, return_counts=True)
    # if it's pd.Series you can use: counts = labels.value_counts(normalize=True, sort=False),
    # but it's 20x times slower
    counts = counts / counts.sum()
    return scipy.stats.entropy(counts, base=base)


class ExploreTable:
    """
    usage example:
        table = ExploreTable(df)
        table.get_table_statistics()
        table.statistics
        table.frequent_values
        table.bars

    """

    def __init__(self, df):
        self.max_rows = 1000
        self.number_of_frequent_values = 6

        # original table
        self.df = df
        # statistics summary. each df column will be a row here
        self.statistics = None
        # each df column will have self.number_of_frequent_values rows here
        self.frequent_values = None
        self.bars = None
        self.number_of_rows = df.shape[0]

        self._statistics_table()
        self._frequent_values()
        self._add_bars()

    def get_table_statistics(self):
        return self.statistics.copy()

    def get_columns_statistics(self):
        stats = self.get_table_statistics().set_index('column_name')
        stats = stats.join(self.bars)
        stats = stats.sort_values('diversity')
        return stats

    def get_frequent_values_wide(self):
        stats = self.bars.copy()
        stats = stats.join(self.frequent_values.filter(regex='bar|val'))
        stats = stats.sort_values('diversity')
        return stats

    def get_frequent_values_long(self):
        stats = pd.wide_to_long(self.get_frequent_values_wide().reset_index(),
                                sep='_',
                                stubnames=['bar', 'val'],
                                i='col',
                                j='place')\
            .sort_index()
        stats[['bar', 'val']].reset_index(drop=False)
        return stats

    def _statistics_table(self):
        self._initialize_statistics()
        self._count_nans()
        self._calc_columns_average_len()
        self._calc_columns_diversity()
        self.statistics = self.statistics.reset_index(drop=True)

    def _initialize_statistics(self):
        self.statistics = self.df.columns.to_series().to_frame('column_name')
        self.statistics['rows'] = self.number_of_rows
        self.statistics['uniques'] = self.df.nunique()

    def _count_nans(self):
        df = self.df.isna().mean().fillna(0)
        if self.number_of_rows is None:
            nan_perc = None
        else:
            nan_perc = (df * 100).astype(int)
        self.statistics['nan_perc'] = nan_perc

    def _calc_columns_diversity(self):
        """
            in entropy at base 2
        :param df:
        :return:
        """
        if self.number_of_rows is None:
            self.statistics['diversity_inx'] = None
            return
        df = self.df.copy()
        try:
            columns_entropy = df.astype(str).apply(lambda r: entropy(r.dropna()))
        except (AttributeError, TypeError):
            columns_entropy = df.select_dtypes(object).astype(str).apply(lambda r: entropy(r.dropna()))
        columns_entropy = columns_entropy.sort_values(ascending=False)
        # entropy at base 2. when having 200 unique values out of 200 rows, then 2**entropy will give us 200
        # this is better than taking unique/rows as unique can be unbalances. value_counts give more information
        self.statistics['diversity_inx'] = (2**columns_entropy).div(self.number_of_rows / 100).round(0).astype(int)

    def _calc_columns_average_len(self):
        """
            converting content to string, then calculating length of each cell, then average on all column.
        :param df:
        :return:
        """
        if self.number_of_rows is None:
            self.statistics['avg_length'] = None
            return
        try:
            df = self.df.fillna('').astype(str).applymap(len)
        except (AttributeError, TypeError):
            # sometimes you have oracle object with dtype of object, and pandas cannot read it as str
            df = self.df.select_dtypes([object, 'category']).dropna().astype(str).applymap(len)
        df = df.apply(lambda c: c[c > 0].mean(), axis=0).fillna(0)
        self.statistics['avg_length'] = df

    @staticmethod
    def _frequent_values_at_column(sr, number_of_frequent_values=6, max_value_length=10):
        values = sr.astype(str).str[:max_value_length] \
            .value_counts() \
            .mul(100 / sr.shape[0]) \
            .round(0) \
            .astype(int) \
            .to_frame('freq')
        values = values.head(number_of_frequent_values)
        values['bar'] = values.freq.apply(bar)
        values = values.rename_axis(index='val').reset_index(drop=False)

        # adding columns that contains all data - value, frequency and bar
        values['all_data'] = values.val.astype(str) + ':' + values.freq.astype(str) + '%:' + values.bar
        values = values.stack()
        # converting multi index to combined single index
        values.index = values.index.to_frame().astype(str).iloc[:, ::-1].apply('_'.join, axis=1).values
        values = values.sort_index()
        return values

    def _frequent_values(self):
        values = []
        for col in self.df.columns:
            values += [self._frequent_values_at_column(self.df[col], self.number_of_frequent_values).to_frame(col)]
        self.frequent_values = pd.concat(values, axis=1).T
        self.frequent_values.index.name = 'col'

    def _add_bars(self):
        nans = self.statistics.nan_perc.fillna(0).apply(bar).rename('nans')
        diversity = self.statistics.diversity_inx.apply(bar).rename('diversity')
        self.bars = pd.concat([nans, diversity, self.statistics.column_name], axis=1)
        self.bars = self.bars.set_index('column_name')
        self.bars.index.name = 'col'
