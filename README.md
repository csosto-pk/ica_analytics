# ica_analytics

python3 ica_analysis.py ../data/censys.io/cisco_umbrella/certs_cisco_20200602.json > certs_umbrella_results

./run_ica_analysis.sh

python3 topumbrella-alexa1m-comparison.py ../data/censys.io/certs_alexa/certs_alexa_20210501.json ../data/censys.io/cisco_umbrella/certs_cisco_20210501.json --top 25


