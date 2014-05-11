import time
from abc import ABCMeta
from jenkinsapi.jenkins import Jenkins
from notify import APIFactory


class JenkinsClient():

    __metaclass__ = ABCMeta

    def __init__(self, address, build_names=[], polling_interval=300):
        # start connection to Jenkins
        self._jenkins_server = Jenkins(address)
        self._notifier = APIFactory.create()
        self._interval = polling_interval
        self._build_names = build_names

    def run(self):
        try:
            while True:
                self._poll_jenkins()
                time.sleep(self._interval)
        except (KeyboardInterrupt, SystemExit):
            # if we catch either exception, just quit the program
            print "\nQuitting..."

    def _poll_jenkins(self):
        for name in self._build_names:
            build = self._jenkins_server[name].get_last_completed_build()
            build_good = build.is_good()
            build_number = build.buildno
            url = self._jenkins_server[name].baseurl

            if not build_good:
                last_good_build = self._jenkins_server[name].get_last_good_buildnumber()
                if last_good_build == build_number - 1:
                    # build has just broken
                    self._notifier.build_failed(name, url)

            elif build_good:
                last_failed_build = self._jenkins_server[name].get_last_failed_buildnumber()
                if last_failed_build == build_number - 1:
                    # build was fixed on this
                    self._notifier.build_fixed(name, url)


if __name__ == "__main__":
    j = JenkinsClient(address="http://builds.mantidproject.org",
                      build_names=['develop_incremental'],
                      polling_iterval=10)
    j.run()
