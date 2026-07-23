from utils import format_name


def test_basic_format():
    fmt = "{title} - S{season:02}E{episode:02} [{quality}].{ext}"

    fields = {
        "title": "Test",
        "season": 1,
        "episode": 2,
        "quality": "720p",
        "ext": "mkv",
    }

    out = format_name(fmt, fields)

    assert "S01E02" in out
    assert out.endswith(".mkv")