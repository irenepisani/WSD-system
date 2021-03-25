import pyconll
import sys
import codecs
import re

def split_on_tab (test): #suddivido un testo sul tab creando una lista di elementi 
	test = str(test)
	test_split = test.split("\t")
	return test_split 

# -------- count FP TP FN TN:parametri per valutare il sistema
def count_true_positive (tp, sense_gold, sense_auto):
	if sense_gold!="_" and sense_gold==sense_auto: #se il gold è annotato con lo stesso senso attribuito dal sistema automatico
		tp=tp+1	#incremento di uno i true positive trovati 
	return tp

def count_true_negative (tn, sense_gold, sense_auto):
	if sense_gold=="_" and sense_gold==sense_auto:	#se sia nel gold che nell'automatico non annotato il senso
		tn=tn+1	#incremento di uno i true negative trovati 
	return tn

def count_false_positive (fp, sense_gold, sense_auto):
	if sense_auto!="_" and sense_gold!=sense_auto: #se l'automatico è annotato ma è diverso dal gold
		fp=fp+1	#incremento di uno i false posative trovati
	return fp

def count_false_negative(fn, sense_gold, sense_auto):

	if sense_auto=="_" and sense_auto!=sense_gold: #se il gold non è annotato ma l'auto si 
		fn=fn+1	#incremento di uno i false negative trovati
		print(sense_auto)
		print(sense_gold)
	return fn 

# -------- count FPmissing TPmissing FNmissing :parametri per valutare il tag automatico di missing
def count_true_positive_missing (tpm, sense_gold, sense_auto):
	if "missing" in sense_gold and sense_gold==sense_auto:
		tpm=tpm+1
	return tpm

def count_false_positive_missing (fpm, sense_gold, sense_auto):
	if "missing" in sense_auto and sense_auto!=sense_gold:
		fpm=fpm+1
	if "missing" in sense_gold and sense_auto!="_" and sense_auto!=sense_gold:
		fpm=fpm+1
	return fpm

def count_false_negative_missing (fnm, sense_gold, sense_auto):
	if sense_auto=="_" and "missing" in sense_gold:
		fnm=fnm+1
	return fnm

def row_comparison (lines_gold,lines_auto, k):
	
	#inizializzo variabili utili per il calcolo delle metriche di valutazione 
	tot, tp, fp, tn, fn, tpm, fpm, fnm, = 0, 0, 0, 0, 0, 0, 0, 0

	evaluation_metric={}	# definisco un dizionario per riportare il totale dei casi osservati tipo per tipo
	difference=[]	#definisco una lista per riportare la posizione delle differenze osservate
	
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

				tot = tot + 1 #incremento di uno il totale dei casi considerati 
				#salvo l'annotazione semantica trovata nel gold nell'auto 
				gold = line_gold[k]
				auto = line_auto[k]

				#le confronto per individuare il caso in cui rientrano 
				tp = count_true_positive (tp, gold, auto)
				tn = count_true_negative (tn, gold, auto)
				fp = count_false_positive (fp, gold, auto)
				fn = count_false_negative (fn, gold, auto)
				tpm = count_true_positive_missing (tpm, gold, auto)
				fpm = count_false_positive_missing (fpm, gold, auto)
				fnm = count_false_negative_missing (fnm, gold, auto)

			else:
				#se non è tra le pos richieste puo comunque essere che sia annoata (es. preposizioni di una multiword)
				gold = line_gold[k]
				auto = line_auto[k] 

				#ripeto quanto eseguito prima se e solo se l'annotazione non è vuota in entrambi le parti 
				if gold!="_" or auto!="_":
					tot = tot+1

					tp = count_true_positive (tp, gold, auto)
					fp = count_false_positive (fp, gold, auto)
					fn = count_false_negative (fn, gold, auto)
					tpm = count_true_positive_missing (tpm, gold, auto)
					fpm = count_false_positive_missing (fpm, gold, auto)
					fnm = count_false_negative_missing (fnm, gold, auto)

	#aggiorno vocabolario dei parametri 
	evaluation_metric.update({ "tot": tot})
	evaluation_metric.update({ "tp": tp})
	evaluation_metric.update({ "fp": fp})
	evaluation_metric.update({ "tn": tn})
	evaluation_metric.update({ "fn": fn})
	evaluation_metric.update({ "tpm": tpm})
	evaluation_metric.update({ "fpm": fpm})
	evaluation_metric.update({ "fnm": fnm})

	return evaluation_metric

