# ica_analytics

This repository includes programs that process datasets from Censys.io which contain TLS certificate 
chain information from the Alexa Top1M and Cisco Umbrella Top1M sites. They analyze statistics 
regarding the certificate chains for the datasets, and the dataset comparison. 

## Alexa, Cisco Umbrella Top1M Analytics

More specifically, you can run analytics on JSON files generated by Censys.io that include the 
certificate chains for the Alexa or Cisco Umbrella Top1M sites. Examples of such datasets are in 
the [data directory](https://github.com/csosto-pk/ica_analytics/tree/main/data/censys.io).

To run analytics on such files, you can run in the 
[python directory](https://github.com/csosto-pk/ica_analytics/tree/main/python) 

    python3 ica_analysis.py ../data/censys.io/example_umbrella1M.json --top 100 --csv 
    python3 ica_analysis.py ../data/censys.io/example_umbrella1M.json --top 100 --verbose

When using the --csv option, the results output is in CSV format. 
The CSV output columns are 
  - \# of servers with 0 ICAs 
  - of servers with 1 ICA 
  - of servers with 2 ICAs 
  - of servers with 3 ICAs 
  - of servers with >3 ICAs 
  - \# of distinct servers seen 
  - \# self-signed certs seen
  - \# of non-CA/leaf certs seen
  - \# of certs w/o Subject_DN seen
  - \# of distinct ICAs seen (that would need to be cached)

Alternatively, you can run a bash script that runs analytics on all the Censys.io JSON files and 
stores the results in a CSV file. 
In the [python directory](https://github.com/csosto-pk/ica_analytics/tree/main/python), run 

    ./run_ica_analysis.sh 
    cat ../certs_results.csv

The program assumes all JSON files (for Alexa and Cisco Umbrella) are stored in two separate directories 
(certs_alexa and cisco_umbrella) in the CENSYS_IO_DIR 
[parent directory](https://github.com/csosto-pk/ica_analytics/tree/main/data/censys.io).


## Alexa - Cisco Umbrella Comparison

To run analytics on the difference between Alexa and Cisco Umbrella datasets, you can run in the 
[python directory](https://github.com/csosto-pk/ica_analytics/tree/main/python) 

    python3 top1M-umbrella-alexa-comparison.py ../data/censys.io/example_alexa1M.json \
                                     ../data/censys.io/example_umbrella1M.json --top 100 
    python3 top1M-umbrella-alexa-comparison.py ../data/censys.io/example_alexa1M.json \
                               ../data/censys.io/example_umbrella1M.json --top 100 --csv 

This program parses the Censys.io Alexa and Umbrella JSON files and returns statistics on the differences between 
the datasets. It takes two files as input. These are assumed to be the Alexa and Umbrella JSON files extracted from 
Censys.io for the same day for more accurate results. 

The first input file must contain Alexa rankings. And the second the Umbrella rankings. Otherwise the program 
will throw an error when trying to parse the "alexa_rank"/"cisco_rank" rankings in the JSON.

The program returns the statistical differences between the files. There are different metrics it calculates: 
  - the simplest one is the difference of the server domains. It calculates % of servers which exist in one 
    of the JSON files, but not both. The % of servers not existing in the other file is returned for each 
    file differntly. If the input files were the same, the metric should be calculated to be 0.
  - another metric is the diff of the rankings of the server domains divided by 1000000. For servers that exist 
    in both files it adds the difference of the ranking of these servers. If a server only exists in one file 
    it adds a difference of 1,000,000. To lower the metric, it divides it with 1000000 in the end. If the input 
    files were the same, the metric should be calculated to be 0.

When using the --csv option, the results output is in CSV format.
