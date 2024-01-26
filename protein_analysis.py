#!/usr/bin/python3

import os, subprocess, sys, shutil
import pandas as pd
from decimal import Decimal


####################################################################################################################################
#Searching the user's protein and taxon query on NCBI protein database


#Function to retrieve the main query fasta sequences from NCBI protin database
def retrieve_fasta(NCBI_query):
    
    #Running the search command, limiting at the first 1000 results. 'head -n 100' is used in comparison to '-start 1 -stop 1000' as the latter does not run when the search contains less than 1000 results.
    query = f"esearch -db protein -query \"{NCBI_query}\" | head -n 1000 | efetch -format fasta > ./{query_name}/{query_name}.pro.fa"
    subprocess.call(query, shell=True, stderr=subprocess.DEVNULL)
    
    #Splitting the created file containing the query fasta sequences into a list based on each '>' in the headers
    query_file = open(f"./{query_name}/{query_name}.pro.fa")
    sequence_list = query_file.read().rstrip().split(">")
    query_file.close()
    
    #Turning each element in the list of fastas to a dictionary of the headers as the keys and fasta sequences as the values
    sequence_dict = {}
    for i in sequence_list:
        if i != '':                                          #Removing the first empty element
            sequence_index = i.find('\n')                    #Splits the list of fastas based on each new line character
            keys = i[:sequence_index]                        #Sets the header as the dictionary key
            values = i[sequence_index:].replace("\n","")     #Sets the fasta sequences as the dictionary value
            sequence_dict[keys] = values                     #Creates the new entry in the dictionary
    
    #Filtering through the results to remove sequences with ambiguous headers
    items_to_delete = []
    for keys in sequence_dict.keys():                                       
        
        #Removes the fasta entries in the dictionary if any of these words are present in the header
        if "associated" in keys or "unknown" in keys or "unnamed" in keys:  
            items_to_delete.append(keys)        #Adding the entries to remove to the temporary list
    
    for key in items_to_delete:                 #Looping through the temporary list to remove the entries from the dictionary
        del sequence_dict[key]

    #The output of the function involves the dictionary of each search result header and corresponding fasta sequence
    return sequence_dict 
    


#First output on screen for the user: explaining the search on NCBI
print("By inputting a protein family and taxonomic group, fasta sequences of proteins found form NCBI protein database will be saved. Please be warned that if the query search contains more than 1000 protein results, only the first 1000 will be considered and the search will take long.")


