import imaplib
import logging
import email

from zope import component
from zope import schema
from zope import interface
from zope import i18nmessageid

from Products.Five.browser import BrowserView

from collective.coderactivities import action
from collective.coderactivities import vocabulary

_ = i18nmessageid.MessageFactory("collective.coderactivities")
logger = logging.getLogger('collective.coderactivities')

class IIMAP(interface.Interface):
    """action provider schema"""
    
    host = schema.ASCIILine(title=_(u"Hostname"),
                            default="localhost")
    port = schema.Int(title=_(u"Port"),
                      default=993)
    ssl = schema.Bool(title=_(u"SSL"),
                      default=True)

    user = schema.ASCIILine(title=_(u"user name"))
    password = schema.Password(title=_(u"password"))
    
    mailbox = schema.ASCIILine(title=_(u"Mailbox"),
                               default="INBOX") #gmail example= '(\\HasNoChildren) "/" "svn collective"'

    search_criterion = schema.ASCIILine(title=_(u"Search criterion"),
                                        default="ALL")
    search_charset = schema.ASCIILine(title=_(u"Search charset"),
                                      description=_(u"Can be US-ASCII or UTF-8"),
                                      default='UTF-8',
                                      required=False)
    
    kind = schema.Choice(title=_(u"Kind"),
                        description=_(u"An action can be a commit, an email,..."),
                        vocabulary=vocabulary.kind)

    extractor = schema.Choice(title=_(u"Extractor of action"),
                              vocabulary="collective.coderactivities.vocabulary.extractor")


class IMAPView(action.ActionPersistentProvider):
    """default imap view"""
    
    def __init__(self, context, request):
        super(IMAPView, self).__init__(context, request)
        self._mails = []

    def update(self):
        #http://hg.python.org/cpython/file/b9a95ce2692c/Lib/imaplib.py
        """
        """
        self._actions = []
        host = self.context.host
        port = self.context.port
        ssl = self.context.ssl
        
        password = self.context.password
        user = self.context.user
        
        mailbox = self.context.mailbox
        
        if ssl:
            M = imaplib.IMAP4_SSL(host, port)
        else:
            M = imaplib.IMAP4(host, port)

        M.login(user, password)
        resp = M.select(mailbox, True) #read only
        if resp[0] == 'NO':
            logger.error('mail box doesn t exists')
            #TODO: add status message
            self.request.response.redirect(self.context.absolute_url()+'/edit')
            return
        charset = self.context.search_charset
        if not charset or charset == 'None':
            charset = None
        criterion = self.context.search_criterion
        try: #to use sort command
            sort_on = 'SORTDATE'
            typ, data = M.sort(sort_on,charset, criterion) #IMAP4rev1 extension
        except imaplib.IMAP4.error, e:
            typ, data = M.search(charset, criterion)

        for num in data[0].split():
            action = self.build_action(M, num, typ, data)
            if action:
                self._actions.append(action)

        M.close()
        M.logout()

    def build_action(self, imap, num, typ, data):
        """Override for specific mail send by projects"""
        extractor_name = self.context.extractor
        extractor = component.getAdapter((self.context, self.request), name=extractor_name)
        extractor()


class PloneSVNCommitActionBuilder(IMAPView):
    """Build action from mail send by the plone community on svn commit"""
    
    def build_action(self, imap, num, typ, data):
        """Override for specific mail on projects"""
        parser = email.parser.Parser()
        mtyp, mdata = imap.fetch(num, '(BODY.PEEK[HEADER] BODY.PEEK[TEXT])')
        mbody = mdata[0][1]
        mhead = mdata[1][1]
        headers = parser.parsestr(mhead)
#        ['Delivered-To', 'Received', 'Received', 'Return-Path', 'Received',
#        'Received-SPF', 'Authentication-Results', 'Received', 'Received',
#        'X-ACL-Warn', 'Received', 'Received', 'Date', 'Message-Id', 'From',
#        'To', 'MIME-Version', 'X-Spam-Score', 'X-Spam-Report', 'X-Headers-End',
#        'Subject', 'X-BeenThere', 'X-Mailman-Version', 'Precedence',
#        'Reply-To', 'List-Id', 'List-Unsubscribe', 'List-Archive',
#        'List-Post', 'List-Help', 'List-Subscribe', 'Content-Type',
#        'Content-Transfer-Encoding', 'Errors-To']
        info = {'id':headers['Message-Id']}
        info['kind'] = self.context.kind #may be forced to commit
        if headers['Reply-To']:
            info['author'] = headers['Reply-To']
        else:
            info['author'] = headers['From']
        info['date'] = headers['Date'] #should be a datetime
        info['description'] = mbody
        action = self.add(info)
        return action

