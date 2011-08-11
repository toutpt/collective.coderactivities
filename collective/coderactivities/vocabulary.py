from zope import component
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.interfaces import IVocabularyFactory
from zope.site.hooks import getSite

from collective.coderactivities import interfaces

kind = SimpleVocabulary.fromItems((
    ("commit", u"Commit"),
    ("documentation", u"Documentation"),
    ("blog", u"Blog"),
    ("email", u"Email"),
    ("bug", u"Bug")))

from operator import itemgetter

from zope.interface import implements
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


from Products.CMFCore.utils import getToolByName


class ExtractorVocabularyFactory(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        items = []
        site = getSite()
        import pdb;pdb.set_trace()
        extractors = list(component.getAdapters((context, request),
                                           interfaces.IIMAPActionExtractor))
        if extractors:
            items = [(name, _(unicode(name))) for name,adapter in extractors]
            items = [SimpleTerm(i[0], i[0], i[1]) for i in items]
        return SimpleVocabulary(items)

ExtractorVocabulary = ExtractorVocabularyFactory()
