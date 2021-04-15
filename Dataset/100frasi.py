#trova10 frasi con il numero più alto di lemmi presenti in PSC/IWN prese sulla prima metà del corpus. 

import pyconll
import sys
import codecs
import MySQLdb
import re

def convert_accents (lemma):
	accents=['à','è','ì','ò','ù','ō']
	NOaccents=['a','e','i','o','u','o']
	count=-1
	for acc in accents:
		count=count+1
		if lemma.endswith(acc):
			x=accents[count]
			y=NOaccents[count]
			lemma=re.sub(x, y, lemma)+"''"
	return lemma

def iwn_get_synset(lemma):
	connection=start_db_connection()
	query = "SELECT synsetid FROM NEWIWN.senses WHERE wordid = ANY (SELECT wordid FROM NEWIWN.words WHERE lemma='%s')" % lemma
	connection.query(query)
	r=connection.store_result()
	rows = r.fetch_row(maxrows=0)
	if(len(rows))>0:
		return "true"
	else:
		return "false"


def simple_get_usem(lemma):
	connection=start_db_connection()
	lemma=convert_accents(lemma)
	query = "SELECT idusem FROM simplelexicon.usem WHERE naming='%s'" % lemma
	connection.query(query)
	r=connection.store_result()
	rows = r.fetch_row(maxrows=0)
	if(len(rows))>0:
		return "true"
	else:
		return "false"

def start_db_connection():
	connection = MySQLdb.connect(
		host = 'localhost',
		user = 'root',
		passwd = 'elexis2021',
		port = 3306)
	return connection

def listaUS4sentence(sentence):
	spos=[]	
	for token in sentence:
		if token.upos == "VERB" or token.upos == "ADJ" or token.upos == "NOUN" or token.upos == "ADV": 
			addelement=str(token.lemma)				
			spos.append(addelement)
		if token.upos=="PROPN":
			element=str(token.lemma)
			if element.endswith('\''):
				element=re.sub('\'', '', element)
				spos.append(addelement)
	return spos


def contacorrdb(listalemmi,db):
	numUS=0

	for i in listalemmi:			
		if db=="simplelexicon":
			booleano=simple_get_usem(i)
			if booleano=="true":				
				numUS=numUS+1
		else:		
			rows=iwn_get_synset(i)
			if rows=="true":				
				numUS=numUS+1
	return numUS
	

def main(file):

	#file=codecs.open(file, "r", "utf-8"):
	fileInput=pyconll.load_from_file(file)

	generale=[]

	for sentence in fileInput:
		stampa=[]
		sd=str(sentence.id)
		print(sd)
		listaUS=listaUS4sentence(sentence)

		numOCCPSc=contacorrdb(listaUS,"simplelexicon")
		numOCCIWN=contacorrdb(listaUS,"iwn")

		stampa.append(sd)
		#stampa.append(numOCCPSc)
		#stampa.append(numOCCIWN)
		stampa.append(numOCCPSc+numOCCIWN)

		generale.append(stampa)
	print(sorted(generale, key=lambda x: x[1], reverse=True))


	#PRIMI DIECI RISULTATI [['20', 38], ['104', 37], ['228', 36], ['434', 36], ['87', 31], ['648', 31], ['81', 30], ['197', 30], ['526', 29], ['205', 28]]
	#sentence id da annotare per prime: 20, 104, 228, 434, 87, 648, 81, 197, 526, 205

main(sys.argv[1])