# sistema per il Word Sense Disamiguation

#importo librerie necessarie 
import pyconll
import sys
import codecs
import MySQLdb
import re
import random
import pylev
from googletrans import Translator
import stanza
import spacy

# avvio connessione con MySQL
def start_db_connection():
	connection = MySQLdb.connect(
		host = 'localhost',
		user = 'root',
		passwd = '', #put here password
		port = 3306)
	return connection

#converto i caratteri accententati per i db che non li supportano 
def convert_accents (lemma):
	accents=['à','è','ì','ò','ù']
	NOaccents=['a','e','i','o','u']
	count=-1
	for acc in accents:
		count=count+1
		if lemma.endswith(acc):
			x=accents[count]
			y=NOaccents[count]
			lemma=re.sub(x, y, lemma)+"''"
	return lemma

#converto le Universal Dependecies POS nelle corrispondenti POS dei db 
def pos_converter (udpos, db):
	UD=["ADJ", "ADV", "NOUN", "PROPN", "VERB"]
	PSC=["A","ADV","N","NP","V"]
	IWN=["AG","AV","N","NP","V"]
	conta=-1;
	postag="POSnotvalid"
	for pos in UD:
		conta=conta+1
		if pos==udpos:
			if db=="simplelexicon":
				postag=str(PSC[conta])
			else:
				postag=str(IWN[conta])
	return postag

# se un senso ha definizone nulla, cerco di assegnarli una definizione prendendola da sensi a lui mappati 
# mapping tra IWN_PSC e IWN_WORDNET
def manage_null_def (db, rows, lemma, pos):
	tokenpos = pos_converter(pos,db)
	connection = start_db_connection()

	for row in rows:
		if row[1] == "":	#se la definizione associata al senso è vuota 
			senseID = str(row[0])	#memorrizo l'ID del senso 
			dict_mappedsense = get_mapping_IWN2PSC (senseID)#verifico se è mappato con 
			emptydict = bool(dict_mappedsense) #true se è pieno -false se è vuoto 

			if emptydict == True:
				if db == "simplelexicon":
					sense_searched = dict_mappedsense["synset"]
					query = "SELECT definition FROM NEWIWN.wordsxsensesxsynsets WHERE synsetid='%s' AND lemma ='%s'" % (sense_searched,lemma)
				else: 
					sense_searched = dict_mappedsense["usem"]
					query = "SELECT definition FROM simplelexicon.usem WHERE idUsem ='%s'" % sense_searched
				
				connection=start_db_connection()
				connection.query(query)
				r = connection.store_result()
				rows_ = r.fetch_row(maxrows=0)
				if len(rows_)>0:
					row[1]=rows_[0][0]#associo nuova def al senso di partenza

	for row in rows:
		if row[1]=="":
			if db == "NEWIWN":
				synset_IT = str(row[0])
				new_def = str(row[1])
				query = "SELECT  synsetwn30def FROM IWNMAPDB.wn15wn30 WHERE synsetwn15id = ANY (SELECT synset2id FROM IWNMAPDB.iwn2wn15ililinks WHERE synset1id='%s' and pos='%s')  and synsetwn15pos='%s' " % (synset_IT, tokenpos, tokenpos)
				connection.query(query)
				r=connection.store_result()
				results = r.fetch_row(maxrows=0)
				results = [list (x) for x in results]
				for res in results:
					def_IT= res[0]
					new_def = new_def +" "+def_IT
				row[1]=new_def #associo nuova def al senso di partenza
	return rows

def get_mapping_IWN2PSC (senso):
	dict_mapping={}
	connection=start_db_connection()
	query = "SELECT synset1id, word2id FROM IWNMAPDB.iwn2psc WHERE synset1id='%s' OR word2id='%s'" % (senso, senso)
	connection.query(query)
	r = connection.store_result()
	rows = r.fetch_row(maxrows=0)
	if len(rows)>0:
		for row in rows:
			synset=str(row[0])
			usem=str(row[1])
			dict_mapping["synset"] = synset
			dict_mapping["usem"] = usem 
	return dict_mapping

def translate_EN2IT (en_str): #traduttore inglese-italiano di una stringa
	translator = Translator()
	result = translator.translate(en_str, src='en', dest='it')
	it_str = result.text
	return it_str


