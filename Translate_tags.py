# -*- python -*-
"""Translation tags for Translate.py"""

__version__ = "0.3 (tiepin) of 1999-11-15"
__author__ = "Tibs"

# This is a back-translation of the tuples which were written by hand
# within Translate.py, *but* it is also suitable for translation (by
# said module) into Python code, and then importing into Translate.py
# for use instead of the original (hand written) tuples.

from TextTools import *

# ------------------------------------------------------------
# We are not, initially, going to try for anything very sophisticated
# - just something that will get us bootstrapped, so that I can use the
#   "little language" to write more sophisticated stuff (without having
#   to worry about dropped commas between tuples, and so on!)


# Whitespace is always useful
t_whitespace = \
    (None,AllIn,' \t')

t_opt_whitespace = \
    t_whitespace    + (+1,)              # move to next tuple if not whitespace

# Comments are fairly simple
t_comment = \
    ('comment',Table,(
        (None,Is,'#'),
        (None,AllNotIn,'\n\r',MatchOk),
    ))

# We care about the "content" of the indentation at the start of a
# line, but note that it is optional
t_indent = \
    ('indent',AllIn,' \t')
t_indentation = \
    t_indent        + (+1,)              # zero indentation doesn't show

# A string is text within single or double quotes
# (of course, this is an oversimplification, because we should also
#  deal with things like "This is a \"substring\"", and it would be
#  nice to be able to cope with triple-quoted strings too, but it
#  will do for a start)

# Major bug - doesn't recognised zero length strings...
# (since "AllNotIn" must match at least one character)
t_string = \
    ('str',Table,(
        (None,Is,"'",+3,+1),
            ('text',AllNotIn,"'"),
            (None,Is,"'",MatchFail,MatchOk),
        (None,Is,'"'),
        ('text',AllNotIn,'"'),
        (None,Is,'"'),
    ))

# An integer is a series of digits...
t_integer = \
    ('int',AllIn,number)

t_signed_integer = \
    ('signed_int',Table,(
        ('sign',Is,"+",+1,+2),
        ('sign',Is,"-",+1),             # sign is optional
        # <int>
        t_integer,
    ))

# We'll only go for the simplest words
# Remember to be careful to specify the LONGEST possible match first, so that
# we try for "IsIn" before we try for "Is" (because "IsIn" would *match* "Is",
# leaving us with a spurious "In" hanging around...)
t_operation = \
    ('op',Table,(
        ('op',Word,"AllInSet",+1,MatchOk),
        ('op',Word,"AllIn",+1,MatchOk),
        ('op',Word,"AllNotIn",+1,MatchOk),
        ('op',Word,"CallArg",+1,MatchOk),
        ('op',Word,"Call",+1,MatchOk),
        ('op',Word,"EOF",+1,MatchOk),
        ('op',Word,"Fail",+1,MatchOk),
        ('op',Word,"IsInSet",+1,MatchOk),
        ('op',Word,"IsIn",+1,MatchOk),
        ('op',Word,"IsNotIn",+1,MatchOk),
        ('op',Word,"IsNot",+1,MatchOk),
        ('op',Word,"Is",+1,MatchOk),
        ('op',Word,"Jump",+1,MatchOk),
        ('op',Word,"LoopControl",+1,MatchOk),
        ('op',Word,"Loop",+1,MatchOk),
        ('op',Word,"Move",+1,MatchOk),
        ('op',Word,"NoWord",+1,MatchOk), # alias for WordStart
        ('op',Word,"Skip",+1,MatchOk),
        ('op',Word,"SubTableInList",+1,MatchOk),
        ('op',Word,"SubTable",+1,MatchOk),
        ('op',Word,"sFindWord",+1,MatchOk),
        ('op',Word,"sWordStart",+1,MatchOk),
        ('op',Word,"sWordEnd",+1,MatchOk),
        ('op',Word,"TableInList",+1,MatchOk),
        ('op',Word,"Table",+1,MatchOk),
        ('op',Word,"WordStart",+1,MatchOk),
        ('op',Word,"WordEnd",+1,MatchOk),
        ('op',Word,"Word",MatchFail,MatchOk),
    ))

