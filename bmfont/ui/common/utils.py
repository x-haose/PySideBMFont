import asyncio
import inspect
from typing import Callable

from PySide6.QtWidgets import QAbstractButton
from qfluentwidgets import MessageBox


def add_btn_click_event(
        btn: QAbstractButton,
        func: Callable,
        click_text: str = "",
        *args, **kwargs
):
    """
    给按钮添加点击事件
    Args:
        btn: 按钮
        func: 点击事件
        click_text: 点击过程中按钮显示的文字

    Returns:

    """
    btn_text = btn.text()
    click_text = click_text or btn_text

    async def _async_cb():
        if inspect.iscoroutinefunction(func):
            await func(*args, **kwargs)
        else:
            func(*args, **kwargs)

    def _cb():
        btn.setText(click_text)
        btn.setDisabled(True)
        task = asyncio.create_task(_async_cb())
        task.add_done_callback(_done)

    def _done(_):
        btn.setDisabled(False)
        btn.setText(btn_text)

    getattr(btn, "clicked").connect(_cb)


def show_message_box(
        parent,
        title: str,
        content: str = "",
        yes_cb: Callable = None,
        hide_yes_btn: bool = False,
        hide_cancel_btn: bool = False,
        yes_text: str = None,
        cancel_text: str = None,
):
    mb = MessageBox(title, content, parent)
    hide_cancel_btn and mb.cancelButton.hide()
    hide_yes_btn and mb.yesButton.hide()
    yes_text and mb.yesButton.setText(yes_text)
    cancel_text and mb.cancelButton.setText(cancel_text)
    if mb.exec() and yes_cb:
        yes_cb()
