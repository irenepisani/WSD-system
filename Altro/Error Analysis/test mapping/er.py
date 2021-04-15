import sys
import codecs
import re

def split_on_tab (test): #suddivido un testo sul tab creando una lista di elementi 
	test = str(test)
	test_split = test.split("\t")
	return test_split 

# -------- count FP TP FN TN:parametri per valutare il sistema
def count_true_positive (tp, sense_gold, sense_auto):
	if sense_gold!="_" and sense_auto!="_" and sense_gold==sense_auto: #se il gold è annotato con lo stesso senso attribuito dal sistema automatico
		tp=tp+1	#incremento di uno i true positive trovati 
	return tp


def row_comparison (lines_gold,lines_auto, k):
	
	#inizializzo variabili utili per il calcolo delle metriche di valutazione 
	tp, tot =0, 0

	evaluation_metric={}	# definisco un dizionario per riportare il totale dei casi osservati tipo per tipo
	
	#lista delle Part of Speech da annotare presenti nel corpus 
	pos=["NOUN", "ADJ", "ADV", "VERB"]

	#prendo una frase alla volta con stesso indice
	for i, j  in zip(lines_gold,lines_auto):


		# se la riga è una riga di token
		if not i.startswith("#") and not j.startswith("#") and not i.startswith("\n") and not j.startswith("\n"):

			#allora eseguo lo split su ogni tab presente nella riga considerata 
			line_gold=split_on_tab(i)	#riga del gold standard 
			line_auto=split_on_tab(j)	#riga corrispondente dell'annotazione automatica

			#se le righe non hanno l'annotazione semantica aggiungo due elementi vuoti uno per psc uno per iwn
			if len(line_gold)==10:
				line_gold.extend(["_","_"])
			if  len(line_auto)==10:	
				line_auto.extend(["_","_"])
			if len(line_gold)==11:
				line_gold.extend(["_"])	
			if len(line_gold)==11:
				line_gold.extend(["_"])	

			matched_pos=line_gold[3] #controllo la pos della riga di token che analizzo 
			if matched_pos in pos: #se è tra quelle da annotare 
				print(line_gold)
				print(line_auto)

				tot = tot +1
				#salvo l'annotazione semantica trovata nel gold nell'auto 
				gold = line_gold[k]
				auto = line_auto[k]

				#le confronto per individuare il caso in cui rientrano 
				tp = count_true_positive (tp, gold, auto)

	return tp, tot



def main (file1,file2):

	file1=codecs.open(file1, "r", "utf-8")	#annotazione manuale
	file2=codecs.open(file2, "r","utf-8")	#annotazione automatica

	#leggo i due file annotati riga per riga
	linefile1= file1.readlines() 
	linefile2=file2.readlines() 
	

	psc, iwn = 10, 11
	# eseguo funzione principale e ottengo i parametri per il calcolo delle misure di valutazione e lista delle posizioni delle differenze trovate 
	tp_psc, tot_psc = row_comparison(linefile1,linefile2, psc)

	tp_iwn, tot_iwn= row_comparison(linefile1,linefile2, iwn)

	print(tp_psc)
	print(tot_psc)
	print(tp_iwn)
	print(tot_iwn)
	print(tp_psc+tp_iwn)
	print(tot_psc+tot_iwn)





main(sys.argv[1],sys.argv[2])







