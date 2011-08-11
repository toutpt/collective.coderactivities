from zope import interface
# -*- Additional Imports Here -*-


class ICoderActivitiesLayer(interface.Interface):
    """ A layer specific to this product. 
        Is registered using browserlayer.xml
    """

class IIMAPActionExtractor(interface.Interface):
    """An action builder is a browser view responsible to create an action info
    from the email"""
    
    def __call__(email):
        """do it an return me a dict with all info for the action manager"""
