#! /usr/bin/env python

from __future__ import unicode_literals, print_function
import os
import pytest
import pathlib
import re
import subprocess
from subsfinder.subsfinder import SubsFinder
from subsfinder.subsearcher import get_subsearcher
from subsfinder.utils import rm_subtitles

test_dir = '~/Downloads/subsfinder_test/'


def test_search_subs_by_shooter():
    directory = os.path.expanduser(test_dir)
    if not os.path.exists(directory):
        pytest.skip('test directory not exists')
    rm_subtitles(directory)
    subfinder = SubsFinder(path=directory, subsearcher_class=get_subsearcher('shooter'), debug=True)
    subfinder.start()
    files = [f for f in os.listdir(directory) if f.endswith('.ass') or f.endswith('.srt')]
    assert len(files) >= 0


@pytest.fixture(scope='module')
def videofile(tmp_path_factory) -> pathlib.Path:
    videofile = tmp_path_factory.mktemp('subsfinder_test') / 'Yellowstone.2018.S03E04.1080p.WEB.H264-METCON.mkv'
    videofile.touch()
    return videofile


@pytest.fixture(scope="module")
def conf_file(tmp_path_factory: pathlib.Path) -> pathlib.Path:
    conf = '''
    {
        "method": ["zimuku", "zimuzu", "subhd"],
        "api_urls": {
            "zimuku": "http://www.zimuku.la/search/",
            "subhd": "https://subhd.tv/search/",
            "subhd_api_subtitle_download": "/ajax/down_ajax/",
            "subhd_api_subtitle_preview": "/ajax/file_ajax/"
        }
    }
    '''
    conf_file = tmp_path_factory.mktemp('subsfinder_conf') / 'subsfinder.json'
    conf_file.write_text(conf)
    return conf_file


def test_search_subs_by_zimuku(videofile: pathlib.Path):
    parent = videofile.parent
    rm_subtitles(parent)
    sc = get_subsearcher('zimuku')
    subsfinder = SubsFinder(path=videofile, subsearcher_class=sc, debug=True)
    subsfinder.start()
    exts = sc.SUPPORT_EXTS
    files = [f for f in parent.iterdir() if f.suffix[1:] in exts]
    assert len(files) >= 0



def test_search_subs_by_subhd(videofile: pathlib.Path):
    parent = videofile.parent
    rm_subtitles(parent)
    sc = get_subsearcher('subhd')
    subsfinder = SubsFinder(path=videofile, subsearcher_class=sc, debug=True)
    subsfinder.start()
    exts = sc.SUPPORT_EXTS
    files = [f for f in parent.iterdir() if f.suffix[1:] in exts]
    assert len(files) >= 0


PATTERN = re.compile(r'下载 (\d+) 个字幕')


def check_cmd_output(cmd):
    p = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
    output = p.stdout.decode('utf8')
    assert p.returncode == 0
    assert '[ERROR]' not in output
    m = PATTERN.search(output)
    n = int(m.group(1)) if m else 0
    return n


def test_run_from_cmd(videofile: pathlib.Path):
    parent = videofile.parent
    rm_subtitles(parent)
    cmd = 'subsfinder {} -m zimuku subhd'.format(videofile)
    n = check_cmd_output(cmd)
    assert n > 0

def test_cmd_option_exclude(videofile: pathlib.Path):
    parent = videofile.parent
    rm_subtitles(parent)
    cmd = 'subsfinder {} -m zimuku -x Yellowstone*.mkv'.format(videofile)
    n = check_cmd_output(cmd)
    assert n == 0


def test_cmd_option_ignore(videofile: pathlib.Path):
    parent = videofile.parent
    rm_subtitles(parent)
    subtitle = videofile.with_suffix('.ass')
    subtitle.touch()
    cmd = 'subsfinder {} -m zimuku --ignore'.format(videofile)
    n = check_cmd_output(cmd)
    assert n > 0


def test_cmd_option_conf_and_api_urls(videofile, conf_file: pathlib.Path):
    parent = videofile.parent
    rm_subtitles(parent)
    cmd = 'subfinder {} --conf {}'.format(videofile, conf_file)
    n = check_cmd_output(cmd)
    assert n > 0


def test_cmd_option_video_exts(tmp_path: pathlib.Path):
    videofile = tmp_path / 'Yellowstone.2018.S03E04.1080p.WEB.H264-METCON.fake_ext'
    videofile.touch()
    cmd = 'subsfinder {} --video_exts {} -m zimuku'.format(videofile, '.fake_ext')
    n = check_cmd_output(cmd)
    assert n > 0


def test_cmd_option_keyword(videofile: pathlib.Path):
    parent = videofile.parent
    rm_subtitles(parent)
    cmd = 'subsfinder {} -m zimuku -k Yellowstone.2018.S03E04'.format(videofile)
    n = check_cmd_output(cmd)
    assert n > 0


def test_cmd_option_languages(videofile: pathlib.Path):
    parent = videofile.parent
    rm_subtitles(parent)
    cmd = 'subsfinder {} -m zimuku -l zh_chs'.format(videofile)
    n = check_cmd_output(cmd)
    assert n > 0


def test_cmd_option_exts(videofile: pathlib.Path):
    parent = videofile.parent
    rm_subtitles(parent)
    cmd = 'subsfinder {} -m zimuku -e ass --debug'.format(videofile)
    n = check_cmd_output(cmd)
    assert n > 0
