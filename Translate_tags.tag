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
t_whitespace is:
    AllIn ' \t'

t_opt_whitespace is:
    t_whitespace F:next       # move to next tuple if not whitespace

# Comments are fairly simple
t_comment is:
    'comment' = Table is:
        Is '#'
        AllNotIn '\n\r' F:MatchOk

# We care about the "content" of the indentation at the start of a
# line, but note that it is optional
t_indent is:
    'indent' = AllIn ' \t'
t_indentation is:
    t_indent F:next           # zero indentation doesn't show

# A string is text within single or double quotes
# (of course, this is an oversimplification, because we should also
#  deal with things like "This is a \"substring\"", and it would be
#  nice to be able to cope with triple-quoted strings too, but it
#  will do for a start)

# Major bug - doesn't recognised zero length strings...
# (since "AllNotIn" must match at least one character)
t_string is:
    'str' = Table is:
        Is "'":
            'text' = AllNotIn "'"
            Is "'" F:MatchFail T:MatchOk
        Is '"'
        'text' = AllNotIn '"'
        Is '"'

# An integer is a series of digits...
t_integer is:
    'int' = AllIn number

t_signed_integer is:
    'signed_int' = Table is:
        'sign' = Is "+" F:next T:<int>
        'sign' = Is "-" F:next         # sign is optional
        <int>
        t_integer

# We'll only go for the simplest words
# Remember to be careful to specify the LONGEST possible match first, so that
# we try for "IsIn" before we try for "Is" (because "IsIn" would *match* "Is",
# leaving us with a spurious "In" hanging around...)
t_operation is:
    'op' = Table is:
        'op' = Word "AllInSet"        F:next T:MatchOk
        'op' = Word "AllIn"           F:next T:MatchOk
        'op' = Word "AllNotIn"        F:next T:MatchOk
        'op' = Word "CallArg"         F:next T:MatchOk
        'op' = Word "Call"            F:next T:MatchOk
        'op' = Word "EOF"             F:next T:MatchOk
        'op' = Word "Fail"            F:next T:MatchOk
        'op' = Word "IsInSet"         F:next T:MatchOk
        'op' = Word "IsIn"            F:next T:MatchOk
        'op' = Word "IsNotIn"         F:next T:MatchOk
        'op' = Word "IsNot"           F:next T:MatchOk
        'op' = Word "Is"              F:next T:MatchOk
        'op' = Word "Jump"            F:next T:MatchOk
        'op' = Word "LoopControl"     F:next T:MatchOk
        'op' = Word "Loop"            F:next T:MatchOk
        'op' = Word "Move"            F:next T:MatchOk
        'op' = Word "NoWord"          F:next T:MatchOk # alias for WordStart
        'op' = Word "Skip"            F:next T:MatchOk
        'op' = Word "SubTableInList"  F:next T:MatchOk
        'op' = Word "SubTable"        F:next T:MatchOk
        'op' = Word "sFindWord"       F:next T:MatchOk
        'op' = Word "sWordStart"      F:next T:MatchOk
        'op' = Word "sWordEnd"        F:next T:MatchOk
        'op' = Word "TableInList"     F:next T:MatchOk
        'op' = Word "Table"           F:next T:MatchOk
        'op' = Word "WordStart"       F:next T:MatchOk
        'op' = Word "WordEnd"         F:next T:MatchOk
        'op' = Word "Word"            F:MatchFail T:MatchOk

# Python keywords
t_keyword is:
    'keyword' = Table is:
        Word "and"      F:next T:<check>
        Word "assert"   F:next T:<check>
        Word "break"    F:next T:<check>
        Word "class"    F:next T:<check>
        Word "continue" F:next T:<check>
        Word "def"      F:next T:<check>
        Word "del"      F:next T:<check>
        Word "elif"     F:next T:<check>
        Word "else"     F:next T:<check>
        Word "except"   F:next T:<check>
        Word "exec"     F:next T:<check>
        Word "finally"  F:next T:<check>
        Word "for"      F:next T:<check>
        Word "from"     F:next T:<check>
        Word "global"   F:next T:<check>
        Word "if"       F:next T:<check>
        Word "import"   F:next T:<check>
        Word "in"       F:next T:<check>
        Word "is"       F:next T:<check>
        Word "lambda"   F:next T:<check>
        Word "not"      F:next T:<check>
        Word "or"       F:next T:<check>
        Word "pass"     F:next T:<check>
        Word "print"    F:next T:<check>
        Word "raise"    F:next T:<check>
        Word "return"   F:next T:<check>
        Word "try"      F:next T:<check>
        Word "while"    F:MatchFail T:<check>
        <check>
        # In order to not recognise things like "in_THIS_CASE"
        # we must check that the next character is not legitimate
        # within an identifier
        IsIn alpha+"_"+number F:next T:MatchFail
        # If it wasn't another identifier character, we need to
        # unread it so that it can be recognised as something else
        # (so that, for instance, "else:" is seen as "else" followed
        #  by ":")
        Skip back

