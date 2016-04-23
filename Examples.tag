# -*- Mode: Python -*-
"""Examples.tag -- Tag metalanguage examples

 Original examples from Marc-Andre Lemburg, translated into the metalanguage
 by Tony J Ibbs, at various dates up to and including 1999-10-12

 Note that these are *examples*, and not all can actually be parsed by the
 current translator...

 My comments start "#TJI"

 All original examples are:
    (c) Copyright Marc-Andre Lemburg; All Rights Reserved.
    See the documentation for further information on copyrights,
    or contact the author (mal@lemburg.com).
"""


""" RTF - tag a RTF string (Version 0.2) [alternative version]

    This version does recursion using the ThisTable special argument
    to the Table cmd.
"""
        
numeral = Table is:
    # sign ?
    Is '-' F:next
    AllIn number
        
# XXX: doesn't know how to handle \bin et al. with embedded {}
        
ctrlword = Table is:
    'name' = AllIn a2z          # name
    Is ' ' F:next T:MatchOk     # delimiter
    IsIn number+'-' F:MatchOk
    Skip back                   # unread the previous character
    'param' = Table numeral F:repeat T:MatchOk
    Is ' ' F:next T:MatchOk
    Skip back                   # unread the previous character

hex = set(number+'abcdefABCDEF')
notalpha = set(alpha,0)
        
#TJI ------------------------------------------------------------
#TJI The original text for ctrlsymbol is:
#TJI
#TJI       ctrlsymbol = (
#TJI                     (None,Is,"'",+3),         # hexquote
#TJI                      (None,IsInSet,hex),
#TJI                      (None,IsInSet,hex),
#TJI                     (None,IsInSet,notalpha,+1,MatchOk) # other
#TJI                    )
#TJI
#TJI A first transformation of the orginal text gives us:
#TJI
#TJI       ctrlsymbol = Table is:
#TJI           Is "'" F:<4>                # hexquote
#TJI           IsInSet hex
#TJI           IsInSet hex
#TJI           <4>
#TJI           IsInSet notalpha F:next T:MatchOk   # other
#TJI
#TJI which quickly further transforms to become:

ctrlsymbol = Table is:
    Is "'":                             # hexquote
        IsInSet hex
        IsInSet hex
    IsInSet notalpha F:next T:MatchOk   # other

#TJI which I think is a lot clearer, except that the last line could
#TJI presumably be better written as:
#TJI    IsInSet notalpha F:MatchOK T:MatchOk       # other
#TJI ------------------------------------------------------------

rtf = Table is:
    <top>       # this is a label at the top of the definition
    Is '\\':                                            # control ?
        'word'   = Table ctrlword   F:next T:previous   # word
        'symbol' = Table ctrlsymbol F:next T:<top>      # symbol
    Is '}':                                             # closing group
        Skip back F:repeat T:MatchOk                    # nested group
    Is '{':                                             # recurse
        'group' = Table ThisTable                       # using ourselves
        Is '}'
        Jump To <top>
    'text' = AllNotIn '\\{}' F:next T:<top>             # document text
    'eof'  = EOF Here                                   # EOF or fail
        

""" HTML - tag a HTML string (Version 0.6)"""
        

# ErrorTag
error = '***syntax error'                       # error tag obj
        
tagname_set = set(alpha+'-'+number)
tagattrname_set = set(alpha+'-'+number)
tagvalue_set = set('"\'> ',0)
white_set = set(' \r\n\t')
        
tagattr = Table is:
    'name' = AllInSet tagattrname_set   # name
    AllInSet white_set F:next           # skip junk
    Is '=' F:MatchOk                    # with value ?
    AllInSet white_set F:next           # skip junk
    'value' = AllInSet tagvalue_set F:next T:MatchOk    # unquoted value
    Is '"':                             # double quoted value
        'value' = AllNotIn '"'
        Is '"'
        Jump To MatchOk
    Is "'":                             # single quoted value
        'value' = AllNotIn "'"
        Is "'"
        
