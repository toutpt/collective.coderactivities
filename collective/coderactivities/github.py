import urllib2
import json

from zope import component
from zope import event
from zope import interface
from zope import schema
from zope import lifecycleevent

from collective.coderactivities import action
from collective.coderactivities import rss
from collective.github.browser import github as utils
from plone.directives import form

class IGithub(form.Schema):
    """A github link to a person or an organisation"""
    
    url = schema.URI(title=u"Github URL",
                     description=u"A person or an organisation")

class FakeLink(object):
    def __init__(self, url):
        self.url = url
    
    def getRemoteUrl(self):
        return self.url

class GithubView(rss.RSSView):
    """Github is a container of rss activities"""

    def __init__(self, context, request):
        super(GithubView, self).__init__(context, request)
        self._rsss = []
    
    def update(self):
        self._rsss = self.context.objectValues()
        self._actions = []
        for rss in self._rsss:
            view = rss.restrictedTraverse('rss_view')
            self._actions.extend(view.actions())
    
class GithubUpdateView(GithubView):

    def __call__(self):
        
        url = self.context.url
        if not utils.isGithubUrl(url):
            raise ValueError(u'not a valid github url')
        fake_link = FakeLink(url)
        github_bv = utils.GithubLink(fake_link, self.request)
        repositories = github_bv.repositories(stay_in_plone=False)
        for repository in repositories:
            #create a rss and build it
            self.add_rss(repository)

    def add_rss(self, info):
        """Build a RSS from repository info and update it"""
        context = self.context
        url_info = utils.githubUrlInfo(info['url'])

        plone_utils = self.context.plone_utils
        nid = plone_utils.normalizeString(info['url'].replace('/','').replace(':','').replace(',','').replace('.',''))
        rss = getattr(self.context, nid, None)
        if rss is None:
            context.invokeFactory(id=nid,
                                   type_name='collective.coderactivities.rss')
            rss = getattr(self.context, nid)
            evt = lifecycleevent.ObjectCreatedEvent(rss)
            event.notify(evt)
        rss.kind = 'commit'
        rss.url = 'https://github.com/%s/%s/commits/master.atom'%(info['owner'],url_info['repo'])
        rss.title = info['name']
        rss.description = info['description']
        evt = lifecycleevent.ObjectModifiedEvent(rss)
        event.notify(evt)
        context.restrictedTraverse(nid+'/rss_update_view')()
        return rss
