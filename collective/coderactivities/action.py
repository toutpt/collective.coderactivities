from zope import event
from zope import interface
from zope import schema
from zope import lifecycleevent

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from collective.coderactivities import vocabulary

class IAction(interface.Interface):
    """An action is done by someone to something. It can be an email, a commit,
    documentation"""
    
    author = schema.ASCIILine(title=u"Author ID")
    
    kind = schema.Choice(title=u"Kind",
                            description=u"An action can be a commit, an email,...",
                            vocabulary=vocabulary.kind)

    description = schema.Text(title=u"Description")

    date = schema.Datetime(title=u"Date of the action")

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

    def actions():
        """Return an iterator on all action"""

class ActionManager(BrowserView):
    """Dexterity action manager"""
    interface.implements(IActionManager)

    def get(self, id):
        return getattr(self.context, id, None)

    def add(self, info):
        context = self.context
        if type(info) == dict:
            info_type = 'dict'
        else:
            info_type = 'object'
        if 'id' not in info:
            raise Exception()
        
        #try to get it first:
        action = self.get(info['id'])
        if action is None:
            context.invokeFactory(id=info['id'],
                                   type_name='collective.coderactivities.action')
            action = self.get(info['id'])
            evt = lifecycleevent.ObjectCreatedEvent(action)
            event.notify(evt)
        action.kind = info['kind']
        action.author = info['author'].encode() #TODO: encoding -> ascii
        action.date = info['date']
        action.description = info['description']
        evt = lifecycleevent.ObjectModifiedEvent(action)
        event.notify(evt)
        #TODO: find how to change the creation date
        return action

    def search(self, query):
        catalog = getToolByName(self.context, 'portal_actions_catalog')
        brains = catalog(**query)
        return brains

def index(obj, evt):
    catalog = getToolByName(obj, 'portal_actions_catalog')
    catalog.catalog_object(obj)

def reindex(obj, evt):
    unindex(obj,evt)
    index(obj,evt)

def unindex(obj, evt):
    catalog = getToolByName(obj, 'portal_actions_catalog')
    catalog.uncatalog_object(obj)