# Python keywords
t_keyword = \
    ('keyword',Table,(
        (None,Word,"and",+1,+28),
        (None,Word,"assert",+1,+27),
        (None,Word,"break",+1,+26),
        (None,Word,"class",+1,+25),
        (None,Word,"continue",+1,+24),
        (None,Word,"def",+1,+23),
        (None,Word,"del",+1,+22),
        (None,Word,"elif",+1,+21),
        (None,Word,"else",+1,+20),
        (None,Word,"except",+1,+19),
        (None,Word,"exec",+1,+18),
        (None,Word,"finally",+1,+17),
        (None,Word,"for",+1,+16),
        (None,Word,"from",+1,+15),
        (None,Word,"global",+1,+14),
        (None,Word,"if",+1,+13),
        (None,Word,"import",+1,+12),
        (None,Word,"in",+1,+11),
        (None,Word,"is",+1,+10),
        (None,Word,"lambda",+1,+9),
        (None,Word,"not",+1,+8),
        (None,Word,"or",+1,+7),
        (None,Word,"pass",+1,+6),
        (None,Word,"print",+1,+5),
        (None,Word,"raise",+1,+4),
        (None,Word,"return",+1,+3),
        (None,Word,"try",+1,+2),
        (None,Word,"while",MatchFail,+1),
        # <check>
        # In order to not recognise things like "in_THIS_CASE"
        # we must check that the next character is not legitimate
        # within an identifier
        (None,IsIn,alpha+"_"+number,+1,MatchFail),
        # If it wasn't another identifier character, we need to
        # unread it so that it can be recognised as something else
        # (so that, for instance, "else:" is seen as "else" followed
        #  by ":")
        (None,Skip,-1),
    ))

# Do the same for mxText commands
t_mxkeyword = \
    ('mxKeyword',Table,(
        t_operation,
        (None,IsIn,alpha+"_"+number,+1,MatchFail),
        (None,Skip,-1),
    ))

# Traditional identifiers
t_identifier = \
    ('identifier',Table,(
        t_keyword       + (+1,MatchFail), # don't allow Python keywords
        t_mxkeyword     + (+1,MatchFail), # don't allow mxText commands
        (None,IsIn,alpha+"_"),          # can't start with a digit
        (None,AllIn,alpha+'_'+number,MatchOk),
    ))

# We don't yet deal with the following with anything in parentheses,
# which means we can't handle functions or command lists, or other
# things which "look like" a tuple
t_argument = \
    ('arg',Table,(
        ('arg',Word,"Here",+1,MatchOk), # EOF Here, Fail Here
        ('arg',Word,"ToEOF",+1,MatchOk), # Move ToEOF
        ('arg',Word,"To",+1,MatchOk),   # Jump To
        ('arg',Word,"ThisTable",+1,MatchOk), # [Sub]Table ThisTable
        ('arg',Word,"back",+1,MatchOk), # Skip back
        ('arg',Word,"Break",+1,MatchOk), # LoopControl Break
        ('arg',Word,"Reset",+1,MatchOk), # LoopControl Reset
        t_string        + (+1,MatchOk), # e.g., Word "Fred"
        t_signed_integer + (+1,MatchOk), # e.g., Skip -4, Move 3
        t_identifier,                   # e.g., Table Fred
    ))

# Recognise a plus sign bordered by optional whitespace
t_plus = \
    ('plus',Table,(
        t_opt_whitespace,
        (None,Is,"+"),
        t_opt_whitespace,
    ))

# Arguments can contain "+"
t_plus_arg = \
    ('plusarg',Table,(
        t_argument,                     # start with a single argument
        # <again>
        t_plus          + (MatchOk,),    # if we have a "+"
        t_argument,                     # then we expect another argument
        (None,Jump,To,-2),              # then look for another "+"
    ))

# Match, for example:
#        <fred>
t_label = \
    ('label',Table,(
        (None,Is,"<"),
        t_identifier,
        (None,Is,">"),
    ))

# Targets for Jump and F:/T:
t_target = \
    ('target',Table,(
        ('tgt',Word,"next",+1,MatchOk),
        ('tgt',Word,"previous",+1,MatchOk),
        ('tgt',Word,"repeat",+1,MatchOk),
        ('tgt',Word,"MatchOk",+1,MatchOk),
        ('tgt',Word,"MatchOK",+1,MatchOk), # for kindness' sake
        ('tgt',Word,"MatchFail",+1,MatchOk),
        t_label,
    ))

# A value is either an identifier, or a string, or an integer
t_value = \
    ('val',Table,(
        t_identifier    + (+1,MatchOk),
        t_string        + (+1,MatchOk),
        t_integer,
    ))