class DocIMAPView(BrowserView):
    """Documentation view"""
    
    def criterion(self):
        c = []
        c.append({'arg':'message set',
                  'description':_(u"""Messages with message sequence numbers
                         corresponding to the specified message sequence
                         number set""")})
        c.append({'arg':'ALL',
                  'description':_(u"""All messages in the mailbox; the default initial
                         key for ANDing.""")})
        c.append({'arg':'ANSWERED',
                  'description':_(u"""Messages with the \Answered flag set.""")})
        c.append({'arg':'BCC <string>',
                  'description':_(u"""Messages that contain the specified string in the
                         envelope structure's BCC field.""")})
        c.append({'arg':'BEFORE <date>',
                  'description':_(u"""Messages whose internal date is earlier than the
                         specified date.""")})
        c.append({'arg':'BODY <string>',
                  'description':_(u"""Messages that contain the specified string in the
                         body of the message.""")})
        c.append({'arg':'CC <string>',
                  'description':_(u"""Messages that contain the specified string in the
                         envelope structure's CC field.""")})
        c.append({'arg':'DELETED',
                  'description':_(u"""Messages with the \Deleted flag set.""")})
        c.append({'arg':'DRAFT',
                  'description':_(u"""Messages with the \Draft flag set.""")})
        c.append({'arg':'FLAGGED',
                  'description':_(u"""Messages with the \Flagged flag set.""")})
        c.append({'arg':'FROM <string>',
                  'description':_(u"""Messages that contain the specified string in the
                         envelope structure's FROM field.""")})
        c.append({'arg':'HEADER <field-name> <string>',
                  'description':_(u"""Messages that have a header with the specified
                         field-name (as defined in [RFC-822]) and that
                         contains the specified string in the [RFC-822]
                         field-body.""")})
        c.append({'arg':'KEYWORD <flag>',
                  'description':_(u"""Messages with the specified keyword set.""")})
        c.append({'arg':'LARGER <n>',
                  'description':_(u"""Messages with an RFC822.SIZE larger than the
                         specified number of octets.""")})
        c.append({'arg':'NEW',
                  'description':_(u"""Messages that have the \Recent flag set but not the
                         \Seen flag.  This is functionally equivalent to
                         "(RECENT UNSEEN)".""")})
        c.append({'arg':'NOT <search-key>',
                  'description':_(u"""Messages that do not match the specified search
                         key.""")})
        c.append({'arg':'OLD',
                  'description':_(u"""Messages that do not have the \Recent flag set.
                         This is functionally equivalent to "NOT RECENT" (as
                         opposed to "NOT NEW").""")})
        c.append({'arg':'ON <date>',
                  'description':_(u"""Messages whose internal date is within the
                         specified date.""")})
        c.append({'arg':'OR <search-key1> <search-key2>',
                  'description':_(u"""Messages that match either search key.""")})
        c.append({'arg':'RECENT',
                  'description':_(u"""Messages that have the \Recent flag set.""")})
        c.append({'arg':'SEEN',
                  'description':_(u"""Messages that have the \Seen flag set.""")})
        c.append({'arg':'SENTBEFORE <date>',
                  'description':_(u"""Messages whose [RFC-822] Date: header is earlier
                         than the specified date.""")})
        c.append({'arg':'SENTON <date>',
                  'description':_(u"""Messages whose [RFC-822] Date: header is within the
                         specified date.""")})
        c.append({'arg':'SENTSINCE <date>',
                  'description':_(u"""Messages whose [RFC-822] Date: header is within or
                         later than the specified date.""")})
        c.append({'arg':'SINCE <date>',
                  'description':_(u"""Messages whose internal date is within or later
                         than the specified date.""")})
        c.append({'arg':'SMALLER <n>',
                  'description':_(u"""Messages with an RFC822.SIZE smaller than the
                         specified number of octets.""")})
        c.append({'arg':'SUBJECT <string>',
                  'description':_(u"""Messages that contain the specified string in the
                         envelope structure's SUBJECT field.""")})
        c.append({'arg':'TEXT <string>',
                  'description':_(u"""Messages that contain the specified string in the
                         header or body of the message.""")})
        c.append({'arg':'TO <string>',
                  'description':_(u"""Messages that contain the specified string in the
                         envelope structure's TO field.""")})
        c.append({'arg':'UNANSWERED',
                  'description':_(u"""Messages that do not have the \Answered flag set.""")})
        c.append({'arg':'UNDELETED',
                  'description':_(u"""Messages that do not have the \Deleted flag set.""")})
        c.append({'arg':'UNDRAFT',
                  'description':_(u"""Messages that do not have the \Draft flag set.""")})
        c.append({'arg':'UNFLAGGED',
                  'description':_(u"""Messages that do not have the \Flagged flag set.""")})
        c.append({'arg':'UNKEYWORD <flag>',
                  'description':_(u"""Messages that do not have the specified keyword
                         set.""")})
        c.append({'arg':'UNSEEN',
                  'description':_(u"""Messages that do not have the \Seen flag set.""")})
        return c