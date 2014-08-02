from libs.plugins import WikiPlugins


class WikiPlugin(WikiPlugins):
    tag_name = 'site_structure'
    active = True

    def extra_tag(self, context):
        return {'section1': ['page1', 'page2'], 'section2': ['page3', 'page4', 'page5']}