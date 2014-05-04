from fabric.api import task, run, local, env
import time
env.hosts = ['98.129.6.188']

@task
def host_type():
    """
    test description
    """
    run('uname -a')
    run('ls -l /usr/lib')
    time.sleep(4)
    env['foo'] = 'bar'
    return "shit worked"

@task
def check_foo():
    return env['foo']
