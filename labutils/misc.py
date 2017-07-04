def new_identifier_name(base, names, sep='_'):
        """
        For finding an unused identifier name.

        Examples:

        * 'sum' is taken, so 'sum2' is used.
        * 'sum', 'sum2', and 'sum3' are taken, so 'sum4' is used.

        :param base: A base string e.g.
        :return:
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
