from libs.plugins import WikiPlugins


class WikiPlugin(WikiPlugins):
    tag_name = 'search'
    active = False

    def website_tag(self, website_context):
        return ''