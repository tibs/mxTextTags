#!/usr/bin/env python2

"""Translate - a first attempt at parsing my little language

Usage: Translate [switches] <infile> [<outfile>]

        -stdout         -- write to standard output instead of a file
        -force          -- write to the <outfile> even if it already
                           exists (overwrite any existing file)

        -import         -- import tag table from Translate_tags.py,
                           instead of using the internal table

        -compare        -- compare the imported and internal tag tables
                           (development option!)

        -test           -- use our internal test data and write to stdout
        -pytag          -- use the interpreted tagging engine
        -debug          -- if -pytag, enable its debugger
        -diag           -- enable general debugging
                           Beware that this currently also writes line
                           numbers to the start of each line in the output,
                           so it doesn't emit legal Python...

        -help           -- show this text
        -history        -- show the module history
        -version        -- show the module version

If <outfile> is not specified, <infile> will be used with its extension
replaced by ".py".
"""

__author__  = """Tibs (Tony J Ibbs)
tony@lsl.co.uk or tibs@tibsnjoan.demon.co.uk or tibs@bigfoot.com
http://www.tibsnjoan.demon.co.uk/
"""
__version__ = "0.3 (tiepin) of 1999-11-15"
__history__ = """\
Originally created 1999-08-13

First released version is 0.2 (bootstrap)/1999-09-09, which gave
an idea of how the thing would work, and nearly did.

Second released version is 0.3 (tiepin)/1999-11-15, which is sufficient
to allow the parser used within this utility to be written in the little
language, translated and then used as such.
"""

import sys
import os
import string

# ............................................................
# How we want to work things - this is fudge for me in initial development
if os.name == "posix":
    # Unix at work
    DEFAULT_DEBUG = 0
    DEFAULT_PYTAG = 0
else:
    # Windows 95 at home
    TEXTTOOLS_PATH = "C:\\Program Files\\Python"
    PYTAG_PATH  = "C:\\Program Files\\Python\\TextTools\\Examples"
    DEFAULT_DEBUG = 0
    DEFAULT_PYTAG = 0

    if TEXTTOOLS_PATH not in sys.path:
        print "Adding",TEXTTOOLS_PATH
        sys.path.append(TEXTTOOLS_PATH)

    if PYTAG_PATH not in sys.path:
        print "Adding",PYTAG_PATH
        sys.path.append(PYTAG_PATH)
# ............................................................

# Import the TextTools themselves
# - I'm not personally too keen on import *, but it seems to be
#   the recommended thing, so I'll leave it for now...
try:
    from mx.TextTools import *
except:
    from TextTools.Constants.TagTables import *
    from TextTools.Constants.Sets import *


# ------------------------------------------------------------
# Useful little constants for unpicking the parsed tuples
OBJECT  = 0
LEFT    = 1
RIGHT   = 2
SUBLIST = 3

# We want to align inline comments when possible - so this is
# the column at which we will try to place their "#" marks...
COMMENT_COLUMN = 40

# Are we (generally) debugging?
DEBUGGING = 0

# Do we want a comma after the last tuple (or item) in a table?
WANT_LAST_COMMA = 1


