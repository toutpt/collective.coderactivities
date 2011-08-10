import feedparser
from datetime import datetime

from zope import component
from zope import interface
from zope import schema
from Products.Five.browser import BrowserView

from collective.coderactivities.action import IActionManager
from collective.coderactivities import vocabulary

class IRSS(interface.Interface):
    """A mailing list to discuss on a topic of a project"""
    
    url = schema.URI(title=u"RSS URL")
    
    kind = schema.Choice(title=u"Kind",
                         vocabulary=vocabulary.kind)

class RSSView(BrowserView):
    """Default mailing list view"""

    def __init__(self, context, request):
        super(RSSView, self).__init__(context, request)
        self.entries = []

    def update(self):
        url = self.context.url
        feed = feedparser.parse(url)
        self.entries = feed['entries']
        self.actions()
    
    def project(self):
        context = self.context
        while context.portal_type not in ('Plone Site', 'collective.coderactivities.project'):
            context = context.aq_parent
        
        if context.portal_type == 'Plone Site':
            raise KeyError('can t find project')

        return context

    def actions(self):
        """Import entries into actions"""
# planet plone
#        ['updated', 'published_parsed', 'updated_parsed', 'links', 'title',
#         'feedburner_origlink', 'authors', 'summary', 'content', 'source',
#         'title_detail', 'href', 'link', 'author', 'published', 'author_detail',
#         'id']
#github
#['updated', 'updated_parsed', 'links', 'title', 'author', 'media_thumbnail',
#'summary', 'content', 'title_detail', 'href', 'link', 'authors',
#'author_detail', 'id']
        entries = self.entries
        project = self.project()
        action_manager = component.queryMultiAdapter((project, self.request),
                                                     name="action_manager")
        if not action_manager:
            return
        plone_utils = self.context.plone_utils
        kind = self.context.kind

        for entry in entries:
            info = {'kind':kind}
            author = None
            if 'author' in entry:
                info['author'] = entry['author']
                
            date = None
            if 'updated_parsed' in entry:
                tmp = entry['updated_parsed']
                date = datetime(tmp[0],tmp[1],tmp[2],tmp[3],tmp[4])
                info['date'] = date
            description = None
            if 'summary' in entry:
                info['description'] = entry['summary']
            info['id'] = plone_utils.normalizeString(entry['id'])
            if len(info.keys())==5:
                action_manager.add(info)
            else:
                self.context.plone_log('incomplete data: %s'%info)
                