valuetable = Table is:
    # ignore whitespace + '='
    AllInSet set(' \r\n\t=') F:next
    # unquoted value
    'value' = AllInSet tagvalue_set F:next T:MatchOk
    # double quoted value
    Is '"':
        'value' = AllNotIn '"'
        Is '"'
        Jump To MatchOk
    # single quoted value
    Is "'":
        'value' = AllNotIn "'"
        Is "'"

allattrs = Table is:
    <top>
    # look for attributes
    AllInSet white_set:
        Is '>' F:next T:MatchOk
        'tagattr' = Table tagattr
        Jump To <top>
    Is '>' F:next T:MatchOk
    # handle incorrect attributes
    error = AllNotIn '> \r\n\t'
    Jump To <top>
        
htmltag = Table is:
    Is '<':
        # is this a closing tag ?
        'closetag' = Is '/' F:next
        # a comment ?
        'comment' = Is '!':
            Word '--'
            'text' = sWordStart BMS('-->') F:next
            Skip 3
            Jump To MatchOk
        # a SGML-Tag ?
        'other' = AllNotIn '>' F:next
        Is '>'
        Jump To MatchOk
        # XMP-Tag ?
        'tagname' = Word 'XMP':
            Is '>'
            'text' = WordStart '</XMP>'
            Skip len('</XMP>')
            Jump To MatchOk
        # get the tag name
        'tagname' = AllInSet tagname_set
        # look for attributes
        <huntAttributes>
        AllInSet white_set:
            Is '>' F:next T:MatchOk
            'tagattr' = Table tagattr
            Jump To <huntAttributes>
        Is '>' F:next T:MatchOk
        # handle incorrect attributes
        error = AllNotIn '> \n\r\t'
        Jump To <huntAttributes>

htmltable = Table is:
    <top>
    # HTML-Tag
    'htmltag' = Table htmltag F:next T:<text>
    # not HTML, but still using this syntax: error or inside XMP-tag !
    error = Is '<':
        error = AllNotIn '>' F:next
        error = Is '>'
    <text>    # normal text
    'text' = AllNotIn '<' F:next
    # end of file
    'eof' = EOF Here F:<top>
        

""" Loop - loop examples (Version 0.1)"""

#TJI ------------------------------------------------------------
#TJI Looping must be susceptible to a better representation, but since I don't
#TJI have any documentation for it, I'll leave it alone for now...
#TJI ------------------------------------------------------------
        
# use Loop to match a certain number of subtags
table1 = Table is:
    Word 'loop '
    # match <= 5 stars
    <loop>
    'loop' = Loop 5:
        Is '*' F:next T:previous
        LoopControl Break
        Jump To <loop>
    # must end with a dot
    Is '.'
        
# use Loop to tag subsections of a tagging table, i.e.
# emulate a Table-match
table2 = Table is:
    'presection' = AllNotIn '(' F:next
    # match a group of characters enclosed in ()
    <loop>
    'section' = Loop 1:
        Is '('
        AllNotIn ')'
        Is ')' F:repeat T:<loop>
    # must end with a dot
    Is '.'
        
# read in all chars and then do lots of null loops
table3 = Table is:
    'Loops' = Loop 10000 F:MatchOK
    AllNotIn '' F:previous T:previous

#TJI which is identical in effect to:
#TJI
#TJI table3a = Table is:
#TJI    'Loops' = Loop 10000:
#TJI        AllNotIn '' F:previous T:previous
#TJI
#TJI which is presumably the same as:
#TJI
#TJI table3b = Table is:
#TJI     <loop>
#TJI     'Loops' = Loop 10000:
#TJI         AllNotIn '' F:<loop> T:<loop>


""" Python - tag table for Python (Version 0.6)

    * 0.5->0.6: changed the names of the tags !
                fixed bug in match_str()

    XXX can't handle (lambda ...) and misses not in 'if x is not'
"""

comment = Table is:
    'comment' = Table is:
        Is '#'
        AllNotIn '\n\r' F:MatchOk
        
