==========
mxTextTags
==========
Back in the late 1990s, I discovered Marc-Andre Lemburg's mxTextTools_, which
is a fascinating and elegant parsing mechanism. At the time, ASCII text was
dominant, and the version of mxTextTools that worked on 8-bit data was
blindingly fast compare to other Python solutions.

.. _mxTextTools: http://www.egenix.com/products/python/mxBase/mxTextTools/

However, I found there were various problems with writing a program in a
sequence of tuples. I had two main grumbles.

The first was the fragility of using a sequence of tuples, and how often I
forgot to put a trailing comma after one of the intermediate tuples (sometimes
related to adding new tuples after the last). I don't think I'd have so much
problem with that now - adding a comma after a tuple, including the last one,
is much more a reflex (which causes problems when dealing with JSON or
JavaScript, but one can't have everything).

The second was that navigation between tuples was all by shifts - i.e.,
plus or minus an offset. This makes it awkward to add or remove tuples, and to
move sequence around. So my "mini language" added labels. Of course, since
then modern mxTextTools has also added labels (and no, I don't think I can
claim any credit for that!).

So perhaps I would not have invented the tag format if I were coming to the
situation nowadays.

Anyway, the code has all been available at http://tibsnjoan.co.uk/mxtext/Metalang.html
for a long time, but in the modern world of distributed version control
systems, that's not actually *very* visible. Also, there are a couple of
things I'd like to try with the codebase. So it seems sensible to make it
available here - even if I never actually get round to those couple of things...

Things you should know:

* It does seem to work (if the minimal testing of doing::

    $ ./Translate.py Examples.tag temp.py
    $ diff -du Examples.py temp.py

  and getting no differences between the current output and the expected
  output can be taken as proof of working - so yeh for the stability of
  Python, since this code was written for Python 1.5, and my Mac is running
  2.7). However, I've not tried to see if the output is still valid for
  current day mxTexTools yet (that's gone from v1.1.1 to v3.2) - I'll update
  this when I know.
* Email addresses and links in the Metadata.html page have rotted - don't
  trust them!
* There aren't any unit tests - this is *old* software. In fact, there aren't
  any tests at all, apart from comparing the output to an earlier version,
  and the fact that the program itself seems to run.
* mxTextTools itself doesn't appear to have a version that works on Python 3,
  so it probably doesn't hurt that this is solidly Python 2 code.

.. vim: set filetype=rst tabstop=8 softtabstop=2 shiftwidth=2 expandtab:
