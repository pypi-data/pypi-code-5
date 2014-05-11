import os
from abc import ABCMeta, abstractmethod


class BaseAdaptor():
    """
        This class defines an iterface for adaptors to different system
        notification libraries
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def build_failed():
        raise NotImplementedError("This method has not been implemented.")

    @abstractmethod
    def build_fixed():
        raise NotImplementedError("This method has not been implemented.")


class pync_adaptor(BaseAdaptor):
    """
        Adaptor for pync for OSX notifications
    """
    def __init__(self):
        from pync import Notifier
        self._api = Notifier

    def build_failed(self, name='', url=''):
        self._api.notify('Build Failed: ' + name, title='Jenkins Notify',
                         open=url, group=os.getpid())

    def build_fixed(self, name='', url=''):
        self._api.notify('Build Fixed: ' + name, title='Jenkins Notify',
                         open=url, group=os.getpid())


class notify2_adaptor(BaseAdaptor):
    """
        Adaptor for notify2 for Ubuntu notifications
    """
    def __init__(self):
        import notify2
        self._api = notify2

    def build_failed(self, name=''):
        n = self._api.Notification("Build Failed", name,
                                   "notification-message-im")
        n.set_urgency(self._api.URGENCY_CRITICAL)
        n.show()

    def build_fixed(self, name=''):
        n = self._api.Notification("Build Fixed", name,
                                   "notification-message-im")
        n.show()


class APIFactory():
    """
        Factory for creating the appropriate wrapper to a
        notification api based on the detected operating system.
    """

    @staticmethod
    def create():
        import platform
        if platform.system() == "Darwin":
            return pync_adaptor()
        elif platform.system() == "Linux" and "Ubuntu" in platform.platform():
            return notify2_adaptor()
        else:
            raise NotImplementedError("jenkins-notify has not been implemented"
                                      " on this platform.")