whitespace is:
    AllIn ' \t'
opt_whitespace is:
    whitespace F:MatchOk
        
identifier =Table is:
    'identifier' = Table is:
        IsIn alpha+'_'
        AllIn alpha+'_'+number F:MatchOk

#TJI Note that CallArg,(<args>) gets translated to CallArg(<args>) in our
#TJI translated form (also note that this is not actually supported yet)

string = Table is:
    'str' = Table is:
        # hints
        IsIn '\"\''
        Skip back
        # now let's see what we have...
        Word '"""':
            'string' = NoWord '"""' F:next
            Word '"""'
            Jump To MatchOk
        Word "'''":
            'string' = NoWord "'''" F:next
            Word "'''"
            Jump To MatchOk
        Is '"':
            'string' = CallArg(match_str,'"') F:next
            Word '"'
            Jump To MatchOk
        Is "'"
        'string' = CallArg(match_str,"'") F:next
        Word "'"
        Jump To MatchOk
        
skw = ["del", "from", "lambda", "return", "and", "elif",
       "global", "not", "try", "break", "else", "if", "or", "while",
       "except", "import", "pass", "continue", "finally", "in", "print",
       "for", "is", "raise"]
keywords = word_in_list(skw)
        
# note: '=lambda x:...' and '(lambda x:...' are not recognized,
#       yet '= lambda x:...' and '( lambda x:...' are (just like in
#       emacs python-mode) !
        
keyword = Table is:
    'kw' = Table is:
        AllIn ' \t\n\r'
        # hints
        IsIn alpha
        Skip back
        # one in the list keywords
        'keyword' = Table keywords:
            IsIn ': \t\n\r'
            Jump To MatchOk
        # a function declaration
        'keyword' = Word 'def':
            whitespace
            identifier
            Is '('
            # scan parameters
            <startTuple>
            'parameter' = AllNotIn '(),':
                # are there more ?
                Is ',' F:next T:<startTuple>
            # tuple in param-list ?
            Is '(' F:next T:<startTuple>
            # maybe we're done
            Is ')'
            # to make sure...
            Is ',' F:next T:<startTuple>
            Is ')' F:next
            # test for correct syntax
            IsIn ': \t\n\r'
            Jump To MatchOk
        # a class declaration:
        'keyword' = Word 'class':
            whitespace
            identifier
            Is '(' F:MatchOk
            # scan base-classes
            'baseclass' = AllNotIn '),' F:<done>
            # are there more ?
            Is ',' F:next T:previous
            # we're done
            <done>
            Is ')'
            IsIn ': \t\n\r'

python_script = Table is:
    <top>
    comment F:next T:repeat
    string F:next T:previous
    keyword F:next T:<top>
    # end-of-file ?
    EOF Here F:next T:MatchOk
    # skip uninteresting chars and restart
    IsIn any
    AllNotIn '#\'\"_ \n\r\t' F:<top> T:<top>
        

""" RTF - tag a RTF string (Version 0.2)
    
    This version does recursion using the TableInList cmd.
"""
        
# list of tables (hack to be able to do recursion)
tables = []

# indices
rtf_index = 0
        
numeral = Table is:
    # sign ?
    Is '-' F:next
    AllIn number
        
# XXX: doesn't know how to handle \bin et al. with embedded {}
        
ctrlword = Table is:
    # name
    'name' = AllIn a2z
    # delimiter
    Is ' ' F:next T:MatchOk
    IsIn number+'-':
        Skip back
        'param' = Table numeral F:repeat T:MatchOk
        Is ' ' F:next T:MatchOk
        Skip back
        
hex = set(number+'abcdefABCDEF')
notalpha = set(alpha,0)
        
ctrlsymbol = Table is:
    # hexquote
    Is "'":
        IsInSet hex
        IsInSet hex
    # other
    IsInSet notalpha F:next T:MatchOk
        
