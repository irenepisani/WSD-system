import sys
import csv

def main(file):

	tsv_file = open(file)
	read_tsv = csv.reader(tsv_file, delimiter="\t")
	
	with open('datasetFP.conllu', 'w') as outfile:
		for line in read_tsv:
			
			a=['', '', '', '', '', '', '', '', '', '', '', '']
			if line!= a:
				stampa = ""
				for element in line:
					if element!=str(''):
						stampa = stampa+str(element)+"\t"
				stampa = stampa[0:-1]+"\n"
				outfile.writelines(stampa)

main(sys.argv[1])
