# This program is free software: you can redistribute it and/or modify it under the
# terms of the Apache License (v2.0) as published by the Apache Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the Apache License for more details.
#
# You should have received a copy of the Apache License along with this program.
# If not, see <https://www.apache.org/licenses/LICENSE-2.0>.

"""
Application class implementation.
"""


# standard libs
import abc
from typing import NamedTuple, List

# internal libs
from . import cli
from . import config
from .logging import log


class exit_status:
    """Collection of exit status values."""
    success:            int = 0
    usage:              int = 1
    bad_argument:       int = 2
    bad_config:         int = 3
    keyboard_interrupt: int = 4
    runtime_error:      int = 5


class Application(abc.ABC):
    """
    Abstract base class for all application interfaces.
    """

    interface: cli.Interface = None
    ALLOW_NOARGS: bool = False

    def __init__(self, **parameters) -> None:
        """Direct initialization sets `parameters`."""
        for name, value in parameters.items():
            setattr(self, name, value)

    @classmethod
    def from_cmdline(cls, cmdline: List[str] = None) -> 'Application':
        """Initialize via command line arguments (e.g., `sys.argv`)."""
        return cls.from_namespace(cls.interface.parse_args(cmdline))

    @classmethod
    def from_namespace(cls, namespace: cli.Namespace) -> 'Application':
        """Initialize via existing namespace/namedtuple."""
        return cls(**vars(namespace))

    @classmethod
    def main(cls, cmdline: List[str] = None) -> int:
        """Entry-point for application."""

        try:
            if not cmdline:
                if hasattr(cls, 'ALLOW_NOARGS') and cls.ALLOW_NOARGS is True:
                    pass
                else:
                    print(cls.interface.usage_text)
                    return exit_status.usage

            app = cls.from_cmdline(cmdline)
            app.run()

            return exit_status.success

        except cli.HelpOption as help_text:
            print(help_text)
            return exit_status.usage

        except cli.ArgumentError as error:
            log.critical(error)
            return exit_status.bad_argument

        except KeyboardInterrupt:
            log.critical('keyboard-interrupt: going down now!')
            return exit_status.keyboard_interrupt

        except Exception as error:
            log.critical(f'uncaught exception occurred!')
            raise error

    @abc.abstractmethod
    def run(self) -> None:
        """Business-logic of the application."""
        raise NotImplementedError()