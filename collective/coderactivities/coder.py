from zope import interface
from zope import schema
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class ICoder(interface.Interface):
    """an identified person"""
    
    fullname = schema.TextLine(title=u"Full name")
    
    ids = schema.List(title=u"Ids of this user throw action providers",
                      value_type=schema.ASCIILine(title=u"Id"),
                      required=False)


class CoderView(BrowserView):
    """Coder default view"""
    
    embeded_template = ViewPageTemplateFile("templates/coder_embeded_view.pt")
    
    def embeded(self):
        return self.embeded_template()

    def fullname(self):
        return self.context.fullname

