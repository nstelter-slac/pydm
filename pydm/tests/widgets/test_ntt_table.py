import pytest
import numpy as np
from pydm.widgets.nt_table import PyDMNTTable


def test_construct(qtbot):
    """
    Test that PyDMNTTable initializes without error.
    """
    widget = PyDMNTTable()
    qtbot.addWidget(widget)
    assert widget._read_only is True
    assert widget._model is None
    assert widget._table is not None


def test_value_changed_with_labels_and_values(qtbot):
    widget = PyDMNTTable()
    qtbot.addWidget(widget)

    data = {
        "labels": ["A", "B", "C"],
        "value": {
            "A": [1, 2, 3],
            "B": [4, 5, 6],
            "C": [7, 8, 9],
        },
    }

    widget.value_changed(data)

    assert widget._model is not None
    assert widget._table_labels == ["A", "B", "C"]
    assert widget._table_values == [(1, 4, 7), (2, 5, 8), (3, 6, 9)]


def test_value_changed_without_labels(qtbot):
    widget = PyDMNTTable()
    qtbot.addWidget(widget)

    data = {
        "A": [10, 20],
        "B": [30, 40],
    }

    widget.value_changed(data)

    assert sorted(widget._table_labels) == ["A", "B"]
    assert widget._model is not None
    assert isinstance(widget._table_values, list)
    assert widget._model.rowCount(None) == 2


def test_value_changed_invalid_data_type(qtbot, caplog):
    widget = PyDMNTTable()
    qtbot.addWidget(widget)

    # Non-iterable values will cause a TypeError
    data = {
        "labels": ["A"],
        "A": 42,
    }

    widget.value_changed(data)

    assert "NTTable value items must be iterables." in caplog.text


def test_send_table_boolean_conversion(qtbot, mocker):
    widget = PyDMNTTable()
    qtbot.addWidget(widget)

    widget._table_labels = ["Flag"]
    widget.value = {"Flag": np.array([True, False]), "labels": ["Flag"]}

    emit_mock = mocker.patch.object(widget.send_value_signal[dict], "emit")
    widget.send_table(0, 0, "False")

    assert widget.value["Flag"][0] is False
    emit_mock.assert_called_once()
    assert emit_mock.call_args[0][0] == {"value": {"Flag": [False, False]}}


def test_send_table_string_value(qtbot, mocker):
    widget = PyDMNTTable()
    qtbot.addWidget(widget)

    widget._table_labels = ["Name"]
    widget.value = {"Name": ["Alice", "Bob"], "labels": ["Name"]}

    emit_mock = mocker.patch.object(widget.send_value_signal[dict], "emit")
    widget.send_table(1, 0, "Charlie")

    assert widget.value["Name"][1] == "Charlie"
    emit_mock.assert_called_once()
    assert emit_mock.call_args[0][0] == {"value": {"Name": ["Alice", "Charlie"]}}


def test_check_enable_state_sets_tooltip(qtbot):
    widget = PyDMNTTable()
    qtbot.addWidget(widget)

    widget.setToolTip("Hello")
    widget.check_enable_state()

    assert "Read-Only" in widget.toolTip()
