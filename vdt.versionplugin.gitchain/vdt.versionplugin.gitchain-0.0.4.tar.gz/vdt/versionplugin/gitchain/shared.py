import argparse

def parse_version_extra_args(version_args):
    p = argparse.ArgumentParser(description="Instead of building packages as a freezed state, propagate tags between git repositories.")
    p.add_argument('--target-repo', help="The full url to the target repository, the tag will be pushed there", required=True)
    p.add_argument('--target-ref', help="A branch name or refspec on the target repository to receive the changes.", required=True)
    p.add_argument('--force', '-f', help="Push with --force.", action="store_true")
    p.add_argument('--tags', help="Also push tags", action="store_true")

    return p.parse_args(version_args)
