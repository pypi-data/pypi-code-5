import logging
import subprocess

from vdt.versionplugin.gitchain.shared import parse_version_extra_args

log = logging.getLogger(__name__)


def build_package(version):
    """
    Build package with debianize.
    """
    args = parse_version_extra_args(version.extra_args)
    log.debug("Arguments are {0}".format(args))

    log.debug("Building version {0} with gitchain.".format(version))
    with version.checkout_tag:
        cmd = ['git', 'push']
        if args.force:
            cmd.append('--force')
        if args.tags:
            cmd.append('--tags')

        cmd += [args.target_repo, "HEAD:{0}".format(args.target_ref)]

        log.debug("Running command {0}".format(" ".join(cmd)))
        log.debug(subprocess.check_output(cmd))

    return 0
