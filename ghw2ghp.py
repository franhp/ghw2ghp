import os
import commands
import shutil
import time
import webbrowser

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

from libs.page import Page
from libs.website import Website


website = Website(os.path.join(os.getcwd(), 'wiki'), os.path.join(os.getcwd(), 'www'), 'http://www.dev')


class FileWatcher(PatternMatchingEventHandler):
    patterns = ['*']

    def on_created(self, event):
        if event.src_path.endswith('.md'):
            p = Page(event.src_path, website)
            p.save_html()
        else:
            website.generate_site()


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


website.generate_site()

if True: # TODO actually do the check

    # Set a watchdog on markdown changes
    observer = Observer()
    observer.schedule(FileWatcher(), path=website.source, recursive=True)
    observer.start()

    try:
        webbrowser.open('http://www.dev/')
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()


    observer.join()

else:
    print "* Committing new webpage to gh-pages ..."
    status, output = commands.getstatusoutput('cd %s && ghp-import -p %s ' % (website.source, website.dest_web))
    if status is not 0:
        raise Exception('There was an error during upload of gh-pages!\n%s' % output)
    else:
        print 'Success!!'