# ------------------------------------------------------------
def define_tagtable():
    """Returns our tag table, if we're not importing it."""

    # We are not, initially, going to try for anything very sophisticated
    # - just something that will get us bootstrapped, so that I can use the
    #   "little language" to write more sophisticated stuff (without having
    #   to worry about dropped commas between tuples, and so on!)


    # Whitespace is always useful
    t_whitespace = (None,AllIn,' \t')
    t_opt_whitespace = t_whitespace + (+1,)

    # Comments are fairly simple
    t_comment = ('comment',Table,
                 ((None,Is,'#'),
                  (None,AllNotIn,'\n\r',MatchOk))
                 )

    # We care about the "content" of the indentation at the start of a line,
    # but note that it is optional
    t_indent = ('indent',AllIn,' \t')
    t_indentation = t_indent + (+1,)        # zero indentation doesn't show

    # A string is text within single or double quotes
    # (of course, this is an oversimplification, because we should also
    #  deal with things like "This is a \"substring\"", and it would be
    #  nice to be able to cope with triple-quoted strings too, but it
    #  will do for a start)

    # Major bug - doesn't recognised zero length strings...
    # (since "AllNotIn" must match at least one character)
    t_string = ('str',Table,
                ((None,Is,"'",+3,+1),
                 ('text',AllNotIn,"'"),
                 (None,Is,"'",MatchFail,MatchOk),
                 (None,Is,'"'),
                 ('text',AllNotIn,'"'),
                 (None,Is,'"'),
                 ))

    # An integer is a series of digits...
    t_integer = ('int',AllIn,number)
    
    t_signed_integer = ('signed_int',Table,
                        (('sign',Is,"+",+1,+2),
                         ('sign',Is,"-",+1,+1),
                         t_integer
                         ))

    # Remember to be careful to specify the LONGEST possible match first,
    # so that we try for "IsIn" before we try for "Is" (because "IsIn"
    # would *match* "Is", leaving us with a spurious "In" hanging around...)
    t_operation = ('op',Table,
                   (('op',Word,"AllInSet",   +1,MatchOk),
                    ('op',Word,"AllIn",      +1,MatchOk),
                    ('op',Word,"AllNotIn",   +1,MatchOk),
                    ('op',Word,"CallArg",    +1,MatchOk),
                    ('op',Word,"Call",       +1,MatchOk),
                    ('op',Word,"EOF",        +1,MatchOk),
                    ('op',Word,"Fail",       +1,MatchOk),
                    ('op',Word,"IsInSet",    +1,MatchOk),
                    ('op',Word,"IsIn",       +1,MatchOk),
                    ('op',Word,"IsNotIn",    +1,MatchOk),
                    ('op',Word,"IsNot",      +1,MatchOk),
                    ('op',Word,"Is",         +1,MatchOk),
                    ('op',Word,"Jump",       +1,MatchOk),
                    ('op',Word,"LoopControl",+1,MatchOk),
                    ('op',Word,"Loop",       +1,MatchOk),
                    ('op',Word,"Move",       +1,MatchOk),
                    ('op',Word,"NoWord",     +1,MatchOk), # alias for WordStart
                    ('op',Word,"Skip",       +1,MatchOk),
                    ('op',Word,"SubTableInList",+1,MatchOk),
                    ('op',Word,"SubTable",   +1,MatchOk),
                    ('op',Word,"sFindWord",  +1,MatchOk),
                    ('op',Word,"sWordStart", +1,MatchOk),
                    ('op',Word,"sWordEnd",   +1,MatchOk),
                    ('op',Word,"TableInList",+1,MatchOk),
                    ('op',Word,"Table",      +1,MatchOk),
                    ('op',Word,"WordStart",  +1,MatchOk),
                    ('op',Word,"WordEnd",    +1,MatchOk),
                    ('op',Word,"Word",       MatchFail,MatchOk),
                    ))

    # Python keywords
    t_keyword = ('keyword',Table,
                 ((None,Word,"and",     +1,+28),
                  (None,Word,"assert",  +1,+27),
                  (None,Word,"break",   +1,+26),
                  (None,Word,"class",   +1,+25),
                  (None,Word,"continue",+1,+24),
                  (None,Word,"def",     +1,+23),
                  (None,Word,"del",     +1,+22),
                  (None,Word,"elif",    +1,+21),
                  (None,Word,"else",    +1,+20),
                  (None,Word,"except",  +1,+19),
                  (None,Word,"exec",    +1,+18),
                  (None,Word,"finally", +1,+17),
                  (None,Word,"for",     +1,+16),
                  (None,Word,"from",    +1,+15),
                  (None,Word,"global",  +1,+14),
                  (None,Word,"if",      +1,+13),
                  (None,Word,"import",  +1,+12),
                  (None,Word,"in",      +1,+11),
                  (None,Word,"is",      +1,+10),
                  (None,Word,"lambda",  +1,+9),
                  (None,Word,"not",     +1,+8),
                  (None,Word,"or",      +1,+7),
                  (None,Word,"pass",    +1,+6),
                  (None,Word,"print",   +1,+5),
                  (None,Word,"raise",   +1,+4),
                  (None,Word,"return",  +1,+3),
                  (None,Word,"try",     +1,+2),
                  (None,Word,"while",   MatchFail,+1),
                  # In order to not recognise things like "in_THIS_CASE"
                  # we must check that the next character is not legitimate
                  # within an identifier
                  (None,IsIn,alpha+'_'+number,+1,MatchFail),
                  # If it wasn't another identifier character, we need to
                  # unread it so that it can be recognised as something else
                  # (so that, for instance, "else:" is seen as "else" followed
                  #  by ":")
                  (None,Skip,-1)
                  ))

    # Do the same for mxText commands
    t_mxkeyword = ('mxKeyword',Table,
                   (t_operation,
                    (None,IsIn,alpha+'_'+number,+1,MatchFail),
                    (None,Skip,-1)
                    ))

    # Traditional identifiers
    t_identifier = ('identifier',Table,
                    (t_keyword   + (+1,MatchFail), # don't allow Python keywords
                     t_mxkeyword + (+1,MatchFail), # don't allow mxText commands
                     (None,IsIn,alpha+'_'),        # can't start with a digit
                     (None,AllIn,alpha+'_'+number,MatchOk))
                    )

    # We don't yet deal with the following with anything in parentheses,
    # which means we can't handle functions or command lists, or other
    # things which "look like" a tuple
    t_argument = ('arg',Table,
                  (('arg',Word,"Here",     +1,MatchOk), # EOF Here, Fail Here
                   ('arg',Word,"ToEOF",    +1,MatchOk), # Move ToEOF
                   ('arg',Word,"To",       +1,MatchOk), # Jump To
                   ('arg',Word,"ThisTable",+1,MatchOk), # [Sub]Table ThisTable
                   ('arg',Word,"back",     +1,MatchOk), # Skip back
                   ('arg',Word,"Break",    +1,MatchOk), # LoopControl Break
                   ('arg',Word,"Reset",    +1,MatchOk), # LoopControl Reset
                   t_string             + (+1,MatchOk), # e.g., Word "Fred"
                   t_signed_integer     + (+1,MatchOk), # e.g., Skip -4, Move 3
                   t_identifier                         # e.g., Table Fred
                   ))

    t_plus = ('plus',Table,
              (t_opt_whitespace,
               (None,Is,"+"),
               t_opt_whitespace
               ))

    # Arguments can contain "+"
    t_plus_arg = ('plusarg',Table,
                  (t_argument,              # start with a single argument
                   t_plus + (MatchOk,),     # if we have a "+"
                   t_argument,              # then we expect another argument
                   (None,Jump,To,-2),       # then look for another "+"
                   ))

    # Match, for example:
    #        <fred>
    t_label = ('label',Table,
               ((None,Is,"<"),
                t_identifier,
                (None,Is,">")
                ))

    # Targets for Jump and F:/T:
    t_target = ('target',Table,
                (('tgt',Word,"next",     +1,MatchOk),
                 ('tgt',Word,"previous", +1,MatchOk),
                 ('tgt',Word,"repeat",   +1,MatchOk),
                 ('tgt',Word,"MatchOk",  +1,MatchOk),
                 ('tgt',Word,"MatchOK",  +1,MatchOk), # For kindness sake
                 ('tgt',Word,"MatchFail",+1,MatchOk),
                 t_label
                 ))

    # A value is either an identifier, or a string, or an integer
    t_value = ('val',Table,
               (t_identifier +(+1,MatchOk),
                t_string     +(+1,MatchOk),
                t_integer
                ))

    # An assignment is (optionally) used in Tuple and Table definitions...
    t_assignment = ('assignment',Table,
                    (t_value,
                     t_opt_whitespace,
                     (None,Is,'='),
                     ))

    # A common error when writing tuples is to miss off the "=" sign
    # - the following is used in diagnosing that (see t_bad_tuple below)
    # (it's useful to have something with identical structure to the
    #  "real thing")
    t_bad_tagobj = ('tagobj',Table,
                    (t_string,
                     ))

    t_bad_assignment = ('assignment',Table,
                        (t_value,
                         ))

    # This is the line that starts the definition of a single tuple.
    # For the moment, restrict what it gets assigned to to a simple identifier.
    # Match, for example:
    #        Fred is:
    t_tupleblock = ('tupleblock',Table,
                    (t_identifier,
                     t_whitespace,
                     (None,Word,"is:")
                     ))

    # This is the line that starts a new table or sub-table.
    # For the moment, we only cope with full Tables.
    # NOTE that this is used for the "outer" declaration of a tag table,
    # and also for the "inner" declaration of an inner table or sub-table.
    # The discrimination between these is done after initial parsing.
    # Match, for example:
    #        'keyword' = Table is:      (inner)
    #        tagtable = Table is:       (outer)
    t_tableblock = ('tableblock',Table,
                    (t_assignment + (+2,+1),  # left hand side is optional
                     t_opt_whitespace,
                     ('type',Word,"Table",+1,+2),  # Either "Table"
                     ('type',Word,"SubTable"),     # or "SubTable" is required
                     t_whitespace,            # whitespace is required
                     (None,Word,"is:")        # "is:" is required
                     ))

    # This is the line that starts an "if" block
    # Match, for example:
    #        Is "Fred":
    #        controlsymbol:
    t_ifblock = ('ifblock',Table,
                 (t_assignment + (+2,+1),      # left hand side is optional
                  t_opt_whitespace,
                  t_operation + (+4,+1),
                  t_whitespace,
                  t_plus_arg,
                  (None,Is,":",MatchFail,MatchOk),
                  t_identifier,
                  (None,Is,":")
                  ))

    # Note that we don't allow spaces WITHIN our false and true thingies

    t_onfalse = ('onfalse',Table,
                 (t_whitespace,
                  (None,Word,"F:"),
                  t_target
                  ))

    t_ontrue = ('ontrue',Table,
                (t_whitespace,
                 (None,Word,"T:"),
                 t_target
                 ))

    # Valid examples are things like:
    #        'fred' = Is "xxx" F:<wow> T:MatchOk
    #       AllIn jim T:<foundJim>
    #
    # For the moment, we're not trying to recognise things in any detail
    t_tuple = ('tuple',Table,
               (t_assignment + (+2,+1),  # left hand side is optional
                t_opt_whitespace,
                t_operation,         # operation is required
                t_whitespace,        # for the moment, we always require space here
                t_plus_arg,          # argument is required
                t_onfalse + (+1,+1),          # F:target is optional
                t_ontrue  + (MatchOk,MatchOk) # T:target is also optional
                ))

    # If the user has defined a "partial" tuple, they might use something
    # of the form:
    #       match_fred  F:MatchFalse T:MatchOk
    t_tupleplus = ('tupleplus',Table,
                   (t_identifier,
                    t_onfalse + (+1,+1),          # F:target is optional
                    t_ontrue  + (MatchOk,MatchOk) # T:target is also optional
                    ))

    # Treat Jump To specially - for example:
    #       Jump To <top>
    # so that they don't have to do the less obvious "Jump To F:<label>"
    # (although that will still be recognised, of course, for people who
    # are used to the tag tuple format itself)
    t_jumpto = ('jumpto',Table,
                ((None,Word,"Jump"),
                 t_whitespace,
                 (None,Word,"To"),
                 t_whitespace,
                 t_target
                 ))

    # Is it worth coping with these?
    t_bad_jumpto = ('jumpto',Table,
                    ((None,Word,"Jump",+2),         # cope with Jump to
                     (None,Word,"to",MatchFail,+2),
                     (None,Word,"JumpTo"),          # and with JumpTo
                     t_target
                     ))

    # The "content" of a line is the bit after any indentation, and before
    # any comment...
    # For the moment, we won't try to maintain ANY context, so it is up to the
    # user of the tuples produced to see if they make sense...
    t_content = ('content',Table,
                 (t_label        + (+1,MatchOk),
                  t_tableblock   + (+1,MatchOk), # [<value> =] [Sub]Table is:
                  t_tupleblock   + (+1,MatchOk), # <identifier> is:
                  t_ifblock      + (+1,MatchOk), # <cmd> <arg>: OR <identifier>:
                  t_jumpto       + (+1,MatchOk), # Jump To <target>
                  t_tuple        + (+1,MatchOk),
                  t_tupleplus    + (+1,MatchOk), # name [F:<label> [T:<label>]]
                  ))

    t_contentline = ('contentline',Table,
                     (t_content,            # something that we care about
                      t_opt_whitespace,
                      t_comment   +(+1,+1), # always allow a comment
                      (None,IsIn,newline)   # the end of the line
                      ))

    # Sometimes, the user (e.g., me) writes:
    #	'fred' = Table:
    # instead of:
    #	'fred' = Table is:
    # Unfortunately, without the "is", it would get too confusing whether
    # we actually wanted an if block...
    t_bad_tableblock = ('tableblock',Table,
                        (t_assignment + (+2,+1),  # left hand side is optional
                         t_opt_whitespace,
                         (None,Word,"Table"),     # "Table" is required
                         (None,Is,":")            # "is" is needed before the ":"
                         ))

    # Sometimes, the use (e.g., me again) write:
    #	'fred' IsIn jim
    # instead of:
    #	'fred' = IsIn jim
    # Whilst I'm not entirely convinced that "=" is the best character
    # to use here, I think we do need something!
    t_bad_tuple = ('tuple',Table,
                   (t_bad_assignment, # obviously we have to have this!
                    t_whitespace,     # in which case the whitespace IS needed
                    t_operation,      # operation is required
                    t_whitespace,     # for the moment, we must have space here
                    t_plus_arg,       # argument is required
                    t_onfalse + (+1,+1),          # F:target is optional
                    t_ontrue  + (MatchOk,MatchOk) # T:target is also optional
                    ))

    # Make some attempt to recognise common errors...
    t_badcontent = ('badcontent',Table,
                    (t_bad_tableblock +(+1,MatchOk),
                     t_bad_tuple
                     ))

    t_badline = ('badline',Table,
                 (t_badcontent,         # something that we sort of care about
                  t_opt_whitespace,
                  t_comment   +(+1,+1), # always allow a comment
                  (None,IsIn,newline)   # the end of the line
                  ))

    t_emptyline = ('emptyline',Table,
                   (t_opt_whitespace,
                    (None,IsIn,newline)     # the end of the line
                    ))

    t_commentline = ('commentline',Table,
                     (t_comment,
                      (None,IsIn,newline)   # the end of the line
                      ))

    t_passthruline = ('passthruline',Table,
                      (('passthru',AllNotIn,newline,+1), # owt else on the line
                       (None,IsIn,newline)               # the end of the line
                       ))

    # Basically, a file is a series of lines
    t_line = ('line',Table,
              (t_emptyline   +(+1,MatchOk),    # empty lines are simple enough
               t_indent      +(+1,+1),         # optional indentation
               t_commentline +(+1,MatchOk),    # always allow a comment
               t_contentline +(+1,MatchOk),    # a line we care about
               t_badline     +(+1,MatchOk),    # a line we think is wrong
               t_passthruline                  # a line we don't care about
               ))

    t_file = (t_line,
              (None,EOF,Here,-1)
              )

    return t_file


