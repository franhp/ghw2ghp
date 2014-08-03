import os
import glob


class WikiPlugins:
    tag_name = 'please-overwrite'
    active = False
    modules = [f for f in glob.glob(os.path.dirname(__file__)+"/*.py") if '__init__' not in f]

    def __init__(self):
        pass

    def page_tag(self, context):
        raise NotImplementedError()

    def website_tag(self, context):
        raise NotImplementedError()

    def parse(self, context):
        raise NotImplementedError()
