from getpass import getpass
from fabric.api import *
from apt import apt_get


def db_env(database=None, database_user=None, database_password=None, password=None):
    if password is None:
        password = getpass('Please enter MySQL root password:')

    env.root_password = password

    if database is None:
        database = prompt('Please enter database name:')
    env.database = database

    if database_user is None:
        database_user = prompt('Please enter user name for database %s:' % database)
    env.database_user = database_user

    if database_password is None:
        database_password = getpass('Please enter password for database user %s' % database_user)
    env.database_password = database_password


# kudos for http://blog.muhuk.com/2010/05/22/how-to-install-mysql-with-fabric.html#.U2iVe62SyQ0
def install_mysql(server=True, client=True):
    if server:
        with settings(hide('warnings', 'stderr'), warn_only=True):
            result = sudo('dpkg-query --show mysql-server')
            if result.failed is False:
                warn('MySQL is already installed')
                return
            sudo('echo "mysql-server-5.0 mysql-server/root_password password ' \
                                      '%s" | debconf-set-selections' % env.root_password)
            sudo('echo "mysql-server-5.0 mysql-server/root_password_again password ' \
                                      '%s" | debconf-set-selections' % env.root_password)
            apt_get('mysql-server')
    if client:
        apt_get('mysql-client')


def create_database():
    with settings(hide('everything'), warn_only=True):
        run('echo "CREATE DATABASE %s DEFAULT CHARACTER SET utf8" | mysql -uroot -p%s' % (env.database, env.root_password))


def create_user():
    with settings(hide('everything'), warn_only=True):
        run('echo "GRANT ALL PRIVILEGES ON %s.* TO \'%s\'@\'localhost\' IDENTIFIED BY \'%s\'" | mysql -uroot -p%s' %
            (env.database, env.database_user, env.database_password, env.root_password))
