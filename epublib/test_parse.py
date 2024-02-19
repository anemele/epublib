from pprint import pprint

from .parser import Chapter, parse_text


def test_parse_text():
    sample = '''\
    # h1
    abcd
    ## h2
    ABCD
    ### h3
    12345
    ## h22
    67890'''
    expect = [
        Chapter('h1', 1).append('abcd'),
        Chapter('h2', 2).append('ABCD').append('### h3').append('12345'),
        Chapter('h22', 2).append('67890'),
    ]

    result = parse_text(iter(sample.splitlines()))

    assert result == expect, pprint(result)
