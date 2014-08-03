import os
import imp
import distutils.core
import shutil

from libs.page import Page

from libs.plugins import WikiPlugins


class Website:
    ignored_directories = ('static', 'templates', '.git')

    def __init__(self, source, dest_web, url):
        self.source = source
        self.dest_web = dest_web
        self.url = url
        self.website_plugins = self.run_website_plugins()
        self.sections = self.get_sections()
        self.tags = {'sections': self.sections, 'STATIC_URL': url + '/static/', 'URL': url}


    def get_sections(self):
        sections = []
        for directory in os.listdir(self.source):
            if os.path.isdir(os.path.join(self.source, directory)) \
                    and directory not in self.ignored_directories:
                sections.append(directory)
        return sections

    def run_website_plugins(self):
        plugins = {}
        for plugin_path in WikiPlugins.modules:
            c = imp.load_source(os.path.split(plugin_path)[1].replace('.py', ''), plugin_path)
            p = c.WikiPlugin()
            if p.active:
                try:
                    plugins[p.tag_name] = p.website_tag(self)
                except NotImplementedError:
                    pass
        return plugins

    def generate_site(self):
        # Convert the site into html in www
        print '* Generating all HTML files ...'

        for root, dirs, files in os.walk(self.source):
            for name in files:
                if name.endswith('.md'):
                    page = Page(os.path.join(root, name), self)
                    page.save_html()

        # Copy all other important files into the dest_web
        print('* Copying other important files ...')
        distutils.dir_util.copy_tree(os.path.join(self.source, 'static'), os.path.join(self.dest_web, 'static'))
        shutil.copy(os.path.join(self.source, 'CNAME'), os.path.join(self.dest_web, 'CNAME'))

