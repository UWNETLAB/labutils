import warnings


def rank_pairs(comp, by, method='cols',ascending=True):
    """
    rank_pairs sorts pairs from a recordlinkage.Compare object, based on computed comparison values.

    Available methods:
        * 'cols': sort by first, column, ties broken by subsequent columns. See pandas.DataFrame.sort_values.
        * 'sum': sort by the sum of a list of columns.
        * 'avg': sort by the mean of a list of columns.

    :param comp: A recordlinkage.Compare object.
    :param list by: A list of column name strings to sort on by "method".
    :param str method: A the method to sort by (see above).
    :return: A MultiIndexed pandas.DataFrame
    """

    # Sorting by columns is simple!
    if method == 'value':

        # Enforce input type.
        if not isinstance(by, list):
            raise ValueError('Value of "by" must be a list of column names.')

        return comp.vectors.sort_values(by=by)

    # For aggregate methods, a bit of extra work is required.

    working_df = comp.vectors.copy()

    def find_name(base):
        """
        For finding an unused column name.

        Examples:

        * 'sum' is taken, so 'sum2' is used.
        * 'sum', 'sum2', and 'sum3' are taken, so 'sum4' is used.

        :param base: A base string e.g.
        :return:
        """
        # Find an unused column name
        col_name = base
        if col_name in working_df.columns:
            i = 2
            while True:
                if col_name + '_' + str(i) in working_df.columns:
                    i += 1
                    continue
                else:
                    col_name += '_' + str(i)
                    break
        return col_name

    if method == 'sum':


        # Enforce input type.
        if not isinstance(by, list):
            raise ValueError('Value of "by" must be a list of column names.')

        # Find an unused column name
        temp_col = find_name('sum')

        # Make a temporary column, which is the sum of columns of interest.
        working_df[temp_col] = sum([working_df[c] for c in by])

        return working_df.sort_values(by=temp_col,ascending=ascending)

    elif method == 'avg':

        working_df = comp.vectors.copy()

        # Enforce input type.
        if not isinstance(by, list):
            raise ValueError('Value of "by" must be a list of column names.')

        # Find an unused column name
        temp_col = find_name('avg')

        # Make a temporary column, which is the sum of columns of interest.
        working_df[temp_col] = sum([working_df[c] for c in by])/len(by)

        return working_df.sort_values(by=temp_col,ascending=ascending)

    else:
        raise ValueError('Unrecognized ranking method.')
        return None


def refine_mapping():
    return None


def fuse():
    return None