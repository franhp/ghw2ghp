from libs.plugins import WikiPlugins


class WikiPlugin(WikiPlugins):
    tag_name = 'livejs'
    active = True

    def extra_tag(self, context):
        return '<script type="text/javascript" src="http://livejs.com/live.js"></script>'


