def transform_rl_rst(docstr, indent=''):
    """
    Transforms an RST docstring in PyCharm's default format,
    to recordlinkage's RST format.

    PLEASE NOTE that this function is fairly piecewise, and may not
    handle edge cases & indentation perfectly. Please test it
    out on a copy of your code, and review the changes. Minor
    manual tweaks may be necessary after processing.

    :param docstr: A docstring, not including the quotes at beginning.
    :param indent: Whitespace to add to the beginning of each line.
    :return: String
    """
    def _parse_param(s):
        info, desc = [s.strip() for s in s.split(':') if len(s.strip()) > 0]
        info = info.split(' ')
        if len(info) < 3:
            raise Exception(f'No param type for {s}.')
        return {'name': info[-1], 'type': info[-2], 'desc': desc}

    def _parse_return(s):
        info, desc = [s.strip() for s in s.split(':') if len(s.strip()) > 0]
        return desc

    def _format_param_list(params):
        l = []
        for d in params:
            l.append(d['name'] + ' : ' + d['type'])
            l.append('    ' + d['desc'])
        return l

    def _format_return_list(returns):
        return [indent + returns[0]]

    def _transform_rl_rst(s):
        lines = [s.strip() for s in s.split('\n') if len(s.strip()) > 0]
        lines = _preprocess_docstr_lines(lines)
        summary = [s for s in lines if s[0] != ':']
        params = [_parse_param(s) for s in lines if s[:6] == ':param']
        returns = [_parse_return(s) for s in lines if s[:7] == ':return']
        doc_string = summary + [''] + ['Parameters', '----------'] + _format_param_list(params) + \
                     ['Returns', '-------'] + _format_return_list(returns) + ['\n']
        doc_string = [indent + s for s in doc_string]
        return ('\n').join(doc_string) + indent

    def _preprocess_docstr_lines(l):
        params_seen = False
        merge_lines = []
        for line in l:
            if not params_seen:
                if line[:6] == ':param' or line[:7] == ':return':
                    params_seen = True
                merge_lines.append(line)
            else:
                if not line[:6] == ':param' and not line[:7] == ':return':
                    merge_lines[-1] = merge_lines[-1].replace('\n', ' ') + line
                else:
                    merge_lines.append(line)
        return merge_lines

    return _transform_rl_rst(docstr)


def transform_rl_file_rst(fname: str):
    """
    Takes a python file and processes PyCharm-formatted-RST docstrings,
    replacing them with recordlinkage-formatted-RST docstrings.

    PLEASE NOTE that this function is fairly piecewise, and may not
    handle edge cases & indentation perfectly. Please test it
    out on a copy of your code, and review the changes. Minor
    manual tweaks may be necessary after processing.

    :param fname: The name of the file you'd like to process.
    :return: The processed file as a string.
    """
    docsep = '"""\n'

    def _trailing_spaces(s):
        n = 0
        for i in range(len(s)):
            if s[-i] == ' ':
                n += 1
            else:
                break
        return max(n-1, 4)

    def _transform_if_docstring(chunk: str, indent: str):
        if ':return:' in chunk or ':param:' in chunk:
            return transform_rl_rst(chunk, indent=indent)
        else:
            return chunk

    with open(fname, 'r') as f:
        old_string = f.read()
        chunks = old_string.split(sep=docsep)
        new_chunks = []
        for i in range(len(chunks)):
            if i > 0:
                print(chunks[i-1])
                n_spaces = _trailing_spaces(chunks[i-1])
                print(n_spaces)
            else:
                n_spaces = 4
            new_chunks.append(_transform_if_docstring(chunks[i], ' '*n_spaces))
        new_string = docsep.join(new_chunks)

    return new_string
