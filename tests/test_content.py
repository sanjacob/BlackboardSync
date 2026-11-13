from pathlib import Path
from unittest import mock

from hypothesis import given
from hypothesis import assume

from blackboard.blackboard import (
    BBCourse,
    BBCourseContent,
    BBContentHandler,
    BBResourceType,
    BBAttachment,
    BBAvailability
)

from blackboard_sync.content import (
    BBContentPath,
    Course,
    Content,
    Folder,
    Document,
    Unhandled
)

from blackboard_sync.content.base import FStream


def assert_written(path, content):
    assert path.is_file()
    with path.open('r') as f:
        assert content == f.read()


def make_available(model):
    return model.model_copy(update={
        'availability': BBAvailability(available='Yes')
    })


def get_module(class_name):
    return 'blackboard_sync.content.content.' + class_name


def test_fstream_write(tmpdir):
    new_file_path = Path(tmpdir, 'my_new_file.txt')
    contents = 'whatever the file says\nincluding newlines'

    # Write a text file to disk
    assert not new_file_path.exists()

    content = FStream()
    content.write_base(new_file_path, mock.Mock(submit=lambda x: x()),
                       contents)

    assert new_file_path.is_file()

    with new_file_path.open('r') as f:
        assert contents == f.read()


@given(...)
def test_course_api_call(course: BBCourse):
    course = make_available(course)

    job = mock.Mock()
    job.session.fetch_contents.return_value = []

    Course(course, job)

    job.session.fetch_contents.assert_called_once_with(
        course_id=course.id
    )


@given(...)
def test_folder_api_call(api_path: BBContentPath):
    job = mock.Mock()
    job.session.fetch_content_children.return_value = []

    Folder(None, api_path, job)
    job.session.fetch_content_children.assert_called_once_with(**api_path)


@given(...)
def test_file_api_call(api_path: BBContentPath):
    job = mock.Mock()
    job.session.fetch_file_attachments.return_value = []

    Document(None, api_path, job)

    job.session.fetch_file_attachments.assert_called_once_with(
        **api_path
    )


@given(...)
def test_children_course(course: BBCourse, contents: list[BBCourseContent]):
    job = mock.Mock()
    job.session.fetch_contents.return_value = contents

    course = make_available(course)

    calls = []
    for content in contents:
        api_path = BBContentPath(course_id=course.id, content_id=content.id)
        calls.append(mock.call(content, api_path, job))

    with mock.patch('blackboard_sync.content.course.Content') as p:
        Course(course, job)
        p.assert_has_calls(calls)


@given(...)
def test_children_folder(api_path: BBContentPath,
                         children: list[BBCourseContent]):
    job = mock.Mock()
    job.session.fetch_content_children.return_value = children

    calls = []
    for child in children:
        api_path = BBContentPath(course_id=api_path.get('course_id'),
                                 content_id=child.id)
        calls.append(mock.call(child, api_path, job))

    with mock.patch('blackboard_sync.content.folder.content.Content') as p:
        Folder(None, api_path, job)
        p.assert_has_calls(calls)


@given(...)
def test_children_file(api_path: BBContentPath,
                       attachments: list[BBAttachment]):
    job = mock.Mock()
    job.session.fetch_file_attachments.return_value = attachments

    calls = []

    # Setup calls
    for att in attachments:
        if att.mimeType is not None:
            assume(not att.mimeType.startswith("video/"))
            assume(not att.mimeType == '*')

        calls.append(mock.call(att, api_path, job))

    with mock.patch('blackboard_sync.content.document.Attachment') as p:
        Document(None, api_path, job)
        p.assert_has_calls(calls)


@given(...)
def test_content_folder(api_path: BBContentPath):
    job = mock.Mock()
    job.has_changed.return_value = True

    content = mock.MagicMock()
    content.contentHandler = BBContentHandler(id=BBResourceType.Folder)
    content.availability = True
    content.id = api_path['content_id']
    content.body = False

    with mock.patch(get_module('folder.Folder')) as p:
        Content(content, api_path, job)
        p.assert_called_once_with(content, api_path, job)


@given(...)
def test_content_file(api_path: BBContentPath):
    job = mock.Mock()
    job.has_changed.return_value = True

    content = mock.MagicMock()
    content.contentHandler = BBContentHandler(id=BBResourceType.Document)
    content.availability = True
    content.id = api_path['content_id']
    content.body = False

    with mock.patch(get_module('document.Document')) as p:
        Content(content, api_path, job)
        p.assert_called_once_with(content, api_path, job)


@given(...)
def test_content_link(api_path: BBContentPath):
    job = mock.Mock()
    job.has_changed.return_value = True

    content = mock.MagicMock()
    content.contentHandler = BBContentHandler(id=BBResourceType.ExternalLink)
    content.availability = True
    content.id = api_path['content_id']
    content.body = False

    with mock.patch(get_module('externallink.ExternalLink')) as p:
        Content(content, api_path, job)
        p.assert_called_once_with(content, api_path, job)


@given(...)
def test_content_unhandled(api_path: BBContentPath):
    job = mock.Mock()
    job.has_changed.return_value = True

    content = mock.MagicMock()
    content.contentHandler = BBContentHandler(id=BBResourceType.Blankpage)
    content.availability = True
    content.id = api_path['content_id']
    content.body = False

    with mock.patch(get_module('unhandled.Unhandled')) as p:
        Content(content, api_path, job)
        p.assert_called_once_with(content, api_path, job)


def test_unhandled():
    executor = mock.Mock()

    content = Unhandled(mock.Mock(title="Content title"), None, mock.Mock())
    content.write(None, executor)
    executor.submit.assert_not_called()


def make_child(title, ignore=False):
    child = mock.Mock()
    child.title = title
    child.ignore = ignore
    return child


def test_folder_write_collapses_single_child_with_same_title(tmpdir):
    """A folder whose only child shares its own title (how
    Blackboard models a folder's single "page") should be written
    directly into the folder, instead of creating a redundant
    nested folder with the same name."""
    executor = mock.Mock()
    path = Path(tmpdir, 'Lecture notes')

    folder = Folder.__new__(Folder)
    folder.children = [make_child('Lecture notes')]
    folder.write(path, executor)

    folder.children[0].write.assert_called_once_with(Path(tmpdir), executor)


def test_folder_write_does_not_collapse_different_title(tmpdir):
    executor = mock.Mock()
    path = Path(tmpdir, 'Lecture notes')

    folder = Folder.__new__(Folder)
    folder.children = [make_child('Lect01.pdf')]
    folder.write(path, executor)

    folder.children[0].write.assert_called_once_with(path, executor)


def test_folder_write_does_not_collapse_multiple_children(tmpdir):
    executor = mock.Mock()
    path = Path(tmpdir, 'Lecture notes')

    folder = Folder.__new__(Folder)
    folder.children = [make_child('Lecture notes'), make_child('Other.pdf')]
    folder.write(path, executor)

    for child in folder.children:
        child.write.assert_called_once_with(path, executor)


def test_folder_write_does_not_collapse_ignored_child(tmpdir):
    """Even if the title matches, an ignored child has no `.title`
    attribute set (see Content.__init__), so it must not be used to
    decide whether to collapse the folder."""
    executor = mock.Mock()
    path = Path(tmpdir, 'Lecture notes')

    folder = Folder.__new__(Folder)
    folder.children = [make_child('Lecture notes', ignore=True)]
    folder.write(path, executor)

    folder.children[0].write.assert_called_once_with(path, executor)
