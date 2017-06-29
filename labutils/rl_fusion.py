# *****************************************************************************
# Data Fusion Functions
#   draft data fusion workflow for recordlinkage
# *****************************************************************************

import copy
import warnings
import pandas as pd
import jellyfish
import numpy as np


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

    # For aggregate methods, a bit of extra work is required.

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
        if col_name in working_comp.vectors.columns:
            i = 2
            while True:
                if col_name + '_' + str(i) in working_comp.vectors.columns:
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
        working_comp.vectors[temp_col] = sum([working_comp.vectors[c] for c in by])

        working_comp.vectors =  working_comp.vectors.sort_values(by=temp_col,ascending=ascending)
        return working_comp

    elif method == 'avg':

        # Enforce input type.
        if not isinstance(by, list):
            raise ValueError('Value of "by" must be a list of column names.')

        # Find an unused column name
        temp_col = find_name('avg')

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

def fuse():
    return None

