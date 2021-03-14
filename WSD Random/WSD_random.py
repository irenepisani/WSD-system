# sistema WSD - scelta random di un senso


#importo librerie necessarie 
import pyconll
import sys
import codecs
import MySQLdb
import re
import random

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

#converto i le Universal Dependecies POS nelle corrispondenti POS dei db 
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

# ottengo la lista dei possibili sensi attribuiili ad un dato lemma 
def get_senseID (lemma, pos, db):
	connection = start_db_connection() 

	#eseguo la query in base al db per estrarre gli id dei possibili sensi
	if db == "simplelexicon":
		correctlemma = convert_accents(lemma)
		pos = pos_converter(pos,db)
		query = "SELECT idusem FROM simplelexicon.usem WHERE naming='%s' and pos='%s'" % (correctlemma, pos)
	else:
		pos=pos_converter(pos,db)
		query = "SELECT synsetid, senseid FROM NEWIWN.wordsxsensesxsynsets WHERE lemma='%s' and pos='%s'" % (lemma, pos)

	connection.query(query)
	r = connection.store_result()
	rows = r.fetch_row(maxrows=0)
	list_rows = [list(x) for x in rows]
	isempty = bool(list_rows)	#se nessun senso è disponibile per quel lemma segno l'assenza con il tag missing
	if isempty == False:
		if db == "simplelexicon":
			missing = ["missing"]
		else:
			missing = ["missing", "missing"]
		list_rows.append(missing)

	return list_rows

#dati tutti i possibili sensi di un lemma restituisco un senso a caso (scelta random)	
def random_result(rows):
	
	if len(rows)>0:
		result = random.choice(rows)
	else:
		result = "IDmissing"
	return result

#stampo tutti i risultati in un nuovo file 
def get_result (oldfile, lista, numfrase):
	
	frase=[]
	with open('provaxtag.conllu', 'a') as outfile, open(oldfile, 'r', encoding='utf-8') as infile:
		
		a = [0]
		lines = infile.readlines()
		
		for j in range(0,len(lines)):
			if lines[j] == "\n":
				a.append(j)
		
		lenA = len(a)
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
				if line.startswith(str(element[0])+"\t"):	
					line = line.replace("\n", "")
					line = line +"\tusemID:"+element[1]+"\tsynsetID:"+element[2]+";senseID:"+element[3]+"\n"			
			outfile.writelines(line)


# funzione principale
def main(file):

	fileconllu=pyconll.load_from_file(file) #utilizzo pyconll per aprire il file in input
	
	pos = ["NOUN","ADJ","ADV","VERB"] #lista delle pos da annotare semanticamente
	num=-1
	for sentence in fileconllu: #per ogni frase nel file
		num=num+1
		list_forsenses=[]
		
		
		for token in sentence:	#per ogni token nella frase
			infotoken=[]	#creo una lista per aggiungere in seguito le informazioni semantiche 

			if str(token.upos) in pos: #se la pos del token è tra quelle annotabili 
				
				tokenlemma=str(token.lemma)	#salvo lemma del token
				tokenid=str(token.id)	#salvo id del token 
				tokenpos=str(token.upos) #salvo pos del token

				#interrogo il database PSC
				db = "simplelexicon"
				usemrows=get_senseID(tokenlemma,tokenpos, db)	#salvo lista dei possibili sensi attruibili al token
				usemresult=random_result(usemrows)	#scelgo un senso random 
				if usemresult!="IDmissing":	
					usem=str(usemresult[0])
				else: 	#marco con il tag missing se non sono disponibili sensi per quel lemma 					
					usem="missing"

				#interrogo il database IWN
				db = "NEWIWN"
				synsetrows=get_senseID(tokenlemma,tokenpos, db)	#salvo lista dei possibili sensi attruibili al token
				synsetresult=random_result(synsetrows)	#scelgo un senso random 
				if synsetresult!="IDmissing":
					synset=str(synsetresult[0])
					sense = str(synsetresult[1])

				else:	#marco con il tag missing se non sono disponibili sensi per quel lemma 
					synset="missing"
					sense="missing"

				
				#salvo informazioni utili per stampare l'output 
				infotoken.append(tokenid)
				infotoken.append(usem)
				infotoken.append(synset)
				infotoken.append(sense)
				list_forsenses.append(infotoken)
		
		get_SenseColumn(file, list_forsenses, num)
		#restituisco un nuovo file contenente per ogni token annotabile anche le informazioni semantiche 

main(sys.argv[1])