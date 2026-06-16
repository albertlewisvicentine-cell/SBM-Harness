import pytest

from sbm_harness.renderer import DriftRenderer, generate_fault_bloom_events


class FakeCell:
    def __init__(self):
        self.value = None
        self.fill = None


class FakeSheet:
    def __init__(self):
        self._cells = {}

    def __getitem__(self, cell_ref):
        if cell_ref not in self._cells:
            self._cells[cell_ref] = FakeCell()
        return self._cells[cell_ref]


def test_topology_wiring_uses_anchor_offset():
    renderer = DriftRenderer(FakeSheet(), topology_shape=(2, 3), anchor_cell="C4")

    assert renderer.map_index_to_cell(0) == "C4"
    assert renderer.map_index_to_cell(1) == "D4"
    assert renderer.map_index_to_cell(3) == "C5"
    assert renderer.map_index_to_cell(5) == "E5"


def test_render_applies_heatmap_values_and_colors():
    sheet = FakeSheet()
    renderer = DriftRenderer(sheet, topology_shape=(1, 3))

    renderer.render([-1.0, 0.0, 1.0])

    assert sheet["A1"].value == -1.0
    assert sheet["B1"].value == 0.0
    assert sheet["C1"].value == 1.0

    # openpyxl fallback shape when dependency is unavailable
    if isinstance(sheet["A1"].fill, dict):
        assert sheet["A1"].fill["rgb"] == (0, 0, 255)
        assert sheet["B1"].fill["rgb"] == (255, 255, 255)
        assert sheet["C1"].fill["rgb"] == (255, 0, 0)


def test_replay_processes_incremental_events_and_throttles():
    sheet = FakeSheet()
    renderer = DriftRenderer(sheet, topology_shape=(1, 2))

    now = [0.0]
    sleeps = []

    def fake_clock():
        return now[0]

    def fake_sleep(delay):
        sleeps.append(delay)
        now[0] += delay

    rendered = renderer.replay(
        [
            {"updates": [{"index": 0, "drift": 1.0}]},
            {"updates": [{"index": 1, "drift": 0.5}]},
            {"updates": [{"index": 0, "drift": 0.2}]},
        ],
        fps=2.0,
        sleep_fn=fake_sleep,
        clock_fn=fake_clock,
    )

    assert rendered == 3
    assert sleeps == pytest.approx([0.5, 0.5, 0.5])
    assert sheet["A1"].value == 0.2
    assert sheet["B1"].value == 0.5


def test_fault_bloom_stream_peaks_at_epicenter():
    events = generate_fault_bloom_events((3, 3), epicenter_index=4, frames=2, peak_drift=1.0)

    first = events[0]["drift_field"]
    assert len(first) == 9
    assert first[4] == pytest.approx(1.0)
    assert first[4] > first[0]