rtf = Table is:
    <top>
    # control ?
    Is '\\':
        # word
        'word' = Table ctrlword F:next T:previous
        # symbol
        'symbol' = Table ctrlsymbol F:next T:<top>
    # closing group
    Is '}':
        Skip back F:repeat T:MatchOk
    # nested group
    Is '{':
        # recurse
        'group' = TableInList(tables,rtf_index) #TJI Not yet supported
        Is '}'
        Jump To <top>
    # document text
    'text' = AllNotIn '\\{}' F:next T:<top>
    # EOF
    'eof' = EOF Here
        
# add tables to list
tables.append(rtf)
        

""" Example for dynamic programming with Tag Tables... originated from
    a posting to comp.lang.python by Tim Peters:

 [Tim]
 > [Marc-Andre]
 > I can stick in any matching function I want, so I might even
 > let re.match() do some of the work. That should get me pretty close
 > to their semantics -- ok, I can't do it all the way:

 Sure you can:  just let re.match() do *all* the work!  Presto, tables are as
 powerful as re.

 > e.g. I currently don't have registers so back-references to already
 > matched groups will probably not work without reanalysing them.

 So you have trouble recognizing e.g. the language of the form

   <tag> ... </tag>

 where "tag" can be any (say) arbitrary alphanumeric string?  <S> <Like> this
 clause is in that language </Like>, <but> this clause isn't <but/>, while
 the whole sentence is -- if you ignore the trailing period </S>.  It's even
 better if you can do computation on backreferences and use the results to
 guide further parsing.  E.g., recognizing Fortran Hollerith strings requires
 this (a string of digits, followed by "H" or "h", followed by any string of
 characters whose length is equal to the decimal value of the string of
 digits; and that's too hard for regexps too).

 teasingly y'rs  - tim
 """

#TJI The original code is:
#TJI       TIM = (
#TJI           # Check starting tag
#TJI           (opening_tag,Table+CallTag,
#TJI            ((None,Is,'<'),
#TJI             (None,AllInSet,alphanumeric_set),
#TJI             (None,Is,'>'),
#TJI             )),
#TJI           # Find closing tag
#TJI           ('text',TableInList,(tables,0)),
#TJI           # For completeness mark the closing tag too
#TJI           (closing_tag,Table+CallTag,
#TJI            ((None,Word,'</'),
#TJI             (None,AllInSet,alphanumeric_set),
#TJI             (None,Is,'>'),
#TJI             )),
#TJI       )

#TJI This translates as the following, which can't yet be translated...

#TJI TIM = Table is:
#TJI     # Check starting tag
#TJI     opening_tag = Table+CallTag is: #TJI This is not supported yet
#TJI         Is '<'
#TJI         AllInSet alphanumeric_set
#TJI         Is '>'
#TJI     # Find closing tag
#TJI     'text' = TableInList(tables,0)  #TJI This is not supported yet
#TJI     # For completeness mark the closing tag too
#TJI     closing_tag = Table+CallTag is: #TJI This is not supported yet
#TJI         Word '</'
#TJI         AllInSet alphanumeric_set
#TJI         Is '>'
        

""" Words - tag words in a string (Version 0.2) """
        
lcwords = []
cwords = []

#TJI The commented out portions cannot yet be translated...

#TJI lower_case_word = Table is:
#TJI     lcwords = AppendToTag+Table is: #TJI This is not supported yet
#TJI         # first char in word
#TJI         IsIn a2z+umlaute
#TJI         # all other chars (if there are any)
#TJI         AllIn german_alpha F:MatchOk
   
#TJI capital_word = Table is:
#TJI     cwords = AppendToTag+Table is: #TJI This is not supported yet
#TJI         # first char in word
#TJI         IsIn A2Z+Umlaute
#TJI         # all other chars (if there are any)
#TJI         AllIn german_alpha F:MatchOk
        
tag_words = Table is:
    <top>
    lower_case_word F:next T:<after>
    capital_word F:next
    <after>
    AllIn white+newline F:next
    AllNotIn german_alpha+white+newline F:next  # uninteresting
    EOF Here F:<top>                            # EOF
        
