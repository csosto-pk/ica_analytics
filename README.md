# ica_analytics


In python directory
./run_ica_analysis.sh 

Bash script that runs analytics on censys.io JSON files and stored the results in CSV file. 

It assumes all json files (for Alexa and Cisco Umbrella are stored in two separate directories 
(certs_alexa and cisco_umbrella) in the CENSYs_IO_DIR parent directory.

The results output CSV is in RESULTS_FILE
The output CSV columns titles are 
[
 0 ICAs # of servers, 1 ICA # of servers, 2 ICAs # of servers, 3 ICAs # of servers, >3 ICAs # of servers, 
 # distinct servers, Self-signed certs found, non-CA certs found, Certs w/o Subject found, Distinct ICAs found 
]

python3 ica_analysis.py ../data/censys.io/cisco_umbrella/certs_cisco_20200602.json > certs_umbrella_results


# This program parses the Censys.io Alexa and Umbrella JSON files and returns statistics on the differences between 
# the Alexa and Cisco Umbrella datasets. 

# It takes two files as input. These are assumed to be the Alexa and Umbrella JSON files extracted from Censys.io 
# on the same day for more accurate results. 

# The first input file SHOULD contain Alexa rankings. And the second the Umbrella rankings. Otherwise the program 
# will through an error when trying to parse the "alexa_rank"/"cisco_rank" rankings in the JSON.

# It returns the statistics differences between the files. There are different metrics it calculates: 
#   - the simplest one is the difference of the server domains. It calculates the # servers that exist on one 
#     file but not the other and divides be the sum of the servers in each file. If the input files were the same,  
#     the metric should be calculated to be 0.
#   - another metric is the diff of the rankings of the server domains divided by 1000. For servers that exist 
#     in both files it adds the difference of the ranking of these servers. If a server only exists in one file 
#     it adds a difference of 1,000,000. To lower the metric, it divides it with 1000 in the end. If the input 
#     files were the same, the metric should be calculated to be 0.


python3 top1M-umbrella-alexa-comparison.py ../data/censys.io/example_alexa1M.json ../data/censys.io/example_umbrella1M.json --top 25 
python3 top1M-umbrella-alexa-comparison.py ../data/censys.io/example_alexa1M.json ../data/censys.io/example_umbrella1M.json --top 25 --csv