# ------------------------------------------------------------
# We'll define some moderately interesting test data

test_data = """\
# This example isn't *meant* to make any sense!
# It's just an accumulation of things that got checked for various reasons 
from TextTools import *
# Some Python code
a = b;
fred = 3;
if a == 1:
    print "a == 1"
else:
    print "a != 1"

# And the rest is our business...
t_integer is:
    'int' = AllIn '0123456789'
t_integer is:
    'int' = AllIn number
t_indent is:
    # A comment here is OK
    <label> # Strangely enough, so is a label
    'indent' = AllIn ' \t'
t_buggy = Table is:
    'int' AllIn number    # BUGGY LINE (missing "=")
    (None,"AllIn",number) # BUGGY LINE (an actual tuple)
    fred = jim            # BUGGY LINE (not our business)
    tagobj F:<op> T:next  # label <op> is undefined
    # The next line is totally empty

    # The next line contains just indentation

    # This line is just a comment
# And this comment should be JUST after the preceding block...
t_indentation is:          # This should be "= Table is:"
    t_indent
    t_indent F:previous
    t_indent T:previous
    t_indent F:previous T:previous
t_deep = Table is:
    'a' = SubTable is:
        SubTable is:
            'this' = Table ThisTable
            t_integer
t_fred = Table is:
    <top>
    AllIn 'a'
    'a' = AllIn 'a'
    'a' = AllIn 'a' F:previous
    'a' = AllIn 'a' T:previous
    'a' = AllIn 'a' F:previous T:previous
    AllIn 'abcd':
        AllIn 'xyz' F:<later> T:<top>
    'a' = AllIn 'abcd':
        AllIn 'xyz'
    <later>
    t_indent:
        AllIn 'xyz'
    AllIn number + '_'
    AllIn number+"_"+alpha
    Jump To <top>
"""


# ------------------------------------------------------------
# Our own exceptions

class OutsideError(Exception):
    """The entity is not permitted outside a block."""
    pass

class IndentError(Exception):
    """An indentation error has been detected."""
    pass

class NoIdentifier(Exception):
    """We're missing an identifier (to assign to)."""
    pass


# ------------------------------------------------------------
def LineFactory(lineno,tagtuple,text):
    """Take some tagged data and return an appropriate line class.

    lineno   -- the line number in the "file". Note that the first line
                in the file is line 1
    tagtuple -- a tag tuple for a single line of data
    text     -- the text for the "file". All the "left" and "right" offsets
                are relative to this text (i.e., it is the entire content
                of the file)

    The tag tuples we get back from the parser will be of the form:

        ('line',left,right,[
          ('indent',left,right,None),    -- this is optional
          ('content',left,right,[<data>])
        ])

    Looking at <type> should enable us to decide what to do with
    the <data>.
    """

    # Extract the list of tuples from this 'line'
    tuples = tagtuple[SUBLIST]

    # First off, do we have any indentation?
    tup = tuples[0]
    if tup[OBJECT] == "indent":
        # This is inefficient, because it actually copies strings
        # around - better would be to duplicate the calculation
        # that string.expandtabs does internally...
        indent_str = string.expandtabs(text[tup[LEFT]:tup[RIGHT]])
        tuples = tuples[1:]
    else:
        indent_str = ""
        tuples = tuples

    # Now, work out which class we want an instance of
    # (this is the 'fun' bit)

    type = tuples[0][OBJECT]
    if type == 'emptyline':
        return EmptyLine(lineno,indent_str,tuples[0],text)
    elif type == 'commentline':
        return CommentLine(lineno,indent_str,tuples[0],text)
    elif type == 'passthruline':
        return PassThruLine(lineno,indent_str,tuples[0],text)
    elif type == 'contentline':
        # OK - we need to go down another level
        sublist = tuples[0][SUBLIST]

        # Do we also have an in-line comment?
        if len(sublist) > 1:
            comment = sublist[1]
        else:
            comment = None

        # And the actual DATA for our line is down yet another level...
        sublist = sublist[0][SUBLIST]
        type = sublist[0][OBJECT]
        if type == 'label':
            return LabelLine(lineno,indent_str,sublist[0],comment,text)
        elif type == 'tableblock':
            return TableBlockLine(lineno,indent_str,sublist[0],comment,text)
        elif type == 'tupleblock':
            return TupleBlockLine(lineno,indent_str,sublist[0],comment,text)
        elif type == 'ifblock':
            return IfBlockLine(lineno,indent_str,sublist[0],comment,text)
        elif type == 'tuple':
            return TupleLine(lineno,indent_str,sublist[0],comment,text)
        elif type == 'tupleplus':
            return TuplePlusLine(lineno,indent_str,sublist[0],comment,text)
        elif type == 'jumpto':
            return JumpToLine(lineno,indent_str,sublist[0],comment,text)
        else:
            raise ValueError,\
                  "Line %d is of unexpected type 'contentline/%s'"%(lineno,
                                                                    type)
    elif type == 'badline':
        # OK - we need to go down another level
        sublist = tuples[0][SUBLIST]

        # Do we also have an in-line comment?
        if len(sublist) > 1:
            comment = sublist[1]
        else:
            comment = None

        # And the actual DATA for our line is down yet another level...
        sublist = sublist[0][SUBLIST]
        type = sublist[0][OBJECT]
        if type == 'tableblock':
            return BadTableBlockLine(lineno,indent_str,sublist[0],comment,text)
        if type == 'tuple':
            return BadTupleLine(lineno,indent_str,sublist[0],comment,text)
        else:
            raise ValueError,\
                  "Line %d is of unexpected type 'badline/%s'"%(lineno,type)
    else:
        raise ValueError,"Line %d is of unexpected type '%s'"%(lineno,type)



# ------------------------------------------------------------
class BaseLine:
    """The base class on which the various line types depend

    Contains:

      tagtuple    -- the tagtuple we (our subclass instance) represent(s)
      lineno      -- the line number in the file (first line is line 1)
      indent      -- our indentation (integer)
      indent_str  -- our indentation (a string of spaces)
      text        -- the text of the "file" we're within
      class_name  -- the name of the actual class this instance belongs to
                     (i.e., the name of the subclass, suitable for printing)

    Some things only get useful values after we've been instantiated
    
      next_indent -- the indentation of the next line
      index       -- for a line in a block, its index therein
    """

    def __init__(self,lineno,indent_str,tagtuple,text):
        """Instantiate a BaseLine.

        lineno     -- the line number in the "file". Note that the first line
                      in the file is line 1
        indent_str -- the indentation of the line (a string of spaces)
        tagtuple   -- the tag tuple for this line of data
        text       -- the text for the "file". All the "left" and "right"
                      offsets are relative to this text (i.e., it is the
                      entire content of the file)

        The content of the tagtuple depends on which of our subclasses
        is being used. Refer to the relevant doc string.
        """

        self.tagtuple = tagtuple
        self.lineno   = lineno
        self.text     = text

        self.class_name = self._class_name()
        self.indent_str = indent_str
        self.indent     = len(indent_str)

        # OK - we don't really know! (but this will do for "EOF")
        self.next_indent = 0

        # We don't always HAVE a sensible value for this
        self.index = None

        #if DEBUGGING:
        #    print "Line %3d: %s%s"%(lineno,indent_str,self.class_name)

    def change_indent(self,count=None,spaces=""):
        """Change our indentation.

        Specify either "count" or "spaces" (if both are given,
        "count" will be used, if neither is given, then the
        indentation will be set to zero)
        
        count  -- the number of spaces we're indented by
        spaces -- a string of spaces
        """
        if count:
            self.indent = count
            self.indent_str = count * " "
        else:
            self.indent_str = spaces
            self.indent = len(spaces)

    def _class_name(self):
        """Return a representation of the class name."""

        full_name = "%s"%self.__class__
        bits = string.split(full_name,".")
        return bits[-1]

    def starts_block(self):
        """Return true if we start a new block."""
        return 0

    def only_in_block(self):
        """Return true if we can only occur inside a block."""
        return 0

    def our_business(self):
        """Return true if we are a line we understand."""
        return 1

    def __str__(self):
        return "%3d %s%-10s"%(self.lineno,self.indent_str,self.class_name)

    def _intro(self):
        """Returns a useful 'introductory' string."""
        return "%3d %-10s %s"%(self.lineno,self.class_name,self.indent_str)

    def _trunc(self):
        """Returns a "truncated" representation of our text."""

        text = "%s %s"%(self._intro(),
                        `self.text[self.tagtuple[LEFT]:self.tagtuple[RIGHT]]`)

        if len(text) > 60:
            return text[:60]+"..."
        else:
            return text

    def resolve_labels(self,block):
        """Called to resolve any labels use in this line.

        block -- the block that contains us
        """
        # The default is to do nothing as we don't HAVE any labels...
        return

    def expand(self,stream,block=None):
        """Write out the expanded equivalent of ourselves.

        stream  -- an object with a "write" method, e.g., a file
        newline -- true if we should output a terminating newline
        block   -- used to pass the containing Block down to lines
                   within a block, or None if we're not in a block
        """

        if DEBUGGING:
            stream.write("Line %3d: "%self.lineno)

        stream.write(self.indent_str)
        stream.write(self.text[self.tagtuple[LEFT]:self.tagtuple[RIGHT]])
        stream.write(",\n")

    def warning(self,text):
        """Report a warning message.

        text -- the text to report
        """

        lines = string.split(text,"\n")
        print "###WARNING: line %d (%s)"%(self.lineno,self.class_name)
        for line in lines:
            print "###         %s"%line

    def error(self,text):
        """Report an error.

        text -- the error text to report
        """

        lines = string.split(text,"\n")
        print "###ERROR: line %d (%s)"%(self.lineno,self.class_name)
        for line in lines:
            print "###       %s"%line