#Running while loop until user inputs the protein family and taxonomic group with the desired output
while True:

    #User specifies the protein family and taxonomic group of their query and these inputs get saved to the variables protein_family and taxonomic_group. Unwanted characters are changed to a space.
    protein_family = input("What is the protein family of your query?\n").replace("."," ").replace(";"," ").replace(","," ").replace("/"," ").replace("\\"," ").replace(":"," ").replace("'"," ").replace("\""," ").replace("_"," ")
    
    taxonomic_group = input("What is the taxonomic group of your organism query?\n").replace("."," ").replace(";"," ").replace(","," ").replace("/"," ").replace("\\"," ").replace(":"," ").replace("'"," ").replace("\""," ").replace("_"," ")
    
    #Identifies the taxonomic group ID on NCBI taxonomy database
    temporary_taxon = subprocess.check_output(f"esearch -db taxonomy -query '{taxonomic_group}' | efetch -format docsum | xtract -pattern DocumentSummary -element Id", shell=True, text=True, stderr=subprocess.DEVNULL).strip()
    
    #If a valid taxon has been entered by the user, taxonomc_group will be reassigned to the taxonomid ID in the format txid____
    if temporary_taxon.isnumeric():
        taxonomic_group = "txid" + temporary_taxon
    
    #Checks whether the user has inputted the queries in a valid format, so eliminating blank spaces and other characters. Inputs including a number or letter will be valid to continue to esearch
    if any(char.isalnum() for char in protein_family) and any(char.isalnum() for char in taxonomic_group):
    
        pass
    
    else:
        
        #Identifying invalid format of taxonomic group
        if any(char.isalnum() for char in protein_family):
            print("You have not enetered a valid taxonomic group. Please re-enter your query.")

        #Identifying invalid format of protein family
        elif any(char.isalnum() for char in taxonomic_group):
            print("You have not entered a valid protein family. Please re-enter your query.")

        continue
    

    while True:
        
        #User names a new directory as well as the name of most files produced for a specific query, so all outputs can be saved in the same location. Each query will therefore have its own directory.
        query_name = input("What would you like to name the folder and subsequent outputs from this search? Please note that any of the following characters, as well as a space, will be changed to '_' for readability: '\\ / , ; :'\n")

        #Removing unwanted characters from the directory name given by the user
        query_name = query_name.replace(";","_").replace(",","_").replace("/","_").replace("\\","_").replace(":","_").replace("'","_").replace("\"","_").replace(" ","_")
 
        try:
            #Creating the new directory
            os.mkdir(query_name)
            break

        except FileExistsError:
            
            file_decision = input("This directory name already exists. Would you like to set it as the directory path for this query too? Please input 'Y' for yes or 'N' for no.\n")
            if file_decision.upper() == "Y" or file_decision.lower() == "yes":
                break

            else:
                pass



    #Attempting to catch out any error when running esearch and efetch
    try:

        #Running the user query until the input for including 'NOT PARTIAL' or not is provided well
        while True:


            #Asking the user if they want to run esearch with 'NOT PARTIAL' or not
            partial = input("Would you like to consider all protein sequences found from your search, including those that contain an incomplete version of of the amino acid sequence (partial)? Please input 'Y' for yes or 'N' for no.\n")

            #Not including 'NOT PARTIAL' in the NCBI search        
            if partial.upper() == "Y" or partial.lower() == "yes":
                print("Retrieving protein sequences of query from NCBI databases...")
                
                #Setting the -query field to be inputted into the esearch command
                esearch_query = f"{protein_family}[PROT] AND {taxonomic_group}[ORGN]"

                #Contains dictionary of the search fasta result
                sequence_dict = retrieve_fasta(esearch_query)
                

                #Checking if the search contains any results. If there are no results, retrieve_fasta() is run again one more time,                     without keeping results as specific by removing [PROT]
                if len(sequence_dict) == 0:
                    esearch_query = f"{protein_family} AND {taxonomic_group}[ORGN]"
                    sequence_dict = retrieve_fasta(esearch_query)

                break

            #Including 'NOT PARTIAL' in the NCBI search
            elif partial.upper() == "N" or partial.lower() == "no":
                print("Retrieving protein sequences of query from NCBI databases...")

                #Setting the -query field to be inputted into the esearch command
                esearch_query = f"{protein_family}[PROT] AND {taxonomic_group}[ORGN] NOT PARTIAL"
                
                #Contains dictionary of the search fasta result
                sequence_dict = retrieve_fasta(esearch_query)

                #Checking if the search contains any results. If there are no results, retrieve_fasta() is run again one more time,                      without keeping results as specific by removing [PROT]
                if len(sequence_dict) == 0:
                    esearch_query = f"{protein_family} AND {taxonomic_group}[ORGN] NOT PARTIAL"
                    sequence_dict = retrieve_fasta(esearch_query)

                break

            else:
                print("You have not entered a valid character. Please try again.")


        #Checks if the final search has any results
        if len(sequence_dict) != 0:
            
            #Checks whether the search was limited to 1000
            if len(sequence_dict) > 1000:
                length = 1000
            else:
                length = len(sequence_dict)

            #Outputs the number of searches found and displays the first 5
            print("Your query has returned " + str(length) + " protein sequences of the protein family " + protein_family + " and taxonomic group " + taxonomic_group + ". The first few outputs of this search are shown below:")
            
            print(subprocess.call(f"grep '>' ./{query_name}/{query_name}.pro.fa | head -n5", shell=True))
        
            
            #Allows user to confirm whether the displayed results are as they desired. Any other input other than yes will not be considered
            decision = input("Is this your desired search? Please type 'Y' for yes or 'N' for no.\n")

            if decision.upper() == "Y" or decision.lower() == "yes":
                print(f"Great! The fasta sequences for your protein query are saved under ./{query_name}/{query_name}.pro.fa")
                
                break

            else:

                #Will delete the directory created if the output is not as desired.
                shutil.rmtree(f"./{query_name}/")
                print("It seems you have instructed that these results are not as you desired. Please start this process again.")
        
        else:
            
            #Will delete the directory created if there are no search results for the query given.    
            shutil.rmtree(f"./{query_name}/")
            print("There are no results for your query. Please start again.")


    except:
        shutil.rmtree(f"./{query_name}/")
        print("There are no results for your query. Please start again.")



