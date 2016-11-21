# -*- coding: utf-8 -*-
'''
TODO
0. Write unit tests for these methods.
1. Fetch/update if there hasn't been one in a given period of time (an hr?).
2. Store data on conflicts in a class that says which branch(es) each file
   conflict is with.
3. Turn this into a Sublime plugin.
'''

from datetime import datetime, timedelta
from pygit2 import Repository, GIT_BRANCH_REMOTE

CUTOFF_TIME_IN_DAYS = 7

class MergeBliss:
    def __init__(self, path):
        '''
        Using the specified path (presumably to a git repository):
        1. Create a repo from that path.
        2. Store the repo's current head commit.
        3. Translate CUTOFF_TIME_IN_DAYS to a fixed datetime.
        4. Set self.remote_branch_commits to the current set of remote branches.
        5. Create a blank set of conflicting files.
        '''
        self.repo = Repository(path)
        self.head_commit = self.repo.revparse_single(self.repo.head.target.hex)
        self.cutoff_time = datetime.today() - timedelta(days = CUTOFF_TIME_IN_DAYS)
        self.set_remote_branches()
        self.conflicting_files = set()

    def set_remote_branches(self):
        '''
        Set self.remote_branch_commits to a list of the commits tipping all the remote
        branches, sorted most recently modified first, and excluding those
        commits that are more than CUTOFF_TIME_IN_DAYS old.
        '''
        remote_branch_names = self.repo.listall_branches(GIT_BRANCH_REMOTE)
        self.remote_branch_commits = [self.repo.revparse_single(branch_name) for branch_name in remote_branch_names]
        self.remote_branch_commits = [branch for branch in self.remote_branch_commits if branch.commit_time >= self.cutoff_time.timestamp()]
        self.remote_branch_commits.sort(key=lambda x: x.commit_time, reverse=True)

    def update_conflicting_files(self):
        '''
        Add the path of each file that has a pairwise conflict between HEAD
        and the remote branches.
        '''
        for remote_branch_commit in self.remote_branch_commits:
            merge_base = self.repo.merge_base(self.head_commit.id, remote_branch_commit.id)
            index = self.repo.merge_trees(merge_base, self.head_commit.id, remote_branch_commit.id)
            if index.conflicts:
                ## Add our file path to conflicting files.
                self.conflicting_files.update([x[1].path for x in index.conflicts])

if __name__ == "__main__":
    bliss = MergeBliss('.')
    bliss.update_conflicting_files()
    if bliss.conflicting_files:
        for conflicting_file in bliss.conflicting_files:
            print(conflicting_file)
