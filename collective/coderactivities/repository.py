from zope import interface
from zope import schema
from Products.Five.browser import BrowserView

class IRepository(interface.Interface):
    """A mailing list to discuss on a topic of a project"""
    
    software = schema.ASCIILine(title=u"Software",
                                description=u"Git, SVN, ...")
    
    url = schema.URI(title=u"URL",
                     description=u"To manage your subscription")

    web_ui = schema.URI(title=u"Source code browser",
                        description=u"URL to browse de code",
                        required=False)

class RepositoryView(BrowserView):
    """Default mailing list view"""