# ------------------------------------------------------------
class EmptyLine(BaseLine):
    """An empty line.

    Note that the indentation of an empty line is taken to be the
    same as that of the next (non-empty) line. This is because it
    seems to me that (a) an empty line should not per-se close a
    block (which it would do if it had indentation 0) and (b) we
    don't remember any whitespace in an empty line, so the user
    can't assign an indentation themselves (which is a Good Thing!)
    """

    def __init__(self,lineno,indent_str,tagtuple,text):
        """Instantiate an EmptyLine.

        The content of the tagtuple is:
            None
        """

        BaseLine.__init__(self,lineno,indent_str,tagtuple,text)

    def expand(self,stream,block=None):
        """Write out the expanded equivalent of ourselves.

        stream  -- an object with a "write" method, e.g., a file
        block   -- used to pass the containing Block down to lines
                   within a block, or None if we're not in a block
        """

        if DEBUGGING:
            stream.write("Line %3d: "%self.lineno)

        # um - there's nothing to do, folks
        stream.write("\n")

    def our_business(self):
        """Return true if we are a line we understand."""
        return 0

    def _trunc(self):
        """Returns a "truncated" representation of our text."""

        return self._intro()


# ------------------------------------------------------------
class CommentLine(BaseLine):
    """A comment line."""

    def __init__(self,lineno,indent_str,tagtuple,text):
        """Instantiate a CommentLine.

        The content of the tagtuple is:
            ('comment',left,right,None)
        and the demarcated text includes the initial '#' character
        """

        BaseLine.__init__(self,lineno,indent_str,tagtuple,text)

        # We actually want the next tuple down (so to speak) so that
        # we lose the trailing newline...
        tup = self.tagtuple[SUBLIST][0]
        self.data = self.text[tup[LEFT]:tup[RIGHT]]

    def our_business(self):
        """Return true if we are a line we understand."""
        return 0

    def expand(self,stream,block=None):
        """Write out the expanded equivalent of ourselves.

        stream  -- an object with a "write" method, e.g., a file
        block   -- used to pass the containing Block down to lines
                   within a block, or None if we're not in a block
        """

        if DEBUGGING:
            stream.write("Line %3d: "%self.lineno)

        stream.write(self.indent_str)
        stream.write("%s\n"%self.data)


# ------------------------------------------------------------
class PassThruLine(BaseLine):
    """A line we just pass throught without interpretation."""

    def __init__(self,lineno,indent_str,tagtuple,text):
        """Instantiate a PassThruLine.

        The content of the tagtuple is:
            ('passthru',left,right,None)
        """

        BaseLine.__init__(self,lineno,indent_str,tagtuple,text)

        # We actually want the next tuple down (so to speak) so that
        # we lose the trailing newline...
        tup = self.tagtuple[SUBLIST][0]
        self.data = self.text[tup[LEFT]:tup[RIGHT]]

    def our_business(self):
        """Return true if we are a line we understand."""
        return 0

    def expand(self,stream,block=None):
        """Write out the expanded equivalent of ourselves.

        stream  -- an object with a "write" method, e.g., a file
        block   -- used to pass the containing Block down to lines
                   within a block, or None if we're not in a block
        """

        if DEBUGGING:
            stream.write("Line %3d: "%self.lineno)

        if block:
            err_str = "Unparsed line inside a block"\
                      " - it has been commented out"
            # Hmm - the following advice is less often useful than I
            # had hoped - leave it out for now...
            #if string.find(self.data,",") != -1:
            #    err_str = err_str + "\nCheck for a trailing comma?"

            self.error(err_str)

        # Always output the indentation, 'cos otherwise it looks silly
        stream.write(self.indent_str)

        if block:
            stream.write("#[ignored]#")

        stream.write("%s\n"%self.data)


# ------------------------------------------------------------
class ContentLine(BaseLine):
    """A line we have to interpret - another base class.

    Adds the following variables:

    comment -- any in-line comment on this line
    """

    def __init__(self,lineno,indent_str,tagtuple,comment,text):
        """Instantiate a ContentLine.

        comment -- either a comment tuple or None

        The content of the tagtuple is:
            ('contentline',left,right,
              [('content',left,right,[<data>]),
               ('comment',left,right,None)      -- optional
              ])
        where <data> is used in the internals of one of our subclasses
        (i.e., it is what is passed down in the "tagtuple" argument)
        """

        BaseLine.__init__(self,lineno,indent_str,tagtuple,text)
        self.comment = comment

        # Assume we're not the last "our business" line in a block...
        self.is_last = 0

    def _write_comment(self,stream,sofar):
        """Write out the in-line comment string.

        Since we're the only people to call this, we can safely
        rely on it only being called when there IS a comment tuple
        to output...

        stream  -- an object with a "write" method, e.g., a file
        sofar   -- the number of characters written to the line
                   so far
        """
        if sofar < COMMENT_COLUMN:
            stream.write(" "*(COMMENT_COLUMN - sofar))
        else:
            # always write at least one space...
            stream.write(" ")
        stream.write(self.text[self.comment[LEFT]:self.comment[RIGHT]])

    def _write_text(self,stream,block):
        """Write out the main tuple text.

        stream  -- an object with a "write" method, e.g., a file
        block   -- used to pass the containing Block down to lines
                   within a block, or None if we're not in a block

        This should generally be the method that subclasses override.
        It returns the number of characters written, or -1 if we had
        an error.
        """
        stream.write(self.text[self.tagtuple[LEFT]:self.tagtuple[RIGHT]])
        return self.tagtuple[RIGHT] - self.tagtuple[LEFT]

    def expand(self,stream,block=None):
        """Write out the expanded equivalent of ourselves.

        stream  -- an object with a "write" method, e.g., a file
        block   -- used to pass the containing Block down to lines
                   within a block, or None if we're not in a block
        """

        if DEBUGGING:
            stream.write("Line %3d: "%self.lineno)

        stream.write(self.indent_str)
        nchars = self._write_text(stream,block)
        # Don't write any in-line comment out if we had an error,
        # as the layout won't work!
        if nchars > -1 and self.comment:
            self._write_comment(stream,sofar=nchars+self.indent)
        stream.write("\n")


# ------------------------------------------------------------
class LabelLine(ContentLine):
    """A line containing a label.

    Contains:
        label -- our label string
    """

    def __init__(self,lineno,indent_str,tagtuple,comment,text):
        """Instantiate a LabelLine.

        For instance:

            <fred>

        The content of the tagtuple is:

            ('label',left,right,[
              ('identifier',left,right,None)
             ])
        """

        ContentLine.__init__(self,lineno,indent_str,tagtuple,comment,text)

        self.label = self.text[self.tagtuple[LEFT]:self.tagtuple[RIGHT]]

    def _write_text(self,stream,block):
        """Write out the main tuple text.

        stream  -- an object with a "write" method, e.g., a file
        block   -- used to pass the containing Block down to lines
                   within a block, or None if we're not in a block
        """
        # Enough difficult length calculation - let's do this one
        # the easy way...
        if DEBUGGING:
            text = "# Label %s at index %d"%(self.label,self.index)
        else:
            text = "# %s"%(self.label)  # surely enough for most people...
        stream.write(text)
        return len(text)

    def translate(self,index,block):
        """Return the translation of a use of this label as a target.

        index -- the index of the line which uses the label as a target
        block -- the Block we are within
        """

        # Hmm - I don't think this CAN go wrong at this point...
        return block.translate_label(self.label,self)

    def only_in_block(self):
        """Return true if we can only occur inside a block."""
        return 1


