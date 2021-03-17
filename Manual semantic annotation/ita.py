
# Calcolo dell'Inter-Tagger-Agreement

# INPUT:  dataset_50_FP_new.conllu dataset_50_IP_new.conllu
# OUPUT: 
'''		 Inter-Tagger-Agreement
		ITA ParoleSimpleClips: 0.8382147838214784
		ITA ItalWordNet: 0.7681564245810056
		ITA: 0.803185604201242'''

import sys
import codecs

def split_on_tab (test): #suddivido un testo sul tab creando una lista di elementi 
	test = str(test)
	test_split = test.split("\t")
	return test_split 

# -------- funzione principale di confronto riga per riga
def row_comparison (lines_gold,lines_auto, k):
	
	tot, disaccordo = 0, 0	#inizializzo variabili utili per il calcolo dell'ITA
	evaluation_metric={}	# definisco un dizionario per riportare il totale dei casi osservati
	pos=["NOUN", "ADJ", "ADV", "VERB"]	#lista delle Part of Speech annotabili 

	#considero una riga alla volta presa dai due file annotati
	for i, j  in zip(lines_gold,lines_auto):

		# se la riga è una riga di token
		if not i.startswith("#") and not j.startswith("#") and not i.startswith("\n") and not j.startswith("\n"):

			#allora eseguo lo split su ogni tab presente nella riga considerata 
			line_gold=split_on_tab(i)	#riga file annotato 1
			line_auto=split_on_tab(j)	#riga file annotato 2

			#se le righe non hanno l'annotazione semantica aggiungo due elementi vuoti uno per psc uno per iwn
			if len(line_gold)==10 or len(line_auto)==10:
				line_gold.extend(["_","_"])
				line_auto.extend(["_","_"])

			matched_pos=line_gold[3] #controllo la pos della riga di token che analizzo 	

			if matched_pos in pos: #se è tra quelle da annotare 
				tot = tot + 1 #incremento di uno il totale dei casi considerati 
				#salvo l'annotazione semantica trovata nei due file per la stessa riga
				gold = line_gold[k]
				auto = line_auto[k]
				# se le celle contengono etichette semantiche diverse incremento il disaccordo di uno
				if line_gold[k]!=line_auto[k]: 
					disaccordo = disaccordo+1

			else:	#se non è tra le pos richieste puo essere che il token sia annotato per errore o per un caso particolare
				gold = line_gold[k]
				auto = line_auto[k]
				if gold!="_" or auto!="_":	#se una delle due non è vuota le confronto e incremento di uno i casi considerati
					tot = tot+ 1
					# se le celle contengono etichette semantiche diverse incremento il disaccordo di uno
					if line_gold[k]!=line_auto[k]:	#
						disaccordo = disaccordo + 1

	#aggiorno vocabolario dei parametri 
	evaluation_metric.update({ "tot": tot})
	evaluation_metric.update({ "disaccordo": disaccordo})

	return evaluation_metric

def get_ITA_risorsa (dictionary): #calcolo ITA
	tot = dictionary.get("tot")
	disaccordo = dictionary.get("disaccordo")
	ita = (tot-disaccordo) / tot
	return ita

def get_ITA(dictionary1, dictionary2): #calcolo ITA
	tot1 = dictionary1.get("tot")
	disaccordo1 = dictionary1.get("disaccordo")
	tot2 = dictionary2.get("tot")
	disaccordo2 = dictionary2.get("disaccordo")
	tot = tot1 + tot2
	disaccordo = disaccordo1+disaccordo2
	ita = (tot-disaccordo) / tot
	return ita
 
def main (file1,file2):

	file1=codecs.open(file1, "r", "utf-8")	#annotazione 1
	file2=codecs.open(file2, "r","utf-8")	#annotazione 2

	#leggo i due file annotati riga per riga
	linefile1= file1.readlines() 
	linefile2=file2.readlines() 

	psc, iwn = 10, 11
	# ottengo valori per il calcolo dell'agreeement parallello per le due risorse
	evaluation_metric_dict_psc = row_comparison(linefile1,linefile2, psc)
	evaluation_metric_dict_iwn = row_comparison(linefile1,linefile2, iwn)

	# calcolo dell'ITA per i vari casi
	ITA_psc = get_ITA_risorsa(evaluation_metric_dict_psc)
	ITA_iwn = get_ITA_risorsa(evaluation_metric_dict_iwn)
	ita = get_ITA(evaluation_metric_dict_psc, evaluation_metric_dict_iwn)

	print("Inter-Tagger-Agreement")
	print("ITA ParoleSimpleClips: " + str(ITA_psc))
	print("ITA ItalWordNet: " + str(ITA_iwn))
	print("ITA:"+ str(ita))
		
main(sys.argv[1],sys.argv[2])
