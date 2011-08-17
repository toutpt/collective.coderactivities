from zope import interface
from zope import schema
from Products.Five.browser import BrowserView

class IProject(interface.Interface):
    """An IT project"""

    #title and description are taken from behavior


class ProjectView(BrowserView):
    """Default project view"""

    def actions(self):
        return []
