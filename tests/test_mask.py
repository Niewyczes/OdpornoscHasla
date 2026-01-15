from mask_test import MASK_CHARSETS

def test_mask_definitions():
    assert "?l" in MASK_CHARSETS
    assert "?u" in MASK_CHARSETS
    assert "?d" in MASK_CHARSETS
    assert "?s" in MASK_CHARSETS

def test_mask_sizes():
    assert len(MASK_CHARSETS["?l"]) == 26
    assert len(MASK_CHARSETS["?d"]) == 10
