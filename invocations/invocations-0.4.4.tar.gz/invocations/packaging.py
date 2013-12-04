from glob import glob
import os
from shutil import rmtree, copy, copytree
from tempfile import mkdtemp

from invoke import ctask as task


def unpack(ctx, tmp, package, version, git_url=None):
    """
    Download + unpack given package into temp dir ``tmp``.

    Return ``(real_version, source)`` where ``real_version`` is the "actual"
    version downloaded (e.g. if a Git master was indicated, it will be the SHA
    of master HEAD) and ``source`` is the source directory (relative to
    unpacked source) to import into ``<project>/vendor``.
    """
    real_version = version[:]
    source = None
    if git_url:
        pass
    #   git clone into tempdir
    #   git checkout <version>
    #   set target to checkout
    #   if version does not look SHA-ish:
    #       in the checkout, obtain SHA from that branch
    #       set real_version to that value
    else:
        cwd = os.getcwd()
        print("Moving into temp dir %s" % tmp)
        os.chdir(tmp)
        try:
            # Nab from index
            flags = "--download-cache= --download=. --build=build"
            cmd = "pip install %s %s==%s" % (flags, package, version)
            ctx.run(cmd)
            # Identify basename
            zipfile = os.path.basename(glob("*.zip")[0])
            source = os.path.splitext(zipfile)[0]
            # Unzip
            ctx.run("unzip *.zip")
        finally:
            os.chdir(cwd)
    return real_version, source


@task
def vendorize(ctx, distribution, version, vendor_dir, package=None,
    git_url=None, license=None):
    """
    Vendorize Python package ``distribution`` at version/SHA ``version``.

    Specify the vendor folder (e.g. ``<mypackage>/vendor``) as ``vendor_dir``.

    For Crate/PyPI releases, ``package`` should be the name of the software
    entry on those sites, and ``version`` should be a specific version number.
    E.g. ``vendorize('lexicon', '0.1.2')``.

    For Git releases, ``package`` should be the name of the package folder
    within the checkout that needs to be vendorized and ``version`` should be a
    Git identifier (branch, tag, SHA etc.) ``git_url`` must also be given,
    something suitable for ``git clone <git_url>``.

    For SVN releases: xxx.

    For packages where the distribution name is not the same as the package
    directory name, give ``package='name'``.

    By default, no explicit license seeking is done -- we assume the license
    info is in file headers or otherwise within the Python package vendorized.
    This is not always true; specify ``license=/path/to/license/file`` to
    trigger copying of a license into the vendored folder from the
    checkout/download (relative to its root.)
    """
    tmp = mkdtemp()
    package = package or distribution
    target = os.path.join(vendor_dir, package)
    try:
        # Unpack source
        real_version, source = unpack(ctx, tmp, distribution, version, git_url)
        abs_source = os.path.join(tmp, source)
        source_package = os.path.join(abs_source, package)
        # Ensure source package exists
        if not os.path.exists(source_package):
            rel_package = os.path.join(source, package)
            raise ValueError("Source package %s doesn't exist!" % rel_package)
        # Nuke target if exists
        if os.path.exists(target):
            print("Removing pre-existing vendorized folder %s" % target)
            rmtree(target)
        # Perform the copy
        print("Copying %s => %s" % (source_package, target))
        copytree(source_package, target)
        # Explicit license if needed
        if license:
            copy(os.path.join(abs_source, license), target)
        # git commit -a -m "Update $package to $version ($real_version if different)"
    finally:
        rmtree(tmp)


@task
def release(ctx):
    """
    Upload an sdist to PyPI via ye olde 'setup.py sdist register upload'.
    """
    ctx.run("python setup.py sdist register upload")
