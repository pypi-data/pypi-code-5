from distutils.command.install import install


class DjangoInstall(install):
    def run(self):
        install.run(self)

        from django.core.management import call_command
        call_command('deploy')