protein_family = protein_family.replace(" ","_")
taxonomic_group = taxonomic_group.replace(" ","_")




##############################################################################################################################
#Aligning and plotting conservation across protein query

if os.path.exists(f"./{query_name}/{query_name}.pro.fa"):
    aligned_fasta = f"{query_name}_aligned.pro.fa"

    #Creating a function to align the fasta sequeces of the protein query and generate a conservation plot png
    def plot_conservation(query, aligned_file):

        print("Aligning clustered query sequences...")

        #Aligning the query sequences, and outputting a conservation score and similarity score
        subprocess.call(f"clustalo -i ./{query}/{query}.pro.fa --force --threads=256 -o ./{query}/{aligned_file}", shell=True)
        print(f"Aligned fasta sequences of your protein query have been saved in ./{query}/{aligned_file}")


        print("Generating plot of conservation of query sequence...")

        #Plotting the aligned sequences
        subprocess.call(f"plotcon -sequence ./{query}/{aligned_file} -winsize 7 -graph png -goutfile ./{query}/{query}_conservation_plot", shell=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        os.rename(f"./{query}/{query}_conservation_plot.1.png", f"./{query}/{query}_conservation_plot.png")
        print(f"Your generated conservation plot has been saved in the path ./{query}/{query}_conservation_plot.png")



    #First output on screen to start the process of alignment of user query
    alignment_question = input("Would you like to determine and plot the level of conservation between the protein sequences of your query? Please input 'Y' for yes or 'N' for no.\n")


    #Runs the alignment function and plots the conservation
    if alignment_question.upper() == "Y" or alignment_question.lower() == "yes":

        plot_conservation(query_name, aligned_fasta)

        #Asks user if they want the plot to be opened in a separate window
        view_image = input("Would you like to view the conservation plot? Please input 'Y' for yes or 'N' for no.\n")
        if view_image.upper() == "Y" or view_image.lower() == "yes":

            print("Plot is opening in separate window...")
            subprocess.call(f"eog ./{query_name}/{query_name}_conservation_plot.png", shell=True)

    else:

        print("It seems you have decided not to generate conservation plots of your query.")






###########################################################################################################################
#Identifying motifs from the protein and taxon query



if os.path.exists(f"./{query_name}/{query_name}.pro.fa"):
    query_file = open(f"./{query_name}/{query_name}.pro.fa")
    sequence_list = query_file.read().rstrip().split(">")
    query_file.close()


    #Making a function to find the motifs in the protein sequence query
    def find_motifs(list_of_sequences, find=None, motif_chosen=None):
        if os.path.exists(f"./{query_name}/{query_name}_motifs.txt"):
            os.remove(f"./{query_name}/{query_name}_motifs.txt")
    
        print("Identifying motifs in the protein sequence query...")

        #Looping through the fasta sequences one at a time to identify motifs
        for i in list_of_sequences:
            if i != '':              #Ignoring the first empty entry

                #Creating a new temporary file and writing each sequence to it
                with open(f"./{query_name}/temporary_fasta_file", "w") as temporary_file:
                    temporary_file.write(">" + i)

                #Identifies motifs from PROSITE database in the protein sequences from the query
                subprocess.call(f"patmatmotifs -sequence ./{query_name}/temporary_fasta_file -outfile ./{query_name}/{query_name}_temporary_motifs.txt", shell=True, stderr=subprocess.DEVNULL)

                #Opening the newly made temporary file
                with open(f"./{query_name}/{query_name}_temporary_motifs.txt") as temporary_motif_file:
                    fasta_content = temporary_motif_file.read()

                    #Creating a new file to append each fasta sequnce followed by "\nnew_seuqnce". This way, each fasta sequnce has a clear separater of this string.
                    with open(f"./{query_name}/{query_name}_motifs.txt", "a") as motif_file:
                        motif_file.write(fasta_content + "\nnew_sequence")

        #Removng the temporary files
        os.remove(f"./{query_name}/temporary_fasta_file")
        os.remove(f"./{query_name}/{query_name}_temporary_motifs.txt")

        #Opens the final motif file
        motif_open = open(f"./{query_name}/{query_name}_motifs.txt")

        #Splits the file into a list, separating by each "\nnew_sequence"
        motif_sequences = motif_open.read().split("\nnew_sequence")
        motif_open.close()


        if find is None:

            #Creating a dictionary to save all the types of motifs present along with their counts from the query search
            motifs = {}

    
            #Looping through all the motifs found in the fasta sequences and counting them and storing the number of each motif in a dictionary
            for j in motif_sequences:   
                try:

                    #Splitting the lines of the patmatmotifs output into a list
                    lines = j.split("\n")

                    #Retrieving the line that contains the type of motif present
                    motif_name = lines[25][8:]
                    motifs[motif_name] = motifs.get(motif_name, 0) + 1

                #Excludes any sequences not containing a motif
                except IndexError:
                    continue

            #Check whether any motifs were found    
            if len(motifs) != 0:
                motifs_found = []

                #Joins all the motifs found and how many times each were found to a list
                for key, value in motifs.items():
                    motifs_found.append(f"Found the motif {key} {value} times.")

                #Outputs all the motifs found and how many times they were found
                print("Summary of motifs found in protein sequence query below:\n" + "\n".join(motifs_found))


            else:
                print("No motifs found in the protein sequence query.")

            #The output of the function is the dictionary of the motifs found with the corresponding number of times they were found
            return motifs


        #Section for wildcard blast step
        elif find == True:

            ids_with_chosen_motif = []

            for j in motif_sequences:
                try:

                    #Splitting the lines of the patmatmotifs output into a list
                    lines = j.split("\n")

                    #Retrieving the line that contains the type of motif present
                    if lines[25][8:] == motif_chosen:
                        name = lines[12][12:].split(" ")
                        ids_with_chosen_motif.append(name[0])

                #Excludes any sequences not containing a motif
                except IndexError:

                    continue

            #Returns the accession numbers
            return set(ids_with_chosen_motif)



    #First output to the user before finding protein query motifs
    motif_decision = input("Would you like the identify the motifs from PROSITE in your protein query sequences? Please input 'Y' for yes or 'N' for no.\n")

    if motif_decision.upper() == "Y" or motif_decision.lower() == "yes":

        #Running the function find_motifs() using the query
        motifs_found = find_motifs(sequence_list)
        print(f"The full output of motifs per protein sequence from your query can be found in ./{query_name}/{query_name}_motifs.txt")

    else:

        print("It seems you have chosen to not identify the motifs in your protein query.")




###############################################################################################################################
#WILDCARD: Building a blast database off of a motif subset of the user's protein query and asking for a new taxon to blast against





#Making a variable for the pullseq command path
pullseq_path = "/localdisk/data/BPSM/ICA2/pullseq"




#Function to extract the wanted fasta sequences with the chosen motif and make a blastp database out of these fasta sequences
def motif_assessment(motif_chosen):

    #Finding the accession numbers of the fasta sequences containing the chosen motif and adding them to a list
    ids = list(find_motifs(sequence_list, find=True, motif_chosen=motif_chosen))

    #Opening a new temporary file to add the list of accession numbers to
    with open(f"./{query_name}/{query_name}_temporary_list.txt", "w") as id_file:
        for each_id in ids:
            id_file.write(each_id + "\n")

    #Running pullseq to extract the fasta sequences from the original query search fasta file that contain the accession number from the newly-made list in their headers
    subprocess.call(f"{pullseq_path} -i ./{query_name}/{query_name}.pro.fa -n ./{query_name}/{query_name}_temporary_list.txt > ./{query_name}/{query_name}_motif_db.pro.fa ", shell=True)
    
    #Deleting the temporary file listing accesion numbers
    os.remove(f"./{query_name}/{query_name}_temporary_list.txt")
    
    #Checks if this function has been run for this original query yet or not
    try:

        #A new subdirectory will be made when this function is run for the first time per original query
        os.mkdir(f"./{query_name}/blast_database")

    except FileExistsError:

        #Will not re-create a subdirectory when this function has already been run
        pass

    #Makes a database of the fasta sequences containing the chosen motif to be able to use in blast
    subprocess.call(f"makeblastdb -in ./{query_name}/{query_name}_motif_db.pro.fa -dbtype prot -out ./{query_name}/blast_database/{motif_chosen}", shell=True, stdout=subprocess.DEVNULL)

    print(f"The database out of proteins from your query with your chosen motifs is saved in ./{query_name}/blast_database/")

    #Deletes the output file from pullseq as it is no longer needed: the database has already been made
    os.remove(f"./{query_name}/{query_name}_motif_db.pro.fa")





#Function to identify the user's new query they want to use in blast, and subsequently runs ths query in blastp against the newly-made database from fasta sequences containing a certain motif
def run_blast(motif_chosen):

    #Defining a function within run_blast() that refines the search query of the user for esearch
    def carry_on(new_query):

        #Removing unwanted spaces form the new query name
        new_query = new_query.replace(" ", "_")

        #Opens the temporary file created later on in the run_blast() function, containing the accession numbers of esearch
        with open(f"./{query_name}/{query_name}_temporary_accs.txt", "r") as accs:

            counter=0
            options = {}
            
            #Looping through each accession number
            for line in accs:
                counter += 1

                #Enumerates each accession number
                print(str(counter) + ": " + line)

                #Adds the number and corresponding accession number to a dictionary
                options[counter] = line.rstrip()
                

            #Loops until a valid input is given to identify which accession number will be used for the blast
            while True:

                #Asks the user to input a number from the dictionary of accession numbers created
                id_choice = input("Which species would you like to pick from the list to blast against your protein motif query database? Please input a number from the list of choices from above.\n")

                #Checks if the user has inputted an integer
                try:

                    #Checks if the user has inputted a number present in the dictionary, corresponding to an accession number
                    if int(id_choice) in options.keys():

                        #Extracts the fasta sequence corresponding to the chosen accession number and saves that to a new file
                        subprocess.call(f"efetch -db protein -id {options[int(id_choice)]} -format fasta > ./{query_name}/{new_query}.pro.fa", shell=True)
                        
                        break
                    
                    #The user has the chance to re-input a number if the given number is invalid
                    else:

                        print("The number you have chosen is not in the list of accession names listed above. Please input another number.\n")
                
                #If the user has inputted anything besides an integer, they will have the change to re-enter
                except ValueError:

                    print("The number you have chosen is not in the correct format. Please ensure you only enter the number from the list shown.")


    #Loops until the user has entered a valid input as to whether they want to input their own accession number or to run esearch on a taxon to chose from a list of accession number
    while True:

        #Asks the user to decide between option 1 or 2
        own_query = input(f"Would you like to (1) enter your own query accession number for a taxon and {protein_family} or would you like to (2) search up top results for a general taxon? Please enter '1' or '2' corresponding to the these options.\n")
        
        #Checks if the user has inputted an integer
        try:

            #Checks if the user has chosen option 1
            if int(own_query) == 1:

                while True:
                    new_query = input("What is the accession number of your query?\n").upper()

                    print("Accessing the sequence to your accession number from NCBI protein database...")

                    #Extracts the fasta sequence corresponding to the accession number provided by the user
                    subprocess.call(f"efetch -db protein -id {new_query} -format fasta > ./{query_name}/{new_query}.pro.fa", shell=True, stderr=subprocess.DEVNULL)
                    
                    if os.path.getsize(f"./{query_name}/{new_query}.pro.fa") != 0:
                        break
                    else:
                        print("The access number you entered was either mistyped or does not correspond to a sequence. Please enter another one.")
                                        

                break

            #Checks if the user has chosen option 2
            elif int(own_query) == 2:

                #Loops until an esearch result desired is achieved
                while True:

                    #Asks the user to input the taxon to use for as a blast query. Any unwanted characters in the input will be replaced by a space
                    new_query = input(f"What is the taxon of your new query to blastp {protein_family} againist your initial query of {taxonomic_group}? Please note that only the first 10 NCBI protein database results will be considered.\n").replace("."," ").replace(";"," ").replace(","," ").replace("/"," ").replace("\\"," ").replace(":"," ").replace("'"," ").replace("\""," ").replace("_"," ")

                    print("Finding results for your new query on NCBI protein database...")        
        
                    #Runs esearch to achieve the accession numbers of the first 10 results with their taxon query
                    subprocess.call(f"esearch -db protein -query '{protein_family}[PROT] AND {new_query}[ORGN]' -retmax 10 | efetch -format acc -start 0 -stop 10 > ./{query_name}/{query_name}_temporary_accs.txt", shell=True, stderr=subprocess.DEVNULL)
                    
                    #Checks if the file outputted from esearch contains any accession numbers
                    if os.path.getsize(f"./{query_name}/{query_name}_temporary_accs.txt") != 0:
                        
                        #Runs carry_on() function described above
                        carry_on(new_query)

                        break
                    
                    #If the file outputted form esearch does not contain any accession numbers, esearch will be run one more time without including [PROT] to check if any accession numbers can be achieved if the search is less specific
                    else:
                        
                        #Runs esearch to acheive the accession numbers of the first 10 results with thei user's taxon query
                        subprocess.call(f"esearch -db protein -query '{protein_family} AND {new_query}[ORGN]' -retmax 10 | efetch -format acc -start 0 -stop 10 > ./{query_name}/{query_name}_temporary_accs.txt", shell=True, stderr=subprocess.DEVNULL)
        
                        #Again checks if the file outputted from esearch contains any accession numbers
                        if os.path.getsize(f"./{query_name}/{query_name}_temporary_accs.txt") != 0:
                            
                            #Runs carry_oun() function described above
                            carry_on(new_query)

                            break

                        
                        else:

                            #If there are no results in esearch, the user has the choice to try searching again
                            again_decision = input("There are no results for your query. Would you like to input another new query? Please input 'Y' for yes or 'N' for no.\n")

                            #Checks if the user wants to try search with a new taxon
                            if again_decision.upper() == "Y" or again_decision.lower() == "yes":
                                
                                continue

                            else:

                                break
                break
            
            #If the user has not inputted 1 or 2, they can re-enter a number
            else:
                print("You did not enter a valid number. Please try again.")
        

        #If the user inputted anything besides an integer, they can re-enter a number
        except ValueError:
            
            print("You did not enter a valid number. Please try again.")


    #Checks if the file containing accession number has been created, and if it has, it is deleted
    if os.path.exists(f"./{query_name}/{query_name}_temporary_accs.txt"):
        os.remove(f"./{query_name}/{query_name}_temporary_accs.txt")
    
    #Ensures that the new_query variable does not have any spaces remaining
    new_query = new_query.replace(" ", "_")

    #Checks if the fasta sequence for the new taxon query has been extracted
    if os.path.exists(f"./{query_name}/{new_query}.pro.fa"):

        print("Running blastp of your new query against your intial protein motif query database...")

        #Runs blastp of the new query fasta file aganst the database made of protein fasta sequences containing the chosen motif from the original query
        subprocess.call(f"blastp -query ./{query_name}/{new_query}.pro.fa -db ./{query_name}/blast_database/{motif_chosen} -outfmt 7 > ./{query_name}/{motif_chosen}_{new_query}_blast.out", shell=True)
    
    #Function returns the name of the new taxon query
    return new_query





#Function that assesses the blastp output, saves the output as a csv file, and summarises the most similar sequences found across the new query and old query with a chosen motif
def assess_blastp(motif_chosen, new_query):
    
    try:
        #Reads the blastp outfut as a data frame, only if hits were found, ignoring the comment lines in the file
        df = pd.read_csv(f"./{query_name}/{motif_chosen}_{new_query}_blast.out", sep="\t", comment ="#")

    except pd.errors.EmptyDataError:

        #Lets the user know that no hits were found with this blast, so they should try with a different query
        print("There are no resulting hits form your results! Please start again with a new query.")
        return

    #Sets the column names of the data frame
    df.columns = ['Query Accession Number', f'{taxonomic_group} Accesion Number', '% Identity', 'Alignment Length', 'Mismatches', 'Gap Opens', 'Query Sequence Start', 'Query Sequence End', f'{taxonomic_group} Sequence Start', f'{taxonomic_group} Sequence End', 'E-value', 'Bit Score']
    
    
    #Loops until a valid threshold value is entered by the user
    while True:

        try:
            
            #Asks the user to enter a threshold for E-value. The user can input this value in scientific e notation
            threshold = input("What is your E-value threshold to indicate a significant match? You can enter this value as a decimal or in scientific e notation, however ensure it is in this format, e: '5e-2'. Typically, a very high similarity between two proteins results in an E-value lower than 1e-50, and related homologues may have an E-value lower than 1.\n").replace(" ","")

            threshold = Decimal(threshold)                   #Checks that the user has entered a number
            if threshold > 0:                                #Checks that the user has entered a number larger than 0
                if len(df[df.iloc[:,10] <= threshold]) > 0:  #Checks whether any E-values in the blast output are lower than the threshold
                    
                    break
                
                #If the user has entered a valid threshold that is too low in comparison to the blast output E-values, they are asked to                re-enter one
                else:
                    
                    #Find the lowest E-value present to let the user know about the range of the results
                    lowest_evalue = df['E-value'].min()
                    print(f"None of the blast output have an E-value lower than your threshold. The lowest E-value achieved is {lowest_evalue}. Please re-enter a threshold.")

            #If the user has entered a number lower or equal to 0, they have the change to re-enter a number
            else:
                print("Your E-value threshold seems to be out of the range, and cannot be lower or equal to 0. Please re-enter a suitable threshold number.")

        #Checks whether the user has inputted anything besides a number, and the user will be able to re-enter a number
        except ValueError:
            
            print("You did not enter a valid E-value threshold. Please make sure you input a number.")

        except decimal.InvalidOperation:

            print("Your input has not been recognized. Please re-enter the number again.") 

    
    df = df[df.iloc[:,10] <= threshold]                            #Subsets the data to E-values lower than the threshold
    df.sort_values(df.columns[10], ascending=True, inplace=True)   #Sorts the data in ascending number of E-value

    #Saves the new data frame to a csv file
    df.to_csv(f"./{query_name}/{motif_chosen}_{new_query}_blast.csv", header=True, index=False)

    #Lets the user know the best results from blastp
    print("The top performing 3 results of the blast with your query are tabulated below (sorted by E-value):")
    print(df.head(3))
    print(f"The protein with the lowest E-value from your blast, and thus the most significant match to your query sequence of {new_query} has accession number {df.iloc[0,1]}")
    print(f"The full list of blast results with an E-value lower than {threshold} can be found in ./{query_name}/{motif_chosen}_{new_query}_blast.out or in csv format in /{query_name}/{motif_chosen}_{new_query}_blast.csv")





#Looping until the user has ran blast as many times as they desire
while True:

    #The first output to the user before identifying the new query to blast against a database of a chosen motif from the original query
    motif_assessment_decision = input("Would you like to make a database of a certain motif found in your protein sequence query to subsequently run blastp on a separate query against? This involves running blastp across the same protein family, but with two different taxonomic groups as query (new) and subject (original query: to make database). Please input 'Y' for yes or 'N' for no.\n")
    
    if motif_assessment_decision.upper() == 'Y' or motif_assessment_decision.lower() == 'yes':
        
        #Checks if motifs have already been identified for the original taxon query
        if os.path.exists(f"./{query_name}/{query_name}_motifs.txt"):
            
            #Asks the user to pick from a list of motifs
            print("Please pick the motif for which you would like to create a blast database. This database will be constructed using the proteins from your query search containing this motif.\n")

            counter = 1
            motif_choice_dict = {}

            #Loops through each motif present from the original taxon query
            for m in motifs_found.keys():     
                print(str(counter) + ": " + m)   #Enumerates each motif and prints each combination
                motif_choice_dict[counter] = m   #Saves each combination of number and motif to a dictionary
                counter += 1
            
            #Loops until a valid motif number has been picked by the user
            while True:

                #Asks the user to input a number corresponding to a motif
                motif_choice = input("Input the number corresponding to your chosen motif.\n")

                #Checks that the motif chosen is an integer
                try:

                    int(motif_choice)
                
                #If the motif chosen is not an integer, the user has the chance to re-enter a number
                except ValueError:

                    print("You have not chosen a valid motif number. Please input a number that corresponds to a motif from your protein query search shown above.")
                    
                    #Does not continue on to the remainder of this interation
                    continue


                #Checks if the user has chosen a number corresponding to a motif by checking the dictionary created
                if int(motif_choice) in motif_choice_dict.keys():

                    #Extracts the motif name corresponding to the chosen number and saves it to chosen_motif
                    chosen_motif = motif_choice_dict[int(motif_choice)]
                        
                    #Runs the motif_assessment() function to make the blast database
                    motif_assessment(chosen_motif)
                    
                    #Runs the new_query() function to blast a new query to the database created
                    new_query = run_blast(chosen_motif)

                    #Runs the assess_blastp() function to output the results of blastp
                    assess_blastp(chosen_motif, new_query)
                        
                    break
                    

                #If the user did not pick a valid motif number, they can re-enter a new number
                else:
                    print("You have not chosen a valid motif number. Please input a number that corresponds to a motif from your protein query search shown above.")


            
        #If motifs have not yet been identified of the fasta sequences from the original query, the user has the choice to do so now
        else:

            rerun_decision = input("It appears you have not yet identified motifs from your protein sequence query. Would you like to do that now? Please input 'Y' for yes or 'N' for no.\n")

            #If user has chosen to identify the motifs now, find_motifs() function is run
            if rerun_decision.upper() == "Y" or rerun_decision.lower() == "yes":

                print("Identifying motifs from your protein query sequences...")
                find_motifs(sequence_list)

                continue

            else:
                print("A motif from your protein sequence query cannot be assessed if motifs have not been identified yet.")

    #Loop will be broken if the user does not choose to find the motifs from the original query
    else:

        break

    
    #Checks if blastp has already been run
    if os.path.exists(f"./{query_name}/{chosen_motif}_{new_query}_blast.out"):

        #Asks the user if they want to start the process again
        again = input("Would you like to run blast again with a different motif or taxon query? Please input 'Y' for yes or 'N' for no.\n")

        if again.upper() == "Y" or again.lower() == "yes":

            #Will continue to the next iteration if the user chooses to blast again
            pass

        else:

            #Breaks the loop if the user chooses not to blast again
            break





#################################################################################################################################
#Plotting the transmembrane segments of the user's original protein and taxon query



#Checks whether the query sequences have been aligned yet
if os.path.exists(f"./{query_name}/{query_name}_aligned.pro.fa"):


    #Asks the user if they want to identify transmembrane segments of their query
    tmap_decision = input("Would you like to predict whether there are transmembrane segments in the proteins of your query? Please input 'Y' for yes or 'N' for no.\n")

    if tmap_decision.upper() == "Y" or tmap_decision.lower() == "yes":

        #Generates a plot showing transmembrane regions. Plot will be blank if no transmembrane regions are present
        subprocess.call(f"tmap -sequence ./{query_name}/{query_name}_aligned.pro.fa -sformat fasta -graph png -outfile ./{query_name}/{query_name}_tmap.res -goutfile ./{query_name}/{query_name}_tmap_plot", shell=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

        os.rename(f"./{query_name}/{query_name}_tmap_plot.1.png", f"./{query_name}/{query_name}_tmap_plot.png")

        print(f"Your transmembrane segment plot is saved in ./{query_name}/{query_name}_tmap.png\nOpening this plot in a separate window...")

        #Displays the plot in a separate window
        subprocess.call(f"eog ./{query_name}/{query_name}_tmap_plot.png", shell=True)

    else:

        print("It seems you have decided not to predict transmembrane segments in your protein query.")

else:

    print("Once you have generated aligned sequences of your query, you will have the choice to identify transmembrane segments of your query.")



################################################################################################################################
