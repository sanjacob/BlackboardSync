from bs4 import BeautifulSoup
from requests.structures import CaseInsensitiveDict

from blackboard_sync.content.webdav import (
    ContentParser,
    filename_from_bbfile,
    filename_from_disposition,
)


def make_tag(html: str):
    return BeautifulSoup(html, 'html.parser').find()


def test_filename_from_disposition_plain():
    headers = CaseInsensitiveDict(
        {'Content-Disposition': 'attachment; filename="Lect01.pdf"'}
    )
    assert filename_from_disposition(headers) == 'Lect01.pdf'


def test_filename_from_disposition_rfc5987():
    headers = CaseInsensitiveDict({
        'Content-Disposition': "inline; filename*=UTF-8''Lect%2001.pdf"
    })
    assert filename_from_disposition(headers) == 'Lect 01.pdf'


def test_filename_from_disposition_missing():
    assert filename_from_disposition(CaseInsensitiveDict()) is None


def test_filename_from_bbfile_link_name():
    el = make_tag('<a data-bbfile=\'{"linkName": "syll_ProbI.pdf"}\'>x</a>')
    assert filename_from_bbfile(el) == 'syll_ProbI.pdf'


def test_filename_from_bbfile_display_name_fallback():
    el = make_tag(
        '<a data-bbfile=\'{"displayName": "Preliminaries.pdf"}\'>x</a>'
    )
    assert filename_from_bbfile(el) == 'Preliminaries.pdf'


def test_filename_from_bbfile_missing():
    el = make_tag('<a>x</a>')
    assert filename_from_bbfile(el) is None


def test_filename_from_bbfile_invalid_json():
    el = make_tag("<a data-bbfile='not json'>x</a>")
    assert filename_from_bbfile(el) is None


def test_content_parser_prefers_bbfile_name_over_url():
    html = '''
    <a href="https://bb.example.com/bbcswebdav/xid-123_1?sig=abc"
       data-bbfile='{"linkName":"syll_ProbI.pdf"}'>Syllabus</a>
    '''
    parser = ContentParser(html, 'https://bb.example.com')
    links = parser.links

    assert len(links) == 1
    assert links[0].text == 'syll_ProbI.pdf'


def test_content_parser_falls_back_to_url_filename():
    html = '<a href="https://bb.example.com/path/to/file.pdf">link</a>'
    parser = ContentParser(html, 'https://bb.example.com')
    links = parser.links

    assert len(links) == 1
    assert links[0].text == 'file.pdf'


def test_content_parser_strips_query_string_from_url_filename():
    html = (
        '<a href="https://bb.example.com/bbcswebdav/xid-123_1'
        '?sig=abc&exp=456">link</a>'
    )
    parser = ContentParser(html, 'https://bb.example.com')
    links = parser.links

    assert len(links) == 1
    assert links[0].text == 'xid-123_1'
