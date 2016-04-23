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

numeral = (
    # sign ?
    (None,Is,'-',+1),
    (None,AllIn,number),
)

# XXX: doesn't know how to handle \bin et al. with embedded {}

ctrlword = (
    ('name',AllIn,a2z),                 # name
    (None,Is,' ',+1,MatchOk),           # delimiter
    (None,IsIn,number+'-',MatchOk),
    (None,Skip,-1),                     # unread the previous character
    ('param',Table,numeral,0,MatchOk),
    (None,Is,' ',+1,MatchOk),
    (None,Skip,-1),                     # unread the previous character
)

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

ctrlsymbol = (
    (None,Is,"'",+3,+1),     # hexquote
        (None,IsInSet,hex),
        (None,IsInSet,hex),
    (None,IsInSet,notalpha,+1,MatchOk), # other
)

#TJI which I think is a lot clearer, except that the last line could
#TJI presumably be better written as:
#TJI    IsInSet notalpha F:MatchOK T:MatchOk       # other
#TJI ------------------------------------------------------------

rtf = (
    # <top>                             # this is a label at the top of the definition
    (None,Is,'\\',+3,+1),    # control ?
        ('word',Table,ctrlword,+1,-1),  # word
        ('symbol',Table,ctrlsymbol,+1,-2), # symbol
    (None,Is,'}',+2,+1),     # closing group
        (None,Skip,-1,0,MatchOk),       # nested group
    (None,Is,'{',+4,+1),     # recurse
        ('group',Table,ThisTable),      # using ourselves
        (None,Is,'}'),
        (None,Jump,To,-8),
    ('text',AllNotIn,'\\{}',+1,-9),     # document text
    ('eof',EOF,Here),                   # EOF or fail
)


""" HTML - tag a HTML string (Version 0.6)"""


# ErrorTag
error = '***syntax error'                       # error tag obj

tagname_set = set(alpha+'-'+number)
tagattrname_set = set(alpha+'-'+number)
tagvalue_set = set('"\'> ',0)
white_set = set(' \r\n\t')

tagattr = (
    ('name',AllInSet,tagattrname_set),  # name
    (None,AllInSet,white_set,+1),       # skip junk
    (None,Is,'=',MatchOk),              # with value ?
    (None,AllInSet,white_set,+1),       # skip junk
    ('value',AllInSet,tagvalue_set,+1,MatchOk), # unquoted value
    (None,Is,'"',+4,+1),     # double quoted value
        ('value',AllNotIn,'"'),
        (None,Is,'"'),
        (None,Jump,To,MatchOk),
    (None,Is,"'",+3,+1),     # single quoted value
        ('value',AllNotIn,"'"),
        (None,Is,"'"),
)

valuetable = (
    # ignore whitespace + '='
    #[ignored]#AllInSet set(' \r\n\t=') F:next
    # unquoted value
    ('value',AllInSet,tagvalue_set,+1,MatchOk),
    # double quoted value
    (None,Is,'"',+4,+1),
        ('value',AllNotIn,'"'),
        (None,Is,'"'),
        (None,Jump,To,MatchOk),
    # single quoted value
    (None,Is,"'",+3,+1),
        ('value',AllNotIn,"'"),
        (None,Is,"'"),
)

allattrs = (
    # <top>
    # look for attributes
    (None,AllInSet,white_set,+4,+1),
        (None,Is,'>',+1,MatchOk),
        ('tagattr',Table,tagattr),
        (None,Jump,To,-3),
    (None,Is,'>',+1,MatchOk),
    # handle incorrect attributes
    (error,AllNotIn,'> \r\n\t'),
    (None,Jump,To,-6),
)