# Do the same for mxText commands
t_mxkeyword is:
    'mxKeyword' = Table is:
        t_operation
        IsIn alpha+"_"+number F:next T:MatchFail
        Skip back

# Traditional identifiers
t_identifier is:
    'identifier' = Table is:
        t_keyword F:next T:MatchFail      # don't allow Python keywords
        t_mxkeyword F:next T:MatchFail    # don't allow mxText commands
        IsIn alpha+"_"                    # can't start with a digit
        AllIn alpha+'_'+number F:MatchOk

# We don't yet deal with the following with anything in parentheses,
# which means we can't handle functions or command lists, or other
# things which "look like" a tuple
t_argument is:
    'arg' = Table is:
        'arg' = Word "Here"      F:next T:MatchOk # EOF Here, Fail Here
        'arg' = Word "ToEOF"     F:next T:MatchOk # Move ToEOF
        'arg' = Word "To"        F:next T:MatchOk # Jump To
        'arg' = Word "ThisTable" F:next T:MatchOk # [Sub]Table ThisTable
        'arg' = Word "back"      F:next T:MatchOk # Skip back
        'arg' = Word "Break"     F:next T:MatchOk # LoopControl Break
        'arg' = Word "Reset"     F:next T:MatchOk # LoopControl Reset
        t_string                 F:next T:MatchOk # e.g., Word "Fred"
        t_signed_integer         F:next T:MatchOk # e.g., Skip -4, Move 3
        t_identifier                              # e.g., Table Fred

# Recognise a plus sign bordered by optional whitespace
t_plus is:
    'plus' = Table is:
        t_opt_whitespace
        Is "+"
        t_opt_whitespace

# Arguments can contain "+"
t_plus_arg is:
    'plusarg' = Table is:
        t_argument              # start with a single argument
        <again>
        t_plus F:MatchOk        # if we have a "+"
        t_argument              # then we expect another argument
        Jump To <again>         # then look for another "+"

# Match, for example:
#        <fred>
t_label is:
    'label' = Table is:
        Is "<"
        t_identifier
        Is ">"

# Targets for Jump and F:/T:
t_target is:
    'target' = Table is:
        'tgt' = Word "next"      F:next T:MatchOk
        'tgt' = Word "previous"  F:next T:MatchOk
        'tgt' = Word "repeat"    F:next T:MatchOk
        'tgt' = Word "MatchOk"   F:next T:MatchOk
        'tgt' = Word "MatchOK"   F:next T:MatchOk # for kindness' sake
        'tgt' = Word "MatchFail" F:next T:MatchOk
        t_label

# A value is either an identifier, or a string, or an integer
t_value is:
    'val' = Table is:
        t_identifier F:next T:MatchOk
        t_string     F:next T:MatchOk
        t_integer

# An assignment is (optionally) used in Tuple and Table definitions...
t_assignment is:
    'assignment' = Table is:
        t_value
        t_opt_whitespace
        Is '='

# A common error when writing tuples is to miss off the "=" sign
# - the following is used in diagnosing that (see t_bad_tuple below)
# (it's useful to have something with identical structure to the
#  "real thing")
t_bad_tagobj is:
    'tagobj' = Table is:
        t_string

t_bad_assignment is:
    'assignment' = Table is:
        t_value

# This is the line that starts the definition of a single tuple.
# For the moment, restrict what it gets assigned to to a simple
# identifier.
# Match, for example:
#        Fred is:
t_tupleblock is:
    'tupleblock' = Table is:
        t_identifier
        t_whitespace
        Word "is:"

# This is the line that starts a new table or sub-table.
# For the moment, we only cope with full Tables.
# NOTE that this is used for the "outer" declaration of a tag table,
# and also for the "inner" declaration of an inner table or sub-table.
# The discrimination between these is done after initial parsing.
# Match, for example:
#        'keyword' = Table is:      (inner)
#        tagtable = Table is:       (outer)
t_tableblock is:
    'tableblock' = Table is:
        t_assignment:  # left hand side is optional
            t_opt_whitespace
        'type' = Word "Table" F:next T:<ok>  # Either "Table"
        'type' = Word "SubTable"             # or "SubTable"
        <ok>
        t_whitespace   # whitespace is required
        Word "is:"     # "is:" is required

# This is the line that starts an "if" block
# Match, for example:
#        Is "Fred":
#        controlsymbol:
t_ifblock is:
    'ifblock' = Table is:
        t_assignment:     # left hand side is optional
            t_opt_whitespace
        t_operation:
            t_whitespace
            t_plus_arg
            Is ":" F:MatchFail T:MatchOk
        # Else:
        t_identifier
        Is ":"

# Note that we don't allow spaces WITHIN our false and true thingies
t_onfalse is:
    'onfalse' = Table is:
        t_whitespace
        Word "F:"
        t_target

