import warnings
import pandas as pd
import jellyfish
import numpy as np


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


# *****************************************************************************
# Custom Comparison Functions
#   to be used with recordlinkage's Compare.compare() method
# *****************************************************************************

def compare_lists(s1, s2):
    """
    A custom comparison function to be used with the Compare.compare() method
    within recordlinkage. This is used to compare two lists, computing a
    match score based on the number of items shared between two lists.

    The score resulting from the comparison can be expressed as the number of
    shared items between two sets, divided by the total number of unique items
    in the smaller set.

    :param (label, pandas.Series) s1:  Series or DataFrame to compare all fields.

    :param (label, pandas.Series) s2: Series or DataFrame to compare all fields.

    :return: pandas.Series with similarity values equal or between 0 and 1.
    """

    conc = pd.concat([s1, s2], axis=1, ignore_index=True)

    def list_apply(x):
        """
        An internal function for computing the match score between two lists.
        This is the function that is applied to the concatenated s1 and s2 dataframe.

        # Returns a score of 1
        >>> list_apply((["Lodge V", "Cooper B", "Andrews A"], ["Andrews A"]))

        # Returns a score of 0
        >>> list_apply((["Lodge V", "Cooper B"], ["Andrews A", "Jones J"]))

        # Returns a score of 0.5
        >>> list_apply((["Lodge V", "Cooper B", "Andrews A"], ["Andrews A", "Jones J"]))
        """
        try:
            set1 = set(x[0])
            set2 = set(x[1])

            min_length = min(len(set1), len(set2))
            intersect_length = len(set1.intersection(set2))

            return intersect_length/min_length

        except Exception as err:
            if pd.isnull(x[0]) or pd.isnull(x[1]):
                return np.nan
            else:
                raise err

    return conc.apply(list_apply, axis=1)


def compare_fuzzy_substring(s1, s2):
    # TODO: Make the scoring scheme values optional parameters.
    """
       A custom comparison function to be used with the Compare.compare() method
       within recordlinkage. This is used to compare two strings, computing a
       match score based on the length of the longest similar substring between
       the two strings.

       The score resulting from the comparison is computed using a dynamic
       programming algorithm that creates a score based on the existence of

       This algorithm is equivalent to the Smith-Waterman algorithm used in the
       field of bioinformatics. To learn more about this algorithm see:
       https://en.wikipedia.org/wiki/Smith%E2%80%93Waterman_algorithm.

       The current implementation uses the following scoring scheme:
            match    => +1.0
            mismatch => -0.5
            gap      => -1.0

       The final match score is normalized by taking the maximum score between two
       strings and dividing it by the length of the smaller string.

       :param (label, pandas.Series) s1:  Series or DataFrame to compare all fields.

       :param (label, pandas.Series) s2: Series or DataFrame to compare all fields.

       :return: pandas.Series with similarity values equal or between 0 and 1.
   """

    conc = pd.concat([s1, s2], axis=1, ignore_index=True)

    # match -> add 1, mismatch & gap -> subtract 1, until 0
    # The scoring algorithm should
    def fuzzy_substring_apply(x):
        """
        An internal function for computing the match score between two strings.
        This is the function that is applied to the concatenated s1 and s2
        Dataframes. It returns a score based on the presence of similar
        substrings. This score is normalized by the shorter string's length.

        This is an implementation similar to the Smith-Waterman dynamic
        programming algorithm employed in bioinformatics.

        Examples
        >>> fuzzy_substring_apply(("Elizabeth", "Elisabeth")) # => 0.83
        >>> fuzzy_substring_apply(("James", "Robert")) # => 0.2
        >>> fuzzy_substring_apply(("John", "Jon")) # => 0.66
        >>> fuzzy_substring_apply(("University of Waterloo, Canada", "University of Waterloo, Ontario, Canada")) #=> 0.8

        """
        str1 = x[0]
        str2 = x[1]

        if min(len(str1), len(str2)) == 0:
            return 0

        m = [[0] * (1 + len(str2)) for i in range(1 + len(str1))]

        highest = 0

        for x in range(1, 1 + len(str1)):
            for y in range(1, 1 + len(str2)):
                if str1[x - 1] == str2[y - 1]:
                    diagnol = m[x - 1][y - 1] + 1
                else:
                    diagnol = m[x - 1][y - 1]-0.5
                gap_left = m[x - 1][y] - 1
                gap_above = m[x][y - 1] - 1

                m[x][y] = max(diagnol, gap_left, gap_above)

                # If negative, boost to 0
                if m[x][y] < 0:
                    m[x][y] = 0

                # Update Highest
                if m[x][y] > highest:
                    highest = m[x][y]

        return highest / min(len(str1), len(str2))

    return conc.apply(fuzzy_substring_apply, axis=1)


