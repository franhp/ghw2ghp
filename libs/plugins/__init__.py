import os
import glob


class WikiPlugins:
    tag_name = 'please-overwrite'
    active = False
    modules = [f for f in glob.glob(os.path.dirname(__file__)+"/*.py") if '__init__' not in f]

    def __init__(self):
        pass

    def extra_tag(self, context):
        raise NotImplementedError()

    def parse(self, context):
        raise NotImplementedError()