htmltag = (
    (None,Is,'<',+21,+1),
        # is this a closing tag ?
        ('closetag',Is,'/',+1),
        # a comment ?
        ('comment',Is,'!',+4,+1),
            (None,Word,'--'),
            #[ignored]#'text' = sWordStart BMS('-->') F:next
            (None,Skip,3),
            (None,Jump,To,MatchOk),
        # a SGML-Tag ?
        ('other',AllNotIn,'>',+1),
        (None,Is,'>'),
        (None,Jump,To,MatchOk),
        # XMP-Tag ?
        ('tagname',Word,'XMP',+4,+1),
            (None,Is,'>'),
            ('text',WordStart,'</XMP>'),
            #[ignored]#Skip len('</XMP>')
            (None,Jump,To,MatchOk),
        # get the tag name
        ('tagname',AllInSet,tagname_set),
        # look for attributes
        # <huntAttributes>
        (None,AllInSet,white_set,+4,+1),
            (None,Is,'>',+1,MatchOk),
            ('tagattr',Table,tagattr),
            (None,Jump,To,-3),
        (None,Is,'>',+1,MatchOk),
        # handle incorrect attributes
        (error,AllNotIn,'> \n\r\t'),
        (None,Jump,To,-6),
)

htmltable = (
    # <top>
    # HTML-Tag
    ('htmltag',Table,htmltag,+1,+4),
    # not HTML, but still using this syntax: error or inside XMP-tag !
    (error,Is,'<',+3,+1),
        (error,AllNotIn,'>',+1),
        (error,Is,'>'),
    # <text>                            # normal text
    ('text',AllNotIn,'<',+1),
    # end of file
    ('eof',EOF,Here,-5),
)


""" Loop - loop examples (Version 0.1)"""

#TJI ------------------------------------------------------------
#TJI Looping must be susceptible to a better representation, but since I don't
#TJI have any documentation for it, I'll leave it alone for now...
#TJI ------------------------------------------------------------

# use Loop to match a certain number of subtags
table1 = (
    (None,Word,'loop '),
    # match <= 5 stars
    # <loop>
    ('loop',Loop,5,+4,+1),
        (None,Is,'*',+1,-1),
        (None,LoopControl,Break),
        (None,Jump,To,-3),
    # must end with a dot
    (None,Is,'.'),
)

# use Loop to tag subsections of a tagging table, i.e.
# emulate a Table-match
table2 = (
    ('presection',AllNotIn,'(',+1),
    # match a group of characters enclosed in ()
    # <loop>
    ('section',Loop,1,+4,+1),
        (None,Is,'('),
        (None,AllNotIn,')'),
        (None,Is,')',0,-3),
    # must end with a dot
    (None,Is,'.'),
)

# read in all chars and then do lots of null loops
table3 = (
    ('Loops',Loop,10000,MatchOk),
    #[ignored]#AllNotIn '' F:previous T:previous
)

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

comment = (
    ('comment',Table,(
        (None,Is,'#'),
        (None,AllNotIn,'\n\r',MatchOk),
    )),
)

whitespace = \
    (None,AllIn,' \t')
opt_whitespace = \
    whitespace      + (MatchOk,)

identifier = (
    ('identifier',Table,(
        (None,IsIn,alpha+'_'),
        (None,AllIn,alpha+'_'+number,MatchOk),
    )),
)

#TJI Note that CallArg,(<args>) gets translated to CallArg(<args>) in our
#TJI translated form (also note that this is not actually supported yet)

string = (
    ('str',Table,(
        # hints
        #[ignored]#IsIn '\"\''
        (None,Skip,-1),
        # now let's see what we have...
        (None,Word,'"""',+4,+1),
            ('string',NoWord,'"""',+1),
            (None,Word,'"""'),
            (None,Jump,To,MatchOk),
        (None,Word,"'''",+4,+1),
            ('string',NoWord,"'''",+1),
            (None,Word,"'''"),
            (None,Jump,To,MatchOk),
        (None,Is,'"',+3,+1),
            #[ignored]#'string' = CallArg(match_str,'"') F:next
            (None,Word,'"'),
            (None,Jump,To,MatchOk),
        (None,Is,"'"),
        #[ignored]#'string' = CallArg(match_str,"'") F:next
        (None,Word,"'"),
        (None,Jump,To,MatchOk),
    )),
)

skw = ["del", "from", "lambda", "return", "and", "elif",
       "global", "not", "try", "break", "else", "if", "or", "while",
       "except", "import", "pass", "continue", "finally", "in", "print",
       "for", "is", "raise"]