# ------------------------------------------------------------
class TableBlockLine(ContentLine):
    """A line starting a table block."""

    def __init__(self,lineno,indent_str,tagtuple,comment,text):
        """Instantiate a TableBlockLine.

        For instance:

            "fred" = Table is:
            Table is:

        This is used for two purposes:
        1. To define the actual tag table itself (i.e., at the outer
           level). Only "Table" is allowed in this instance, but since
           that is all we recognised for now, we shan't worry about it...
        2. To define an inner table (i.e., at an inner level)

        The content of the tagtuple is:

            ('tableblock',left,right,[
              ('assignment',left,right,[           -- optional if inner
                 ('val',left,right,[

                    ('identifier',left,right,[])
                 OR
                    ('str',left,right,[
                       ('text',left,right,None)
                     ])
                 OR
                    ('int',left,right,[])

                  ])
               ])
              ('type',left,right,[])       -- either "Table" or "SubTable"
             ])

        NOTE: as an "emergency" measure (so we can `pretend' that a
        TupleBlock was actually a TableBlock as part of attempted
        error correction), if tagtuple == ("error",tagobj) then we
        short-circuit some of the initialisation...
        """

        ContentLine.__init__(self,lineno,indent_str,tagtuple,comment,text)

        if tagtuple[0] == "error":
            # We're "bluffing" at the creation of a TableBlock
            self.tagobj = tagtuple[1]
            self.is_subtable = 0
        elif len(self.tagtuple[SUBLIST]) == 1:
            self.tagobj = "None"
            tup = self.tagtuple[SUBLIST][0]
            self.is_subtable = (self.text[tup[LEFT]:tup[RIGHT]] == "SubTable")
        else:
            # The first tuple down gives us the "<value> = " string
            tup = self.tagtuple[SUBLIST][0]
            # The next tuple down gives us "<value>" which is what we want
            tup = tup[SUBLIST][0]
            self.tagobj = self.text[tup[LEFT]:tup[RIGHT]]
            # Then we have the type of table
            tup = self.tagtuple[SUBLIST][1]
            self.is_subtable = (self.text[tup[LEFT]:tup[RIGHT]] == "SubTable")

    def got_tagobj(self):
        return (self.tagobj != "None")

    def starts_block(self):
        """Return true if we start a new block."""
        return 1

    def _write_text(self,stream,block):
        """Write out the main tuple text.

        stream  -- an object with a "write" method, e.g., a file
        block   -- used to pass the containing Block down to lines
                   within a block, or None if we're not in a block

        It returns the number of characters written, or -1 if we had
        an error.
        """

        if block:
            if self.is_subtable:
                stream.write("(%s,SubTable,("%self.tagobj)
                return len(self.tagobj) + 11
            else:
                stream.write("(%s,Table,("%self.tagobj)
                return len(self.tagobj) + 8
        else:
            stream.write("%s = ("%self.tagobj)
            return len(self.tagobj) + 4


# ------------------------------------------------------------
class TupleBlockLine(ContentLine):
    """A line starting a tuple block (i.e., defining a single tuple)

    Contains:
    
        name -- the "name" of this tuple (i.e., what comes
                before the "is:")
    """

    def __init__(self,lineno,indent_str,tagtuple,comment,text):
        """Instantiate a TupleBlockLine.

        For instance:

            Fred is:

        The content of the tagtuple is:
        
            ('tupleblock',left,right,[
              ('identifier',left,right,None)
             ])
        """

        ContentLine.__init__(self,lineno,indent_str,tagtuple,comment,text)

        tup = self.tagtuple[SUBLIST][0]
        self.name = self.text[tup[LEFT]:tup[RIGHT]]

    def starts_block(self):
        """Return true if we start a new block."""
        return 1

    def only_in_block(self):
        """Return true if we can only occur inside a block."""
        return 0

    def _write_text(self,stream,block):
        """Write out the main tuple text.

        stream  -- an object with a "write" method, e.g., a file
        block   -- used to pass the containing Block down to lines
                   within a block, or None if we're not in a block

        It returns the number of characters written, or -1 if we had
        an error.
        """
        # The "\" at the end is somewhat clumsy looking, but the
        # only obvious way of preserving layout...
        stream.write("%s = \\"%self.name)
        return len(self.name) + 5


# ------------------------------------------------------------
class IfBlockLine(ContentLine):
    """A line starting an if block.

    Contains:
        cmd  -- the command within this if block
        arg  -- the argument for said command
    or:
        name -- the name within this if block
    """

    def __init__(self,lineno,indent_str,tagtuple,comment,text):
        """Instantiate an IfBlockLine.

        For instance:

            'jim' = Is "Fred":
            Is "Fred":
            fred:

        The content of the tagtuple is:

            ('ifblock',left,right,[
              ('assignment',left,right,[
                 ('val',left,right,[

                    ('identifier',left,right,[])
                 OR
                    ('str',left,right,[
                       ('text',left,right,None)
                     ])
                 OR
                    ('int',left,right,[])

                  ])
               ])
              ('op',left,right,None),
              ('arg',left,right,None),
             ])
        or:
            ('ifblock',left,right,[
              ('op',left,right,None),
              ('arg',left,right,None),
             ])
        or:
            ('ifblock',left,right,[
              ('identifier',left,right,None)
             ])
        """

        ContentLine.__init__(self,lineno,indent_str,tagtuple,comment,text)

        tuples = self.tagtuple[SUBLIST]
        if tuples[0][OBJECT] == 'op':
            tup1 = tuples[0]
            tup2 = tuples[1]
            self.tagobj = "None"
            self.cmd    = self.text[tup1[LEFT]:tup1[RIGHT]]
            self.arg    = self.text[tup2[LEFT]:tup2[RIGHT]]
            self.name   = None
        elif tuples[0][OBJECT] == 'assignment':
            # The "<value>" in the "<value> = " string is down
            # one level more than the others
            tup0 = tuples[0][SUBLIST][0]
            self.tagobj = self.text[tup0[LEFT]:tup0[RIGHT]]
            tup1 = tuples[1]
            tup2 = tuples[2]
            self.cmd    = self.text[tup1[LEFT]:tup1[RIGHT]]
            self.arg    = self.text[tup2[LEFT]:tup2[RIGHT]]
            self.name   = None
        elif tuples[0][OBJECT] == 'identifier':
            tup = tuples[0]
            self.name   = self.text[tup[LEFT]:tup[RIGHT]]
            self.cmd    = None
            self.arg    = None
            self.tagobj = None
        else:
            # Hmm - try to continue with anything unexpected
            tup = tuples[0]
            self.error("Unexpected IfBlock subtype %s"%tup[OBJECT])
            self.name   = self.text[tup[LEFT]:tup[RIGHT]]
            self.cmd    = None
            self.arg    = None
            self.tagobj = None

        # Currently, we have one 'special' argument
        if self.arg == "back": self.arg = "-1"

        # We don't yet know the offset of the "virtual label" at the
        # end of this if block...
        self.end_label = None

    def starts_block(self):
        """Return true if we start a new block."""
        return 1

    def only_in_block(self):
        """Return true if we can only occur inside a block."""
        return 1

    def resolve_labels(self,block):
        """Called to resolve any labels used in this line.

        block -- the block that contains us

        Note that this only does something the first time it
        is called - this will be when the IF block's startline
        is asked to resolve its labels. If it is called again,
        as a 'normal' line, it will do nothing...
        """
        if not self.end_label:
            self.end_label = "%+d"%(len(block.business)+1)

    def _write_text(self,stream,block):
        """Write out the main tuple text.

        stream  -- an object with a "write" method, e.g., a file
        block   -- used to pass the containing Block down to lines
                   within a block, or None if we're not in a block

        It returns the number of characters written, or -1 if we had
        an error.
        """
        if not self.end_label:
            # This should never happen, but just in case, warn the user!
            self.error("Unable to determine 'onFalse' destination in IF")

        if self.name:
            stream.write("%s + (%s,+1),"%(self.name,
                                          self.end_label or "<undefined>"))
            return len(self.name) + 20
        else:
            stream.write("(%s,%s,%s,%s,+1),"%(self.tagobj,self.cmd,self.arg,
                                              self.end_label or "<undefined>"))
            return len(self.tagobj) + len(self.cmd) + len(self.arg) + \
                   len(self.end_label) + 20


