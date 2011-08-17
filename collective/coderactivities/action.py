import datetime
import time
import json

from zope import component
from zope import event
from zope import interface
from zope import schema
from zope import lifecycleevent

from plone.directives import form

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from collective.coderactivities import vocabulary

class IAction(form.Schema):
    """An action is done by someone to something. It can be an email, a commit,
    documentation"""
    
    author = schema.ASCIILine(title=u"Author ID")
    
    kind = schema.Choice(title=u"Kind",
                            description=u"An action can be a commit, an email,...",
                            vocabulary=vocabulary.kind)

    description = schema.Text(title=u"Description")

    date = schema.Datetime(title=u"Date of the action")

class IActionProvider(form.Schema):
    """action provider"""
    
    
    coder_mapping = schema.List(title=u"coder id mapping",
                                value_type=schema.ASCIILine(title=u"coder"),
                                required=False,
                                default=[])
    
    def ids():
        """Return action ids"""
    
    def get(id):
        """return IAction object defined by id"""
        
    def actions():
        """return actions"""

    def search(query={}):
        """Search actions. query is a catalog queries"""

    
class IPersistentActionProvider(IActionProvider):
    """a persistent action provider can add/remove/update actions"""
    
    def add(info):
        """Add an action. info must be a dict or an IAction object"""
    
    def remove(id):
        """Remove an action based on its id"""
    

class IActionManager(IActionProvider):
    """Manage actions"""
    
    def providers():
        """Return the list of providers"""

class ActionView(BrowserView):
    """Default view for action"""


class ActionPersistentProvider(BrowserView):
    """View over a Dexterity action container"""
    interface.implements(IPersistentActionProvider)

    def __init__(self, context, request):
        super(ActionPersistentProvider, self).__init__(context, request)
        self._actions = []

    def get(self, id):
        return getattr(self.context, id, None)

    def ids(self):
        return self.context.objectIds()

    def actions(self):
        if not self._actions:
            self.update()
        return self._actions
    
    def update(self):
        raise NotImplementedError('you must implement this in subclass')
    
    def add(self, info):
        context = self.context
        if type(info) == dict:
            info_type = 'dict'
        else:
            info_type = 'object'
        if 'id' not in info:
            raise Exception()
        
        #try to get it first:
        plone_utils = self.context.plone_utils
        
        nid = plone_utils.normalizeString(info['id'].replace('/','').replace(':','').replace(',','').replace('.',''))
        action = self.get(nid)
        if action is None:
            context.invokeFactory(id=nid,
                                   type_name='collective.coderactivities.action')
            action = self.get(nid)
            evt = lifecycleevent.ObjectCreatedEvent(action)
            event.notify(evt)
        action.kind = info['kind']
        action.author = info['author'].encode("utf-8") #TODO: encoding -> ascii
        self.add_author(action.author)
        action.date = info['date']
        action.description = info['description']
        evt = lifecycleevent.ObjectModifiedEvent(action)
        event.notify(evt)
        #TODO: find how to change the creation date
        return action

    def search(self, query):
        catalog = self.catalog
        brains = catalog(**query)
        return brains

    @property
    def catalog(self):
        catalog = getToolByName(self.context, 'portal_actions_catalog')
        return catalog

    def add_author(self, authorid):
        coders = self.context.coder_mapping or []
        coderids = [coder.split('|')[0] for coder in coders]
        if authorid not in coderids:
            coders.append('%s|'%authorid)
        
        self.context.coder_mapping = coders

#view related stuff
    def years(self):
        """return last 5 years"""
        current_y = datetime.date.today().year
        years = range(current_y - 5)
        return map(str, years)
    
    def month(self):
        return str(datetime.date.today().month)
    
    def monthes(self):
        return map(str, range(1,12))
    
    def kinds(self):
        return []
    
    def kind(self):
        return self.context.kind


    def plot_js(self):
        #x = date, y = amount
        #http://people.iola.dk/olau/flot/examples/time.html
        actions = self.actions()
        struct = {}
        for action in actions:
            date = action.date
            if type(date) == str:
                date = datetime.datetime.strptime(date[:-6],'%a, %d %b %Y %H:%M:%S')
            date = int(1000*time.mktime(date.date().timetuple())) #transform datetime into timestamp
            if date not in struct:
                struct[date] = 0
            struct[date] += 1

        dates = struct.keys()
        dates.sort()
        if not len(dates):
            return 'alert("no data"); var data = [];'
        oneday = 86400000
        range_date = range(dates[0],dates[-1],oneday)
        data = []
        for date in range_date:#
            data.append([date, struct.get(date,0)])
        return 'var data = %s;'%json.dumps(data)


def index(obj, evt):
    site = component.getSiteManager()
    catalog = getToolByName(site, 'portal_actions_catalog')
    catalog.catalog_object(obj)

def reindex(obj, evt):
    unindex(obj,evt)
    index(obj,evt)

def unindex(obj, evt):
    site = component.getSiteManager()
    catalog = getToolByName(site, 'portal_actions_catalog')
    catalog.uncatalog_object(obj)
