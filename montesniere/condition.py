#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Functionality for conditions applicable to DependencyGraph nodes."""

import re

def makeElementFixedObj(obj):
    """
    >>> alphabet = {chr(n) for n in range(0x61, 0x61 + 26)}
    >>> inAlphabet = makeElementFixedObj(alphabet)
    >>> inAlphabet('s')
    True
    >>> inAlphabet('%')
    False
    """
    def elementFixedObj(subj):
        return subj in obj
    return elementFixedObj

def makeSubsetFixedObj(obj):
    """
    >>> alphabet = {chr(n) for n in range(0x61, 0x61 + 26)}
    >>> abc = {'a', 'b', 'c'}
    >>> subAlphabet = makeSubsetFixedObj(alphabet)
    >>> subAlphabet(abc)
    True
    >>> subAlphabet({'%'})
    False
    """
    def subsetFixedObj(subj):
        return subj.issubset(obj)
    return subsetFixedObj

def makeSupersetFixedObj(obj):
    """
    >>> alphabet = {chr(n) for n in range(0x61, 0x61 + 26)}
    >>> abc = {'a', 'b', 'c'}
    >>> lowerAlphanumeric = alphabet.union({str(i) for i in range(0,10)})
    >>> superAlphabet = makeSupersetFixedObj(alphabet)
    >>> superAlphabet(lowerAlphanumeric)
    True
    >>> superAlphabet(abc)
    False
    """
    def supersetFixedObj(subj):
        return subj.issuperset(obj)
    return supersetFixedObj

def makeCardinalityFixedObj(obj):
    """
    >>> ten = {10}
    >>> oneToTen = set(range(1,11))
    >>> cardinalityTen = makeCardinalityFixedObj(ten)
    >>> cardinalityOneToTen = makeCardinalityFixedObj(oneToTen)
    >>> cardinalityTen(set(range(5,51,5)))
    True
    >>> cardinalityOneToTen({'foo', 'bar'})
    True
    >>> cardinalityOneToTen(set())
    False
    """
    # Convert strings to integers.
    newObj = set()
    for o in obj:
        try:
            newObj.add(int(o))
        except ValueError:
            pass
    obj = newObj

    def cardinalityFixedObj(subj):
        for n in obj:
            try:
                if len(subj) == n:
                    return True
            except TypeError:
                return False
        else:
            return False
    return cardinalityFixedObj

def makeExist(obj):
    def exist(subj):
        return bool(subj)
    return exist

def makeNotElementFixedObj(obj):
    def notElementFixedObj(subj):
        return subj not in obj
    return notElementFixedObj

def makeNotSubsetFixedObj(obj):
    def notSubsetFixedObj(subj):
        return not subj.issubset(obj)
    return notSubsetFixedObj

def makeNotSupersetFixedObj(obj):
    def notSupersetFixedObj(subj):
        return not subj.issuperset(obj)
    return notSupersetFixedObj

def makeNotCardinalityFixedObj(obj):
    def notCardinalityFixedObj(subj):
        for n in obj:
            try:
                if len(subj) == n:
                    return False
            except TypeError:
                return True
        else:
            return True
    return notCardinalityFixedObj

def makeNotExist(obj):
    def notExist(subj):
        return not bool(subj)
    return notExist

