## Dependency-based semantics construction with lambda calculus


### Authors

Lukas Mülleder

Rebekka Hubert

Simon Will

{mülleder, will, hubert}@cl.uni-heidelberg.de

Institute for Computational Linguistics

Heidelberg University, Germany


### Outline

The algorithm presented in this module takes already parsed sentences, extracts their meaning
and returns a logical expression representing the given sentence. During this process, 
a depedencygraph is created out of the given sentence and each node is assigned a unique 
lambda expression representing its meaning. Then these expression are merged using functional
application and returned to the user.
This complete expression can be accessed and later used to assign a truth value to an other sentence
related to that extracted knowledge. This function is represented by our testsuit.


### Requirements

Python 3.4

NLTK 3.0

CONLL06 File


#### `montesniere_get_Semantics.sh`
We recommend using our shell script in order to avoid dependency errors. Start it from
the command line by running `./montesniere_get_Semantics.sh test/conll/<filename>`.


#### `normalize.py`

This module is only needed if you intend to add new data to or test directory.
Use `normalize.py` to normalize the input sentences in order to avoid unfortunate
coordination of phrases. 
This script takes one sentence in conll06-format as input parameter and returns the normalized
sentence. 

Example:

our testsentence.morph.conll as input yields:

    1	Ein	ein	DET	ART	_	2	NK	_	_
    2	Kind	kind	NOUN	NN	_	3	SB	_	_
    3	isst	issen	VERB	VVFIN	_	0	--	_	_
    4	alle	aller	PRON	PIAT	_	5	NK	_	_
    5	Kekse	keks	NOUN	NN	_	3	OA	_	_
    6	und	und	CONJ	KON	_	3	CD	_	_
    7	Ein	ein	DET	ART	_	8	NK	_	_
    8	Kind	kind	NOUN	NN	_	9	SB	_	_
    9	isst	issen	VERB	VVFIN	_	6	--	_	_
    10	alle	aller	PRON	PIAT	_	11	NK	_	_
    11	Brezeln	brezel	NOUN	NN	_	9	CJ	_	_
    12	.	--	.	$.	_	3	--	_	_




#### `assign.py`

The SemRepAssigner relies on the Condition module to work properly, 
therefore you have to import it first.
Use the heuristic rules in the rules directory as a parameter to create a
SemRepAssigner object. Then read a conll06-formated sentence from a file
and use nltk's parse module to create a DependencyGraph object.
Now call the function assignToDependencyGraph of the SemRepAssigner object
to assign a logical lambda expression to every relevent word in the parsed
sentence. By calling the `get_by_address` function you can access every node
and all its attributes.

Example for the sentence “Eine Taube beißt Peter Müller.” (Leading `>` marks the Python interpreter):

    > import nltk.parse as nlp
    > from montesniere.assign import SemRepAssigner
    > ass = SemRepAssigner.fromfile('rules/heuristic_rules.json')
    > sTaube = open('test/conll/beissende_taube_und_Peter_Mueller.conll').read()
    > dgTaube = nlp.DependencyGraph(sTaube)
    > ass.assignToDependencyGraph(dgTaube)
    > print(dgTaube.get_by_address(3)['semrep'])
    \y x.beissen(x,y)
    > print(dgTaube.get_by_address(3)['semrep'].type)
    <e,<e,t>>


#### `merge.py`

The algorithm merges all logical expressions into one representing the input sentence.
Consequently, you have to use a dependencygraph preprocessed by a SemRepAssigner object
to create a SemMerger object. Then call the getSemantics function of the SemMerger object
to receive the merged logical expression.

Example, using the same sentence as before (Leading `>` marks the shell):

    > lambdaTaube = SemMerger(dgTaube)
    > lambdaTaube.getSemantics()
    exists x.(Taube(x) & beissen(x, Peter_Mueller))


### Rules

The `SemRepAssigner` from the `montesniere.assign` is best created from a `json`
file containing the rules that are to be used. We wrote some heuristic rules
(`rules/heuristic_rules.json`) for dependencyGraphs that contain POS tags
conforming to the
[Stuttgart-Tübingen-Tagset](http://homepage.ruhr-uni-bochum.de/stephen.berman/Korpuslinguistik/Tagsets-STTS.html)
(the ones used in [DWDS](http://dwds.de/))
and dependency tags conforming to the
[TIGER annotation scheme](http://www.ims.uni-stuttgart.de/forschung/ressourcen/korpora/TIGERCorpus/annotation/tiger_scheme-syntax.pdf).
These rules cover very basic German sentences
(notably excluding definite determiners).

You can write your own rules or improve on ours.
The `json` file has to consist of an array of rule objects.
A rules objects has to include three keys:

  * The key `conditions` has to map to an array of strings conforming to the
    syntax of a montesniere.condition.Condition object.
  * The key `semRepPat` has to map to a string interpretable by an
    nltk.sem.logic.LogicParser object. But before that, it is passed to Python
    str.format method. This is so that you can dynamically add the lemma of an
    encountered word to the semantic representation by specifying `{[lemma]}`
  * The key `semSig` has to map to a signature object each key of which should
    be an expression used in the `semRepPat`. The keys have to map to strings
    specifying the types of the respective expressions.

It is recommended to add an explanation to each rule to describe what phenomena
it is concerned with. Otherwise you will quickly get overwhelmed when you add
more rules.

Example rule:

```json
{
    "explanation": "proper name in subject position",
    "conditions": [
        "tag element {NE}",
        "rel element {SB}"
    ],
    "semRepPat": "\\P. P({[lemma]})",
    "semSig": {
        "P": "<e,t>",
        "{[lemma]}": "e"
    }
}
```


### Test suite

 This test suite is based on the English [FraCaS test suite](http://www-nlp.stanford.edu/~wcmac/downloads/).
Both premises and an hypothesis are stored in the testsuite. It's structure is similar to the FraCaS test suit (not yet including downward entailing). Call `testFracas.py` from the commandline,
use `heuristic_rules.json` and `testsuite_text_tags.xml` as arguments. The number of failed and
succesful tests is shown on the commandline.


Example (Leading `>` marks the shell):

    >./testFracas.py ../rules/heuristic_rules.json testsuite_text_tags.xml
    33 out of 39 failed
    IDs of failed tests: 1, 3, 4, 5, 6, 7, 10, 11, 12, 13, 14, 15, 16, 18, 19, 20,
     21, 22, 23, 24, 26, 27, 28, 29, 31, 32, 33, 34, 35, 36, 37, 38, 38

### Add new data
Follow these steps to add new data:

* Parse your sentences first. We recommend using a RBGParser model trained on the TIGER corpus
* Check your parsed data manuelly and correct wrong parses.
* Use `normalize.py` to normalize your sentences in order to avoid unfortunate coordinations of phrases
* Check your data for mistakes manually.
* Add it to our test data.