# ------------------------------------------------------------
class TupleLine(ContentLine):
    """A line containing a basic tuple.


    Contains:
        tagobj  -- optional
        cmd     -- the command
        arg     -- the argument
        ontrue  -- what to do if true
        onfalse -- ditto false
    """

    def __init__(self,lineno,indent_str,tagtuple,comment,text):
        """Instantiate a TupleLine.

        The content of the tagtuple is:
        
            ('tuple',left,right,[
              ('tagobj',left,right,[           -- optional
                 ('str',left,right,[
                    ('text',left,right,None)
                  ])
               ])
              ('op',left,right,None),
              ('arg',left,right,None),
              ('onfalse',left,right,[          -- optional
                 ('target',left,right,[
                   ('tgt',left,right,None)
                 ]),
              ('ontrue',left,right,[           -- optional
                 ('target',left,right,[
                   ('tgt',left,right,None)
                 ])
               ])
             ])
        """

        ContentLine.__init__(self,lineno,indent_str,tagtuple,comment,text)

        self.unpack()


    def unpack(self):
        """Unpack our contents from our tagtuple."""

        # This is doubtless not the most efficient way of doing this,
        # but it IS relatively simple...
        dict = {}
        #for key in ("assignment","op","arg","onfalse","ontrue"):
        for key in ("assignment","op","plusarg","onfalse","ontrue"):
            dict[key] = None

        tuples = self.tagtuple[SUBLIST]
        for item in tuples:
            name = item[OBJECT]
            if name == "onfalse" or name == "ontrue" or name == "assignment":
                # For these, we need to go "down one level" for our data
                tup = item[SUBLIST][0]
                dict[name] = (tup[LEFT],tup[RIGHT])
            else:
                dict[name] = (item[LEFT],item[RIGHT])

        # The tag object is optional
        if dict["assignment"]:
            left,right = dict["assignment"]
            self.tagobj = self.text[left:right]
        else:
            self.tagobj = "None"

        # The operation (command) and argument are required
        left,right = dict["op"]
        self.cmd = self.text[left:right]

        #left,right = dict["arg"]
        left,right = dict["plusarg"]
        self.arg = self.text[left:right]

        # Currently, we have one 'special' argument
        if self.arg == "back": self.arg = "-1"

        # Actually, we don't want the F and T jumps explicit if not
        # given, since we mustn't output them for a single tuple if
        # they're not given (so they can be "added in" later on)
        if dict["onfalse"]:
            left,right = dict["onfalse"]
            self.onfalse = self.text[left:right]
        else:
            self.onfalse = None		# "MatchFail"
        if dict["ontrue"]:
            left,right = dict["ontrue"]
            self.ontrue = self.text[left:right]
        else:
            self.ontrue = None 		# "next"

    def only_in_block(self):
        """Return true if we can only occur inside a block."""
        return 1

    def resolve_labels(self,block):
        """Called to resolve any labels use in this line.

        block -- the block that contains us
        """
        if self.onfalse:
            self.onfalse = block.translate_label(self.onfalse,self)
        if self.ontrue:
            self.ontrue  = block.translate_label(self.ontrue,self)

    def _write_text(self,stream,block):
        """Write out the main tuple text.

        stream  -- an object with a "write" method, e.g., a file
        block   -- used to pass the containing Block down to lines
                   within a block, or None if we're not in a block

        It returns the number of characters written, or -1 if we had
        an error.
        """

        # Start with the stuff we must have...
        stream.write("(%s,%s,%s"%(self.tagobj,self.cmd,self.arg))
        length = len(self.tagobj) + len(self.cmd) + len(self.arg) + 3

        if self.ontrue:
            if not self.onfalse:
                # OK, we didn't get an explicit F, but because it comes
                # before the T jump in the tuple, we need to fake it
                # anyway...
                stream.write(",%s,%s)"%("MatchFail",self.ontrue))
                length = length + len("MatchFail") + len(self.ontrue) + 3
            else:
                # We had both F and T
                stream.write(",%s,%s)"%(self.onfalse,self.ontrue))
                length = length + len(self.onfalse) + len(self.ontrue) + 3
        elif self.onfalse:
            # We only had F. We shan't "fake" the T jump, *just* in case
            # the user is defining a single tuple that they'll add the
            # T jump to later on (although that *is* a bit dodgy, I think)
            # [[The option would be to "fake" it if we're IN a block - I may
            #   go for that approach later on]]
            stream.write(",%s)"%self.onfalse)
            length = length + len(self.onfalse) + 2
        else:
            # Neither F nor T - so don't write the defaults for either,
            # in case this is a top level tuple they're going to add to
            # later on...
            # [[Comments as for the case above, I think]]
            stream.write(")")
            length = length + 1

        if block and not self.is_last:
            stream.write(",")
            length = length + 1

        return length

# ------------------------------------------------------------
class TuplePlusLine(ContentLine):
    """A line containing a tuple "plus" (e.g., "fred + (+1,+1)").

    Contains:

        name    -- the name/identifier
        ontrue  -- what to do if true
        onfalse -- ditto false
    """

    def __init__(self,lineno,indent_str,tagtuple,comment,text):
        """Instantiate a TuplePlusLine.

            <identifier> + (onF,onT)

        The content of the tagtuple is:
        
            ('tupleplus',left,right,[
              ('identifier',left,right,None)
              ('onfalse',left,right,[          -- optional
                 ('target',left,right,[
                   ('tgt',left,right,None)
                 ]),
              ('ontrue',left,right,[           -- optional
                 ('target',left,right,[
                   ('tgt',left,right,None)
                 ])
               ])
             ])
        """

        ContentLine.__init__(self,lineno,indent_str,tagtuple,comment,text)

        self.unpack()


    def unpack(self):
        """Unpack our contents from our tagtuple."""

        # This is doubtless not the most efficient way of doing this,
        # but it IS relatively simple...
        dict = {}
        for key in ("identifier","onfalse","ontrue"):
            dict[key] = None

        tuples = self.tagtuple[SUBLIST]
        for item in tuples:
            name = item[OBJECT]
            if name == "onfalse" or name == "ontrue":
                # For these, we need to go "down one level" for our data
                tup = item[SUBLIST][0]
                dict[name] = (tup[LEFT],tup[RIGHT])
            else:
                dict[name] = (item[LEFT],item[RIGHT])

        # Start with the identifier
        left,right = dict["identifier"]
        self.name = self.text[left:right]

        # Actually, we don't want the F and T jumps explicit if not
        # given, since we mustn't output them for a single tuple if
        # they're not given (so they can be "added in" later on)
        if dict["onfalse"]:
            left,right = dict["onfalse"]
            self.onfalse = self.text[left:right]
        else:
            self.onfalse = None		# "MatchFail"
        if dict["ontrue"]:
            left,right = dict["ontrue"]
            self.ontrue = self.text[left:right]
        else:
            self.ontrue = None 		# "next"

    def only_in_block(self):
        """Return true if we can only occur inside a block."""
        return 1

    def resolve_labels(self,block):
        """Called to resolve any labels use in this line.

        block -- the block that contains us
        """
        if self.onfalse:
            self.onfalse = block.translate_label(self.onfalse,self)
        if self.ontrue:
            self.ontrue  = block.translate_label(self.ontrue,self)

    def _write_text(self,stream,block):
        """Write out the main tuple text.

        stream  -- an object with a "write" method, e.g., a file
        block   -- used to pass the containing Block down to lines
                   within a block, or None if we're not in a block

        It returns the number of characters written, or -1 if we had
        an error.
        """

        if not self.onfalse and not self.ontrue:
            stream.write("%s"%self.name)
            length = len(self.name)
        else:
            # Make a feeble attempt to cause successive such lines to
            # look neater, by aligning the "+" signs (if we output them)
            stream.write("%-15s + ("%(self.name))
            length = max(len(self.name),15) + 4
            if self.ontrue and self.onfalse:
                stream.write("%s,%s)"%(self.onfalse,self.ontrue))
                length = length + len(self.onfalse) + len(self.ontrue) + 2
            elif self.ontrue:
                stream.write("MatchFail,%s)"%(self.ontrue))
                length = length + len(self.ontrue) + 11
            else:
                # Don't forget that comma to make this a tuple!
                stream.write("%s,)"%(self.onfalse))
                length = length + len(self.onfalse) + 1

        if not self.is_last:
            stream.write(",")
            length = length + 1

        return length


# ------------------------------------------------------------
class JumpToLine(ContentLine):
    """A line containing "Jump To <label>"

    Contains:

        name    -- the name/identifier
        onfalse -- the target (which is technically an "on false" jump)
    """

    def __init__(self,lineno,indent_str,tagtuple,comment,text):
        """Instantiate a JumpLine.

            Jump To <label>

        The content of the tagtuple is:
        
            ('jumpto',left,right,[
               ('target',left,right,[
                 ('tgt',left,right,None)
               ]),
             ])
        """

        ContentLine.__init__(self,lineno,indent_str,tagtuple,comment,text)

        tup = self.tagtuple[SUBLIST][0]
        self.onfalse = self.text[tup[LEFT]:tup[RIGHT]]

    def only_in_block(self):
        """Return true if we can only occur inside a block."""
        return 1

    def resolve_labels(self,block):
        """Called to resolve any labels use in this line.

        block -- the block that contains us
        """
        self.onfalse = block.translate_label(self.onfalse,self)

    def _write_text(self,stream,block):
        """Write out the main tuple text.

        stream  -- an object with a "write" method, e.g., a file
        block   -- used to pass the containing Block down to lines
                   within a block, or None if we're not in a block

        It returns the number of characters written, or -1 if we had
        an error.
        """

        stream.write("(None,Jump,To,%s)"%(self.onfalse))
        length = len(self.onfalse) + 15

        if not self.is_last:
            stream.write(",")
            length = length + 1

        return length


# ------------------------------------------------------------
class BadTableBlockLine(TableBlockLine):
    """We think they MEANT this to be a table block line."""

    def __init__(self,lineno,indent_str,tagtuple,comment,text):
        """Instantiate a BadTableBlockLine.

        For instance:

            "fred" = Table:
            Table:
        """
        TableBlockLine.__init__(self,lineno,indent_str,tagtuple,comment,text)
        self.error("Suspected missing 'is' before the colon\n"
                   "pretending it's there")


# ------------------------------------------------------------
class BadTupleLine(TupleLine):
    """We think they MEANT this to be a tuple line."""

    def __init__(self,lineno,indent_str,tagtuple,comment,text):
        """Instantiate a BadTupleLine.

        For instance:

            "fred" = IsIn "abc"
        """
        TupleLine.__init__(self,lineno,indent_str,tagtuple,comment,text)
        self.error("Suspected missing '=' between tag object and command\n"
                   "pretending it's there")


