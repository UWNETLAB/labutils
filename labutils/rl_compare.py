# *****************************************************************************
# Custom Comparison Functions
#   to be used with recordlinkage's Compare.compare() method
# *****************************************************************************

import pandas as pd
import jellyfish
import numpy as np

# *****************************************************************************
# Longest Common Substring Comparators
# *****************************************************************************


def _longest_common_substring(s1, s2):
        """
        A helper function implementation of the longest common substring algorithm,
        adapted from:
        https://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Longest_common_substring.
        """

        if s1 is np.nan or s2 is np.nan:
            return 0

        if min(len(s1),len(s2)) == 0:
            return 0

        m = [[0] * (1 + len(s2)) for i in range(1 + len(s1))]  # Creating a matrix of 0s

        longest = 0
        x_longest = 0

        for x in range(1, 1 + len(s1)):
            for y in range(1, 1 + len(s2)):
                if s1[x - 1] == s2[y - 1]:  # Check if the chars match
                    m[x][y] = m[x - 1][y - 1] + 1  # add 1 to the diagnol
                    if m[x][y] > longest:
                        longest = m[x][y]
                        x_longest = x
                else:
                    m[x][y] = 0

        return longest


def lcss(s1, s2):
    """
    A custom comparison function to be used with the Compare.compare() method
    within recordlinkage. This is used to compare two strings, computing a
    match score based on the length of the longest common substring between
    the two strings.

    :param (label, pandas.Series) s1:  Series or DataFrame to compare all fields.

    :param (label, pandas.Series) s2: Series or DataFrame to compare all fields.

    :return: pandas.Series of integers (the length of the substring).
    """
    conc = pd.concat([s1, s2], axis=1, ignore_index=True)

    def lcss_apply(x):
        """
        Computes the longest common substring, divided by the length of the shorter string.
        """
        str1 = x[0]
        str2 = x[1]

        longest = _longest_common_substring(str1,str2)

        return longest

    return conc.apply(lcss_apply, axis=1)


def normed_lcss(s1, s2):
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

    def normed_lcss_apply(x):
        """
        Computes the longest common substring, divided by the length of the shorter string.
        """
        str1 = x[0]
        str2 = x[1]

        longest = _longest_common_substring(str1,str2)

        return longest / min(len(str1), len(str2))

    return conc.apply(normed_lcss_apply, axis=1)


def _fuzzy_longest_common_substring(str1, str2, match, mismatch, gap):
    """

    :param str str1: The first string to be compared.
    :param str str2: The second string to be compared.
    :param float match: Value added to score for matching characters.
    :param float mismatch: Value added to score for mismatching characters.
    :param float gap: Value added to score for gaps between similar characters.
    :return: A numeric similarity score.
    """

    if str1 is np.nan or str2 is np.nan:
            return 0

    if min(len(str1), len(str2)) == 0:
        return 0

    m = [[0] * (1 + len(str2)) for i in range(1 + len(str1))]

    highest = 0

    for x in range(1, 1 + len(str1)):
        for y in range(1, 1 + len(str2)):
            if str1[x - 1] == str2[y - 1]:
                diagonal = m[x - 1][y - 1] + match
            else:
                diagonal = m[x - 1][y - 1] + mismatch
            gap_left = m[x - 1][y] + gap
            gap_above = m[x][y - 1] + gap

            m[x][y] = max(diagonal, gap_left, gap_above)

            # If negative, boost to 0
            if m[x][y] < 0:
                m[x][y] = 0

            # Update Highest
            if m[x][y] > highest:
                highest = m[x][y]

    return highest


