import os
import commands
import shutil
import distutils.core

import SimpleHTTPServer
import SocketServer
import webbrowser

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

from libs.page import Page
from libs.website import Website


website = Website(os.path.join(os.getcwd(), 'wiki'), os.path.join(os.getcwd(), 'www'))


class FileWatcher(PatternMatchingEventHandler):
    patterns = ['*']

    def on_created(self, event):
        if event.src_path.endswith('.md'):
            p = Page(event.src_path, website)
            p.save_html()
        else:
            generate_site()


# Delete the previously generated files
try:
    shutil.rmtree(website.dest_web)
except OSError:
    pass


if True: # TODO actually do the check
    print '* Using existing wiki directory'
else:
    # Download the wiki from github
    if os.path.isdir(website.source):
        shutil.rmtree(website.source)
    os.mkdir(website.source)
    print '* Downloading wiki from github ...'
    status, output = commands.getstatusoutput('git clone %s %s' % ('git@github.com:franhp/wiki.git', website.source))
    if status is not 0:
        raise Exception('There was an error downloading the repository!\n%s' % output)


def generate_site():
    # Convert the site into html in www
    print '* Generating all HTML files ...'

    for root, dirs, files in os.walk(website.source):
            for name in files:
                if name.endswith('.md'):
                    page = Page(os.path.join(root, name), website)
                    page.save_html()

    # Copy all other important files into the dest_web
    print('* Copying other important files ...')
    distutils.dir_util.copy_tree(os.path.join(website.source, 'static'), os.path.join(website.dest_web, 'static'))
    shutil.copy(os.path.join(website.source, 'CNAME'), os.path.join(website.dest_web, 'CNAME'))


generate_site()

if True: # TODO actually do the check

    # Set a watchdog on markdown changes
    observer = Observer()
    observer.schedule(FileWatcher(), path=website.source, recursive=True)
    observer.start()

    try:
        print 'Starting web server http://localhost:8080/www/ ...'
        Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
        httpd = SocketServer.TCPServer(('', 8080), Handler)
        webbrowser.open('http://localhost:8080/www/')
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.shutdown()
        observer.stop()

    observer.join()

else:
    print "* Committing new webpage to gh-pages ..."
    status, output = commands.getstatusoutput('cd %s && ghp-import -p %s ' % (website.source, website.dest_web))
    if status is not 0:
        raise Exception('There was an error during upload of gh-pages!\n%s' % output)
    else:
        print 'Success!!'


