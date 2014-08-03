import imp
import os
import errno
import codecs

import markdown
from jinja2 import Environment, FileSystemLoader

from libs.plugins import WikiPlugins


class Page():
    def __init__(self, page_path, website):
        self.origin_page_path = page_path
        self.website = website
        self.source_root_path = website.source
        self.dest_root_path = website.dest_web

        self.all_content = codecs.open(page_path, encoding='utf-8').readlines()
        self.title = self.get_title()
        self.converted_html = self.get_converted_markdown()
        self.template = self.get_template()
        self.category_name = self.get_category()
        self.related_pages = self.get_related_pages()

    def get_title(self):
        """
        Find the first h1 in the file and return it as title, else return the filename
        """
        if self.all_content[0].startswith('# '):
            title = self.all_content[0].replace('#', '').replace('\n', '').strip()
        else:
            print('WARNING: Page [%s] does not follow standard structure of titling' % self.origin_page_path)
            title = os.path.split(self.origin_page_path)[1].replace('.md', '')

        return title

    def get_category(self):
        """
        Finds category of page based on the directory it is in
        """
        relative_path = self.origin_page_path.replace(self.source_root_path, '')
        if relative_path != '/' + os.path.split(self.origin_page_path)[1]:
            return relative_path.split(os.sep)[1]
        else:
            return ''

    def get_related_pages(self):
        """
        Finds pages in the same category
        """
        related_pages = []
        for md_file in os.listdir(os.path.split(self.origin_page_path)[0]):
            if md_file.endswith('.md'):
                section = '' if self.category_name == '' else self.category_name + '/'
                url = self.website.url + '/' + section + md_file.replace('.md', '.html')
                related_pages.append({'url': url,
                                      'name': md_file.replace('.md', '')})
        return related_pages

    def get_converted_markdown(self):
        """
        Generate the HTML code out of the markdown provided
        """
        md = markdown.Markdown(extensions=[
            'fenced_code',
            'codehilite',
            'toc',
            'smarty',
            'meta',
            'tables',
            'footnotes',
            'abbr',
            'wikilinks'
        ])

        # Check if the md files follows protocol
        if self.all_content[0].startswith('# '):
            content = md.convert(''.join(self.all_content[1:]))
        else:
            content = md.convert(''.join(self.all_content))
        return content

    def get_template(self):
        """
        Returns the template that should be used depending on the section
        """
        return os.path.split(self.origin_page_path)[0].split(os.sep)[-1:][0] + '.html'

    def get_or_create_web_path(self):
        """
        Converts markdown path into the path of the html file and creates it if necessary
        """
        web_path, filename = os.path.split(self.dest_root_path + self.origin_page_path.replace(self.source_root_path,  ''))

        if not os.path.exists(web_path):
            # mkdir -p
            try:
                os.makedirs(web_path)
            except OSError as e:
                if e.errno == errno.EEXIST and os.path.isdir(web_path):
                    pass
                else:
                    raise

        return os.path.join(web_path, filename.replace('.md', '.html'))

    def save_html(self):
        """
        Saves the HTML code to a file
        """
        env = Environment(loader=FileSystemLoader(os.path.join(self.source_root_path, 'templates')))
        file_path = self.get_or_create_web_path()
        with open(file_path, 'wb') as f:
            # Using the section template render the markdown file into a file
            print '* Saving html file for [%s] into [%s] ...' % (os.path.split(self.origin_page_path)[1], file_path)
            template = env.get_template(self.template)

            page = {
                'title': self.title,
                'markdown': self.converted_html,
                'related_pages': self.related_pages,
                'current_page': os.path.split(self.origin_page_path)[1].replace('.md', ''),
                'current_section': self.category_name
            }

            # Add in the plugins tags
            for k, v in self.run_page_plugins().items():
                page[k] = v

            # And then add the website ones
            for k, v in self.website.tags.items():
                page[k] = v

            for k, v in self.website.website_plugins.items():
                page[k] = v


            # Actually write the file
            f.write(template.render(page).encode('utf-8'))
            f.close()

    def run_page_plugins(self):
        tags = {}
        for plugin_path in WikiPlugins.modules:
            c = imp.load_source(os.path.split(plugin_path)[1].replace('.py', ''), plugin_path)
            p = c.WikiPlugin()
            if p.active:
                try:
                    tags[p.tag_name] = p.page_tag(self)
                except NotImplementedError:
                    pass
        return tags