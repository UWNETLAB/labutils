import tqdm
import warnings
import pandas as pd
import numpy as np
import itertools as it
import pyperclip
import tabulate


def clip_df(df, tablefmt='html'):
    """
    Copy a dataframe as plain text to your clipboard.
    Probably only works on Mac. For format types see ``tabulate`` package
    documentation.

    :param pandas.DataFrame df: Input DataFrame.
    :param str tablefmt: What type of table?
    :return: None.
    """
    pyperclip.copy(tabulate.tabulate(df, headers=df.columns, tablefmt=tablefmt))
    print('Copied {} table to clipboard!'.format(tablefmt))


def expand_on(df, col1, col2, rename1=None, rename2=None, drop=[], drop_collections=False):
        """
        Returns a reshaped version of extractor's data, where unique combinations of values from col1 and col2
        are given individual rows. This method was pasted form ``tidyextractors`` on 2017-07-10.

        Example function call from ``tidymbox``:

        .. code-block:: python

            self.expand_on('From', 'To', ['MessageID', 'Recipient'], rename1='From', rename2='Recipient')

        Columns to be expanded upon should be either atomic values or dictionaries of dictionaries. For example:

        Input Data:

        +-----------------+-------------------------------------------------------------------+
        | col1 (Atomic)   | col2 (Dict of Dict)                                               |
        +=================+===================================================================+
        | value1          | {valueA : {attr1: X1, attr2: Y1}, valueB: {attr1: X2, attr2: Y2}  |
        +-----------------+-------------------------------------------------------------------+
        | value2          | {valueC : {attr1: X3, attr2: Y3},  valueD: {attr1: X4, attr2: Y4} |
        +-----------------+-------------------------------------------------------------------+

        Output Data:

        +---------------+---------------+-------+-------+
        | col1_extended | col2_extended | attr1 | attr2 |
        +===============+===============+=======+=======+
        | value1        | valueA        | X1    | Y1    |
        +---------------+---------------+-------+-------+
        | value1        | valueB        | X2    | Y2    |
        +---------------+---------------+-------+-------+
        | value2        | valueA        | X3    | Y3    |
        +---------------+---------------+-------+-------+
        | value2        | valueB        | X4    | Y4    |
        +---------------+---------------+-------+-------+

        :param pandas.DataFrame df: Input DataFrame.
        :param str col1: The first column to expand on. May be an atomic value, or a dict of dict.
        :param str col2: The second column to expand on. May be an atomic value, or a dict of dict.
        :param str rename1: The name for col1 after expansion. Defaults to col1_extended.
        :param str rename2: The name for col2 after expansion. Defaults to col2_extended.
        :param list drop: Column names to be dropped from output.
        :param bool drop_collections: Should columns with compound values be dropped?
        :return: pandas.DataFrame
        """

        # Assumption 1: Expanded columns are either atomic are built in collections
        # Assumption 2: New test_data columns added to rows from dicts in columns of collections.

        # How many rows expected in the output?
        count = len(df)

        # How often should the progress bar be updated?
        update_interval = max(min(count//100, 100), 5)

        # What are the column names?
        column_list = list(df.columns)

        # Determine column index (for itertuples)
        try:
            col1_index = column_list.index(col1)
        except ValueError:
            warnings.warn('Could not find "{}" in columns.'.format(col1))
            raise
        try:
            col2_index = column_list.index(col2)
        except ValueError:
            warnings.warn('Could not find "{}" in columns.'.format(col2))
            raise

        # Standardize the order of the specified columns
        first_index = min(col1_index, col2_index)
        second_index = max(col1_index, col2_index)
        first_name = column_list[first_index]
        second_name = column_list[second_index]
        first_rename = rename1 if first_index == col1_index else rename2
        second_rename = rename2 if first_index == col1_index else rename1

        # New column names:
        new_column_list = column_list[:first_index] + \
                          [first_name+'_extended' if first_rename is None else first_rename] + \
                          column_list[first_index+1:second_index] + \
                          [second_name+'_extended' if second_rename is None else second_rename] + \
                          column_list[second_index+1:]

        # Assert that there are no duplicates!
        if len(set(new_column_list)) != len(new_column_list):
            raise Exception('Duplicate columns names found. Note that you cannot rename a column with a name '
                            'that is already taken by another column.')

        # List of tuples. Rows in new test_data frame.
        old_attr_df_tuples = []
        new_attr_df_dicts = []

        # MultiIndex tuples
        index_tuples = []

        def iter_product(item1, item2):
            """
            Enumerates possible combinations of items from item1 and item 2. Allows atomic values.
            :param item1: Any
            :param item2: Any
            :return: A list of tuples.
            """
            if hasattr(item1, '__iter__') and type(item1) != str:
                iter1 = item1
            else:
                iter1 = [item1]
            if hasattr(item2, '__iter__') and type(item2) != str:
                iter2 = item2
            else:
                iter2 = [item2]
            return it.product(iter1, iter2)

        # Create test_data for output.
        with tqdm.tqdm(total=count) as pbar:
            for row in df.itertuples(index=False):
                # Enumerate commit/file pairs
                for index in iter_product(row[first_index],row[second_index]):

                    new_row = row[:first_index] + \
                              (index[0],) + \
                              row[first_index+1:second_index] + \
                              (index[1],) + \
                              row[second_index+1:]

                    # Add new row to list of row tuples
                    old_attr_df_tuples.append(new_row)

                    # Add key tuple to list of indices
                    index_tuples.append((index[0],index[1]))

                    # If there's test_data in either of the columns add the test_data to the new attr test_data frame.
                    temp_attrs = {}

                    # Get a copy of the first cell value for this index.
                    #  If it's a dict, get the appropriate entry.

                    temp_first = row[first_index]
                    if type(temp_first) == dict:
                        temp_first = temp_first[index[0]]
                    temp_second = row[second_index]
                    if type(temp_second) == dict:
                        temp_second = temp_second[index[1]]

                    # Get nested test_data for this index.
                    if type(temp_first) == dict:
                        for k in temp_first:
                            temp_attrs[first_name + '/' + k] = temp_first[k]
                    if type(temp_second) == dict:
                        for k in temp_second:
                            temp_attrs[second_name + '/' + k] = temp_second[k]

                    # Add to the "new test_data" records.
                    new_attr_df_dicts.append(temp_attrs)

                    # Update progress bar
                    pbar.update(update_interval)

        # An expanded test_data frame with only the columns of the original test_data frame
        df_1 = pd.DataFrame.from_records(old_attr_df_tuples, columns=new_column_list)

        # An expanded test_data frame containing any test_data held in value:key collections in the expanded cols
        df_2 = pd.DataFrame.from_records(new_attr_df_dicts)

        # The final expanded test_data set
        df_out = pd.concat([df_1, df_2], axis=1)

        # Drop unwanted columns
        for col in drop:
            if col in df_out.columns:
                df_out = df_out.drop(col,1)

        if drop_collections is True:
            df_out = drop_collection_columns(df_out)

        return df_out


def drop_collection_columns(df):
        """
        Drops columns containing collections (i.e. sets, dicts, lists) from a DataFrame.
        This method was pasted from ``tidyextractors`` on 2017-07-10.

        :param pandas.DataFrame df: Usually self._data.
        :return: pandas.DataFrame
        """
        all_cols = df.columns
        keep_cols = []

        # Check whether each column contains collections.
        for c in all_cols:
            if len(col_type_set(c, df).intersection([set, dict, list])) == 0:
                keep_cols.append(c)
        return df[keep_cols]


def col_type_set(col, df):
        """
        Determines the set of types present in a DataFrame column.
        This function was pasted from ``tidyextractors`` on 2017-07-10.

        :param str col: A column name.
        :param pandas.DataFrame df: The data set. Usually ``self._data``.
        :return: A set of Types.
        """
        type_set = set()
        if df[col].dtype == np.dtype(object):
            unindexed_col = list(df[col])
            for i in range(0, len(df[col])):
                if unindexed_col[i] == np.nan:
                    continue
                else:
                    type_set.add(type(unindexed_col[i]))
            return type_set
        else:
            type_set.add(df[col].dtype)
            return type_set