def get_precision (dictionary):	#calcolo precisin
	tp=dictionary.get("tp")
	fp=dictionary.get("fp")
	precision=tp/(tp+fp)
	return precision

def get_recall (dictionary):	#calcolo recall 
	tp = dictionary.get("tp")
	fn = dictionary.get("fn")
	recall = tp / (tp+fn)
	return recall 

def get_precision_missing (dictionary):	#calcolo precision del tag missing
	tpm=dictionary.get("tpm")
	fpm=dictionary.get("fpm")
	precision_missing=tpm/(tpm+fpm)
	return precision_missing

def get_recall_missing (dictionary):	#calcolo recall del tag missing 
	tpm = dictionary.get("tpm")
	fnm = dictionary.get("fnm")
	recall_missing = tpm / (tpm+fnm)
	return recall_missing

def get_Fmeasure  (p,r):	#calcolo Fmeasure
	Fmeasure = (2*p*r)/(p+r)
	return Fmeasure 

def get_accuracy(dictionary): #calcolo accuracy 
	tot = dictionary.get("tot")
	tp = dictionary.get("tp")
	tn = dictionary.get("tn")
	accuracy = (tp+tn)/ tot
	return accuracy

def get_precisionTOT (dictionary1, dictionary2):	#calcolo precisin
	tp1=dictionary1.get("tp")
	fp1=dictionary1.get("fp")
	tp2=dictionary2.get("tp")
	fp2=dictionary2.get("fp")
	precision=(tp1+tp2)/(tp1+tp2+fp1+fp2)
	return precision

def get_recallTOT (dictionary1, dictionary2):	#calcolo recall 
	tp1 = dictionary1.get("tp")
	fn1 = dictionary1.get("fn")
	tp2 = dictionary2.get("tp")
	fn2 = dictionary2.get("fn")
	recall = (tp1+tp2)/ (tp1+tp2+fn1+fn2)
	return recall 

def get_precision_missingTOT (dictionary1, dictionary2):	#calcolo precision del tag missing
	tpm1=dictionary1.get("tpm")
	fpm1=dictionary1.get("fpm")
	tpm2=dictionary2.get("tpm")
	fpm2=dictionary2.get("fpm")
	precision_missing=(tpm1+tpm2)/(tpm1+tpm2+fpm1+fpm2)
	return precision_missing

def get_recall_missingTOT (dictionary1, dictionary2):	#calcolo recall del tag missing 
	tpm1 = dictionary1.get("tpm")
	fnm1 = dictionary1.get("fnm")
	tpm2 = dictionary2.get("tpm")
	fnm2 = dictionary2.get("fnm")
	recall_missing = (tpm1+tpm2) / (tpm1+tpm2+fnm2+fnm2)
	return recall_missing

def get_FmeasureTOT  (p1,p2,r1,r2):	#calcolo Fmeasure
	Fmeasure = (2*(p1+p2)*(r1+r2))/(p1+p2+r1+r2)
	return Fmeasure 

def get_accuracyTOT(dictionary1, dictionary2): #calcolo accuracy 
	tot1 = dictionary1.get("tot")
	tp1 = dictionary1.get("tp")
	tn1 = dictionary1.get("tn")
	tot2 = dictionary2.get("tot")
	tp2 = dictionary2.get("tp")
	tn2 = dictionary2.get("tn")
	accuracy = (tp1+tn1+tp2+tn2) / (tot1+tot2)
	return accuracy

