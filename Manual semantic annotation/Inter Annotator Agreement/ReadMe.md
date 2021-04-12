Sistema automatico per il calcolo dell’IAA
======
### Descrizione del funzionamento


Una funzione principale `MAIN` legge riga per riga i due dataset annotati semanticamente _A_ e _B_ dati in input per ottenere due insiemi _Lines_A_ e _Lines_B_ tali che:
_Lines_A = {LineA<sup>1</sup> , LineA<sup>2</sup>, … LineA<sup>n</sup>}
Lines_B = {LineB<sup>1</sup>, LineB<sup>2, … LineB<sup>n</sup>}_
dove line_Ai e line_Bi sono rispettivamente le i-esime righe di A e B e n è il numero totale di righe presenti nei due file.

Data D come la risorsa che fornisce lo specifico sense inventory con cui viene svolta l’annotazione, la funzione `ROW_COMPARISON` (Lines_A, Lines_B, D) accede sequenzialmente agli elementi dei due insiemi per confrontare l’i-esimo elemento di Lines_A, ovvero line_Ai, con l’i-esimo elemento di Lines_B, ovvero line_Bi.

Se la riga considerata è una riga di token avente POS appartenente all’insieme delle POS annotabili; allora le due righe presentano un campo apposito, labelD, per conservare l’etichetta semantica attribuita al token sulla base dell’inventario di sensi predisposto dalla risorsa D. Per ogni coppia di righe utili, i campi labelD di line_Ai e line_Bi verranno aggiunti rispettivamente in due insiemi Labels_AD e Labels_BD.
Una volta analizzate tutte le possibili coppie la funzione `ROW_COMPARISON` restituisce i due insiemi Labels_AD e Labels_BD tali che:
Labels_AD = {label_AD1, label_AD2… label_ADn}
Labels_BD = {label_BD1, label_BD2… label_BDn}

L’IAA(k,D), ovvero l’inter annotator agreement basato sul coefficiente Kappa di Cohen è calcolato per mezzo della funzione `COHEN_KAPPA_SCORE` (Labels_AD, Labels_BD) fornita da un’apposita libreria python che prende come parametri gli insiemi Labels_AD, Labels_BD; vengono così restituiti IAA(k,PSC) e IAA(k, IWN).
Il valore finale di Inter Annotator Agreement restituito per le annotazioni A e B è calcolato come:
IAA(k) = COHEN_KAPPA_SCORE (Labels_APSC ∪ Labels_AIWN, Labels_BPSC ∪ Labels_BIWN)
