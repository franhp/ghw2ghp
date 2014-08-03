from libs.plugins import WikiPlugins


class WikiPlugin(WikiPlugins):
    tag_name = 'livejs'
    active = True

    def website_tag(self, website_context):
        return '<script type="text/javascript" src="http://livejs.com/live.js"></script>'