# ------------------------------------------------------------
class Block(ContentLine):
    """This class represents a "block".

    A "block" is a section of code which starts with a line ending in
    a colon (":"), with the next line and subsequent lines ("in" the
    block) having an extra indent. The block ends when a dedent is
    encountered.

    Each instance "eats" lines from the input until (if) it finds the first
    "sub" block.  That then "eats" lines until it finds its own end, and
    then hands control back to the first instance, which does the same thing
    again, and so on.

    Note that we "pretend" to be a content line - it is convenient to
    look like a line class, so that line processing can cope with us,
    and indeed what we do is "pretend" to be a clone of our start line
    with some extra information...

    Contains:
        startline    -- the line that "introduces" this block
        items        -- a list of the lines and blocks within this block
        label_dict   -- a dictionary of {label name : line index}
        inner_indent -- the indentation of our "inner" lines
        outer        -- true if we are an "outer" block
                        (i.e., not contained within another block)
    """

    def __init__(self,startline=None,outer=0,file=None):
        """Instantiate a new block.

        startline -- the line that introduces this block
        outer     -- true if we are an outer block
        file      -- the "file" we're reading lines from
        """

        # Pretend to be our own startline (as a generic)
        ContentLine.__init__(self,
                             startline.lineno,startline.indent_str,
                             startline.tagtuple,startline.comment,
                             startline.text)

        # But also remember the specifics of the startline
        self.startline = startline

        # We "fudge" our class name
        self.class_name = self._block_class_name(startline)

        self.outer    = outer
        self.file     = file

        # If we're an outer table block, do we have a tagobj?
        if self.startline.class_name == "TableBlockLine" and outer:
            if not self.startline.got_tagobj():
                raise NoIdentifier,\
                      "Tag table at line %d is not assigned to a variable"%\
                      (self.lineno)
            elif self.startline.is_subtable:
                raise OutsideError,\
                      "SubTable is not allowed outside a block at line %d"%\
                      (self.lineno)

        self.items    = []	# all lines within this block
        self.business = []	# just those that are "our business"
        self.label_dict = {}    # remember our labels and their locations
        self.next_index = 0     # 'business' line indices
        self.inner_indent = None

        # Eat lines until we reach the end of our block...
        if DEBUGGING: print "%sStart %s"%(self.indent_str,self.class_name)
        self._eat_lines()
        self._end_block()

    def _block_class_name(self,startline):
        """Return a representation of the class name."""

        full_name = "%s"%self.__class__
        bits = string.split(full_name,".")
        return "%s/%s"%(bits[-1],startline.class_name)

    def _eat_lines(self):
        """Eat lines until we run out of block..."""

        while 1:
            try:
                nextline = self.file.next()
            except EOFError:
                return

            # Check the indentation makes sense...
            if self.inner_indent:
                # We already know how much our block is indented
                # - is this line part of the block?
                if nextline.indent < self.inner_indent:
                    # Apparently a dedent - is it what we expect?
                    if nextline.indent <= self.indent:
                        # Unread that line - it isn't one of ours!
                        self.file.unget()
                        return
                    else:
                        raise IndentError,\
                              "Line %d (%s) is indented less than the previous "\
                              "line, but its indentation doesn't match the "\
                              "start of the block at line %d"%\
                              (nextline.lineno,nextline.class_name,self.lineno)
                elif nextline.indent > self.inner_indent:
                    # A spurious indent
                    # (note that doing this stops us from coping with,
                    #  for instance, things in (..), but then we also don't
                    #  cope with any form of continued line, or lots of other
                    #  things, so let's not worry too much for now!)
                    raise IndentError,\
                          "Line %d (%s) is indented more than the previous line"%\
                          (nextline.lineno,nextline.class_name)
            else:
                # This is the first line of the (inside of) the block
                # - check its indentation makes sense...
                self.inner_indent = nextline.indent
                if self.inner_indent <= self.indent:
                    raise IndentError,\
                          "Line %d (%s) should be indented more than line %d (%s)"%\
                          (nextline.lineno,nextline.class_name,
                           self.lineno,self.startline.class_name)

            # Is it a line or the start of another block?
            if nextline.starts_block():
                # Heh - it's the start of an inner block - add it
                # (remember that instantiating it causes it to
                #  "eat" the lines that belong to it)
                self.items.append(Block(startline=nextline,
                                        outer=0,file=self.file))
            else:
                self.items.append(nextline)

    def _end_block(self):
        """End our block"""

        if DEBUGGING: print "%sEnd %s"%(self.indent_str,self.class_name)

        # If we're a tuple block, we should only have one line...
        # (that is, one "business" line)
        if self.startline.class_name == "TupleBlockLine" and \
           len(self.items) > 1:
            # Are all but one of them not "our business"?
            count = 0
            for item in self.items:
                if item.our_business():
                    count = count + 1
                    if count > 1: break
            if count > 1:
                self.error("Tuple declaration can only contain one 'business'"
                           " line, not %d\n"
                           "Assuming it's a table instead (i.e.,"
                           "'Table is:' instead of 'is:')"%len(self.items))
                # Can we correct this by "pretending" its a table?
                temp = TableBlockLine(self.startline.lineno,
                                      self.startline.indent_str,
                                      ("error",self.startline.name),
                                      self.startline.comment,
                                      self.text)
                self.startline = temp

        # We've now got all of our lines, and so we can go back over
        # them, expanding out any IF blocks (whose content is actually
        # within this block's scope, so who need to have their labels
        # (come from or go to) in that scope), working out the label
        # indices, and so on...
        # This uses "next_index" to calculate the indices of business
        # lines (needed for label calculation), and also populates the
        # "business" list with just the items that are "our_business()"
        if DEBUGGING:
            print "Expanding IF blocks, sorting out labels, etc."

        temp       = self.items
        self.items = []
        for item in temp:
            if item.class_name == "Block/IfBlockLine":
                self._add(item.startline)
                for thing in item.items:
                    self._add(thing)
            else:
                self._add(item)

        # Go back through our contents and resolve any labels
        if DEBUGGING:
            print "%s...processing labels (next_index=%d)"%(self.indent_str,
                                                            self.next_index)
        self.startline.resolve_labels(self)
        # If we're an IF block, we mustn't try to resolve our component
        # lines' labels, as they're actually in our parent block's scope...
        if self.startline.class_name != "IfBlockLine":
            for item in self.items:
                item.resolve_labels(self)

        # If we're in a block that wants to suppress the comma at the
        # end of the last item in that block, tell the last item so...
        # (this is debatable for [Bad]TableBlockLine - it might be
        # better to leave the last comma there - so we have an option
        # to determine it...
        if self.startline.class_name == "TupleBlockLine" or \
           (not WANT_LAST_COMMA and \
            (self.startline.class_name == "TableBlockLine" or \
             self.startline.class_name == "BadTableBlockLine")):
            if len(self.business) > 0:
                self.business[-1].is_last = 1

    def _add(self,item):
        """Add a line or block to our list of items.

        item -- the Line or Block instance to add

        NB: Also adds it to our "business" list if it is our business
            (and not a label)
        """

        if item.class_name == "LabelLine":
            self.label_dict[item.label] = self.next_index
            if DEBUGGING:
                print "%sadd [%2d] %s"%(item.indent_str,self.next_index,item)
            # Might as well give it the index it is labelling
            item.index = self.next_index
            self.items.append(item)
        elif item.our_business():
            item.index = self.next_index
            self.items.append(item)
            self.business.append(item)
            if DEBUGGING:
                print "%sadd  %2d  %s"%(item.indent_str,
                                            self.next_index,item)
            self.next_index = self.next_index + 1
        else:
            # It's not something we can assign a sensible index to, so don't
            if DEBUGGING:
                print "%sadd  xx  %s"%(item.indent_str,item)
            self.items.append(item)

    def translate_label(self,label,line):
        """Given a label, return its translation.

        label -- either a string of the form "<...>" to look up in
                 this block's label dictionary, or one of the special
                 targets (e.g., next, MatchOk, etc.)
        line  -- the line using this label

        Reports an error and just returns the original "label" if it
        can't translate it.
        """
        if self.label_dict.has_key(label):
            # How far do we have to jump?
            offset = self.label_dict[label] - line.index
            return "%+d"%offset
        elif label == "MatchOk":
            return "MatchOk"
        elif label == "MatchOK":
            line.warning("Label 'MatchOK' should be spelt 'MatchOk'"
                         " (using 'MatchOk')")
            return "MatchOk"
        elif label == "MatchFail":
            return "MatchFail"
        elif label == "next":
            return "+1"
        elif label == "previous":
            return "-1"
        elif label == "repeat":
            return "0"
        else:
            line.error("Undefined label '%s'"%label)
            return label

    def expand(self,stream,block=None):
        """Write out the expanded equivalent of ourselves.

        stream  -- an object with a "write" method, e.g., a file
        block   -- if we're in a block, this is it, otherwise None
        """

        self.startline.expand(stream,block=block)
        for item in self.items[:-1]:
            item.expand(stream,block=self)

        self.items[-1].expand(stream,block=self)

        # Deal with closing any block parentheses
        if self.startline.class_name == "TableBlockLine" or \
           self.startline.class_name == "BadTableBlockLine":
            if DEBUGGING:
                stream.write("Line ...: ")

            stream.write(self.indent_str)
            if self.outer:
                # Outer block - just close it
                stream.write(")")
            else:
                # Inner block is a Table block, and we need to close both
                # the tuple-of-tuples, and also the tuple containing the
                # Table command...
                stream.write("))")
            if not self.is_last:
                stream.write(",")
            stream.write("\n")