def main (file1,file2):

	file1=codecs.open(file1, "r", "utf-8")	#annotazione manuale
	file2=codecs.open(file2, "r","utf-8")	#annotazione automatica

	#leggo i due file annotati riga per riga
	linefile1= file1.readlines() 
	linefile2=file2.readlines() 
	

	psc, iwn = 10, 11
	# eseguo funzione principale e ottengo i parametri per il calcolo delle misure di valutazione e lista delle posizioni delle differenze trovate 
	evaluation_metric_dict_psc= row_comparison(linefile1,linefile2, psc)
	evaluation_metric_dict_iwn= row_comparison(linefile1,linefile2, iwn)

	# calcolo misure di valutazione del sistema per PSC
	precision_psc = get_precision(evaluation_metric_dict_psc)
	recall_psc = get_recall(evaluation_metric_dict_psc)
	Fmeasure_psc = get_Fmeasure(precision_psc, recall_psc)
	accuracy_psc = get_accuracy (evaluation_metric_dict_psc)
	precision_missing_psc = get_precision_missing(evaluation_metric_dict_psc)
	recall_missing_psc = get_recall_missing(evaluation_metric_dict_psc)
	Fmeasure_missing_psc = get_Fmeasure(precision_missing_psc, recall_missing_psc)

	# calcolo misure di valutazione del sistema per IWN
	precision_iwn = get_precision(evaluation_metric_dict_iwn)
	recall_iwn = get_recall(evaluation_metric_dict_iwn)
	Fmeasure_iwn = get_Fmeasure(precision_iwn, recall_iwn)
	accuracy_iwn = get_accuracy (evaluation_metric_dict_iwn)
	precision_missing_iwn = get_precision_missing(evaluation_metric_dict_iwn)
	recall_missing_iwn = get_recall_missing(evaluation_metric_dict_iwn)
	Fmeasure_missing_iwn = get_Fmeasure(precision_missing_iwn, recall_missing_iwn)

	# calcolo misure di valutazione del sistema per IWN
	precision = get_precisionTOT(evaluation_metric_dict_psc, evaluation_metric_dict_iwn)
	recall = get_recallTOT(evaluation_metric_dict_psc, evaluation_metric_dict_iwn)
	Fmeasure = get_FmeasureTOT(precision_psc, precision_iwn, recall_psc, recall_iwn)
	accuracy = get_accuracyTOT (evaluation_metric_dict_psc, evaluation_metric_dict_iwn)
	precision_missing = get_precision_missingTOT(evaluation_metric_dict_psc, evaluation_metric_dict_iwn)
	recall_missing = get_recall_missingTOT(evaluation_metric_dict_psc, evaluation_metric_dict_iwn)
	Fmeasure_missing = get_FmeasureTOT(precision_missing_psc, precision_missing_iwn, recall_missing_psc, recall_missing_iwn)
 
	# stampo risultati 

	print("METRICHE DI VALUTAZIONE DEL SISTEMA PER PSC")

	print("Precision: " + str(precision_psc))
	print("Recall: " + str(recall_psc))
	print("F-Measure: " + str(Fmeasure_psc))
	print("Accuracy:" + str(accuracy_psc))
	print("Precision of tag 'missing': " + str(precision_missing_psc))
	print("Recall of tag 'missing': " + str(recall_missing_psc))
	print("F-Measure of tag 'missing': " + str(Fmeasure_missing_psc))
	print("\n")

	print("METRICHE DI VALUTAZIONE DEL SISTEMA per IWN")

	print("Precision: " + str(precision_iwn))
	print("Recall: " + str(recall_iwn))
	print("F-Measure: " + str(Fmeasure_iwn))
	print("Accuracy:" + str(accuracy_iwn))
	print("Precision of tag 'missing': " + str(precision_missing_iwn))
	print("Recall of tag 'missing': " + str(recall_missing_iwn))
	print("F-Measure of tag 'missing': " + str(Fmeasure_missing_iwn))
	print("\n")

	print("METRICHE DI VALUTAZIONE DEL SISTEMA")

	print("Precision: " + str(precision))
	print("Recall: " + str(recall))
	print("F-Measure: " + str(Fmeasure))
	print("Accuracy:" + str(accuracy))
	print("Precision of tag 'missing': " + str(precision_missing))
	print("Recall of tag 'missing': " + str(recall_missing))
	print("F-Measure of tag 'missing': " + str(Fmeasure_missing))
	print("\n")

main(sys.argv[1],sys.argv[2])