# An assignment is (optionally) used in Tuple and Table definitions...
t_assignment = \
    ('assignment',Table,(
        t_value,
        t_opt_whitespace,
        (None,Is,'='),
    ))

# A common error when writing tuples is to miss off the "=" sign
# - the following is used in diagnosing that (see t_bad_tuple below)
# (it's useful to have something with identical structure to the
#  "real thing")
t_bad_tagobj = \
    ('tagobj',Table,(
        t_string,
    ))

t_bad_assignment = \
    ('assignment',Table,(
        t_value,
    ))

# This is the line that starts the definition of a single tuple.
# For the moment, restrict what it gets assigned to to a simple
# identifier.
# Match, for example:
#        Fred is:
t_tupleblock = \
    ('tupleblock',Table,(
        t_identifier,
        t_whitespace,
        (None,Word,"is:"),
    ))

# This is the line that starts a new table or sub-table.
# For the moment, we only cope with full Tables.
# NOTE that this is used for the "outer" declaration of a tag table,
# and also for the "inner" declaration of an inner table or sub-table.
# The discrimination between these is done after initial parsing.
# Match, for example:
#        'keyword' = Table is:      (inner)
#        tagtable = Table is:       (outer)
t_tableblock = \
    ('tableblock',Table,(
        t_assignment + (+2,+1), # left hand side is optional
            t_opt_whitespace,
        ('type',Word,"Table",+1,+2),    # Either "Table"
        ('type',Word,"SubTable"),       # or "SubTable"
        # <ok>
        t_whitespace,                   # whitespace is required
        (None,Word,"is:"),              # "is:" is required
    ))

# This is the line that starts an "if" block
# Match, for example:
#        Is "Fred":
#        controlsymbol:
t_ifblock = \
    ('ifblock',Table,(
        t_assignment + (+2,+1), # left hand side is optional
            t_opt_whitespace,
        t_operation + (+4,+1),
            t_whitespace,
            t_plus_arg,
            (None,Is,":",MatchFail,MatchOk),
        # Else:
        t_identifier,
        (None,Is,":"),
    ))

# Note that we don't allow spaces WITHIN our false and true thingies
t_onfalse = \
    ('onfalse',Table,(
        t_whitespace,
        (None,Word,"F:"),
        t_target,
    ))

t_ontrue = \
    ('ontrue',Table,(
        t_whitespace,
        (None,Word,"T:"),
        t_target,
    ))

# Valid examples are things like:
#        'fred' = Is "xxx" F:<wow> T:MatchOk
#       AllIn jim T:<foundJim>
#
# For the moment, we're not trying to recognise things in any detail
t_tuple = \
    ('tuple',Table,(
        t_assignment + (+2,+1), # left hand side is optional
            t_opt_whitespace,
        t_operation,                    # operation is required
        t_whitespace,                   # for now, always require space here
        t_plus_arg,                     # argument is required
        t_onfalse       + (+1,+1),      # F:target is optional
        t_ontrue        + (MatchOk,MatchOk), # T:target is also optional
    ))

# If the user has defined a "partial" tuple, they might use something
# of the form:
#       match_fred  F:MatchFalse T:MatchOk
t_tupleplus = \
    ('tupleplus',Table,(
        t_identifier,
        t_onfalse       + (+1,+1),      # F:target is optional
        t_ontrue        + (MatchOk,MatchOk), # T:target is also optional
    ))

# Treat Jump To specially - for example:
#       Jump To <top>
# so that they don't have to do the less obvious "Jump To F:<label>"
# (although that will still be recognised, of course, for people who
# are used to the tag tuple format itself)
t_jumpto = \
    ('jumpto',Table,(
        (None,Word,"Jump"),
        t_whitespace,
        (None,Word,"To"),
        t_whitespace,
        t_target,
    ))

# Is it worth coping with these?
t_bad_jumpto = \
    ('jumpto',Table,(
        (None,Word,"Jump",+3,+1), # cope with "Jump to"
            t_whitespace,
            (None,Word,"to",MatchFail,+2),
        (None,Word,"JumpTo"),           # and with "JumpTo"
        # <target>
        t_target,
    ))

