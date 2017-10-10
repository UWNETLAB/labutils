def new_identifier_name(base, names, sep='_'):
        """
        For finding an unused identifier name.

        Examples:

        * 'sum' is taken, so 'sum2' is used.
        * 'sum', 'sum2', and 'sum3' are taken, so 'sum4' is used.

        :param base: A base string e.g.
        :return: None
        """
        # Find an unused column name
        col_name = base
        if col_name in names:
            i = 1
            while True:
                if col_name + sep + str(i) in names:
                    i += 1
                    continue
                else:
                    col_name += sep + str(i)
                    break
        return col_name


def hello_world():
    """
    Instantly gratifying reward for installing labutils.
    :return: None
    """
    hello_str = '''
     __   __  _______  ___      ___      _______  
    |  | |  ||       ||   |    |   |    |       | 
    |  |_|  ||    ___||   |    |   |    |   _   | 
    |       ||   |___ |   |    |   |    |  | |  | 
    |       ||    ___||   |___ |   |___ |  |_|  | 
    |   _   ||   |___ |       ||       ||       | 
    |__| |__||_______||_______||_______||_______| 
     _     _  _______  ______    ___      ______  
    | | _ | ||       ||    _ |  |   |    |      | 
    | || || ||   _   ||   | ||  |   |    |  _    |
    |       ||  | |  ||   |_||_ |   |    | | |   |
    |       ||  |_|  ||    __  ||   |___ | |_|   |
    |   _   ||       ||   |  | ||       ||       |
    |__| |__||_______||___|  |_||_______||______| 
        '''
    print(hello_str)


class bcolors:
    """
    Use this class to conveniently add colours and formatting to printed output.
    Taken from https://stackoverflow.com/questions/287871/print-in-terminal-with-colors-using-python.
    Example:
        .. code:: python

            print(bcolors.WARNING + "Warning: No active frommets remain. Continue?" + bcolors.ENDC)

    """
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'