class Condition():
    """A condition for nodes of an nltk.parse.DependencyGraph.

    A Condition object represents a condition that can be satisfied or
    not satisfied for each node in an nltk.parse.DependencyGraph object.

    Each condition at least consists of a subject, a relation and an
    object. The subject is a key in the dictionary of each node in the
    DependencyGraph. Typical examples are 'tag', 'deps' or 'lemma'.
    The object is a set of strings. The relation is 

    Attributes:
        subj: A string that is a key in a dictionary corresponding to a
            node of a DependencyGraph. 
        rel: A string that is a key in Condition.relationDict.
        obj: A set of strings that can occur as values in a dictionary
            corresponding to a node of a DependencyGraph.
        transeunda: A set of strings that can occur as values of a
            dictionary corresponding to a node of a DependencyGraph when
            accessed at the 'rel' key. Typically {'NK'} or other
            dependency tags.
        relationFixedObj: A unary function that already incorporates the
            attribute obj. Applied to a subject, it evaluates to True or
            False, depending on the function and the fixed object.
    """
    # TODO: Describe better what transeunda are used for.

    # Regular expression for the condition
    conditionPat = re.compile(r"""
            \s*                         # leading whitespace
            (?:                         # optional part for negation
                (?P<neg>!)              # negation string (exclamation mark)
                \s+                     # separating whitespace
            )?                          # end of optional part
            (?P<subj>\S+)               # subject string
            \s+                         # separating whitespace
            (?P<rel>[^^]+)              # relation string
            (?:                         # optional part for transeunda
                \^                      # separating circumflex
                (?P<transeunda>{[^}]*}) # transeunda string
            )?                          # end of optional part
            \s+                         # separating whitespace
            (?P<obj>{[^}]*})            # object string
            \s*                         # trailing whitespace
            """, re.VERBOSE)

    # This dictionary maps the relation specified in the string representation
    # of a condition (conditionString) to the factory functions producing a
    # version of the relation with a fixed object.
    relationDict = {
            'element': makeElementFixedObj,
            'notElement': makeNotElementFixedObj,
            'subset': makeSubsetFixedObj,
            'notSubset': makeNotSubsetFixedObj,
            'superset': makeSupersetFixedObj,
            'notSuperset': makeNotSupersetFixedObj,
            'cardinality': makeCardinalityFixedObj,
            'notCardinality': makeNotCardinalityFixedObj,
            'exist': makeExist,
            'notExist' : makeNotExist
            }

    def __init__(self, subj, rel, obj, transeunda=frozenset(), negated=False):
        """Initialize Condition with the given values.

        Args:
            subj: A string that is a key in a dictionary corresponding
                to a node of a DependencyGraph. 
            rel: A string that is a key in Condition.relationDict.
            obj: A set of strings that can occur as values in a
                dictionary corresponding to a node of a DependencyGraph.
            transeunda: A set of strings that can occur as values of a
                dictionary corresponding to a node of a DependencyGraph
                when accessed at the 'rel' key. Typically {'NK'} or
                other dependency tags.

        Returns:
            The initialized SemRepRule.
        """
        self.subj = subj
        self.rel = rel
        self.obj = obj
        self.transeunda = transeunda
        self.negated = negated
        objFixer = Condition.relationDict[self.rel]
        self.relationFixedObj = objFixer(self.obj)

    @classmethod
    def fromstring(cls, conditionString):
        """Initialize Condition from a string.

        Args:
            conditionString: A string representing a condition.

        Returns:
            The initialized SemRepRule.
        """
        negated, subj, rel, transeunda, obj = Condition.readConditionString(
                conditionString)
        return cls(subj, rel, obj, transeunda, negated)

    def __str__(self):
        neg = '! ' if self.negated else ''
        return '{1}{0.subj} {0.rel}^{0.transeunda} {0.obj}'.format(self, neg)
    
    def __call__(self, depGraph, address):
        """Test if a node of a DependencyGraph satisfies this condition.

        Args:
            depGraph: An nltk.parse.DependencyGraph object.
            address: An integer denoting the address of a node in the
                depGraph
        Returns:
            True, if the condition is satisfied; False otherwise.
        """
        node = depGraph.get_by_address(address)
        satisfied = self.subj(depGraph, address, self.relationFixedObj)
        while node['rel'] in self.transeunda:
            node = depGraph.get_by_address(node['head'])
            satisfied = satisfied or self.subj(
                    depGraph, node['address'], self.relationFixedObj)

        if self.negated:
            return not satisfied
        else:
            return satisfied
            
    def _testSubjSet(self, subjSet):
        """Test if a set satisfies the condition.

        Args:
            subjSet: A set of strings or a dict whose keys are strings.

        Returns:
            True if the condition is satisfied; False otherwise.
        """
        # subjSet might not actually be a set, but a dict.
        # Use the keys then.
        if isinstance(subjSet, dict):
            subjSet = set(subjSet.keys())
        return self.relationFixedObj(subjSet)

    def _getSubjSet(self, depGraph, address):
        """Get the subject set from a dependency graph."""
        if callable(self.subj):
            return self.subj(depGraph, address)
        else:
            return depGraph.get_by_address(address)[self.subj]

    @staticmethod
    def readConditionString(conditionString):
        """Construct Condition attributes from a string.

        Args:
            conditionString: A string representing a condition.

        Returns:
            A quadruple containing subj (function), rel (str),
                transeunda (set of str) and obj (set of str).
            
        Raises:
            ValueError if the conditionString is invalid.

        >>> cs1 = 'deps superset {SB}'
        >>> c1 = Condition.readConditionString(cs1)
        >>> (c1[0], c1[2], c1[3], c1[4])
        (False, 'superset', set(), {'SB'})
        >>> cs2 = 'rel element^{NK} {SB, OA}'
        >>> c2 = Condition.readConditionString(cs2)
        >>> (c2[0], c2[2], c2[3])
        (False, 'element', {'NK'})
        >>> sorted(c2[4])
        ['OA', 'SB']
        >>> cs3 = '! deps subset {DA}'
        >>> c3 = Condition.readConditionString(cs3)
        >>> (c3[0], c3[2], c3[3], c3[4])
        (True, 'subset', set(), {'DA'})
        """
        negated, subj, rel, transeunda, obj = (False, '', '', set(), set())
        match = Condition.conditionPat.match(conditionString)
        if match:
            subj = _getSubj(match.group('subj'))
            obj = buildSet(match.group('obj'))
            rel = match.group('rel')
            if match.group('transeunda'):
                transeunda = buildSet(match.group('transeunda'))
            if match.group('neg') == '!':
                negated = True
        else:
            errMsg = '{} is not a valid conditionString.'
            raise ValueError(errMsg.format(conditionString))
        return negated, subj, rel, transeunda, obj

