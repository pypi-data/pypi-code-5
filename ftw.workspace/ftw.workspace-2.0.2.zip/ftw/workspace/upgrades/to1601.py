from ftw.upgrade import UpgradeStep


class HideAction(UpgradeStep):

    def __call__(self):
        self.setup_install_profile(
            'profile-ftw.workspace.upgrades:1601')
