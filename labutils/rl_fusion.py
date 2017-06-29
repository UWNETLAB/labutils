# *****************************************************************************
# Data Fusion Functions
#   draft data fusion workflow for recordlinkage
# *****************************************************************************

import copy
import pandas as pd
from labutils.misc import new_identifier_name

def rank_pairs(comp, by, method='cols',ascending=False):
    """
    rank_pairs sorts pairs from a recordlinkage.Compare object, based on computed comparison values.

    Available methods:
        * 'cols': sort by first, column, ties broken by subsequent columns. See pandas.DataFrame.sort_values.
        * 'sum': sort by the sum of a list of columns.
        * 'avg': sort by the mean of a list of columns.

    :param recordlinkage.Compare comp: A populated Comparison object.
    :param list by: A list of column name strings to sort on by "method".
    :param str method: A the method to sort by (see above).
    :param bool ascending: Specifies ordering of sorted rows.
    :return: recordlinkage.Compare
    """

    # A fresh copy of the comparison object for modification.
    working_comp = copy.deepcopy(comp)

    # Sorting by columns is simple!
    if method == 'cols':

        # Enforce input type.
        if not isinstance(by, list):
            raise ValueError('Value of "by" must be a list of column names.')

        working_comp.vectors = working_comp.vectors.sort_values(by=by, ascending=ascending)
        return working_comp

    # Sort by row sum for specified columns
    if method == 'sum':


        # Enforce input type.
        if not isinstance(by, list):
            raise ValueError('Value of "by" must be a list of column names.')

        # Find an unused column name
        temp_col = new_identifier_name('sum', working_comp.vectors.columns)

        # Make a temporary column, which is the sum of columns of interest.
        working_comp.vectors[temp_col] = sum([working_comp.vectors[c] for c in by])

        working_comp.vectors =  working_comp.vectors.sort_values(by=temp_col,ascending=ascending)
        return working_comp

    # Sort by row mean for specified columns
    elif method == 'avg':

        # Enforce input type.
        if not isinstance(by, list):
            raise ValueError('Value of "by" must be a list of column names.')

        # Find an unused column name
        temp_col = new_identifier_name('avg', working_comp.vectors.columns)

        # Make a temporary column, which is the sum of columns of interest.
        working_comp.vectors[temp_col] = sum([working_comp.vectors[c] for c in by])/len(by)

        working_comp.vectors = working_comp.vectors.sort_values(by=temp_col,ascending=ascending)
        return working_comp

    else:
        raise ValueError('Unrecognized ranking method.')
        return None


def refine_mapping(comp, left_unique=True, right_unique=True):
    """
    Removes pairs that violate uniqueness rules. Matches may be one-to-one (default),
    one-to-many (right_unique=False), or many-to-one (left_unique=False). refine_mapping
    always keeps the first instance of an index. To keep the best matches, sort (or
    filter) pairs before passing to refine_mapping, e.g. with rank_pairs (or a classification
    algorithm).

    :param recordlinkage.Compare comp: A populated Comparison object.
    :param bool left_unique: Specifies uniqueness of left (top-level) indices.
    :param bool right_unique: Specifies uniqueness of right (top-level) indices.
    :return: recordlinkage.Compare
    """

    # Copy comparison object indices.
    working_indices = comp.vectors.index.to_frame()

    # Save indices as pandas.Series.
    working_left_index = list(working_indices[0])
    working_right_index = list(working_indices[1])

    # Track observed indices.
    seen_left = set()
    seen_right = set()

    # Identify records to be kept/discarded.

    # 1 = Keep / 0 = Discard
    keep_vector = []

    # Iterate on indices
    for i in range(0,len(working_indices)):

        keep = True

        # Check/add left index
        if left_unique is True:
            if working_left_index[i] in seen_left:
                keep = False
            else:
                seen_left.add(working_left_index[i])

        # Check/add right index
        if right_unique is True:
            if working_right_index[i] in seen_right:
                keep = False
            else:
                seen_right.add(working_right_index[i])

        keep_vector.append(keep)

    # Return a new comparison object
    working_comp = copy.deepcopy(comp)
    working_comp.vectors = working_comp.vectors.iloc[keep_vector]
    return working_comp


def fast_fuse(comp, left_suffix='_l', right_suffix='_r'):
    """
    Performs data fusion using a recordlinkage.Compare object.
    All data is kept from both original data frames, renaming columns to avoid conflits.
    The result is comp.vectors but with each rows populated with data from
    the original two data frames corresponding to the compared pair.

    :param recordlinkage.Compare comp: Compared pairs to be fused.
    :param str left_suffix: The suffix stem to be used to resolve naming conflits for columns in df_a.
    :param str right_suffix: The suffix stem to be used to resolve naming conflits for columns in df_b.
    :return: pandas.DataFrame
    """

    working_df = copy.deepcopy(comp.vectors)
    index_df = working_df.index.to_frame()

    # Get appropriate columns from df_a and df_b
    working_left = comp.df_a.iloc[list(index_df[0])]
    working_right = comp.df_b.iloc[list(index_df[1])]

    # Index data from left and right dataframes
    working_left = working_left.set_index(working_df.index)
    working_right = working_right.set_index(working_df.index)

    # Get new column names
    left_col_names = [new_identifier_name(c + left_suffix, working_df.columns.tolist()) for c in working_left.columns]
    right_col_names = [new_identifier_name(c + right_suffix, working_df.columns.tolist() + left_col_names) for c in working_right.columns]

    # Apply columnn names
    working_left.columns = left_col_names
    working_right.columns = right_col_names

    return pd.concat([working_df, working_left, working_right],axis=1)
    #return [working_df, working_left, working_right]
