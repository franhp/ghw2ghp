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

source = os.path.join(os.getcwd(), 'wiki')
dest_web = os.path.join(os.getcwd(), 'www')


class FileWatcher(PatternMatchingEventHandler):
    patterns = ['*']

    def on_created(self, event):
        if event.src_path.endswith('.md'):
            p = Page(event.src_path, source, dest_web)
            p.save_html()



# Delete the previously generated files
try:
    shutil.rmtree(dest_web)
except OSError:
    pass


if True: # TODO actually do the check
    print '* Using existing wiki directory'
else:
    # Download the wiki from github
    if os.path.isdir(source):
        shutil.rmtree(source)
    os.mkdir(source)
    print '* Downloading wiki from github ...'
    status, output = commands.getstatusoutput('git clone %s %s' % ('git@github.com:franhp/wiki.git', source))
    if status is not 0:
        raise Exception('There was an error downloading the repository!\n%s' % output)


# Convert the site into html in www
print '* Generating all HTML files ...'

for root, dirs, files in os.walk(source):
        for name in files:
            if name.endswith('.md'):
                page = Page(os.path.join(root, name), source, dest_web)
                page.save_html()

# Copy all other important files into the dest_web
print('* Copying other important files ...')
distutils.dir_util.copy_tree(os.path.join(source, 'static'), os.path.join(dest_web, 'static'))
shutil.copy(os.path.join(source, 'CNAME'), os.path.join(dest_web, 'CNAME'))


if True: # TODO actually do the check

    # Set a watchdog on markdown changes
    observer = Observer()
    observer.schedule(FileWatcher(), path=source, recursive=True)
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
    status, output = commands.getstatusoutput('cd %s && ghp-import -p %s ' % (source, dest_web))
    if status is not 0:
        raise Exception('There was an error during upload of gh-pages!\n%s' % output)
    else:
        print 'Success!!'