def compare_longest_substring(s1, s2):
    """
    A custom comparison function to be used with the Compare.compare() method
    within recordlinkage. This is used to compare two strings, computing a
    match score based on the length of the longest common substring between
    the two strings.

    The score resulting from the comparison can be expressed as the length of
    the longest common substring, divided by the length of the shorter string.
    The resulting score is equal or between 0 and 1.

    :param (label, pandas.Series) s1:  Series or DataFrame to compare all fields.

    :param (label, pandas.Series) s2: Series or DataFrame to compare all fields.

    :return: pandas.Series with similarity values equal or between 0 and 1.
    """
    conc = pd.concat([s1, s2], axis=1, ignore_index=True)

    def long_sub_apply(x):
        """
        An internal function for computing the match score between two strings.
        This is the function that is applied to the concatenated s1 and s2 dataframe.

        This longest substring algorithm was adapted from
        https://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Longest_common_substring.
        """
        str1 = x[0]
        str2 = x[1]
        if min(len(str1),len(str2)) == 0:
            return 0

        m = [[0] * (1 + len(str2)) for i in range(1 + len(str1))]  # Creating a matrix of 0s

        longest = 0
        x_longest = 0

        for x in range(1, 1 + len(str1)):
            for y in range(1, 1 + len(str2)):
                if str1[x - 1] == str2[y - 1]:  # Check if the chars match
                    m[x][y] = m[x - 1][y - 1] + 1  # add 1 to the diagnol
                    if m[x][y] > longest:
                        longest = m[x][y]
                        x_longest = x
                else:
                    m[x][y] = 0

        return longest / min(len(str1), len(str2))

    return conc.apply(long_sub_apply, axis=1)


# Need to decide whether to actually include this or not
def compare_in(s1, s2):
    # TODO: Determine whether this is a needed. compare_longest_substring and compare_fuzzy_substring might do the job
    """

    :param (pandas.Series) s1:
    :param (pandas.Series) s2:
    :return:
    """
    concatenated = pd.concat([s1, s2], axis=1, ignore_index=True)

    def in_apply(x):
        # TODO: Implement functionality for user to specify whether searching colA in colB or colB in colA
        """
        Internal function that compares values from the two series,
         determining whether the value from s1 (x[0]) is contained within
         the value from s2 x[1].

        If x[0] is contained within x[1] a score of 1 is returned.
        If no subset of x[0] is contained within
        """
        try:
            value = x[0]
            max_length = len(value)
            check = x[1]

            def score(val, chk, count=0):
                if value == '':
                    return 0
                elif value in check:
                    return 1 - count/max_length
                else:
                    return score(value[0:-1], check, count+1)

            return score(value, check)
        except Exception as err:
            if pd.isnull(x[0]) or pd.isnull(x[1]):
                return np.nan
            else:
                raise err

    return concatenated.apply(in_apply, axis=1)


# This one is not working properly
def compare_except(s1, s2, exceptions=[]):
    conc = pd.concat([s1, s2], axis=1, ignore_index=True)

    def except_apply(x):
        try:
            str1 = x[0]
            str2 = x[1]

            for ex in exceptions:
                str1 = str1.replace(ex, "")

            return jellyfish.jaro_distance(str1, str2)

        except Exception as err:
            if pd.isnull(x[0]) or pd.isnull(x[1]):
                return np.nan
            else:
                raise err

    return conc.apply(except_apply, axis=1)