def get_iwnsensefromsynset(synset,lemma,pos): #recupero il senseID dato un certo synsetID
	pos = pos_converter(pos, "NEWIWN")
	connection = start_db_connection()
	query = "SELECT senseID FROM NEWIWN.wordsxsensesxsynsets WHERE synsetID= '%s' and lemma = '%s' and pos = '%s' " % (synset, lemma, pos)
	connection.query(query)
	r=connection.store_result()
	rows = r.fetch_row(maxrows=0)
	for row in rows:
		for r in row:
			return r

#per ogni senso calcolo l'edit distance tra la sua glossa e il contesto
def count_edithdistance(sentence, list_definition): 
	for item in list_definition:
		ID_sense = item[0]
		def_sense = item[1]
		if ID_sense!="missing":
			edithdistance=pylev.wf_levenshtein(def_sense, sentence)
		else:
			edithdistance=""
		item.append(edithdistance)
	return list_definition

def min_edithdistance (lista): #trovo il senso la cui definizione ha edit distance minore con il contesto
	lista_ED=[]
	for item in lista:
		var = item[2]
		lista_ED.append(var)
	min_ED = min(lista_ED)
	for item in lista:
		if item[2]==min_ED:
			usem=item[0]
	return usem 


def lemmatization (frase): #lemmatizzazione di una stringa di testo tramite parser stanza
	frase_lemm=""
	poslist = ["NOUN","ADJ","ADV","VERB"]
	if not frase == None:
		nlp = stanza.Pipeline(lang='it', processors='tokenize,mwt,pos,lemma')
		doc = nlp(frase)
		for sent in doc.sentences:
			for word in sent.words:
				if word.upos in poslist:
					wordlemma = word.lemma
					if word.lemma == None:
						wordlemma = word
					frase_lemm = frase_lemm+str(wordlemma)+" "
	return frase_lemm

def split_on_space (test): #suddivido un testo sugli spazi creando una lista di elementi 
	test = str(test)
	test_split = test.split()
	return test_split 


#---------------- WSD MAPPING --------------
def get_mapped_sense_def (db, lemma, pos):
	# ottengo la lista dei possibili sensi e le relative glosse dei sensi del lemma 

	connection = start_db_connection()
	if db == "simplelexicon":
		correctlemma = convert_accents(lemma)
		pos = pos_converter(pos,db)
		query = "SELECT idusem, definition FROM simplelexicon.usem WHERE naming='%s' and pos='%s'" % (correctlemma, pos)
	else:
		pos = pos_converter(pos,db)
		query = "SELECT synsetid, definition FROM NEWIWN.wordsxsensesxsynsets WHERE lemma='%s' and pos='%s'" % (lemma, pos)
	connection.query(query)
	r = connection.store_result()
	rows = r.fetch_row(maxrows=0)
	list_rows = [list(x) for x in rows]
	isempty = bool(list_rows)
	if isempty == False:
		missing = ["missing", ""]
		list_rows.append(missing)
	for row in list_rows:
		if row[1] == None:
			row[1] = ""
	return list_rows

def verify_mapping(rows):
	lista_return = []
	for element in rows:
		senso = element[0]

		connection=start_db_connection()
		query = "SELECT synset1id, word2id FROM IWNMAPDB.iwn2psc WHERE synset1id='%s' OR word2id='%s'" % (senso, senso)
		connection.query(query)
		r = connection.store_result()
		risposta = r.fetch_row(maxrows=0)
		if len(risposta)>0:
			element.append(True)
		else:
			element.append(False)
	
	for element in rows: 
		if element[2]==True:
			lista_return.append(element)
	
	return lista_return


