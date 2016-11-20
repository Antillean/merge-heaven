# -*- coding: utf-8 -*-
import re

'''
The aim of this is to be used in a text editor or IDE plugin that lets you know
if you and a colleague are introducing conflicting code. "Conflicting code" is
defined as either:
    1. A merge conflict, or
    2. A potential conflict.
We find a merge conflict using git merge-tree. This tells you if files as of
the head of your branch will conflict with files in another branch. The
correspondind git command is

git merge-tree $(git merge-base HEAD branch_other) HEAD branch_other

The find_conflicting_file_paths takes a file containing output from that 
git command and returns a list of file paths with conflicts in them. 

TODO: Save the conflicting line numbers, and maybe other details about the conflict?

It'd also be nice to specify where the conflict is. To do that I'll need to
understand merge-tree's cryptic modification notation.

Remaining things to do to get this to a minimally working state:
    
    1. Run the merge-tree command from python to feed things to find_conflicting_file_paths.
        a) Only compare HEAD to recently modified branches.
    2. Store the file paths in a nicer object which should maybe also have branch info, date etc.
    3. Write unit tests!

TODO: Use this logic to revive the merge-heaven dashboard as an intermediary
      step to the Sublime/Atom/IntelliJ/Eclipse plugin?
'''

FILE_NAME_LINE = re.compile(r'^(\s+)(our|result|their)(\s+)(\d+)\s(\w+)\s(.+)$')
CONFLICT_LINE = re.compile(r'^\+<<<<<<<\s\.our$')

def find_conflicting_file_paths(merge_tree_output_file):
    file_path = ''
    conflicting_file_paths = []
    
    with open(merge_tree_output_file, 'r', encoding='utf8', errors='ignore') as f:
        for line in f:
            ## Get the current file name.
            file_name_match = FILE_NAME_LINE.match(line)
            if file_name_match:
                file_path = file_name_match.group(6)
                continue
            
            ## Save the file name if it's a merge conflict line, and then reset
            ## the file name to blank so that we don't save a file more than once.
            if file_path:
                conflict_match = CONFLICT_LINE.match(line)
                if conflict_match:
                    conflicting_file_paths.append(file_path)
                    file_path = ''
            
    return conflicting_file_paths
    
if __name__ == "__main__":
    conflicting_file_paths = find_conflicting_file_paths('C:/Users/Kamal/workspace/deleteme/development/output.txt')
    
    print(len(conflicting_file_paths))
    for path in conflicting_file_paths:
        print(path)
