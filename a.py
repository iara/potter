#!/usr/bin/env python

"""Porter Stemming Algorithm
This is the Porter stemming algorithm, ported to Python from the
version coded up in ANSI C by the author. It may be be regarded
as canonical, in that it follows the algorithm presented in

Porter, 1980, An algorithm for suffix stripping, Program, Vol. 14,
no. 3, pp 130-137,

only differing from it at the points maked --DEPARTURE-- below.

See also http://www.tartarus.org/~martin/PorterStemmer

The algorithm as described in the paper could be exactly replicated
by adjusting the points of DEPARTURE, but this is barely necessary,
because (a) the points of DEPARTURE are definitely improvements, and
(b) no encoding of the Porter stemmer I have seen is anything like
as exact as this version, even with the points of DEPARTURE!

Vivake Gupta (v@nano.com)

Release 1: January 2001

Further adjustments by Santiago Bruno (bananabruno@gmail.com)
to allow word input not restricted to one word per line, leading
to:

release 2: July 2008
"""

import sys


def __init__():
    """The main part of the stemming algorithm starts here.
    b is a buffer holding a word to be stemmed. The letters are in b[k0],
    b[k0+1] ... ending at b[k]. In fact k0 = 0 in this demo program. k is
    readjusted downwards as the stemming progresses. Zero termination is
    not in fact used in the algorithm.

    Note that only lower case sequences are stemmed. Forcing to lower case
    should be done before stem(...) is called.
    """

    word = ""  # buffer for word to be stemmed
    k = 0
    k0 = 0
    offset = 0   # j is a general offset into the string

def cons(i, word, k0):
    """cons(i) is TRUE <=> b[i] is a consonant."""
    if word[i] == 'a' or word[i] == 'e' or word[i] == 'i' or word[i] == 'o' or word[i] == 'u':
        return 0
    if word[i] == 'y':
        if i == k0:
            return 1
        else:
            return (not cons(i - 1))
    return 1

def m(k0, offset):
    """m() measures the number of consonant sequences between k0 and j.
    if c is a consonant sequence and v a vowel sequence, and <..>
    indicates arbitrary presence,

       <c><v>       gives 0
       <c>vc<v>     gives 1
       <c>vcvc<v>   gives 2
       <c>vcvcvc<v> gives 3
       ....
    """
    n = 0
    i = k0
    while 1:
        if i > offset:
            return n
        if not cons(i):
            break
        i = i + 1
    i = i + 1
    while 1:
        while 1:
            if i > offset:
                return n
            if cons(i):
                break
            i = i + 1
        i = i + 1
        n = n + 1
        while 1:
            if i > offset:
                return n
            if not cons(i):
                break
            i = i + 1
        i = i + 1

def vowelinstem(k0):
    """vowelinstem() is TRUE <=> k0,...j contains a vowel"""
    for i in range(k0, offset + 1):
        if not cons(i):
            return 1
    return 0

def doublec(j, word, k0):
    """doublec(j) is TRUE <=> j,(j-1) contain a double consonant."""
    if j < (k0 + 1):
        return 0
    if (word[j] != word[j-1]):
        return 0
    return cons(j)

def cvc(i, word, k0):
    """cvc(i) is TRUE <=> i-2,i-1,i has the form consonant - vowel - consonant
    and also if the second c is not w,x or y. this is used when trying to
    restore an e at the end of a short  e.g.

       cav(e), lov(e), hop(e), crim(e), but
       snow, box, tray.
    """
    if i < (k0 + 2) or not cons(i) or cons(i-1) or not cons(i-2):
        return 0
    ch = word[i]
    if ch == 'w' or ch == 'x' or ch == 'y':
        return 0
    return 1

def ends(s, word, k, k0, offset):
    """ends(s) is TRUE <=> k0,...k ends with the string s."""
    length = len(s)
    if s[length - 1] != word[k]: # tiny speed-up
        return 0
    if length > (k - k0 + 1):
        return 0
    if word[k - length+1:k+1] != s:
        return 0
    offset = k - length
    return 1

def setto(s, word, k, offset):
    """setto(s) sets (j+1),...k to the characters in the string s, readjusting k."""
    length = len(s)
    word = word[:offset+1] + s + word[offset+length+1:]
    k = offset + length

