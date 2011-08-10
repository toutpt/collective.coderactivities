from zope.schema.vocabulary import SimpleVocabulary

kind = SimpleVocabulary.fromItems((
    ("commit", u"Commit"),
    ("documentation", u"Documentation"),
    ("blog", u"Blog"),
    ("email", u"Email")))