def WSD_mapping(tokenlemma, tokenpos, text_sentence):

	db="simplelexicon"
	simplerows = get_mapped_sense_def (db,tokenlemma,tokenpos)
	new_simplerows = manage_null_def(db, simplerows, tokenlemma, tokenpos)
	useful_simplerows = verify_mapping (new_simplerows)
	if len(useful_simplerows)>0:
		usem_list=count_edithdistance(text_sentence,useful_simplerows)
		usem = str(min_edithdistance(usem_list))
	else: 
		usem = "None"

	db="NEWIWN"
	iwnrows=get_mapped_sense_def (db, tokenlemma,tokenpos)
	new_iwnrows = manage_null_def(db, iwnrows, tokenlemma, tokenpos)
	useful_iwnrows = verify_mapping (new_iwnrows)
	if len(useful_iwnrows)>0:
		synset_list=count_edithdistance(text_sentence,useful_iwnrows)
		synset = str(min_edithdistance(synset_list))
	else: 
		synset="None"
		sense="None"
	if synset!="missing" and synset!="None":
		sense=get_iwnsensefromsynset(synset, tokenlemma, tokenpos)
		sense=str(sense)
	else:
		sense="missing"	
	return usem, synset, sense



#-------------------- GESTIONE DELLE MULTIWORD DI IWN -------------

#lemmatizzo una stringa di testo tramite stanza
def sentence_lemmatization (frase):
	nlp = stanza.Pipeline(lang='it', processors='tokenize,mwt,pos,lemma')
	doc = nlp(frase)
	frase_lemm=""
	for sent in doc.sentences:
		for word in sent.words:
			if word.lemma!=None:
				wordlemma= word.lemma
			else:
				wordlemma=word
			frase_lemm=frase_lemm+str(wordlemma)+" "
	return frase_lemm

#dato un lemma, controllo se nel db siano disponibili delle multiword contenenti quel lemma
def get_possible_MW (lemma):
	lista_maybe_MW=[] #inizializzo una lista di di possibili mw
	connection=start_db_connection()
	trasformedlemma=str("%"+lemma+"%") #trasformo il lemma per non cercare la corrispondenza esatta nel db
	#cerco lemma, synsetid, sense id della mw contenente il lemma (non cerco corrispondenze esatte e espressioni che lo contengano)
	query = "SELECT lemma, synsetid, senseid FROM NEWIWN.wordsxsensesxsynsets WHERE lemma LIKE '%s' AND NOT lemma='%s'" % (trasformedlemma,lemma) 
	connection.query(query)
	r=connection.store_result()
	rows = r.fetch_row(maxrows=0) #gestisco il risultato della query
	if len(rows)>0:
		for row in rows:
			var_lemma = row[0] #per ogni lemma 
			var_MW_lemma = "^(.*[\s|_]){0,1}"+lemma+"([\s|_].*$){0,1}$"
			x=re.search(var_MW_lemma, var_lemma) #controllo che sia un mw 
			#(es. se sto cercancando le mw che contengono il lemma "unita'" dovrò escludere righe come "immunita'" ma conservare "unita' di misura" o "unita' perfiferica")
			if x: #se lo aggiungo la riga in esame alla liste delle possibili mw
				lista_maybe_MW.append(row)
	return lista_maybe_MW #lista di tutte le possibili MultiWord che contengono il lemma dato in input 

#controllo che la multiword di quel lemma trovata sia nella frase
def get_certain_MW (tokenid, frase_lemm, possible_MW):
	lista_return=[]
	lista_MW = [list(x) for x in possible_MW]
	index_lemma=int(tokenid)-1
	for element in lista_MW:
		mw_=element[0].replace("_", " ")
		mw= sentence_lemmatization(mw_)
		x = re.search(mw, frase_lemm)
		if x:	
			frase = frase_lemm.split()
			mw = mw.split() 
			i = 0
			#restiuisco l'id del senso della multiword solo se è la multiword osservata ricorre nella frase
			for i in range(len(frase)):
				if frase[i] == mw[0] and frase[i:i+len(mw)] == mw:
					if index_lemma in range(i, i+len(mw)):
						lista_return.append(element)					
	if len(lista_return)>=1 :
		lista_return = lista_return[0]
	return lista_return

# ---------- GESTIONE DEI RISULTATI -----------

#se il token è una multiword attribuisco gli ID dei sensi della multiword
def mergeresult (listaMW, lista):
	for x in listaMW:
		x.insert(0, True)
	for y in lista:
		y.insert(0, False)
	for element in listaMW:
		tokenid = element[1]
		for item in lista: 
			i = lista.index(item)
			if item[1] == tokenid:
				lista[i] = [element[0], item[1], item[2], element[2], element[3], element[4]]
	return lista

