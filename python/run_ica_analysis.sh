
# /bin/bash
# Bash script that runs analytics on censys.io JSON files and stored the results in CSV file. 

# All json files (for Alexa and Cisco Umbrella) MUST be stored in two separate directories 
# (certs_alexa and cisco_umbrella) in the CENSYS_IO_DIR parent directory.

# The results output CSV is in RESULTS_FILE
# The output CSV columns titles are 
# [
#  0 ICAs # of servers, 1 ICA # of servers, 2 ICAs # of servers, 3 ICAs # of servers, >3 ICAs # of servers, 
#  # distinct servers, Self-signed certs found, non-CA certs found, Certs w/o Subject found, Distinct ICAs found 
# ]

# Run as 
#  ./run_ica_analysis.sh 1000000

#TODO: Change the JSON file directory and the results file as necessary. 
CENSYS_IO_DIR=../data/censys.io
RESULTS_FILE=../certs_results.csv

if [ $# -eq 0 ]
  then
    t=1000000
else 
    t=$1
fi

# empty the ouput file first
echo "" > $RESULTS_FILE

# For every JSON file in the certs_alexa subdirectory
for fil in $CENSYS_IO_DIR/certs_alexa/*.json
do 
  # Run the statistics and output the results
  python3 ica_analysis.py $fil --top $t --csv >> $RESULTS_FILE
done

# And for every JSON file in the cisco_umbrella subdirectory
for fil in $CENSYS_IO_DIR/cisco_umbrella/*.json
do
  # Run the statistics and output the results
  python3 ica_analysis.py $fil --top $t --csv >> $RESULTS_FILE
done