# ------------------------------------------------------------
class File:
    """This is the class that holds our processed data

    Contains:
        lines   -- a list of the line instances for each "line" in our text
        items   -- a list of lines and BLOCKs
    """

    def __init__(self,tagtuples,text):
        """Instantiate a File

        tagtuples -- the list of mxTextTools tag tuples generated by
                     parsing the data in "text"
        text      -- the text we parsed
        """

        self.text      = text
        self.tagtuples = tagtuples

        # Assemble our list of lines
        print "Pass 1: assembling lines"
        if DEBUGGING: print "~~~~~~~~~~~~~~~~~~~~~~~~"
        self.lines = []
        lineno     = 0
        prevline   = None
        for tagtuple in tagtuples:
            lineno = lineno + 1
            thisline = LineFactory(lineno,tagtuple,text)

            if prevline:
                prevline.next_indent = thisline.indent

            self.lines.append(thisline)
            prevline = thisline

        #if DEBUGGING: print

        # The indentation of an empty line is taken to be the same
        # as the indentation of the first following non-empty line
        # The easiest way to do that is to work backwards through
        # the list (is it better to take a copy and reverse THAT,
        # or to reverse our original list twice?)
        print "Pass 2: sorting out indentation of empty lines"
        if DEBUGGING: print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        revlist = self.lines[:]
        revlist.reverse()
        indent = 0
        for line in revlist:
            if line.class_name == "EmptyLine":
                line.change_indent(indent)
            else:
                indent = line.indent
        del revlist

        if DEBUGGING:
            print "Pass 2.5 - the contents of those lines..."
            print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
            for line in self.lines:
                print "Line %d %s"%(line.lineno,line.class_name)
                #print_tuples([line.tagtuple],self.text,"  ")
            print

        # Now we need to assemble blocks
        print "Pass 3: assembling blocks"
        if DEBUGGING: print "~~~~~~~~~~~~~~~~~~~~~~~~~"
        self.reset()
        self.items = []

        while 1:
            try:
                item = self.next()
            except EOFError:
                break

            if DEBUGGING:
                print "%sTOP    %s"%(item.indent_str,item)
            if item.starts_block():
                block = Block(startline=item,outer=1,file=self)
                self.items.append(block)
                block.is_last = 1   # Everything at outer level is "last"
            else:
                if item.only_in_block():
                    item.error("This line is not allowed outside a block "
                               "- continuing anyway")
                self.items.append(item)
                if item.our_business():
                    item.is_last = 1    # Everything at outer level is "last"

        if DEBUGGING: print
                

    def reset(self):
        """Ensure that the next call of "nextline" returns the first line."""
        self.index = -1

    def unget(self):
        """Unread the current line."""
        self.index = self.index - 1
        if self.index < 0:
            self.index = 0

    def next(self):
        """Retrieve the next line from the list of lines in this "file".

        Raises EOFError if there is no next line (i.e., "end of file")
        """
        self.index = self.index + 1
        try:
            return self.lines[self.index]
        except IndexError:
            # leave the index off the end, so we get EOF again if
            # we're called again - but there's no point courting overflow...
            self.index = self.index -1
            raise EOFError

    def expand(self,stream):
        """Expand out the result."""
        for item in self.items:
            item.expand(stream)


# ------------------------------------------------------------
def print_tuples(tuples,text,indent=""):
    """Print out a list of tuples in a neat form

    tuples -- our tuple list
    text   -- the text it tags
    indent -- our current indentation
    """

    # Tuples are of the form:
    # (object,left_index,right_index,sublist)

    for obj,left,right,sub in tuples:
        if sub:
            print "%s%s"%(indent,obj)
            print_tuples(sub,text,indent+"  ")
        else:
            # Terminal node - show the actual text we've tagged!
            print "%s%s = %s"%(indent,obj,`text[left:right]`)


# ------------------------------------------------------------
def print_text(text):
    """Print out text with line numbers."""
    lines = string.split(text,"\n")
    lineno = 0

    print "Original text"
    print "============="
    for line in lines:
        lineno = lineno + 1
        print "%3d: %s"%(lineno,`line`)


# ------------------------------------------------------------
def print_usage(argv0):
    #script_name = string.split(argv0, os.sep)[-1]
    #print __doc__%(script_name)
    print argv0
    print __doc__


# ------------------------------------------------------------
def show_tup(indent,nn,tup):
    ll = []
    for item in tup:
        if type(item) == type((1,)) or type(item) == type([]):
            ll.append("(..)")
        else:
            ll.append(`item`)

    if nn:
        print "%s%d: (%s)"%(indent,nn,string.join(ll,","))
    else:
        print "%s(%s)"%(indent,string.join(ll,","))

def comp_sub(indent,one,two):
    len1 = len(one)
    if len(two) != len(one):
        print "%sTuple lengths differ - 1:%d, 2:%d"%(indent,len1,len(two))
        show_tup(indent,1,one)
        show_tup(indent,2,two)
        # If this is all, let's try to continue...
        len1 = min(len1,len(two))

    for count in range(len1):
        a = one[count]
        b = two[count]
        if type(a) != type(b):
            print "%sValue types differ, item %d: 1:%s, 2:%s"%(indent,count,
                                                               type(a),type(b))
            show_tupe(indent,1,one)
            show_tupe(indent2,two)
            return 0
        if type(a) == type((1,)) or type(a) == type([]):
            if not comp_sub(indent+"  ",a,b):
                # They're the same at this level, so show only one...
                show_tup(indent,0,one)
                return 0
        else:
            if a != b:
                print "%sValues differ, item %d: 1:%s, 2:%s"%(indent,count,
                                                              `a`,`b`)
                show_tup(indent,1,one)
                show_tup(indent,2,two)
                return 0
    return 1

def compare_tagtables(one,two):
    # Each table is made up of tuples of the form
    # (tagobj,action,arg,onfalse,ontrue)
    # but if action is Table or SubTable then arg may be a tuple
    # itself...
    if comp_sub("",one,two):
        print "They appear to be the same"


# ------------------------------------------------------------
def main():
    """Used to test the module."""

    debug_pytag  = DEFAULT_DEBUG
    use_pytag    = DEFAULT_PYTAG
    use_stdout   = 0
    import_tags  = 0
    force_overwrite = 0
    compare_tables  = 0

    global DEBUGGING

    if os.name == "posix":
        use_testdata = 0
    else:
        # At home...
        use_testdata = 1
        use_stdout   = 1
        DEBUGGING    = 0

    # Do we have command line arguments?
    arg_list = sys.argv[1:]
    args = []

    while 1:
        if len(arg_list) == 0:
            break

        word = arg_list[0]

        if word == "-pytag":
            use_pytag = 1
        elif word == "-debug":
            debug_pytag = 1
        elif word == "-stdout":
            use_stdout = 1
        elif word == "-force":
            force_overwrite = 1
        elif word == "-import":
            import_tags = 1
        elif word == "-compare":
            compare_tables = 1
        elif word == "-diag":
            DEBUGGING = 1
        elif word == "-test":
            use_testdata = 1
            use_stdout = 1
        elif word == "-help":
            print_usage(sys.argv[0])
            return
        elif word == "-version":
            print "Version:",__version__
            return
        elif word == "-history":
            print "History:"
            print __history__
            return
        else:
            args.append(word)

        arg_list = arg_list[1:]
        continue

    if compare_tables:
        from Translate_tags import t_file
        i_file = define_tagtable()
        print "Comparing internal table (1) against external (2)"
        compare_tagtables(i_file,t_file)
        return

    if not use_testdata and (not args or len(args) > 2):
        print_usage(sys.argv[0])
        return

    if not use_testdata:
        infile = args[0]

    if import_tags:
        print "Importing tag table definition"
        from Translate_tags import t_file
    else:
        print "Using internal tag table definition"
        t_file = define_tagtable()

    if use_stdout:
        outfile = "standard output"
    elif len(args) > 1:
        outfile = args[1]
    else:
        base,ext = os.path.splitext(infile)
        if ext != ".py":
            outfile = base + ".py"
        else:
            print "Input file has extension .py so won't guess"\
                  " an output file"
            return

    if outfile != "standard output":
        if outfile == infile:
            print "The output file is the same as the input file"
            print "Refusing to overwrite %s"%outfile
            return
        elif os.path.exists(outfile):
            if force_overwrite:
                print "Output file %s already exists"\
                      " - overwriting it"%outfile
            else:
                print "Output file %s already exists"%outfile
                return

    # Read the input file
    if use_testdata:
        if DEBUGGING: print
        print "Using test data"
        if DEBUGGING: print "==============="
        text = test_data
    else:
        if DEBUGGING: print
        print "Reading text from %s"%infile
        if DEBUGGING: print "=================="+"="*len(infile)
        file = open(infile,"r")
        text = file.read()
        file.close()

    # Show what we are trying to parse
    if DEBUGGING or use_testdata:
        print
        print_text(text)

    # Tag it
    print
    print "Tagging text"
    if DEBUGGING: print "============"
    if use_pytag:
        import pytag
        pytag.set_verbosity(0)
        if debug_pytag:
            pytag.set_verbosity(1)
            pytag.use_debugger()
        result,taglist,next = pytag.pytag(text,t_file)
    else:
        timer = TextTools._timer()
        timer.start()
        result, taglist, next = tag(text,t_file)
        #result, taglist, next = tag(text,t_file,0,len(text),taglist)
        print "Tagging took",timer.stop()[0],"seconds"

    # Now print out the result of the tagging
    print
    print "Manipulating tagged data"
    if DEBUGGING: print "========================"
    tagfile = File(taglist,text)

    print
    print "Writing translation to %s"%outfile
    if DEBUGGING: print "======================="+"="*len(outfile)

    # Open the output file, if necessary
    if use_stdout:
        file = sys.stdout
    else:
        file = open(outfile,"w")

    tagfile.expand(file)


# ------------------------------------------------------------
if __name__ == '__main__':
    main()
