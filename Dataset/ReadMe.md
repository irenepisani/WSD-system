Dataset selezionati nel progetto ELEXIS per il task di WSD
=====

Dataset
---
* `dataset2000wiki.txt`: dataset delle 2000 frasi selezionate per il task di WSD 
* `dataset2000wiki_UDPIPE.conllu`: dataset annotato morfo-sinttaticamente tramite parser UDPIPE (versione intermedia)
* `datasetCorrected.tsv`: dataset annotato morfo-sinttaticamente tramite parser STANZA (versione ufficiale in ELEXIS)in formato tsv compatibile con conllu
* `dataset_50_1_na.conllu`: dataset delle 50 frasi estratte dalla prima metà del documento `dataset2000wiki_UDPIPE.conllu` con il maggiore numero di corrispondenze lessicali nelle risorse lessicografiche di ItalWordNet e ParoleSimpleClips; compatibile con la versione ufficiale del dataset di ELEXIS (*test set* per gli algoritmi di WSD) 
* `dataset_50_1_na.conllu`: dataset delle 50 frasi estratte dalla seconda metà del documento `dataset2000wiki_UDPIPE.conllu` con il maggiore numero di corrispondenze lessicali nelle risorse lessicografiche di ItalWordNet e ParoleSimpleClips; compatibile con la versione ufficiale del dataset di ELEXIS (*test set* per gli algoritmi di WSD) 
* `dataset_100_na.conllu`: dataset delle 100 estratte da `dataset2000wiki_UDPIPE.conllu` con il maggiore numero di corrispondenze lessicali nelle risorse lessicografiche di ItalWordNet e ParoleSimpleClips; compatibile con la versione ufficiale del dataset di ELEXIS (*test set* per gli algoritmi di WSD) 

Strumenti per la gestione e la conversione dei dataset
---
* `convert_tsv2conllu.py`: convertitore automatico di formato da .tsv a .conllu
* `convertnewformat.py`: sistema automatico per rendere la versione intermedia del dataset compatibile con la versione ufficiale
