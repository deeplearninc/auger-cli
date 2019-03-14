import click
import sys
from contextlib import contextmanager
from auger.hub_api_client import HubApiClient

from .client import AugerClient

class AugerCLIClient(AugerClient):
    @contextmanager
    def cli_error_handler(self):

        try:
            yield
        except HubApiClient.FatalApiError as exc:
            self.print_exception(exc)
            sys.exit(1)
        except HubApiClient.InvalidParamsError as exc:
            self.print_exception(exc)
            sys.exit(1)
        except HubApiClient.RetryableApiError as exc:
            self.print_exception(exc)
            sys.exit(1)
        except HubApiClient.MissingParamError as exc:
            self.print_exception(exc)
            sys.exit(1)

pass_client = click.make_pass_decorator(AugerCLIClient, ensure=True)
