import json

def dict_to_str(d):
    """
    Convert the dictionary to a string in a deterministic manner.
    """

    pieces = []
    for k in sorted(d.keys()):
        if not d[k]:
            continue
        pieces.append(f'"{str(k)}" : {str(d[k])}')
    return f'{{{", ".join(pieces)}}}'

def prettify(o_str, indent=4):
    """
    Makes the string passed in suitable for JSON printing.
    """
    return json.dumps(json.loads(o_str), indent=indent)
