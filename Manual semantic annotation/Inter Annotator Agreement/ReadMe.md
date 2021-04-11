Il sistema implementato per il calcolo dell’IAA prevede che una funzione principale MAIN legga riga per riga i due dataset A e B dati in input per ottenere due insiemi Lines_A e Lines_B tali che:
Lines_A = {LineA1, LineA2, … LineAn}
Lines_B = {LineB1, LineB2, … LineBn}
dove line_Ai e line_Bi sono rispettivamente le i-esime righe di A e B e n è il numero totale di righe presenti nei due file.  
Data D come la risorsa che fornisce lo specifico sense inventory con cui viene svolta l’annotazione, la funzione ROW_COMPARISON (Lines_A, Lines_B, D) accede sequenzialmente agli elementi dei due insiemi per confrontare l’i-esimo elemento di Lines_A, ovvero line_Ai, con l’i-esimo elemento di Lines_B, ovvero line_Bi.
Se la riga considerata è una riga di token avente POS appartenente all’insieme delle POS annotabili; allora le due righe presentano un campo apposito, labelD, per conservare l’etichetta semantica attribuita al token sulla base dell’inventario di sensi predisposto dalla risorsa D. Per ogni coppia di righe utili, i campi labelD di line_Ai e line_Bi verranno aggiunti rispettivamente in due insiemi Labels_AD e Labels_BD.
Una volta analizzate tutte le possibili coppie la funzione ROW_COMPARISON restituisce i due insiemi Labels_AD e Labels_BD tali che:
Labels_AD = {label_AD1, label_AD2… label_ADn}
Labels_BD = {label_BD1, label_BD2… label_BDn}
L’〖IIA〗_k^D, ovvero l’inter annotator agreement basato sul coefficiente Kappa di Cohen è calcolato per mezzo della funzione COHEN_KAPPA_SCORE (Labels_AD, Labels_BD) fornita un’apposita libreria python  che prende come parametri gli insiemi Labels_AD, Labels_BD; vengono così restituiti 〖IIA〗_k^PSCe 〖IIA〗_k^IWN.
Il valore finale di Inter Annotator Agreement restituito per le annotazioni A e B è calcolato come:
IAAk = COHEN_KAPPA_SCORE (Labels_APSC ∪ Labels_AIWN, Labels_BPSC ∪ Labels_BIWN)
