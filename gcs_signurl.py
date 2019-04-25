import re
import warnings
from datetime import datetime, timedelta

import click
from google.cloud.storage.blob import Blob
from google.cloud.storage.bucket import Bucket
from google.cloud.storage.client import Client
from google.oauth2 import service_account


def _DurationToTimeDelta(duration: str) -> timedelta:
    # Borrowed from here: https://github.com/GoogleCloudPlatform/gsutil/blob/master/gslib/commands/signurl.py#L186
    r"""Parses the given duration and returns an equivalent timedelta."""

    match = re.match(r"^(\d+)([dDhHmMsS])?$", duration)
    if not match:
        raise ValueError("Unable to parse duration string")

    duration, modifier = match.groups("h")
    duration = int(duration)
    modifier = modifier.lower()

    if modifier == "d":
        ret = timedelta(days=duration)
    elif modifier == "h":
        ret = timedelta(hours=duration)
    elif modifier == "m":
        ret = timedelta(minutes=duration)
    elif modifier == "s":
        ret = timedelta(seconds=duration)

    return ret


_duration_help = """
Specifies the duration that the signed url should be valid for.
Times may be specified with no suffix (default hours), or
with s = seconds, m = minutes, h = hours, d = days.
"""


@click.command("gcs-signurl")
@click.option("-d", "--duration", default="1h", show_default=True,
              help=_duration_help)
@click.argument("key_file", type=click.File())
@click.argument("resource")
def sign(duration: str, key_file: click.File, resource: str) -> None:
    """
    Generate a signed URL that embeds authentication data
    so the URL can be used by someone who does not have a Google account.

    This tool exists to overcome a shortcoming of gsutil signurl that limits
    expiration to 7 days only.

    KEY_FILE should be a path to a JSON file containing service account private key.
    See gsutil signurl --help for details

    RESOURCE is a GCS location in the form <bucket>/<path>
    (don't add neither "gs://" nor "http://...")

    Example: gcs-signurl /tmp/creds.json /foo-bucket/bar-file.txt
    """
    bucket_name, _, path = resource.lstrip("/").partition("/")
    creds = service_account.Credentials.from_service_account_file(key_file.name)
    till = datetime.now() + _DurationToTimeDelta(duration)

    # Ignoring potential warning about end user credentials.
    # We don't actually do any operations on the client, but
    # unfortunately the only public API in google-cloud-storage package
    # requires building client->bucket->blob
    message = "Your application has authenticated using end user credentials from Google Cloud SDK"
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message=message)
        client = Client()
    bucket = Bucket(client, bucket_name)
    blob = Blob(path, bucket)

    # Not passing version argument - to support compatibility with
    # google-cloud-storage<=1.14.0. They default to version 2 and hopefully
    # will not change it anytime soon.
    signed_url = blob.generate_signed_url(expiration=till, credentials=creds)
    click.echo(signed_url)
