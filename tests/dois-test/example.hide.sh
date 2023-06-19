curl -X PUT -H \
    "Content-Type: application/vnd.api+json" \
    --user CERN.JACOW:DataCite.cub-gwd \
    -d @example.hide.json \
    https://api.test.datacite.org/dois/10.18429/jacow-ipac-23-moa03 -i