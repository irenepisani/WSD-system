# sistema WSD - scelta random di un senso

#importo librerie necessarie 
import pyconll
import sys
import codecs
import MySQLdb
import re
import pylev
from googletrans import Translator
import stanza

# avvio connessione con i database MySQL (ItalWordNet e Simple)
def start_db_connection():
	connection = MySQLdb.connect(
		host = 'localhost',
		user = 'root',
		passwd = 'elexis2021',
		port = 3306)
	return connection

#converto i caratteri accententati per i db che non li supportano 
def convert_accents (lemma):
	accents = ['à','è','ì','ò','ù']
	NOaccents = ['a','e','i','o','u']
	count = -1
	for acc in accents:
		count = count+1
		if lemma.endswith(acc):
			x = accents[count]
			y = NOaccents[count]
			lemma = re.sub(x, y, lemma)+"''"
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

# dato un lemma e la sua POS ottengo la lista di coppie (senso - definizione) disponibili in quel db per il dato lemma 
def get_sense_and_definition (db, lemma, pos):
	info_sense=[]
	connection=start_db_connection()

	if db=="simplelexicon":
		correctlemma=convert_accents(lemma)
		pos=pos_converter(pos,db)
		query = "SELECT idusem, definition FROM simplelexicon.usem WHERE naming='%s' and pos='%s'" % (correctlemma, pos)
	else:
		pos=pos_converter(pos,db)
		query = "SELECT synsetid, definition FROM NEWIWN.wordsxsensesxsynsets WHERE lemma='%s' and pos='%s'" % (lemma, pos)

	connection.query(query)
	r=connection.store_result()
	rows = r.fetch_row(maxrows=0)
	list_rows = [list(x) for x in rows]
	isempty = bool(list_rows)	#se nessun senso è disponibile per quel lemma marco con il tag missing
	if isempty == False:
		missing = ["missing", ""]
		list_rows.append(missing)
	for row in list_rows:
		if row[1]==None:
			row[1] = ""
	return list_rows

#given a sense for which a definition is not available, try to assign it by looking for a mapping with the other db or, for iwn, with English 
def manage_null_def (db, rows, lemma, pos):
	
	tokenpos=pos_converter(pos,db)
	connection=start_db_connection()

	for row in rows:
		if row[1]=="":	#se la definizione associata al senso è vuota 
			senseID = str(row[0])	#memorrizo l'ID del senso 
			dict_mappedsense = get_mapping_IWN2PSC (senseID) #verifico se è mappato con l'altro db
			emptydict = bool(dict_mappedsense) #true se è pieno -false se è vuoto 

			if emptydict == True:	#se è mappato prendo la definizione del senso con cui è mappato 
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
					row[1]=rows_[0][0] #attribuisco la nuova definizione trovata al senso di partenza
	
	for row in rows:
		if row[1]=="": #se la definizione è ancora vuota e sto guardando ai sensi di IWN
			if db == "NEWIWN":
				synset_IT = str(row[0])
				new_def = str(row[1])
				#recupero il mapping con l'inglese e prendo la definizione del senso inglese mappato 
				query = "SELECT  synsetwn30def FROM IWNMAPDB.wn15wn30 WHERE synsetwn15id = ANY (SELECT synset2id FROM IWNMAPDB.iwn2wn15ililinks WHERE synset1id='%s' and pos='%s')  and synsetwn15pos='%s' " % (synset_IT, tokenpos, tokenpos)
				connection.query(query)
				r=connection.store_result()
				results = r.fetch_row(maxrows=0)
				results = [list (x) for x in results]
				for res in results:
					def_IT= translate_EN2IT (res[0]) #traduco la nuova definizione
					new_def = new_def +" "+def_IT
				row[1]=new_def #associo la nuova definizone al senso di partenza

	return rows

# dato un senso estratto da un db controllo se è mappato con un senso di un altro db, se lo è restituisco un dizionario contenente il mapping {synset:"xx";usem:"yy"}
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

def translate_EN2IT (en_str): #traduttore da inglese a italiano
	translator = Translator()
	result = translator.translate(en_str, src='en', dest='it')
	it_str = result.text
	return it_str


def get_iwnsensefromsynset(synset,lemma,pos): #dato lemma pos e synsetID, recupero il senseID corrispondente
	pos=pos_converter(pos, "NEWIWN")
	connection=start_db_connection()
	query = "SELECT senseID FROM NEWIWN.wordsxsensesxsynsets WHERE synsetID= '%s' and lemma = '%s' and pos = '%s' " % (synset, lemma, pos)
	connection.query(query)
	r=connection.store_result()
	rows = r.fetch_row(maxrows=0)
	for row in rows:
		for r in row:
			return r

