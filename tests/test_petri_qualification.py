"""Actual PM4Py comparison, plus independently authored marking controls."""

from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, tostring

from scripts.qualify_petri_nets import compare_net, corpus

ROOT = Path(__file__).resolve().parents[1]


def net_file(path, transitions):
    root = Element("pnml")
    net = SubElement(root, "net", id="synthetic", type="http://www.pnml.org/version-2009/grammar/pnmlcoremodel")
    page = SubElement(net, "page", id="page")
    places = {"source", "sink"} | {p for left, right in transitions.values() for p in (*left, *right)}
    for p in sorted(places):
        node = SubElement(page, "place", id=p)
        if p == "source":
            SubElement(SubElement(node, "initialMarking"), "text").text = "1"
    count = 0
    for t, (left, right) in transitions.items():
        SubElement(page, "transition", id=t)
        for p, weight in left.items():
            arc = SubElement(page, "arc", id=f"a{count}", source=p, target=t)
            SubElement(SubElement(arc, "inscription"), "text").text = str(weight)
            count += 1
        for p, weight in right.items():
            arc = SubElement(page, "arc", id=f"a{count}", source=t, target=p)
            SubElement(SubElement(arc, "inscription"), "text").text = str(weight)
            count += 1
    final = SubElement(SubElement(net, "finalmarkings"), "marking")
    SubElement(SubElement(final, "place", idref="sink"), "text").text = "1"
    path.write_bytes(tostring(root, encoding="utf-8"))
    return path


def test_all_maintained_nets_are_independently_compared():
    result = corpus(ROOT)
    assert len(result["nets"]) >= 22
    assert all(row["matched"] for row in result["nets"])
    assert all(row["status"] in {"sound_in_scope", "unsound"} for row in result["nets"])


def test_weighted_concurrency_and_loop(tmp_path):
    path = net_file(tmp_path / "parallel.pnml", {
        "split": ({"source": 1}, {"left": 2, "right": 1}),
        "loop": ({"right": 1}, {"right": 1}),
        "left-step": ({"left": 2}, {"done": 1}),
        "join": ({"done": 1, "right": 1}, {"sink": 1}),
    })
    result = compare_net(path)
    assert result["matched"]
    assert result["status"] == "sound_in_scope"
    assert result["states"] == 4


def test_deadlock_and_unbounded_growth(tmp_path):
    path = net_file(tmp_path / "deadlock.pnml", {
        "finish": ({"source": 1}, {"sink": 1}),
        "fail": ({"source": 1}, {"trap": 1}),
    })
    result = compare_net(path)
    assert result["matched"]
    assert result["status"] == "unsound"
    assert result["deadlocks"] == 1
    growth = net_file(tmp_path / "grow.pnml", {
        "grow": ({"source": 1}, {"source": 2}),
        "finish": ({"source": 1}, {"sink": 1}),
    })
    result = compare_net(growth, max_tokens=3)
    assert result["matched"]
    assert result["status"] == "held_limit"
