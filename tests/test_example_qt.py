import pytest
from PyQt5.QtWidgets import QWidget
from blackboard_sync.qt import SettingsWindow

@pytest.fixture
def window_a():
    window = SettingsWindow()
    window.show()
    return window

@pytest.fixture
def window_b():
    window = SettingsWindow()
    return window

def test_normal(qtbot):
    window = SettingsWindow()
    window.show()

    qtbot.addWidget(window)

def test_fixture_a(qtbot, window_a):
    qtbot.addWidget(window_a)

def test_fixture_b(qtbot, window_b):
    window_b.show()
    qtbot.addWidget(window_b)

def test_fixture_c(qtbot, window_b):
    qtbot.addWidget(window_b)
    print(window_b.__dict__)