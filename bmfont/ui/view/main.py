from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QDragEnterEvent, QDropEvent, QIcon, QKeyEvent, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from qfluentwidgets import (
    FluentIcon,
    PrimaryPushButton,
    SubtitleLabel,
    TableWidget,
    setFont,
)

from bmfont.service import FontGenerator
from bmfont.ui.common.components import FontPreviewCard, FontSaveCard
from bmfont.ui.common.utils import add_btn_click_event, show_message_box


class MainWindow(QWidget):
    font_dict: dict[int, str] = {}
    images: list[str] = []

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("BitMapFontUi")

        self.label = SubtitleLabel("点击或拖入图片进行制作", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setTextColor(QColor(99, 99, 99))
        setFont(self.label, 24)

        self.btn_reset = PrimaryPushButton("重置", self)

        self.font_table = TableWidget(self)
        self.font_table.setWordWrap(False)
        self.font_table.setColumnCount(6)
        self.font_table.verticalHeader().hide()
        self.font_table.setHorizontalHeaderLabels(["图片", "ID", "X偏移", "Y偏移", "宽度", "高度"])
        self.font_table.resizeColumnsToContents()
        self.font_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.font_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.font_table.setSortingEnabled(True)

        self.prew_img = FontPreviewCard(icon=FluentIcon.FONT, title="预览", get_font_data_func=self.get_font_data)

        self.input_btn_generate = FontSaveCard(icon=FluentIcon.FONT, title="字体名称", btn_text="生成")
        self.font_opts_widget = QWidget()
        self.v_layout = QVBoxLayout(self.font_opts_widget)
        self.v_layout.addWidget(self.prew_img)
        self.v_layout.addWidget(self.font_table)
        self.v_layout.addWidget(self.input_btn_generate)
        self.v_layout.addWidget(self.btn_reset)
        self.font_opts_widget.hide()

        layout = QHBoxLayout(self)
        layout.addWidget(self.label, 1, Qt.AlignCenter)
        layout.addWidget(self.font_opts_widget)

        add_btn_click_event(self.btn_reset, self.on_click_reset)
        add_btn_click_event(self.input_btn_generate.btn_ui, self.on_click_generate)

        self.font_table.itemChanged.connect(self.on_item_changed)

        self.init_window()
        self.setAcceptDrops(True)

    def init_window(self):
        """
        初始化窗口
        Returns:

        """
        self.resize(900, 700)
        self.setWindowIcon(QIcon("./res/images/logo.png"))
        self.setWindowTitle("PySideBMFont")

        desktop = QApplication.screens()[0].availableGeometry()
        width, height = desktop.width(), desktop.height()
        self.move(width // 2 - self.width() // 2, height // 2 - self.height() // 2)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """
        拖拽开始
        Args:
            event:

        Returns:

        """
        event.accept()
        return super().dragEnterEvent(event)

    def dropEvent(self, event: QDropEvent) -> None:
        """
        拖拽结束
        Args:
            event:

        Returns:

        """
        images_ulrs = [url.toLocalFile() for url in event.mimeData().urls() if url.toLocalFile().endswith("png")]
        if not images_ulrs:
            return

        self.input_images(images_ulrs)

    def mouseReleaseEvent(self, event):
        """
        鼠标释放事件
        Args:
            event: 事件

        Returns:

        """
        if not self.acceptDrops():
            return
        images_ulrs = QFileDialog.getOpenFileNames(self, "选择图片", "D:\\work\\arts\\slots一版切图", "PNG Files(*.png);")[0]
        if not images_ulrs:
            return

        self.setAcceptDrops(False)
        self.input_images(images_ulrs)

    def keyPressEvent(self, event: QKeyEvent):
        """
        键盘按下事件
        Args:
            event: 事件

        Returns:

        """
        if event.key() != Qt.Key_Delete:
            return super().keyPressEvent(event)

        row_indexs = {row.row() for row in self.font_table.selectedItems()}
        for row_index in row_indexs:
            self.font_table.removeRow(row_index)
            img = self.font_dict.pop(row_index)
            del self.images[self.images.index(img)]

        if not self.images:
            self.on_click_reset()

        event.accept()
        return super().keyPressEvent(event)

    def input_images(self, paths: list[str]):
        """
        输入图片
        Args:
            paths: 图片路径列表

        Returns:

        """
        self.images.extend(paths)
        self.label.hide()
        self.font_opts_widget.show()

        for i, path in enumerate(self.images):
            self.font_dict[i] = path
            self.font_table.setRowCount(i + 1)

            # 设置第一列：图片
            icon_lab = QLabel()
            icon_pixmap = QPixmap(path)
            icon_lab.setPixmap(icon_pixmap)
            icon_lab.setAlignment(Qt.AlignHCenter)
            self.font_table.setCellWidget(i, 0, icon_lab)

            # 设置第二列：图片ID
            img_name = Path(path).stem
            data = img_name.split("_")[-1]
            data = str(int(data)) if data.isdigit() else data
            table_widget_item = QTableWidgetItem(data)
            table_widget_item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.font_table.setItem(i, 1, QTableWidgetItem(table_widget_item))

            # 设置第三列：X偏移
            xoffset = "0"
            item_x = QTableWidgetItem(xoffset)
            item_x.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.font_table.setItem(i, 2, QTableWidgetItem(item_x))

            # 设置第四列：Y偏移
            yoffset = "0"
            item_y = QTableWidgetItem(yoffset)
            item_y.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.font_table.setItem(i, 3, QTableWidgetItem(item_y))

            # 设置第五列：图片宽度
            item_w = QTableWidgetItem(str(icon_pixmap.width()))
            item_w.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.font_table.setItem(i, 4, QTableWidgetItem(item_w))

            # 设置第六列：图片高度
            item_h = QTableWidgetItem(str(icon_pixmap.height()))
            item_h.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.font_table.setItem(i, 5, QTableWidgetItem(item_h))

    def on_click_reset(self):
        """
        点击重置按钮
        Returns:

        """
        self.prew_img.setValue("")
        self.input_btn_generate.setValue("")
        self.font_table.clear()
        self.font_table.setHorizontalHeaderLabels(["图片", "ID", "X偏移", "Y偏移", "宽度", "高度"])
        self.font_opts_widget.hide()
        self.label.show()
        self.setAcceptDrops(True)
        self.images.clear()
        self.font_dict.clear()

    def on_item_changed(self, item: QTableWidgetItem):
        """
        当表格中的项被更改时调用
        """
        # 确保只有在 Id、X偏移 或 Y偏移 更改时才重新渲染预览
        if item.column() in (1, 2, 3):  # 1、2 和 3 分别是 ID、X偏移 和 Y偏移 的列索引
            self.update_preview()

    def update_preview(self):
        """
        更新预览
        """
        self.prew_img.setValue(self.prew_img.value)

    def get_font_data(self, char: str):
        """
        根据字符获取字体数据，用在预览
        Args:
            char: 字符

        Returns:
            字体图片数据
        """
        font_data = {}
        for row in range(self.font_table.rowCount()):
            image_path = self.font_dict[row]
            value = self.font_table.item(row, 1).text()
            xoffset = self.font_table.item(row, 2).text()
            yoffset = self.font_table.item(row, 3).text()
            width = self.font_table.item(row, 4).text()
            height = self.font_table.item(row, 5).text()

            if value == char:
                font_data = {
                    "path": image_path,
                    "x_offset": float(xoffset),
                    "y_offset": float(yoffset),
                    "width": float(width),
                    "height": float(height),
                }
                break

        return font_data

    def on_click_generate(self):
        """
        点击生成按钮
        Returns:

        """
        if not self.input_btn_generate.value.strip():
            show_message_box(self, "错误", "请输入保存名字", hide_cancel_btn=True)
            return

        character_data = []
        for row in range(self.font_table.rowCount()):
            image_path = self.font_dict[row]
            value = self.font_table.item(row, 1).text()
            xoffset = self.font_table.item(row, 2).text()
            yoffset = self.font_table.item(row, 3).text()

            character_data.append({"image_path": image_path, "value": value, "xoffset": xoffset, "yoffset": yoffset})

        folder = QFileDialog.getExistingDirectory(self, "选择文件夹", "D:\\work\\client-game\\assets")
        if not folder or not Path(folder).exists():
            return

        generator = FontGenerator(
            character_data=character_data, output_folder=folder, name=self.input_btn_generate.value
        )
        generator.generate_font()
        show_message_box(self, "生成成功", hide_cancel_btn=True)
        self.on_click_reset()
