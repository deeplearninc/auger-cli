import click
import sys
from contextlib import contextmanager

from .client import AugerClient

class AugerCLIClient(AugerClient):
    @contextmanager
    def cli_error_handler(self):
        from coreapi.exceptions import ErrorMessage, LinkLookupError, ParseError        
        try:
            yield
        except ErrorMessage as exc:
            self.print_exception(exc)
            sys.exit(1)
        except LinkLookupError as exc:
            self.print_exception(exc)
            sys.exit(1)
        except ParseError as exc:
            self.print_line('Error connecting to {0}'.format(self.coreapi_url), err=True)
            sys.exit(1)
        except Exception as exc:
            self.print_exception(exc)
            sys.exit(1)

pass_client = click.make_pass_decorator(AugerCLIClient, ensure=True)
