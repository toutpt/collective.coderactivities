from zope import interface
from zope import schema
from Products.Five.browser import BrowserView

from collective.coderactivities import vocabulary

class IMailingList(interface.Interface):
    """A mailing list to discuss on a topic of a project"""
    
    email = schema.ASCIILine(title=u"email")
    
    url = schema.URI(title=u"UI to manage your subscription")

    kind = schema.Choice(title=u"Kind",
                         vocabulary=vocabulary.kind)

class MailingListView(BrowserView):
    """Default mailing list view"""

