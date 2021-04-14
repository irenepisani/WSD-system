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

def count_false_positive (fp, sense_gold, sense_auto):
	if sense_gold!="_" and sense_auto!="_" and sense_gold!=sense_auto: #se l'automatico è annotato ma è diverso dal gold
		fp=fp+1	#incremento di uno i false posative trovati
	return fp

def count_false_negative(fn, sense_gold, sense_auto):
	if sense_auto=="_" and sense_auto!=sense_gold: #se il gold non è annotato ma l'auto si 
		fn=fn+1	#incremento di uno i false negative trovati
	return fn 

# -------- count FPmissing TPmissing FNmissing :parametri per valutare il tag automatico di missing
def count_attested_missing (tpm, sense_gold, sense_auto):
	if "missing" in sense_gold and "missing" in sense_auto and sense_gold==sense_auto:
		tpm=tpm+1
	return tpm

def count_auto_missing (fpm, sense_gold, sense_auto):
	if "missing" in sense_auto:
		fpm=fpm+1
	return fpm

def count_gold_missing (fnm, sense_gold, sense_auto):
	if "missing" in sense_gold:
		fnm=fnm+1
	return fnm

def count_true_positive_mw (tpmw, sense_gold, sense_auto):
	if "MW" in sense_gold and "MW" in sense_auto and sense_gold==sense_auto:
		tpmw=tpmw+1
	return tpmw

def count_false_positive_mw (fpmw, sense_gold, sense_auto):
	if "MW" in sense_auto and "MW" not in sense_gold:
		fpmw=fpmw+1
	return fpmw

def count_false_negative_mw (fnmw, sense_gold, sense_auto):
	if "MW" in sense_gold and "MW" not in sense_auto:
		fnmw=fnmw+1
	return fnmw

def row_comparison (lines_gold,lines_auto, k):
	
	#inizializzo variabili utili per il calcolo delle metriche di valutazione 
	tp, fp, fn, tpm, fpm, fnm, tpmw, fpmw, fnmw = 0, 0, 0, 0, 0, 0, 0, 0, 0

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

				#salvo l'annotazione semantica trovata nel gold nell'auto 
				gold = line_gold[k]
				auto = line_auto[k]

				#le confronto per individuare il caso in cui rientrano 
				tp = count_true_positive (tp, gold, auto)
				fp = count_false_positive (fp, gold, auto)
				fn = count_false_negative (fn, gold, auto)
				tpm = count_attested_missing (tpm, gold, auto)
				fpm = count_auto_missing (fpm, gold, auto)
				fnm = count_gold_missing (fnm, gold, auto)
				tpmw = count_true_positive_mw (tpmw, gold, auto)
				fpmw = count_false_positive_mw (fpmw, gold, auto)
				fnmw = count_false_negative_mw (fnmw, gold, auto)

	#aggiorno vocabolario dei parametri 
	evaluation_metric.update({ "tp": tp})
	evaluation_metric.update({ "fp": fp})
	evaluation_metric.update({ "fn": fn})
	evaluation_metric.update({ "tpm": tpm})
	evaluation_metric.update({ "fpm": fpm})
	evaluation_metric.update({ "fnm": fnm})
	evaluation_metric.update({ "tpmw": tpmw})
	evaluation_metric.update({ "fpmw": fpmw})
	evaluation_metric.update({ "fnmw": fnmw})

	return evaluation_metric

def get_precision (tp, fp):	#calcolo precisin
	precision=tp/(tp+fp)
	return precision

def get_recall (tp, fn):	#calcolo recall 
	recall = tp / (tp+fn)
	return recall 

def get_Fmeasure  (p,r):	#calcolo Fmeasure
	Fmeasure = (2*p*r)/(p+r)
	return Fmeasure 

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

def get_NILP (attested, totauto): #calcolo NIL Precision
	nilp = attested/totauto
	return nilp

def get_NILR (attested, totgold): #calcolo NIL Recall
	nilp = attested/totgold
	return nilp

def get_NILPtot (attested1,attested2, totauto1, totauto2):
	nilp = (attested1+attested2)/(totauto1+totauto2)
	return nilp

def get_NILRtot (attested1,attested2, totgold1, totgold2):
	nilp = (attested1+attested2)/(totgold1+totgold2)
	return nilp

def get_precisionMWTOT (dictionary1, dictionary2):	#calcolo precision del tag missing
	tpm1=dictionary1.get("tpmw")
	fpm1=dictionary1.get("fpmw")
	tpm2=dictionary2.get("tpmw")
	fpm2=dictionary2.get("fpmw")
	precision_missing=(tpm1+tpm2)/(tpm1+tpm2+fpm1+fpm2)
	return precision_missing

def get_recallMWTOT (dictionary1, dictionary2):	#calcolo recall del tag missing 
	tpm1 = dictionary1.get("tpmw")
	fnm1 = dictionary1.get("fnmw")
	tpm2 = dictionary2.get("tpmw")
	fnm2 = dictionary2.get("fnmw")

	recall_missing = (tpm1+tpm2) / (tpm1+tpm2+fnm1+fnm2)
	return recall_missing
	