def _getSubj(subjString):
    """Return a subject function from a subject string."""
    # toTraverse contains the paths to the final node.
    toTraverse = [s.strip() for s in subjString.split('.')]
    # The last element is not a path and functions as a key for the
    # dict that is the final node.
    key = toTraverse.pop(-1)

    # Define the subject function
    def subj(depGraph, address, relationFixedObj):
        nodes = [depGraph.get_by_address(address)]
        for t in toTraverse:
            newNodes = []
            if t == '^':
                for n in nodes:
                    try:
                        newNodes.append(depGraph.get_by_address(n['head']))
                    except KeyError:
                        pass
            else:
                for n in nodes:
                    try:
                        newNodes.extend(
                                [depGraph.get_by_address(a)
                                    for a in n['deps'][t]]
                                )
                    except KeyError:
                        pass
            nodes = newNodes

        subjElms = [n[key] for n in nodes]
        subjElms = [set(s.keys()) if isinstance(s, dict) else s
                for s in subjElms]
        bools = {relationFixedObj(s) for s in subjElms}
        return any(bools)

    # Return the subject function that now knows about the nodes it has to
    # traverse.
    return subj

def buildSet(setString):
    """Build a set of strings from a string representation of a set.

    Args:
        setString: A string representing a set. The members of the set
            should not be surrounded by quotes.

    Returns:
        A set of strings.

    >>> sorted(buildSet('{foo, bar, baz}'))
    ['bar', 'baz', 'foo']
    >>> buildSet('{}')
    set()
    >>> buildSet('[not, a, set]')
    Traceback (most recent call last):
        ...
    ValueError: setString '[not, a, set]' does not represent a set.
    """
    setString = setString.strip()
    s = {}
    if setString.startswith('{') and setString.endswith('}'):
        setString = setString[1:-1].strip()
        if setString:
            s = set(re.split(r'\s*,\s*', setString))
        else:
            return set()
    else:
        errMsg = "setString '{}' does not represent a set."
        raise ValueError(errMsg.format(setString))
    return s

def test():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    test()
