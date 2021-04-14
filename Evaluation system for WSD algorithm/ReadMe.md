 Valutazione automatica delle performance degli algoritmi di WSD
====

Sistema automatico per la valutazione
-------
`EvaluationSystem.py` prende in input un annotazione semamtica automatica e una manuale; l'annotazione automatica viene confrontata con quella manuale per ottenere i parametri necessari a calcolare Precision, Recall e F-measure. 

Risultati della valutazione automatica degli algoritmi di WSD
----
La cartella `Performance analysis` contiene:
* La valutazione delle performance dell'algoritmo random: `WSD_random_evaluation.txt`
* La valutazione delle performance dell'algoritmo edit distance: `WSD_editdistance_evaluation.txt`
* La valutazione delle performance dell'algoritmo lesk: `WSD_lesk_evaluation.txt`
* La valutazione delle performance dell'algoritmo extended lesk: `WSD_extendedlesk_evaluation.txt`
* La valutazione delle performance dell'algoritmo semantic relation: `WSD_relation_evaluation.txt`
* La valutazione delle performance dell'algoritmo vector similarity: `WSD_vector_evaluation.txt`

