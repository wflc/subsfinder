#! /usr/bin/env python
# -*- coding: utf -*-

from __future__ import unicode_literals, print_function
import os
import pathlib
from re import sub
from tests.test_subsfinder import videofile
import subsfinder
import pytest
from subsfinder.subsearcher import ZimukuSubSearcher
from subsfinder.subsfinder import SubsFinder
from subsfinder.subsearcher.exceptions import LanguageError, ExtError


@pytest.fixture(scope='module')
def zimuku():
    s = SubsFinder()
    z = ZimukuSubSearcher(s)
    return z


def test_languages(zimuku):
    zimuku._check_languages(['zh_chs'])
    with pytest.raises(LanguageError):
        zimuku._check_languages(['fake_lang'])


def test_exts(zimuku):
    zimuku._check_exts(['ass'])
    with pytest.raises(ExtError):
        zimuku._check_exts(['fake_ext'])


def test_parse_download_count(zimuku):
    test_cases = {
        '100': 100,
        '1千': 1000,
        '10千': 10000,
        '5万': 50000,
        '2百万': 2000000
    }
    for text, count in test_cases.items():
        c = zimuku._parse_downloadcount(text)
        assert c == count

def test_parse(videofile: pathlib.Path):
    zimuku: ZimukuSubSearcher = ZimukuSubSearcher(SubsFinder())
    zimuku._prepare_search_subs(videofile)
    subinfo_list = zimuku._get_subinfo_list(zimuku.keywords[0])
    assert subinfo_list
    subinfo = subinfo_list[0]
    assert subinfo
    assert subinfo['title'] and subinfo['link'] and subinfo['exts'] and subinfo['languages']
