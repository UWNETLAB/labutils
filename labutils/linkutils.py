import warnings

def rank_pairs(comp, by, method='col'):
    """
    rank_pairs sorts pairs from a recordlinkage.Compare object, based on computed comparison values.

    Available methods:
        * 'col': sort by values in a column.
        * 'sum': sort by the sum of a list of columns.
        * 'avg': sort by the mean of a list of columns.

    :param comp: A recordlinkage.Compare object.
    :param list by: A list of column name strings to sort on by "method".
    :param str method: A the method to sort by (see above).
    :return: A MultiIndexed pandas.DataFrame
    """
    working_df = comp.vectors.copy()

    if method == 'value':

        # Get column name and raise a warning if there is a bad input.
        if isinstance(by, str):
            # Strings work, but break the code signature.
            col_name = by
            warnings.warn('Value of "by" is a string, not a list. Converting implicitly.')
        if isinstance(by, list):
            # With this method, only one column should be named.
            # The first column name is taken, and a warning is raised
            # for unused values.
            if len(by) > 1:
                warnings.warn('Ranking method "col" uses a single column. Unused values in "by".')
            col_name = by[0]

        working_df['temp_sorting_col'] = working_df[col_name]

    elif method == 'sum':
        pass

    elif method == 'avg':
        pass

    else:
        raise ValueError('Unrecognized ranking method.')

    return None

def refine_mapping():
    return None

def fuse():
    return None