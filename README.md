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


python3 topumbrella-alexa1m-comparison.py ../data/censys.io/certs_alexa/certs_alexa_20210501.json ../data/censys.io/cisco_umbrella/certs_cisco_20210501.json --top 25


