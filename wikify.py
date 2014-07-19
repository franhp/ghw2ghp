import os
import errno
import shutil
import imp

from jinja2 import Environment, FileSystemLoader
import markdown
import git

import plugins


def process_file(filename, general_plugins):
    """
    Converts the markdown file into html
    """

    # Load file
    content = open(filename).readlines()

    # Find title
    if content[0].startswith('# '):
        title = content[0].replace('#', '').replace('\n', '').strip()
    else:
        title = filename.replace('.md', '')

    # And now the content of the page itself, discarding the title
    markdown_content = ''.join(content[1:])

    # Add plugins for the content of the markdowns
    for plugin_path in plugins.modules:
        c = imp.load_source('', plugin_path)
        if c.active and 'parse' in dir(c):
            markdown_content = c.parse(markdown_content)

    # Process the markdown
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
    page_content = md.convert(markdown_content)

    # And then fill all the tags
    processed_page = {
        'markdown': page_content,
        'title': title,
    }

    # Add plugins for extra tags
    for plugin_path in plugins.modules:
        c = imp.load_source('', plugin_path)
        if c.active and 'extra_tag' in dir(c):
            processed_page[c.name] = c.extra_tag(content)

    # And add the general plugins
    for key, value in general_plugins.items():
        processed_page[key] = value

    return processed_page


def get_or_create_web_path(root_path, file_name, source_dir, output_dir):
    """
    Converts markdown path into the path of the html file and creates it if necessary
    """
    separated_path = os.path.split(root_path)
    web_path = os.path.join(os.getcwd(), output_dir,
                            ''.join(separated_path[1:]) if separated_path[1] is not source_dir else '')

    if not os.path.exists(web_path):
        # mkdir -p
        try:
            os.makedirs(web_path)
        except OSError as e:
            if e.errno == errno.EEXIST and os.path.isdir(web_path):
                pass
            else:
                raise

    return os.path.join(web_path, file_name.replace('.md', '.html'))


def get_section_template(section_path, source_dir):
    """
    Returns the template name of the section
    """
    if section_path is source_dir:
        return 'index.html'
    else:
        return os.path.basename(os.path.normpath(section_path)) + '.html'


def convert_md_to_html(source, output):
    # Set default templates directory
    env = Environment(loader=FileSystemLoader(os.path.join(source, 'templates')))

    # Find all markdown files that need to be processed
    paths = []
    for root, dirs, files in os.walk(source):
        for name in files:
            if name.endswith('.md'):
                paths.append((root, name))

    # Any plugins that use all the content
    general_plugins = {}
    for plugin_path in plugins.modules:
        c = imp.load_source('', plugin_path)
        if c.active and 'general' in dir(c):
            general_plugins[c.name] = c.general(paths)

    # And finally output the html
    for root, name in paths:
        file_path = os.path.join(root, name)
        with open(get_or_create_web_path(root, name, source_dir=source, output_dir=output), 'ab') as f:
            # Using the section template render the markdown file into a file
            print '* Generating html file for [%s]' % file_path
            template = env.get_template(get_section_template(root, source))
            f.write(template.render(process_file(file_path, general_plugins)))
            f.close()


# Delete the previously generated files
try:
    shutil.rmtree(os.path.join(os.getcwd(), 'www'))
except OSError:
    print 'First time run!'

# Download the wiki from github
#git.Git().clone("git://gitorious.org/git-python/mainline.git").wiki

# Convert the site into html in www
convert_md_to_html('wiki', 'www')

# Commit it into gh-pages branch
#git.Git().checkout('gh-pages')
git.add
git.commit
git checkout master

