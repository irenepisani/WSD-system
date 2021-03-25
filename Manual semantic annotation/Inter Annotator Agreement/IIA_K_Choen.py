
# Calcolo dell'Inter-Annotator-Agreement attraverso il coefficente K Choen

# INPUT:  dataset_50_FP_new.conllu dataset_50_IP_new.conllu
# OUPUT: 
'''		 Inter-Tagger-Agreement
		ITA ParoleSimpleClips: 0.8382147838214784
		ITA ItalWordNet: 0.7681564245810056
		ITA: 0.803185604201242'''

import sys
import codecs
from sklearn.metrics import cohen_kappa_score

def split_on_tab (test): #suddivido un testo sul tab creando una lista di elementi 
	test = str(test)
	test_split = test.split("\t")
	return test_split 

# -------- funzione principale di confronto riga per riga
def row_comparison (lines_1,lines_2, k):
	
	ann_1 = []
	ann_2 = []
	pos=["NOUN", "ADJ", "ADV", "VERB"]	#lista delle Part of Speech annotabili 

	#considero una riga alla volta presa dai due file annotati
	for i, j  in zip(lines_1,lines_2):

		# se la riga è una riga di token
		if not i.startswith("#") and not j.startswith("#") and not i.startswith("\n") and not j.startswith("\n"):

			#allora eseguo lo split su ogni tab presente nella riga considerata 
			line_1=split_on_tab(i)	#riga file annotato 1
			line_2=split_on_tab(j)	#riga file annotato 2

			matched_pos=line_1[3] #controllo la pos della riga di token che analizzo 	
			
			if len(line_1)==10 or len(line_2)==10:
				line_1.extend(["_","_"])
				line_2.extend(["_","_"])

			if matched_pos in pos: #se è tra quelle da annotare 

				#salvo l'annotazione semantica trovata nei due file per la stessa riga
				label1 = line_1[k]
				label2 = line_2[k]

				#aggiungo alle liste le etichette
				ann_1.append(label1)
				ann_2.append(label2)
	return ann_1, ann_2
 
def main (file1,file2):

	file1=codecs.open(file1, "r", "utf-8")	#annotazione 1
	file2=codecs.open(file2, "r","utf-8")	#annotazione 2

	#leggo i due file annotati riga per riga
	linefile1= file1.readlines() 
	linefile2=file2.readlines() 

	psc, iwn = 10, 11

	# calcolo il coefficente K di Choen

	ann1_psc, ann2_psc  = row_comparison(linefile1,linefile2, psc)
	K_choen_psc = cohen_kappa_score(ann1_psc, ann2_psc)

	ann1_iwn, ann2_iwn  = row_comparison(linefile1,linefile2, iwn)
	K_choen_iwn = cohen_kappa_score(ann1_iwn, ann2_iwn)

	ann1 = ann1_psc+ann1_iwn
	ann2 = ann2_psc+ann2_iwn
	K_choen = cohen_kappa_score(ann1, ann2)

	print("Inter-Annotator-Agreement: coefficente K di Choen")
	print("Coefficente K di Choen per ParoleSimpleClips: "+str(K_choen_psc))
	print("Coefficente K di Choen per ItalWordNet: "+str(K_choen_iwn))
	print("Coefficente K di Choen: "+str(K_choen))
		
main(sys.argv[1],sys.argv[2])
