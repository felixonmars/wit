#!/usr/bin/env python3

# TODO:
# * Error handling
# * Log all commands into workspace
# * De-couple WorkSpace from GitRepos
# * Write unit tests
# * What to do in case of corrupt dependencies.json
# * How to handle exceptional conditions
# * Use a real logger
# * handle partial sha1s correctly

 
import argparse
from workspace import WorkSpace, GitRepo
import logging
import os
import sys
import tabulate

logging.basicConfig(level = logging.INFO)
log = logging.getLogger(os.path.basename(__file__))
log.setLevel(logging.DEBUG)

def main() -> None:
    # Parse arguments. Create sub-commands for each of the modes of operation
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true')
    subparsers = parser.add_subparsers(dest='command', help='sub-command help')

    create_parser = subparsers.add_parser('create', help='create workspace')
    create_parser.add_argument('-a', '--add', metavar='repo', help='add an initial repo')
    create_parser.add_argument('workspace_name')

    add_parser = subparsers.add_parser('add', help='add repo to workspace')
    add_parser.add_argument('repo_name')

    subparsers.add_parser('status', help='show status of workspace')
    subparsers.add_parser('update', help='update git repos')

    args = parser.parse_args()

    ws = WorkSpace()
    # FIXME: This big switch statement... no good.
    if args.command == 'create':
        create(ws, args)

    else:
        # These commands assume the workspace already exists. Error out if the
        # workspace cannot be found.
        try:
            ws.find()
            
        except FileNotFoundError as e:
            log.error("Unable to find workspace root [{}]. Cannot continue.".format(e))
            sys.exit(1)
            
        if args.command == 'add':
            add(ws, args)

        elif args.command == 'status':
            status(ws, args)

        elif args.command == 'update':
            update(ws, args)


def create(ws, args):
    print("Creating workspace [{}]".format(args.workspace_name))

    ws.create(args.workspace_name)
    if args.add is not None:
        source, revision = split_repo_rev(args.add)
        ws.add_repo(source=source, revision=revision, explicit=True)


def add(ws, args):
    log.info("Adding repo to workspace")
    source, revision = split_repo_rev(args.repo_name)
    ws.add_repo(source=source, revision=revision, explicit=True)


def status(ws, args):
    log.info("Checking workspace status")
    for reponame in ws.manifest:
        print("Status for repo [{}]".format(reponame))

        # FIXME: cheating by diving into the object.
        manifest_commit = ws.manifest[reponame]['commit']
        latest_commit = GitRepo.create(ws.manifest[reponame]['source']).get_latest_commit()

        print("    Manifest commit: {}".format(manifest_commit))
        print("    Latest commit:   {}".format(latest_commit))



def update(ws, args):
    log.info("Updating workspace")
    ws.update()


def split_repo_rev(repo_string):
    # FIXME: This is ugly. Split on '::' into a path and revision, but
    # there may not be a revision. So add an additional array
    source, rev = (repo_string.split("::") + [None])[:2]
    return source, rev


if __name__ == '__main__':
    main()
