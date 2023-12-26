from typing import Callable, Union

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QFrame, QGraphicsPixmapItem, QGraphicsScene, QGraphicsView
from qfluentwidgets import (
    ConfigItem,
    FluentIconBase,
    LineEdit,
    PrimaryPushButton,
    SettingCard,
)
from qfluentwidgets.common.config import qconfig


class InputSettingCard(SettingCard):
    """Setting card with switch button"""

    def __init__(
        self,
        icon: Union[str, QIcon, FluentIconBase],
        title: str,
        content=None,
        config_item: ConfigItem = None,
        parent=None,
    ):
        """
        Parameters
        ----------
        icon: str | QIcon | FluentIconBase
            the icon to be drawn

        title: str
            the title of card

        content: str
            the content of card

        config_item: ConfigItem
            configuration item operated by the card

        parent: QWidget
            parent widget
        """
        super().__init__(icon, title, content, parent)

        self.config_item = config_item
        self.input_ui = LineEdit()

        if config_item:
            self.setValue(qconfig.get(config_item))
            config_item.valueChanged.connect(self.setValue)

        # add switch button to layout
        self.hBoxLayout.addWidget(self.input_ui, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

        self.input_ui.textChanged.connect(self.setValue)

    def setValue(self, text: str):
        if self.config_item:
            qconfig.set(self.config_item, text)

        self.input_ui.setText(text)

    @property
    def value(self):
        return self.input_ui.text()


class FontSaveCard(InputSettingCard):
    """Setting card with switch button"""

    def __init__(self, icon: Union[str, QIcon, FluentIconBase], title: str, btn_text, parent=None):
        super().__init__(icon, title, "", parent)

        self.input_ui.setFixedWidth(300)
        self.btn_ui = PrimaryPushButton(btn_text)

        self.hBoxLayout.addWidget(self.btn_ui, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)


class FontPreviewCard(SettingCard):
    """Setting card with switch button"""

    def __init__(
        self,
        icon: Union[str, QIcon, FluentIconBase],
        title: str,
        get_font_data_func: Callable[[str], dict],
        parent=None,
    ):
        super().__init__(icon, title, "", parent)

        self.get_font_data_func = get_font_data_func
        self.input_ui = LineEdit()
        self.input_ui.setFixedWidth(300)

        self.preview_scene = QGraphicsScene()
        self.preview_view = QGraphicsView(self)
        self.preview_view.setScene(self.preview_scene)
        self.preview_view.setFixedSize(400, self.input_ui.height())
        self.preview_view.setFrameShape(QFrame.Shape.NoFrame)
        self.preview_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.hBoxLayout.addWidget(self.preview_view, 0, Qt.AlignRight)
        self.hBoxLayout.addWidget(self.input_ui, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

        self.input_ui.textChanged.connect(self.setValue)

    @property
    def value(self):
        return self.input_ui.text()

    def setValue(self, value: str):
        self.input_ui.setText(value)
        self.preview_scene = QGraphicsScene()
        self.preview_view.setScene(self.preview_scene)

        offset = 30  # 调整的位置偏移量，可以根据需要调整

        for _index, char in enumerate(value):
            img_data = self.get_font_data_func(char)
            if not img_data:
                continue

            img_path = img_data["path"]
            x_offset = img_data["x_offset"]
            y_offset = img_data["y_offset"]
            width = img_data["width"]

            offset += x_offset

            # 创建QPixmap并设置图片
            pixmap = QPixmap(img_path)

            # 创建QGraphicsPixmapItem并设置位置
            pixmap_item = QGraphicsPixmapItem(pixmap)
            pixmap_item.setPos(offset, y_offset)

            # 添加新的图像项
            self.preview_scene.addItem(pixmap_item)

            offset += width

        # 调整预览视图的显示范围
        items_rect = self.preview_scene.itemsBoundingRect()
        self.preview_view.fitInView(items_rect, Qt.KeepAspectRatio)
