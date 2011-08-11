import feedparser
from datetime import datetime

from zope import component
from zope import interface
from zope import schema
from Products.Five.browser import BrowserView

from collective.coderactivities import action
from collective.coderactivities import vocabulary

class IRSS(interface.Interface):
    """A mailing list to discuss on a topic of a project"""
    
    url = schema.URI(title=u"RSS URL")
    
    kind = schema.Choice(title=u"Kind",
                         vocabulary=vocabulary.kind)

class RSSView(action.ActionPersistentProvider):
    """Default mailing list view"""
    interface.implements(action.IActionProvider)

    def __init__(self, context, request):
        super(RSSView, self).__init__(context, request)
        self.entries = []

    def update(self):
        #Todo: add cache for 10 minutes
        url = self.context.url
        feed = feedparser.parse(url)
        self.entries = feed['entries']
        for entry in self.entries:
            self.build_action(entry)

# planet plone
#        ['updated', 'published_parsed', 'updated_parsed', 'links', 'title',
#         'feedburner_origlink', 'authors', 'summary', 'content', 'source',
#         'title_detail', 'href', 'link', 'author', 'published', 'author_detail',
#         'id']
#github
#['updated', 'updated_parsed', 'links', 'title', 'author', 'media_thumbnail',
#'summary', 'content', 'title_detail', 'href', 'link', 'authors',
#'author_detail', 'id']


    def build_action(self, entry):
        
        kind = self.context.kind
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
        info['id'] = entry['id']
        if len(info.keys())==5:
            self._actions.append(self.add(info))
        else:
            self.context.plone_log('incomplete data: %s'%info)
