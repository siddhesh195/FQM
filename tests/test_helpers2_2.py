import pytest



@pytest.mark.usefixtures('c')
def test_get_translation():
    from app.helpers2 import get_translation

    text = "Hello"
    language = "es"
    result = get_translation(text, language)
    assert result == text  # Since the function currently returns the same text

@pytest.mark.usefixtures('c')
def test_to_bool():
    from app.helpers2 import to_bool

    assert to_bool("true") is True
    