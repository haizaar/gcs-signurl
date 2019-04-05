import re
from datetime import datetime, timedelta

import click
from google.cloud.storage._signing import generate_signed_url
from google.oauth2 import service_account


BASE_URL = "https://storage.googleapis.com"


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

    This tool exists to overcome a shortcomming of gsutil signurl that limits
    expiration to 7 days only.

    KEY_FILE should be a path to a JSON file containing service account private key.
    See gsutil signurl --help for details

    RESOURCE is a GCS location in the form <bucket>/<path>
    (don't add neither "gs://" nor "http://...")

    Example: gcs-signurl /tmp/creds.json /foo-bucket/bar-file.txt
    """
    creds = service_account.Credentials.from_service_account_file(key_file.name)
    till = datetime.now() + _DurationToTimeDelta(duration)
    signed_url = generate_signed_url(creds, resource, till)
    full_url = BASE_URL + signed_url
    click.echo(full_url)