def normed_fuzzy_lcss(s1, s2, match=1, mismatch=-.5, gap=-1):
    """
    A custom comparison function to be used with the Compare.compare() method
    within recordlinkage. This is used to compare two strings, computing a
    match score based on the length of the longest similar substring between
    the two strings.

    The score resulting from the comparison is computed using a dynamic
    programming algorithm that creates a score based on the existence of
    character matches, mismatches, and gaps. This algorithm is equivalent
    to the Smith-Waterman algorithm used in the field of bioinformatics.
    To learn more about this algorithm see:
    https://en.wikipedia.org/wiki/Smith%E2%80%93Waterman_algorithm.

    In this method, the final match score is normalized by dividing the observed
    score by the maximum possible score (i.e. the length of the shorter string
    multiplied by the "match" parameter).

    :param (label, pandas.Series) s1: Series or DataFrame to compare all fields.
    :param (label, pandas.Series) s2: Series or DataFrame to compare all fields.
    :param float match: Value added to score for matching characters.
    :param float mismatch: Value added to score for mismatching characters.
    :param float gap: Value added to score for gaps between similar characters.
    :return: pandas.Series with similarity values equal or between 0 and 1.
    """

    conc = pd.concat([s1, s2], axis=1, ignore_index=True)

    def normed_fuzzy_lcss_apply(x):
        """
        An internal function for computing the match score between two strings.
        This is the function that is applied to the concatenated s1 and s2
        DataFrames. It returns a score based on the presence of similar
        substrings. This score is normalized by the shorter string's length.

        This is an implementation similar to the Smith-Waterman dynamic
        programming algorithm employed in bioinformatics.

        Examples
        >>> normed_fuzzy_lcss_apply(("Elizabeth", "Elisabeth")) # => 0.83
        >>> normed_fuzzy_lcss_apply(("James", "Robert")) # => 0.2
        >>> normed_fuzzy_lcss_apply(("John", "Jon")) # => 0.66
        >>> normed_fuzzy_lcss_apply(("University of Waterloo, Canada", "University of Waterloo, Ontario, Canada")) #=> 0.8
        """
        str1 = x[0]
        str2 = x[1]

        nonlocal match
        nonlocal mismatch
        nonlocal gap

        highest = _fuzzy_longest_common_substring(str1, str2, match, mismatch, gap)

        return highest / (min(len(str1), len(str2)) * match)

    return conc.apply(normed_fuzzy_lcss_apply, axis=1)

def fuzzy_lcss(s1, s2, match=1, mismatch=-.5, gap=-1):
    """
    A custom comparison function to be used with the Compare.compare() method
    within recordlinkage. This is used to compare two strings, computing a
    match score based on the length of the longest similar substring between
    the two strings.

    The score resulting from the comparison is computed using a dynamic
    programming algorithm that creates a score based on the existence of
    character matches, mismatches, and gaps. This algorithm is equivalent
    to the Smith-Waterman algorithm used in the field of bioinformatics.
    To learn more about this algorithm see:
    https://en.wikipedia.org/wiki/Smith%E2%80%93Waterman_algorithm.

    In this method, the raw numeric score is produced.

    :param (label, pandas.Series) s1: Series or DataFrame to compare all fields.
    :param (label, pandas.Series) s2: Series or DataFrame to compare all fields.
    :param float match: Value added to score for matching characters.
    :param float mismatch: Value added to score for mismatching characters.
    :param float gap: Value added to score for gaps between similar characters.
    :return: pandas.Series with numeric similarity values.
    """

    conc = pd.concat([s1, s2], axis=1, ignore_index=True)

    def fuzzy_lcss_apply(x):
        """
        An internal function for computing the match score between two strings.
        This is the function that is applied to the concatenated s1 and s2
        DataFrames. It returns a score based on the presence of similar
        substrings. This score is normalized by the shorter string's length.

        This is an implementation similar to the Smith-Waterman dynamic
        programming algorithm employed in bioinformatics.

        Examples
        >>> fuzzy_lcss_apply(("Elizabeth", "Elisabeth")) # => 7.5
        >>> fuzzy_lcss_apply(("James", "Robert")) # => 1
        >>> fuzzy_lcss_apply(("John", "Jon")) # => 2
        >>> fuzzy_lcss_apply(("University of Waterloo, Canada", "University of Waterloo, Ontario, Canada")) #=> 24
        """
        str1 = x[0]
        str2 = x[1]

        nonlocal match
        nonlocal mismatch
        nonlocal gap

        highest = _fuzzy_longest_common_substring(str1, str2, match, mismatch, gap)

        return highest

    return conc.apply(fuzzy_lcss_apply, axis=1)

# *****************************************************************************
# Collection Comparators
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

# Need to decide whether to actually include this or not
def compare_in(s1, s2):
    # TODO: Determine whether this is a needed. compare_longest_substring and normed_fuzzy_lcss might do the job
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

# *****************************************************************************
# Misc Comparators
# *****************************************************************************

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