#restituisco in output un nuovo file annotato semanticamente
def get_result (oldfile, lista, numfrase):
	frase=[]
	with open('WSD_mapping.conllu', 'a') as outfile, open(oldfile, 'r', encoding='utf-8') as infile:
		a = [0]
		lines = infile.readlines()
		for j in range(0,len(lines)):
			if lines[j] == "\n":
				a.append(j)
		lenA = len(a)
		if lenA-numfrase == 1:
			for y in range(a[numfrase],len(lines)):
				line = lines[y]
				frase.append(line)
		else:
			for y in range(a[numfrase],a[numfrase+1]):
				line = lines[y]
				frase.append(line)
		for line in frase:
			for element in lista:
				if line.startswith(str(element[1])+"\t"):
					line = line.replace("\n", "")

					if element[0] == False:
						line = line +"\tusemID:"+element[2]+"\tsynsetID:"+str(element[3])+";senseID:"+str(element[4])+"\n"
					else:
						line = line +"\tusemID:"+element[2]+"\tMW["+str(element[5])+"]-"+"synsetID:"+str(element[3])+";senseID:"+str(element[4])+"\n"
			outfile.writelines(line)

# ----------------------- FUNZIONE PRINCIPALE -----------------------------
def main(file):

	fileconllu=pyconll.load_from_file(file) #utilizzo pyconll per aprire il file in input
	
	pos = ["NOUN","ADJ","ADV","VERB"] #lista delle pos da annotare semanticamente
	num = -1 #variabile per il conteggio delle frasi

	for sentence in fileconllu: #per ogni frase nel file
		num = num + 1
		list_forsenses = []
		list_forsensesMW = []
		text_sentence=str(sentence.text)
		lemmatized_sentence = lemmatization(text_sentence)
		lemmatized_sentenceMW = sentence_lemmatization(text_sentence)
		countMW=-1
		synsetprec = None
		senseprec = None
		
		for token in sentence:	#per ogni token nella frase
			if str(token.upos) in pos: #se la pos del token è tra quelle annotabili 
				infotoken = []	#creo una lista per aggiungere in seguito le informazioni semantiche 
				infotokenMW = []

				tokenlemma = str(token.lemma)	#salvo lemma del token
				tokenid = str(token.id)	#salvo id del token 
				tokenpos = str(token.upos) #salvo pos del token

				#----- CHOOSE ONE METHOD ---------
				usem, synset, sense = WSD_mapping(tokenlemma, tokenpos, text_sentence)
				#usem, synset, sense = WSD_editdistance(tokenlemma, tokenpos, text_sentence)
				#usem, synset, sense = WSD_lesk(tokenlemma, tokenpos, lemmatized_sentence, text_sentence)
				#usem, synset, sense = WSD_extendedlesk(tokenlemma, tokenpos, lemmatized_sentence, text_sentence)
				#usem, synset, sense = WSD_vectorsimilarity(tokenlemma, tokenpos, text_sentence)
				#usem, synset, sense = WSD_relation(tokenlemma, tokenpos, lemmatized_sentence)

				#salvo informazioni utili per stampare l'output 
				infotoken.append(tokenid)
				infotoken.append(usem)
				infotoken.append(synset)
				infotoken.append(sense)
				list_forsenses.append(infotoken)

				possible_MW = get_possible_MW(tokenlemma)
				if len(possible_MW)>0:
					certain_MW = get_certain_MW(tokenid, lemmatized_sentenceMW, possible_MW)
					if len(certain_MW)>0:
						synsetMW = certain_MW[1]
						senseMW = certain_MW[2]
						infotokenMW.append(tokenid)
						infotokenMW.append(synsetMW)
						infotokenMW.append(senseMW)

						if synsetMW != synsetprec and senseMW!= senseprec:
							countMW = countMW+1
							synsetprec = synsetMW
							senseprec = senseMW
						infotokenMW.append(countMW)
						list_forsensesMW.append(infotokenMW)
					else:
						synetprec = None
						senseprec = None
				else:
					synetprec = None
					senseprec = None
		
		result = mergeresult(list_forsensesMW,list_forsenses)
		get_result (file, list_forsenses, num)
		#restituisco un nuovo file contenente per ogni token annotabile anche le informazioni semantiche 

main(sys.argv[1])