keywords = word_in_list(skw)

# note: '=lambda x:...' and '(lambda x:...' are not recognized,
#       yet '= lambda x:...' and '( lambda x:...' are (just like in
#       emacs python-mode) !

keyword = (
    ('kw',Table,(
        (None,AllIn,' \t\n\r'),
        # hints
        (None,IsIn,alpha),
        (None,Skip,-1),
        # one in the list keywords
        ('keyword',Table,keywords,+3,+1),
            (None,IsIn,': \t\n\r'),
            (None,Jump,To,MatchOk),
        # a function declaration
        ('keyword',Word,'def',+12,+1),
            whitespace,
            identifier,
            (None,Is,'('),
            # scan parameters
            # <startTuple>
            ('parameter',AllNotIn,'(),',+2,+1),
                # are there more ?
                (None,Is,',',+1,-1),
            # tuple in param-list ?
            (None,Is,'(',+1,-2),
            # maybe we're done
            (None,Is,')'),
            # to make sure...
            (None,Is,',',+1,-4),
            (None,Is,')',+1),
            # test for correct syntax
            (None,IsIn,': \t\n\r'),
            (None,Jump,To,MatchOk),
        # a class declaration:
        ('keyword',Word,'class',+8,+1),
            whitespace,
            identifier,
            (None,Is,'(',MatchOk),
            # scan base-classes
            ('baseclass',AllNotIn,'),',+2),
            # are there more ?
            (None,Is,',',+1,-1),
            # we're done
            # <done>
            (None,Is,')'),
            (None,IsIn,': \t\n\r'),
    )),
)

python_script = (
    # <top>
    comment         + (+1,0),
    string          + (+1,-1),
    keyword         + (+1,-2),
    # end-of-file ?
    (None,EOF,Here,+1,MatchOk),
    # skip uninteresting chars and restart
    (None,IsIn,any),
    #[ignored]#AllNotIn '#\'\"_ \n\r\t' F:<top> T:<top>
)


""" RTF - tag a RTF string (Version 0.2)

    This version does recursion using the TableInList cmd.
"""

# list of tables (hack to be able to do recursion)
tables = []

# indices
rtf_index = 0

numeral = (
    # sign ?
    (None,Is,'-',+1),
    (None,AllIn,number),
)

# XXX: doesn't know how to handle \bin et al. with embedded {}

ctrlword = (
    # name
    ('name',AllIn,a2z),
    # delimiter
    (None,Is,' ',+1,MatchOk),
    (None,IsIn,number+'-',+5,+1),
        (None,Skip,-1),
        ('param',Table,numeral,0,MatchOk),
        (None,Is,' ',+1,MatchOk),
        (None,Skip,-1),
)

hex = set(number+'abcdefABCDEF')
notalpha = set(alpha,0)

ctrlsymbol = (
    # hexquote
    (None,Is,"'",+3,+1),
        (None,IsInSet,hex),
        (None,IsInSet,hex),
    # other
    (None,IsInSet,notalpha,+1,MatchOk),
)

rtf = (
    # <top>
    # control ?
    (None,Is,'\\',+3,+1),
        # word
        ('word',Table,ctrlword,+1,-1),
        # symbol
        ('symbol',Table,ctrlsymbol,+1,-2),
    # closing group
    (None,Is,'}',+2,+1),
        (None,Skip,-1,0,MatchOk),
    # nested group
    (None,Is,'{',+3,+1),
        # recurse
        #[ignored]#'group' = TableInList(tables,rtf_index) #TJI Not yet supported
        (None,Is,'}'),
        (None,Jump,To,-7),
    # document text
    ('text',AllNotIn,'\\{}',+1,-8),
    # EOF
    ('eof',EOF,Here),
)

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

tag_words = (
    # <top>
    lower_case_word + (+1,+2),
    capital_word    + (+1,),
    # <after>
    (None,AllIn,white+newline,+1),
    (None,AllNotIn,german_alpha+white+newline,+1), # uninteresting
    (None,EOF,Here,-4),                 # EOF
)

