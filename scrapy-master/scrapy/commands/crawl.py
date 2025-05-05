from __future__ import annotations

from typing import TYPE_CHECKING, cast

from twisted.python.failure import Failure

from scrapy.commands import BaseRunSpiderCommand
from scrapy.exceptions import UsageError

if TYPE_CHECKING:
    import argparse


class Command(BaseRunSpiderCommand):
    """Custom Scrapy command to run a single spider."""
    requires_project = True

    def syntax(self) -> str:
        return "[options] <spider>"

    def short_desc(self) -> str:
        return "Run a spider"

    def run(self, args: list[str], opts: argparse.Namespace) -> None:
        if not args:
            raise UsageError("You must specify a spider to run.")
        if len(args) > 1:
            raise UsageError("Only one spider can be run at a time.")

        spider_name = args[0]

        if not self.crawler_process:
            raise RuntimeError("Crawler process not initialized.")

        crawl_defer = self.crawler_process.crawl(spider_name, **opts.spargs)

        result = getattr(crawl_defer, "result", None)
        if isinstance(result, Failure) and issubclass(result.type, Exception):
            self.exitcode = 1
            return

        self.crawler_process.start()

        if getattr(self.crawler_process, "bootstrap_failed", False) or \
           getattr(self.crawler_process, "has_exception", False):
            self.exitcode = 1