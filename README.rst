###########
gcs-signurl
###########

Generate a signed URL that embeds authentication data
so the URL can be used by someone who does not have a Google account.

This tool exists to overcome a shortcomming of gsutil signurl that limits
expiration to 7 days only.

KEY_FILE should be a path to a JSON file containing service account private key.
See gsutil signurl --help for details

RESOURCE is a GCS location in the form <bucket>/<path>
(don't add neither "gs://" nor "http://...")

Example: ``gcs-signurl /tmp/creds.json /foo-bucket/bar-file.txt``
