#system for delete not useful information for alignment with format of the final dataset
# python3 convertnewformat.py altre50.conllu
import sys
'''
def main(file):

	delete = [4,5,6,7,8,9]

	with open(file, 'r') as infile, open("dataset_50_FP_new.conllu", 'w') as outfile:
		
		lines = infile.readlines()
		for line in zip(lines):
			linea = line[0]
			#linea = list(line)
			#print(linea)
			linea = linea.split("\t")
			print(linea)

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
'''

def main(file):

	delete = [4,5,6,7,8,9]

	with open(file, 'r') as infile, open("prime50_newgold.conllu", 'w') as outfile:
		
		lines = infile.readlines()
		for line in zip(lines):
			linea = line[0]
			#linea = list(line)
			#print(linea)
			linea = linea.split("\t")
			print(linea)

			for i in range(len(linea)):
				if i in delete:
					linea[i]="_"
					
			stampa=""
			print(linea)
			if len(linea)==10:
				for element in linea:
					stampa= stampa+element+"\t"
				stampa = stampa[0:-1]+"\n"
			if len(linea)>10:
				linea.pop(11)
				linea.pop(10)
				for element in linea:
					stampa= stampa+element+"\t"
				stampa = stampa[0:-1]+"\n"
			if len(linea)<10:
				for element in linea:
					stampa= stampa+element+"\t"
				stampa = stampa[0:-1]
			print(stampa)
			
			outfile.writelines(stampa)

main(sys.argv[1])