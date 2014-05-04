import pprint
import coloredlogs
coloredlogs.install()
coloredlogs.increase_verbosity()

from vcs_repo_mgr import GitRepo, HgRepo

print "python-ftplugin git repository:"
git_repo = GitRepo(local='/home/peter/Dropbox/Projects/Vim/python-ftplugin')
pprint.pprint(git_repo.branches)

print
print "v2 release hg repo:"
hg_repo = HgRepo(local='/home/peter/Paylogic/Code/v2/release')
pprint.pprint(hg_repo.branches)