def r(s, word, k, offset):
    """r(s) is used further down."""
    if m() > 0:
        setto(s, word, k, offset)

def step1ab(word, k):
    """step1ab() gets rid of plurals and -ed or -ing. e.g.

       caresses  ->  caress
       ponies    ->  poni
       ties      ->  ti
       caress    ->  caress
       cats      ->  cat

       feed      ->  feed
       agreed    ->  agree
       disabled  ->  disable

       matting   ->  mat
       mating    ->  mate
       meeting   ->  meet
       milling   ->  mill
       messing   ->  mess

       meetings  ->  meet
    """
    if word[k] == 's':
        if ends("sses", word, k, k0, offset):
            k = k - 2
        elif ends("ies", word, k, k0, offset):
            setto("i", word, k, offset)
        elif word[k - 1] != 's':
            k = k - 1
    if ends("eed", word, k, k0, offset):
        if m(k0, offset) > 0:
            k = k - 1
    elif (ends("ed", word, k, k0, offset) or ends("ing", word, k, k0, offset)) and vowelinstem():
        k = offset
        if ends("at", word, k, k0, offset):   setto("ate", word, k, offset)
        elif ends("bl", word, k, k0, offset): setto("ble", word, k, offset)
        elif ends("iz", word, k, k0, offset): setto("ize", word, k, offset)
    elif doublec(k):
            k = k - 1
            ch = word[k]
            if ch == 'l' or ch == 's' or ch == 'z':
                k = k + 1
        elif (m(k0, offset) == 1 and cvc(k)):
            setto("e", word, k, offset)

def step1c(word, k):
    """step1c() turns terminal y to i when there is another vowel in the stem."""
    if (ends("y", word, k, k0, offset) and vowelinstem()):
        word = word[:k] + 'i' + word[k+1:]

def step2(word, k):
    """step2() maps double suffices to single ones.
    so -ization ( = -ize plus -ation) maps to -ize etc. note that the
    string before the suffix must give m() > 0.
    """
    if word[k - 1] == 'a':
        if ends("ational", word, k, k0, offset):   r("ate", word, k, offset)
        elif ends("tional", word, k, k0, offset):  r("tion", word, k, offset)
    elif word[k - 1] == 'c':
        if ends("enci", word, k, k0, offset):      r("ence", word, k, offset)
        elif ends("anci", word, k, k0, offset):    r("ance", word, k, offset)
    elif word[k - 1] == 'e':
        if ends("izer", word, k, k0, offset):      r("ize", word, k, offset)
    elif word[k - 1] == 'l':
        if ends("bli", word, k, k0, offset):       r("ble", word, k, offset)
        # To match the published algorithm, replace this phrase with
        #   if ends("abli"):      r("able")
        elif ends("alli", word, k, k0, offset):    r("al", word, k, offset)
        elif ends("entli", word, k, k0, offset):   r("ent", word, k, offset)
        elif ends("eli", word, k, k0, offset):     r("e", word, k, offset)
        elif ends("ousli", word, k, k0, offset):   r("ous", word, k, offset)
    elif word[k - 1] == 'o':
        if ends("ization", word, k, k0, offset):   r("ize", word, k, offset)
        elif ends("ation", word, k, k0, offset):   r("ate", word, k, offset)
        elif ends("ator", word, k, k0, offset):    r("ate", word, k, offset)
    elif word[k - 1] == 's':
        if ends("alism", word, k, k0, offset):     r("al", word, k, offset)
        elif ends("iveness", word, k, k0, offset): r("ive", word, k, offset)
        elif ends("fulness", word, k, k0, offset): r("ful", word, k, offset)
        elif ends("ousness", word, k, k0, offset): r("ous", word, k, offset)
    elif word[k - 1] == 't':
        if ends("aliti", word, k, k0, offset):     r("al", word, k, offset)
        elif ends("iviti", word, k, k0, offset):   r("ive", word, k, offset)
        elif ends("biliti", word, k, k0, offset):  r("ble", word, k, offset)
    elif word[k - 1] == 'g': # --DEPARTURE--
        if ends("logi", word, k, k0, offset):      r("log", word, k, offset)
    # To match the published algorithm, delete this phrase

