import os
import commands
import shutil
import time
import webbrowser
import argparse
import ConfigParser
from argparse import RawTextHelpFormatter

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

from libs.page import Page
from libs.website import Website


def main(args):
    website = Website(os.path.join(os.getcwd(), 'wiki'),
                      os.path.join(os.getcwd(), 'www'),
                      args.dev_url if args.action != 'deploy' else args.site_url)

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

    if not args.update_wiki:
        print '* Using existing wiki directory'
    else:
        # Download the wiki from github
        if os.path.isdir(website.source):
            shutil.rmtree(website.source)
        os.mkdir(website.source)
        print '* Downloading wiki from github ...'
        status, output = commands.getstatusoutput(
            'git clone %s %s' % (args.wiki_repository, website.source))
        if status is not 0:
            raise Exception('There was an error downloading the repository!\n%s' % output)

    website.generate_site()

    if args.action == 'serve':

        # Set a watchdog on markdown changes
        observer = Observer()
        observer.schedule(FileWatcher(), path=website.source, recursive=True)
        observer.start()

        try:
            webbrowser.open(args.dev_url)
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()

        observer.join()

    elif args.action == 'deploy':
        print "* Committing new webpage to gh-pages ..."
        status, output = commands.getstatusoutput('cd %s && ghp-import -p %s ' % (website.source, website.dest_web))
        if status is not 0:
            raise Exception('There was an error during upload of gh-pages!\n%s' % output)
        else:
            print 'Success!!'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Transforms github wikis into html static files that are pushed into the gh-pages branch',
        epilog='Enjoy your wiki!',
        formatter_class=RawTextHelpFormatter)

    parser.add_argument('-c', '--config_file',
                        help='Specify config file location (default: %(default)s)',
                        metavar='FILE',
                        default='ghw2ghp.conf',
                        nargs=1)

    args, remaining_argv = parser.parse_known_args()

    defaults = {}

    if args.config_file:
        config = ConfigParser.SafeConfigParser()
        config.read([args.config_file])
        try:
            defaults = dict(config.items('config'))
        except ConfigParser.NoSectionError:
            section = 'config'
            config.add_section(section)
            site_url = raw_input(
                'What is the site URL? [http://kiwi.franhp.net] ') or 'http://kiwi.franhp.net'
            dev_url = raw_input(
                'What is the URL that you have configured on Anvil? [http://www.dev] ') or 'http://www.dev'
            wiki_repo = raw_input(
                'What is the wiki repository? [git@github.com:franhp/wiki.git] ') or 'git@github.com:franhp/wiki.git'

            config.set(section, 'site_url', site_url)
            config.set(section, 'dev_url', dev_url)
            config.set(section, 'wiki_repository', wiki_repo)

            # And write it
            config.write(open('ghw2ghp.conf', 'wb'))

            # And try to fetch it again
            defaults = dict(config.items('config'))

    parser.set_defaults(**defaults)

    parser.add_argument('-u', '--update_wiki',
                        help='Redownloads the wiki from github',
                        default=False)

    modes_help = '''
    config      Runs the config helper
    serve       Recompiles the site when a change is detected in the wiki
    deploy      Pushes into gh-pages branch
    '''
    parser.add_argument('action',
                        nargs='?',
                        choices=('config', 'serve', 'deploy', 'commit'),
                        help=modes_help)


    args = parser.parse_args(remaining_argv)

    main(args)