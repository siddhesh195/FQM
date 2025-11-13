from app.middleware import gtranslator

def get_translation(text, language):
    """Translate text to the specified language using gtranslator."""

    translated = gtranslator.translate(text, dest=[language])

    return translated

