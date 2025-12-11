# translator_mock.py  (or put directly in your main.py / __init__.py)

from flask import current_app, request

class MockTranslator:
    def __init__(self, app=None):
        self.readonly = True
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.extensions['googletrans'] = self  # so get_translator() works if used
        # Register the filter globally
        app.jinja_env.globals['translate'] = self.translate
        app.jinja_env.filters['translate'] = self.translate

    def translate(self, text, target='en', source=None):
        """
        Mock translate function that just returns the text unchanged.
        Preserves your exact template syntax: translate('Text', 'en', [defLang])
        """
        # Even if someone passes a list like [defLang], we just ignore it
        return text

# Create global instance
gtranslator = MockTranslator()