def main (file1,file2):

	file1=codecs.open(file1, "r", "utf-8")	#annotazione manuale
	file2=codecs.open(file2, "r","utf-8")	#annotazione automatica

	#leggo i due file annotati riga per riga
	linefile1= file1.readlines() 
	linefile2=file2.readlines() 
	

	psc, iwn = 10, 11
	# eseguo funzione principale e ottengo i parametri per il calcolo delle misure di valutazione e lista delle posizioni delle differenze trovate 
	evaluation_psc= row_comparison(linefile1,linefile2, psc)
	evaluation_iwn= row_comparison(linefile1,linefile2, iwn)
	print(evaluation_psc)
	print(evaluation_iwn)

	# calcolo misure di valutazione del sistema per PSC
	precision_psc = get_precision(evaluation_psc.get("tp"), evaluation_psc.get("fp"))
	recall_psc = get_recall(evaluation_psc.get("tp"), evaluation_psc.get("fn"))
	Fmeasure_psc = get_Fmeasure(precision_psc, recall_psc)
	NIL_P_missingPSC = get_NILP (evaluation_psc.get("tpm"), evaluation_psc.get("fpm"))
	NIL_R_missingPSC = get_NILR (evaluation_psc.get("tpm"), evaluation_psc.get("fnm"))
	

	# calcolo misure di valutazione del sistema per IWN
	precision_iwn = get_precision(evaluation_iwn.get("tp"), evaluation_iwn.get("fp"))
	recall_iwn = get_recall(evaluation_iwn.get("tp"), evaluation_iwn.get("fn"))
	Fmeasure_iwn = get_Fmeasure(precision_iwn, recall_iwn)
	precision_mw_iwn = get_precision(evaluation_iwn.get("tpmw"), evaluation_iwn.get("fpmw"))
	recall_mw_iwn = get_recall(evaluation_iwn.get("tpmw"), evaluation_iwn.get("fnmw"))
	Fmeasure_mw_iwn = get_Fmeasure(precision_mw_iwn, recall_mw_iwn)
	NIL_P_missingIWN = get_NILP (evaluation_iwn.get("tpm"), evaluation_iwn.get("fpm"))
	NIL_R_missingIWN = get_NILR (evaluation_iwn.get("tpm"), evaluation_iwn.get("fnm"))

	# calcolo misure di valutazione del sistema 
	precision = get_precisionTOT(evaluation_psc, evaluation_iwn)
	recall = get_recallTOT(evaluation_psc, evaluation_iwn)
	Fmeasure = get_Fmeasure(precision, recall)
	NIL_P_missing = get_NILPtot (evaluation_iwn.get("tpm"), evaluation_psc.get("tpm"), evaluation_iwn.get("fpm"), evaluation_psc.get("fpm"))
	NIL_R_missing = get_NILRtot (evaluation_iwn.get("tpm"), evaluation_psc.get("tpm"), evaluation_iwn.get("fnm"), evaluation_psc.get("fnm"))
	precision_mw_ = get_precisionMWTOT(evaluation_iwn, evaluation_psc)
	recall_mw_ = get_recallMWTOT(evaluation_iwn, evaluation_psc)
	Fmeasure_mw_ = get_Fmeasure(precision_mw_, recall_mw_)
 
	# stampo risultati 

	print("METRICHE DI VALUTAZIONE DEL SISTEMA PER PSC")
	print("Precision: " + str(precision_psc))
	print("Recall: " + str(recall_psc))
	print("F-Measure: " + str(Fmeasure_psc))
	print("NIL Precision of tag 'missing': " + str(NIL_P_missingPSC))
	print("NIL Recall of tag 'missing': " + str(NIL_R_missingPSC))
	print("\n")

	print("METRICHE DI VALUTAZIONE DEL SISTEMA per IWN")
	print("Precision: " + str(precision_iwn))
	print("Recall: " + str(recall_iwn))
	print("F-Measure: " + str(Fmeasure_iwn))
	print("NILPrecision of tag 'missing': " + str(NIL_P_missingIWN))
	print("NILRecall of tag 'missing': " + str(NIL_R_missingIWN))
	print("Precision of tag 'MW': " + str(precision_mw_iwn))
	print("Recall of tag 'MW': " + str(recall_mw_iwn))
	print("F-Measure of tag 'MW': " + str(Fmeasure_mw_iwn))
	print("\n")

	print("METRICHE DI VALUTAZIONE DEL SISTEMA")
	print("Precision: " + str(precision))
	print("Recall: " + str(recall))
	print("F-Measure: " + str(Fmeasure))
	print("NIL Precision of tag 'missing': " + str(NIL_P_missing))
	print("NIL Recall of tag 'missing': " + str(NIL_R_missing))
	print("Precision of tag 'MW': " + str(precision_mw_))
	print("Recall of tag 'MW': " + str(recall_mw_))
	print("F-Measure of tag 'MW': " + str(Fmeasure_mw_))
	print("\n")

main(sys.argv[1],sys.argv[2])
