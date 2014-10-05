import os
from datetime import datetime
from time import mktime

import git

from libs.plugins import WikiPlugins


class WikiPlugin(WikiPlugins):
    tag_name = 'recent_articles'
    active = True

    def website_tag(self, website_context):
        response = []

        # Avoid when creating
        if not os.path.exists(website_context.source):
            return response

        # Search all files in the last 10 commits
        repo = git.Repo(website_context.source)
        commits = repo.commits(max_count=10)
        commits_contents = []
        for commit in commits:
            commit_files = repo.git.show(commit.parents[0], pretty='format:', name_only=True).split('\n')
            for commit_file in commit_files:
                commits_contents.append(
                    (commit_file, commit.committed_date)
                )

        # Match them against the actual files
        for committed_file, commit_date in reversed(sorted(commits_contents, key=lambda x: x[1])):
            if not committed_file.startswith('templates') \
                    and not committed_file.startswith('static') \
                    and committed_file != '' \
                    and '/' in committed_file \
                    and os.path.exists(os.path.join(website_context.source, committed_file)):
                response.append({'link': committed_file.replace('.md', '.html'),
                                 'date': datetime.fromtimestamp(mktime(commit_date)),
                                 'file': committed_file.split('/')[1].replace('.md', '')
                })
        return response