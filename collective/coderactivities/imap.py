import imaplib

from zope import schema
from zope import interface

from collective.coderactivities import action
from Products.Five.browser import BrowserView

class IIMAP(interface.Interface):
    """action provider schema"""
    
    host = schema.ASCIILine(title=u"Hostname",
                            default="localhost")
    port = schema.Int(title=u"Port",
                      default=143)

    user = schema.ASCIILine(title=u"user name")
    password = schema.Password(title=u"password")
    
    
    search_charset = schema.ASCIILine(title=u"Search charset",
                                      required=False)
    search_criterion = schema.ASCIILine(title=u"Search criterion",
                                        default="ALL")


class IMAPView(BrowserView):
    """default imap view"""
    
    def __init__(self, context, request):
        super(IMAPView, self).__init__(context, request)
        self._mails = []

    def update(self):
        #http://hg.python.org/cpython/file/b9a95ce2692c/Lib/imaplib.py
        """
           example of search criterion:
           
           search(None, '(SUBJECT "test message 2")')
           search(None, '(FROM "Doug" SUBJECT "test message 2"))

          http://tools.ietf.org/html/rfc1730.html#section-6.4.4
         
          The defined search keys are as follows.  Refer to the Formal
          Syntax section for the precise syntactic definitions of the
          arguments.
    
          <message set>  Messages with message sequence numbers
                         corresponding to the specified message sequence
                         number set
    
          ALL            All messages in the mailbox; the default initial
                         key for ANDing.
    
          ANSWERED       Messages with the \Answered flag set.
    
          BCC <string>   Messages that contain the specified string in the
                         envelope structure's BCC field.
    
          BEFORE <date>  Messages whose internal date is earlier than the
                         specified date.
    
          BODY <string>  Messages that contain the specified string in the
                         body of the message.
    
          CC <string>    Messages that contain the specified string in the
                         envelope structure's CC field.
    
          DELETED        Messages with the \Deleted flag set.
    
          DRAFT          Messages with the \Draft flag set.
    
          FLAGGED        Messages with the \Flagged flag set.
    
          FROM <string>  Messages that contain the specified string in the
                         envelope structure's FROM field.
    
          HEADER <field-name> <string>
                         Messages that have a header with the specified
                         field-name (as defined in [RFC-822]) and that
                         contains the specified string in the [RFC-822]
                         field-body.
    
          KEYWORD <flag> Messages with the specified keyword set.
    
          LARGER <n>     Messages with an RFC822.SIZE larger than the
                         specified number of octets.
    
          NEW            Messages that have the \Recent flag set but not the
                         \Seen flag.  This is functionally equivalent to
                         "(RECENT UNSEEN)".
    
          NOT <search-key>
                         Messages that do not match the specified search
                         key.
    
          OLD            Messages that do not have the \Recent flag set.
                         This is functionally equivalent to "NOT RECENT" (as
                         opposed to "NOT NEW").
    
          ON <date>      Messages whose internal date is within the
                         specified date.
    
          OR <search-key1> <search-key2>
                         Messages that match either search key.
    
          RECENT         Messages that have the \Recent flag set.
    
          SEEN           Messages that have the \Seen flag set.
    
          SENTBEFORE <date>
                         Messages whose [RFC-822] Date: header is earlier
                         than the specified date.
    
          SENTON <date>  Messages whose [RFC-822] Date: header is within the
                         specified date.
    
          SENTSINCE <date>
                         Messages whose [RFC-822] Date: header is within or
                         later than the specified date.
    
          SINCE <date>   Messages whose internal date is within or later
                         than the specified date.
    
          SMALLER <n>    Messages with an RFC822.SIZE smaller than the
                         specified number of octets.
    
          SUBJECT <string>
                         Messages that contain the specified string in the
                         envelope structure's SUBJECT field.
    
          TEXT <string>  Messages that contain the specified string in the
                         header or body of the message.
    
          TO <string>    Messages that contain the specified string in the
                         envelope structure's TO field.
    
          UID <message set>
                         Messages with unique identifiers corresponding to
                         the specified unique identifier set.
    
          UNANSWERED     Messages that do not have the \Answered flag set.
    
          UNDELETED      Messages that do not have the \Deleted flag set.
    
          UNDRAFT        Messages that do not have the \Draft flag set.
    
          UNFLAGGED      Messages that do not have the \Flagged flag set.
    
          UNKEYWORD <flag>
                         Messages that do not have the specified keyword
                         set.
    
          UNSEEN         Messages that do not have the \Seen flag set.
    
    
       Example:    C: A282 SEARCH FLAGGED SINCE 1-Feb-1994 NOT FROM "Smith"
                   S: * SEARCH 2 84 882
                   S: A282 OK SEARCH completed

       """
        M = imaplib.IMAP4()
        M.login(self.context.password, self.context.user)
        M.select()
        charset = self.context.search_charset
        if not charset or charset == 'None':
            charset = None
        criterion = self.context.search_criterion
        typ, data = M.search(None, criterion)
        for num in data[0].split():
            typ, data = M.fetch(num, '(RFC822)')
            print 'Message %s\n%s\n' % (num, data[0][1])
        M.close()
        M.logout()
      
        