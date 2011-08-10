import re
import time
import urllib

from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import manage_zcatalog_entries as \
    ManageZCatalogEntries
from AccessControl.Permissions import search_zcatalog as SearchZCatalog
from AccessControl.PermissionRole import rolesForPermissionOn
from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from App.class_init import InitializeClass
from App.special_dtml import DTMLFile
from BTrees.Length import Length
from DateTime import DateTime
from OFS.interfaces import IOrderedContainer
from plone.indexer import indexer
from plone.indexer.interfaces import IIndexableObject
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.utils import _getAuthenticatedUser
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.CatalogTool import _mergedLocalRoles
from Products.CMFCore.CatalogTool import CatalogTool as BaseTool
from Products.CMFCore.permissions import AccessInactivePortalContent
from Products.ZCatalog.ZCatalog import ZCatalog
from zope.component import queryMultiAdapter
from zope.interface import Interface
from zope.interface import implements
from zope.interface import providedBy

from Products.CMFPlone.PloneBaseTool import PloneBaseTool
from Products.CMFPlone.interfaces import INonStructuralFolder
from Products.CMFPlone.utils import base_hasattr
from Products.CMFPlone.utils import safe_callable
from Products.CMFPlone.utils import safe_unicode

from plone.i18n.normalizer.base import mapUnicode

from collective.coderactivities import action

@indexer(action.IAction)
def kind(obj):
    """Return a list of roles and users with View permission.
    Used to filter out items you're not allowed to see.
    """
    return obj.kind

class IActionCatalogTool(Interface):
    """Interface marker"""

class CatalogTool(PloneBaseTool, BaseTool):
    """Plone's catalog tool"""

    implements(IActionCatalogTool)

    meta_type = 'Action Catalog Tool'
    security = ClassSecurityInfo()
    toolicon = 'skins/plone_images/book_icon.png'
    _counter = None

    manage_catalogAdvanced = DTMLFile('www/catalogAdvanced', globals())

    manage_options = (
        {'action': 'manage_main', 'label': 'Contents'},
        {'action': 'manage_catalogView', 'label': 'Catalog'},
        {'action': 'manage_catalogIndexes', 'label': 'Indexes'},
        {'action': 'manage_catalogSchema', 'label': 'Metadata'},
        {'action': 'manage_catalogAdvanced', 'label': 'Advanced'},
        {'action': 'manage_catalogReport', 'label': 'Query Report'},
        {'action': 'manage_catalogPlan', 'label': 'Query Plan'},
        {'action': 'manage_propertiesForm', 'label': 'Properties'},
    )

    def __init__(self):
        ZCatalog.__init__(self, self.getId())

    def _removeIndex(self, index):
        """Safe removal of an index.
        """
        try:
            self.manage_delIndex(index)
        except:
            pass

    security.declarePrivate('indexObject')
    def indexObject(self, object, idxs=[]):
        """Add object to catalog.

        The optional idxs argument is a list of specific indexes
        to populate (all of them by default).
        """
        self.reindexObject(object, idxs)

    security.declareProtected(ManageZCatalogEntries, 'catalog_object')
    def catalog_object(self, object, uid=None, idxs=[],
                       update_metadata=1, pghandler=None):
        self._increment_counter()

        w = object
        if not IIndexableObject.providedBy(object):
            # This is the CMF 2.2 compatible approach, which should be used
            # going forward
            wrapper = queryMultiAdapter((object, self), IIndexableObject)
            if wrapper is not None:
                w = wrapper

        ZCatalog.catalog_object(self, w, uid, idxs,
                                update_metadata, pghandler=pghandler)

    security.declareProtected(ManageZCatalogEntries, 'catalog_object')
    def uncatalog_object(self, *args, **kwargs):
        self._increment_counter()
        return BaseTool.uncatalog_object(self, *args, **kwargs)

    def _increment_counter(self):
        if self._counter is None:
            self._counter = Length()
        self._counter.change(1)

    security.declarePrivate('getCounter')
    def getCounter(self):
        return self._counter is not None and self._counter() or 0

    def __call__(self, REQUEST=None, **kw):
        return self.searchResults(REQUEST=REQUEST, **kw)

    security.declareProtected(ManageZCatalogEntries, 'clearFindAndRebuild')
    def clearFindAndRebuild(self):
        """Empties catalog, then finds all contentish objects (i.e. objects
           with an indexObject method), and reindexes them.
           This may take a long time.
        """
        def indexObject(obj, path):
            if (base_hasattr(obj, 'indexObject') and
                safe_callable(obj.indexObject)):
                try:
                    obj.indexObject()
                except TypeError:
                    # Catalogs have 'indexObject' as well, but they
                    # take different args, and will fail
                    pass
        self.manage_catalogClear()
        portal = aq_parent(aq_inner(self))
        portal.ZopeFindAndApply(portal, search_sub=True,
            apply_func=indexObject)

    security.declareProtected(ManageZCatalogEntries, 'manage_catalogRebuild')
    def manage_catalogRebuild(self, RESPONSE=None, URL1=None):
        """Clears the catalog and indexes all objects with an 'indexObject'
        method. This may take a long time.
        """
        elapse = time.time()
        c_elapse = time.clock()

        self.clearFindAndRebuild()

        elapse = time.time() - elapse
        c_elapse = time.clock() - c_elapse

        if RESPONSE is not None:
            RESPONSE.redirect(
              URL1 + '/manage_catalogAdvanced?manage_tabs_message=' +
              urllib.quote('Catalog Rebuilt\n'
                           'Total time: %s\n'
                           'Total CPU time: %s' % (`elapse`, `c_elapse`)))

InitializeClass(CatalogTool)