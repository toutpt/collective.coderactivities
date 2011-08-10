from zope import interface
from zope import schema

from Products.Five import BrowserView

class IAction(interface.Interface):
    """An action is done by someone to something. It can be an email, a commit,
    documentation"""
    
    author = schema.ASCIILine(title=u"Author ID")
    
    kind = schema.ASCIILine(title=u"Kind",
                            description=u"An action can be a commit, an email,...")

    description = schema.Text(Title=u"Description")

    date = schema.DateTime(title=u"Date of the action")

class ActionView(BrowserView):
    """Default view for action"""

class IActionManager(interface.Interface):
    """Manage actions"""
    
    def add(info):
        """Add an action. info must be a dict or an IAction object"""
    
    def remove(id):
        """Remove an action based on its id"""
    
    def get(id):
        """Return the action by it's id"""
    
    def search(query={}):
        """Search actions. query is a catalog queries"""

class DexterityActionManager(BrowserView):
    """Dexterity action manager"""
    
    def factory(self, info):
        """Return a new action object"""
        pass

    def get(self, id):
        pass

    def add(self, info):
        if type(info) == dict:
            info_type = 'dict'
        else:
            info_type = 'object'
    
    def search(self, query):
        catalog = None #todo get it
        