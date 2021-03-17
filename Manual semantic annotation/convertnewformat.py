#delete useless information to make files compatible with the final dataset

#INPUT: dataset_50_IP.conllu
#OUTPUT: dataset_50_IP_new.conllu

#INPUT: dataset_50_FP.conllu
#OUTPUT: datset_50_FP_new.conllu

import sys

def main(file):

	delete = [4,5,6,7,8,9] #celle da svuotare

	with open(file, 'r') as infile, open("file.conllu", 'w') as outfile:
		lines = infile.readlines()
		for line in zip(lines):
			linea = line[0]
			linea = linea.split("\t")
			for i in range(len(linea)):
				if i in delete:
					linea[i]="_"	
			stampa=""
			print(linea)
			if len(linea)==10:
				for element in linea:
					stampa= stampa+element+"\t"
				stampa = stampa[0:-1]+"\n"
			else:
				for element in linea:
					stampa= stampa+element+"\t"
				stampa = stampa[0:-1]
			outfile.writelines(stampa)
main(sys.argv[1])