t_ontrue is:
    'ontrue' = Table is:
        t_whitespace
        Word "T:"
        t_target

# Valid examples are things like:
#        'fred' = Is "xxx" F:<wow> T:MatchOk
#       AllIn jim T:<foundJim>
#
# For the moment, we're not trying to recognise things in any detail
t_tuple is:
    'tuple' = Table is:
        t_assignment:                 # left hand side is optional
            t_opt_whitespace
        t_operation                   # operation is required
        t_whitespace                  # for now, always require space here
        t_plus_arg                    # argument is required
        t_onfalse F:next    T:next    # F:target is optional
        t_ontrue  F:MatchOk T:MatchOk # T:target is also optional

# If the user has defined a "partial" tuple, they might use something
# of the form:
#       match_fred  F:MatchFalse T:MatchOk
t_tupleplus is:
    'tupleplus' = Table is:
        t_identifier
        t_onfalse F:next    T:next    # F:target is optional
        t_ontrue  F:MatchOk T:MatchOk # T:target is also optional

# Treat Jump To specially - for example:
#       Jump To <top>
# so that they don't have to do the less obvious "Jump To F:<label>"
# (although that will still be recognised, of course, for people who
# are used to the tag tuple format itself)
t_jumpto is:
    'jumpto' = Table is:
        Word "Jump"
        t_whitespace
        Word "To"
        t_whitespace
        t_target

# Is it worth coping with these?
t_bad_jumpto is:
    'jumpto' = Table is:
        Word "Jump":                  # cope with "Jump to"
            t_whitespace
            Word "to" T:<target>
        Word "JumpTo"                 # and with "JumpTo"
        <target>
        t_target

# The "content" of a line is the bit after any indentation, and before
# any comment...
# For the moment, we won't try to maintain ANY context, so it is up
# to the user of the tuples produced to see if they make sense...
t_content is:
    'content' = Table is:
        t_label        F:next T:MatchOk
        t_tableblock   F:next T:MatchOk        # [<tagobj> =] [Sub]Table is:
        t_tupleblock   F:next T:MatchOk        # <identifier> is:
        t_ifblock      F:next T:MatchOk        # <cmd> <arg>: OR <identifier>:
        t_jumpto       F:next T:MatchOk        # Jump To <target>
        t_tuple        F:next T:MatchOk
        t_tupleplus    F:next T:MatchOk        # name [F:<label> [T:<label>]]

t_contentline is:
    'contentline' = Table is:
        t_content                    # something that we care about
        t_opt_whitespace
        t_comment F:next T:next      # always allow a comment
        IsIn newline                 # the end of the line

# Sometimes, the user (e.g., me) writes:
#	'fred' = Table:
# instead of:
#	'fred' = Table is:
# Unfortunately, without the "is", it would get too confusing whether
# we actually wanted an if block...
t_bad_tableblock is:
    'tableblock' = Table is:
        t_assignment:     # left hand side is optional
            t_opt_whitespace
        Word "Table"      # "Table" is required
        Is ":"            # "is" is needed before the ":"

# Sometimes, the use (e.g., me again) write:
#	'fred' IsIn jim
# instead of:
#	'fred' = IsIn jim
# Whilst I'm not entirely convinced that "=" is the best character
# to use here, I think we do need something!
t_bad_tuple is:
    'tuple' = Table is:
        t_bad_assignment  # obviously we have to have this!
        t_whitespace      # in which case the whitespace IS needed
        t_operation       # operation is required
        t_whitespace      # for the moment, we must have space here
        t_plus_arg        # argument is required
        t_onfalse F:next    T:next     # F:target is optional
        t_ontrue  F:MatchOk T:MatchOk  # T:target is also optional

# Make some attempt to recognise common errors...
t_badcontent is:
    'badcontent' = Table is:
        t_bad_tableblock F:next T:MatchOk
        t_bad_tuple

t_badline is:
    'badline' = Table is:
        t_badcontent            # something that we sort of care about
        t_opt_whitespace
        t_comment F:next T:next # always allow a comment
        IsIn newline            # the end of the line

t_emptyline is:
    'emptyline' = Table is:
        t_opt_whitespace
        IsIn newline               # the end of the line

t_commentline is:
    'commentline' = Table is:
        t_comment
        IsIn newline               # the end of the line

t_passthruline is:
    'passthruline' = Table is:
        'passthru' = AllNotIn newline F:next # anything else on the line
        IsIn newline                         # the end of the line

# Basically, a file is a series of lines
t_line is:
    'line' = Table is:
        t_emptyline   F:next T:MatchOk  # empty lines are simple enough
        t_indent      F:next T:next     # optional indentation
        t_commentline F:next T:MatchOk  # always allow a comment
        t_contentline F:next T:MatchOk  # a line we care about
        t_badline     F:next T:MatchOk  # a line we think is wrong
        t_passthruline                  # a line we don't care about

# So read lines until we find the EOF
t_file = Table is:
    t_line
    EOF Here F:previous


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
