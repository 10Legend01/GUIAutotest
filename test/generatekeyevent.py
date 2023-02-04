from ..methods import *


def test_generatekeyevent(text):
    assert isinstance(text, str)

    assert ldtp.generatekeyevent(text)
