# http://countergram.com/software/pytidylib
import tidylib

tidylib.BASE_OPTIONS = {}

def xml(markup):
    if hasattr(markup, "read"):
        markup = markup.read()
    options = {
        # Equivalent to `tidy -utf8 -xml`
        "input-xml": 1,
        "char-encoding": "utf8"
        }
    document, errors = tidylib.tidy_document(markup, options)
    return document

def html(markup):
    if hasattr(markup, "read"):
        markup = markup.read()
    options = {
        # Equivalent to _elementtidy.c from
        # http://effbot.org/zone/element-tidylib.htm
        "char-encoding": "utf8",
        "force-output": 1,
        "wrap": 0,
        "quiet": 1,
        "output-xhtml": 1,
        "add-xml-decl": 1,
        "indent": 0,
        "numeric-entities": 1
        }
    document, errors = tidylib.tidy_document(markup, options)
    return document
