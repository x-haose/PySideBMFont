import asyncio
import functools
import sys

import qasync
from PySide6.QtCore import QLocale
from PySide6.QtWidgets import QApplication
from qfluentwidgets import FluentTranslator

from bmfont.ui.view.main import MainWindow


async def async_main():
    def close_future(_future):
        loop = asyncio.get_event_loop()
        loop.call_later(10, _future.cancel)
        _future.cancel()

    future = asyncio.Future()

    app = QApplication.instance()
    if hasattr(app, "aboutToQuit"):
        getattr(app, "aboutToQuit").connect(
            functools.partial(close_future, future)
        )

    locale = QLocale(QLocale.Chinese, QLocale.China)
    translator = FluentTranslator(locale)
    app.installTranslator(translator)

    window = MainWindow()
    window.show()
    await future


def main():
    try:
        qasync.run(async_main())
    except asyncio.exceptions.CancelledError:
        sys.exit(0)


if __name__ == '__main__':
    main()
