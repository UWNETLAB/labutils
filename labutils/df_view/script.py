import labutils as lu
import pandas as pd

path1 = '/Users/joelbecker/Downloads/idi_data_plus_cf.csv'
path2 = '/Users/joelbecker/Documents/Code/binpy/2017-10-10-cleanup/lcs_test_output.csv'

df = pd.DataFrame.from_csv(path2)

DFV = lu.DFView(df)