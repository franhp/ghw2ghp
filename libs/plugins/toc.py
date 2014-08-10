from libs.plugins import WikiPlugins


class WikiPlugin(WikiPlugins):
    tag_name = 'toc' # Not required
    active = True

    def parse(self, page_context):
        if '## ' not in page_context:
            print '** TOC not necessary ...'
            return page_context
        if '[TOC]' in page_context:
            print '** TOC already existing, not adding it on purpose ...'
            return page_context
        else:
            return '# Table of contents\n[TOC]\n***\n' + page_context