#per ogni definizione del senso calcolo l'editdistance tra definizione e frase di contesto
def list_edithdistance(sentence, list_definition):
	for item in list_definition:
		ID_sense=item[0]
		def_sense= item[1]
		if ID_sense!="missing":
			edithdistance=pylev.wf_levenshtein(def_sense, sentence)
			#edithdistance=pylev.damerau_levenshtein(str1,str2)
		else:
			edithdistance=""
		item.append(edithdistance)
	return list_definition

#trovo per ogni lemma il senso con ED tra def e contesto minore
def min_edithdistance (lista):
	lista_ED=[]
	for item in lista:
		var = item[2]
		lista_ED.append(var)
	min_ED = min(lista_ED)
	for item in lista:
		if item[2]==min_ED:
			sense=item[0]
	return sense 

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

def sentence_lemmatization (frase):
	#lemmatizzo una stringa di testo tramite stanza
	nlp = stanza.Pipeline(lang='it', processors='tokenize,mwt,pos,lemma')
	doc = nlp(frase)
	frase_lemm=""
	for sent in doc.sentences:
		for word in sent.words:
			print(word)
			if word.lemma!=None:
				wordlemma= word.lemma
			else:
				wordlemma=word
			frase_lemm=frase_lemm+str(wordlemma)+" "
	return frase_lemm

#tra tutte le possibili mw del lemma verifico se una di queste è contenuta nella frase
def get_certain_MW (tokenid, frase_lemm, possible_MW):
	lista_return=[]
	lista_MW = [list(x) for x in possible_MW]
	index_lemma=int(tokenid)-1
	for element in lista_MW:
		mw_=element[0].replace("_", " ")
		mw= sentence_lemmatization(mw_)
		x = re.search(mw, frase_lemm)
		if x:
			frase = frase_lemm.split() #suddivido la frase in elementi 
			mw = mw.split()  
			i = 0
			for i in range(len(frase)):
				if frase[i] == mw[0] and frase[i:i+len(mw)] == mw:
					if index_lemma in range(i, i+len(mw)):
						lista_return.append(element)	
	if len(lista_return)>=1 :
		lista_return = lista_return[0]
		#restituisco una lista con solo la multiword contenuta nella frase
	return lista_return

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

def get_result (oldfile, lista, numfrase):

	frase=[]
	with open('WSD_editdistance.conllu', 'a') as outfile, open(oldfile, 'r', encoding='utf-8') as infile:
		a=[0]

		lines= infile.readlines()
		for j in range(0,len(lines)):
			if lines[j] =="\n":
				a.append(j)
		lenA= len(a)
		if lenA-numfrase==1:
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
					if element[0]==False:
						line = line +"\tusemID:"+element[2]+"\tsynsetID:"+str(element[3])+";senseID:"+str(element[4])+"\n"
					else:
						line = line +"\tusemID:"+element[2]+"\tMW["+str(element[5])+"]-"+"synsetID:"+str(element[3])+";senseID:"+str(element[4])+"\n"
			outfile.writelines(line)

#funzione principale 
def main (file):

	fileconllu=pyconll.load_from_file(file)

	pos = ["NOUN","ADJ","ADV","VERB"]
	num=-1

	for sentence in fileconllu:
		num=num+1

		list_forsenses = []
		list_forsensesMW = []

		text_sentence=str(sentence.text)
		sentenceid=str(sentence.id)
		lemmatized_sentence = sentence_lemmatization (text_sentence)

		countMW=-1
		synsetprec = None
		senseprec = None
		
		for token in sentence:
			infotoken=[]
			infotokenMW = []

			if str(token.upos) in pos:
				tokenlemma=str(token.lemma)
				tokenid=str(token.id)
				tokenpos=str(token.upos)

				db="simplelexicon" #cerco il senso (usem) corretto in PSC
				simplerows = get_sense_and_definition(db,tokenlemma,tokenpos)
				new_simplerows = manage_null_def(db, simplerows, tokenlemma, tokenpos)
				usem_list=list_edithdistance(text_sentence,new_simplerows)
				usem = min_edithdistance(usem_list)

				db="NEWIWN"	#cerco il senso(synset+sense) corretto in IWN
				iwnrows=get_sense_and_definition (db, tokenlemma,tokenpos)
				new_iwnrows = manage_null_def(db, iwnrows, tokenlemma, tokenpos)
				synset_list=list_edithdistance(text_sentence,new_iwnrows)
				synset = min_edithdistance(synset_list)
				if synset!="missing":
					sense=get_iwnsensefromsynset(synset, tokenlemma, tokenpos)
					sense=str(sense)
				else:
					sense="missing"

				infotoken.append(tokenid)
				infotoken.append(usem)
				infotoken.append(synset)
				infotoken.append(sense)
				list_forsenses.append(infotoken)

				#cerco multiword di IWN
				possible_MW = get_possible_MW(tokenlemma)
				if len(possible_MW)>0:
					certain_MW = get_certain_MW(tokenid, lemmatized_sentence, possible_MW)
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
		get_result(file, result, num)

main(sys.argv[1])