def step3(word, k):
    """step3() dels with -ic-, -full, -ness etc. similar strategy to step2."""
    if word[k] == 'e':
        if ends("icate", word, k, k0, offset):     r("ic", word, k, offset)
        elif ends("ative", word, k, k0, offset):   r("", word, k, offset)
        elif ends("alize", word, k, k0, offset):   r("al", word, k, offset)
    elif word[k] == 'i':
        if ends("iciti", word, k, k0, offset):     r("ic", word, k, offset)
    elif word[k] == 'l':
        if ends("ical", word, k, k0, offset):      r("ic", word, k, offset)
        elif ends("ful", word, k, k0, offset):     r("", word, k, offset)
    elif word[k] == 's':
        if ends("ness", word, k, k0, offset):      r("", word, k, offset)

def step4(word, k, offset):
    """step4() takes off -ant, -ence etc., in context <c>vcvc<v>."""
    if word[k - 1] == 'a':
        if ends("al", word, k, k0, offset): pass
        else: return
    elif word[k - 1] == 'c':
        if ends("ance", word, k, k0, offset): pass
        elif ends("ence", word, k, k0, offset): pass
        else: return
    elif word[k - 1] == 'e':
        if ends("er", word, k, k0, offset): pass
        else: return
    elif word[k - 1] == 'i':
        if ends("ic", word, k, k0, offset): pass
        else: return
    elif word[k - 1] == 'l':
        if ends("able", word, k, k0, offset): pass
        elif ends("ible", word, k, k0, offset): pass
        else: return
    elif word[k - 1] == 'n':
        if ends("ant", word, k, k0, offset): pass
        elif ends("ement", word, k, k0, offset): pass
        elif ends("ment", word, k, k0, offset): pass
        elif ends("ent", word, k, k0, offset): pass
        else: return
    elif word[k - 1] == 'o':
        if ends("ion", word, k, k0, offset) and (word[offset] == 's' or word[offset] == 't'): pass
        elif ends("ou", word, k, k0, offset): pass
        # takes care of -ous
        else: return
    elif word[k - 1] == 's':
        if ends("ism", word, k, k0, offset): pass
        else: return
    elif word[k - 1] == 't':
        if ends("ate", word, k, k0, offset): pass
        elif ends("iti", word, k, k0, offset): pass
        else: return
    elif word[k - 1] == 'u':
        if ends("ous", word, k, k0, offset): pass
        else: return
    elif word[k - 1] == 'v':
        if ends("ive", word, k, k0, offset): pass
        else: return
    elif word[k - 1] == 'z':
        if ends("ize", word, k, k0, offset): pass
        else: return
    else:
        return
    if m(k0, offset) > 1:
        k = offset

def step5(word, k, offset):
    """step5() removes a final -e if m() > 1, and changes -ll to -l if
    m() > 1.
    """
    offset = k
    if word[k] == 'e':
        a = m(k0, offset)
        if a > 1 or (a == 1 and not cvc(k-1)):
            k = k - 1
    if word[k] == 'l' and doublec(k) and m(k0, offset) > 1:
        k = k -1

def stem(p, i, j, word, k, k0, offset):
    """In stem(p,i,j), p is a char pointer, and the string to be stemmed
    is from p[i] to p[j] inclusive. Typically i is zero and j is the
    offset to the last character of a string, (p[j+1] == '\0'). The
    stemmer adjusts the characters p[i] ... p[j] and returns the new
    end-point of the string, k. Stemming never increases word length, so
    i <= k <= j. To turn the stemmer into a module, declare 'stem' as
    extern, and delete the remainder of this file.
    """
    # copy the parameters into statics
    word = p
    k = offset
    k0 = i
    if k <= k0 + 1:
        return word # --DEPARTURE--

    # With this line, strings of length 1 or 2 don't go through the
    # stemming process, although no mention is made of this in the
    # published algorithm. Remove the line to match the published
    # algorithm.

    step1ab(word, k)
    step1c(word, k)
    step2(word, k)
    step3(word, k)
    step4(word, k)
    step5(word, k)
    return word[k0:k+1]


if __name__ == '__main__':
    #p = PorterStemmer()
    #word = "created"
    word = "processing"
    q = stem(word, 0, len(word)-1)
    print(q)
