Needs an update


Text extractor that extracts parlimentary speeches from xml files in the Icelandix Gigaword Corpus (https://clarin.is/). It also gets the speakers name and title of each speech. It then finds the authors corresponding parliamentary party. 

To run this script please make sure you have all the necessary packages. Run the command: 

		Directory: .\code\Althingi_data_prep\
		pip install –r requriments.txt

To start the extraction process make run the script extractor.py. It has three parameters 
		--data1, -d1: Which is the directory to the Althingi xml files. The script crawls every subfolder of this directory and creates a list with directory to individual xml files

		--data2, -d2: Directory to the file “thingmenn.txt” which includes the list of congress men and their corresponding parliamentary party.
		
		-n_iobs, -n: Integer with the number of parallel processes. Recommended is n= #of cores -1.

The command should look something like this:

		python .\code\Althingi_data_prep\extractor.py -d1 .\data\rmh2\ -d2 .\data\thingmenn.txt -n 3
