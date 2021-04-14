Baseline per il Word Sense Disambiguation
=======

Il sistema automatico `WSD_system.py` incorpora 6 diversi possibili algoritmi di WSD
#####
  
* Random baseline: il senso corretto di una parola target è selezionato casualmente
* Edit Distance baseline: il senso corretto di una parola target è identificato nel senso avente minore Edit Distance tra la sua glossa e il contesto della parola target
* Lesk baseline: il senso corretto di una parola target è identificato nel senso avente il maggior numero di parole in comune tra la sua glossa e il contesto della parola target
* Extended Lesk baseline: il senso corretto di una parola target è identificato nel senso avente il maggior numero di parole in comune tra la sua glossa e il suo esempio da un lato e il contesto della parola target dall'altro
* Semantic Relations baseline: il senso corretto di una parola target è identificato nel senso avente il maggior numero di parole aventi senso in relazione semantica con il senso candidato che ricorrono nel contesto della parola target 
* Vector Similarity baseline: il senso corretto di una parola target è identificato nel senso avente la maggiore similarità vettoriale tra il vettore della sua glossa  e il vettore del contesto della parola target

Sense inventory
####
Come sense inventory si è fatto uso delle basi di conoscenza lessico semantica ItalWordNet e ParoleSimpleClips