# The "content" of a line is the bit after any indentation, and before
# any comment...
# For the moment, we won't try to maintain ANY context, so it is up
# to the user of the tuples produced to see if they make sense...
t_content = \
    ('content',Table,(
        t_label         + (+1,MatchOk),
        t_tableblock    + (+1,MatchOk), # [<tagobj> =] [Sub]Table is:
        t_tupleblock    + (+1,MatchOk), # <identifier> is:
        t_ifblock       + (+1,MatchOk), # <cmd> <arg>: OR <identifier>:
        t_jumpto        + (+1,MatchOk), # Jump To <target>
        t_tuple         + (+1,MatchOk),
        t_tupleplus     + (+1,MatchOk), # name [F:<label> [T:<label>]]
    ))

t_contentline = \
    ('contentline',Table,(
        t_content,                      # something that we care about
        t_opt_whitespace,
        t_comment       + (+1,+1),      # always allow a comment
        (None,IsIn,newline),            # the end of the line
    ))

# Sometimes, the user (e.g., me) writes:
#	'fred' = Table:
# instead of:
#	'fred' = Table is:
# Unfortunately, without the "is", it would get too confusing whether
# we actually wanted an if block...
t_bad_tableblock = \
    ('tableblock',Table,(
        t_assignment + (+2,+1), # left hand side is optional
            t_opt_whitespace,
        (None,Word,"Table"),            # "Table" is required
        (None,Is,":"),                  # "is" is needed before the ":"
    ))

# Sometimes, the use (e.g., me again) write:
#	'fred' IsIn jim
# instead of:
#	'fred' = IsIn jim
# Whilst I'm not entirely convinced that "=" is the best character
# to use here, I think we do need something!
t_bad_tuple = \
    ('tuple',Table,(
        t_bad_assignment,               # obviously we have to have this!
        t_whitespace,                   # in which case the whitespace IS needed
        t_operation,                    # operation is required
        t_whitespace,                   # for the moment, we must have space here
        t_plus_arg,                     # argument is required
        t_onfalse       + (+1,+1),      # F:target is optional
        t_ontrue        + (MatchOk,MatchOk), # T:target is also optional
    ))

# Make some attempt to recognise common errors...
t_badcontent = \
    ('badcontent',Table,(
        t_bad_tableblock + (+1,MatchOk),
        t_bad_tuple,
    ))

t_badline = \
    ('badline',Table,(
        t_badcontent,                   # something that we sort of care about
        t_opt_whitespace,
        t_comment       + (+1,+1),      # always allow a comment
        (None,IsIn,newline),            # the end of the line
    ))

t_emptyline = \
    ('emptyline',Table,(
        t_opt_whitespace,
        (None,IsIn,newline),            # the end of the line
    ))

t_commentline = \
    ('commentline',Table,(
        t_comment,
        (None,IsIn,newline),            # the end of the line
    ))

t_passthruline = \
    ('passthruline',Table,(
        ('passthru',AllNotIn,newline,+1), # anything else on the line
        (None,IsIn,newline),            # the end of the line
    ))

# Basically, a file is a series of lines
t_line = \
    ('line',Table,(
        t_emptyline     + (+1,MatchOk), # empty lines are simple enough
        t_indent        + (+1,+1),      # optional indentation
        t_commentline   + (+1,MatchOk), # always allow a comment
        t_contentline   + (+1,MatchOk), # a line we care about
        t_badline       + (+1,MatchOk), # a line we think is wrong
        t_passthruline,                 # a line we don't care about
    ))

# So read lines until we find the EOF
t_file = (
    t_line,
    (None,EOF,Here,-1),
)


# ----------------------------------------------------------------------
if __name__ == '__main__':

    test_data = "#Test data\n"

    def print_tuples(tuplist):
        print "("
        for item in tuplist:
            print " ",item
        print ")"

    lines = string.split(test_data,"\n")
    count = 0
    print "Test data"
    print "---------"
    for line in lines:
        count = count+1
        print "%2d: %s"%(count,line)
    print

    print "Tagging text"
    print "------------"

    PYTAG = 0

    if PYTAG:
        import pytag
        pytag.set_verbosity(1)
        pytag.use_debugger()
        result,taglist,next = pytag.pytag(test_data,t_file)
    else:
        timer = TextTools._timer()
        timer.start()
        result, taglist, next = tag(test_data,t_file)
        print "Tagging took",timer.stop()[0],"seconds"


    print "Result: ",result
    print "Taglist:"
    print_tuples(taglist)
