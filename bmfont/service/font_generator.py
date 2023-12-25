from collections import UserDict
from pathlib import Path

from loguru import logger
from PIL import Image


class FontData(UserDict):
    image_path: str
    value: str
    width: int
    height: int
    xoffset: int
    yoffset: int


class FontGenerator:
    def __init__(self, character_data: list[dict], output_folder: str, name: str):
        self.character_data = character_data
        self.output_folder = Path(output_folder)
        self.fnt_img_path = self.output_folder / f"{name}.png"
        self.fnt_cfg_path = self.output_folder / f"{name}.fnt"

    def generate_font(self) -> None:
        # 更新每张图片的尺寸
        for char_data in self.character_data:
            char_data["width"], char_data["height"] = self._get_character_size(char_data["image_path"])

        # 获取字符图片中最大的宽度和高度
        char_img_width = max(self.character_data, key=lambda data: data["width"])["width"]
        char_img_height = max(self.character_data, key=lambda data: data["height"])["height"]

        # 计算大图的尺寸
        fnt_img_width = (len(self.character_data) + 1) * char_img_width
        fnt_img_height = char_img_height

        logger.info(f"大图尺寸：width: {fnt_img_width} height: {fnt_img_height}")

        # 创建一个空白的大图
        combined_image = Image.new("RGBA", (fnt_img_width, fnt_img_height), (0, 0, 0, 0))

        # 创建fnt配置文件的内容
        fnt_lines = [
            f"info size={char_img_height} unicode=1 stretchH=100 smooth=1 aa=1 padding=0,0,0,0 spacing=1,1 outline=0 "
            f"common lineHeight={char_img_height} base={char_img_height} "
            f"scaleW={fnt_img_width} scaleH={fnt_img_height} pages=1 packed=0 "
            f'page id=0 file="{self.fnt_img_path}" '
            f"chars count={len(self.character_data)}"
        ]

        # 粘贴每个字符图片到大图上，并添加fnt配置信息
        x, y = 0, 0
        for _i, char_data in enumerate(self.character_data):
            image_path: str = char_data.get("image_path", "")
            character_value: str = char_data.get("value", "")
            xoffset: int = char_data.get("xoffset", 0)
            yoffset: int = char_data.get("yoffset", 0)
            character_image = Image.open(image_path).convert("RGBA")

            # 获取每个字符的实际宽高
            char_width, char_height = self._get_character_size(image_path)

            # 粘贴字符图片到大图上
            combined_image.paste(character_image, (x, y))

            # 添加字符的配置信息到fnt配置文件
            fnt_lines.append(
                f"char id={ord(character_value)} x={x} y={y} "
                f"width={char_width} height={char_height} "
                f"xoffset={xoffset} yoffset={yoffset} xadvance={char_width}"
            )

            # 更新坐标
            x += char_width
            if x >= fnt_img_width:
                x = 0
                y += char_img_height

        # 保存大图
        self.output_folder.mkdir(parents=True, exist_ok=True)
        if self.fnt_img_path.exists():
            self.fnt_img_path.unlink()
        combined_image.save(str(self.fnt_img_path))

        # 保存fnt配置文件
        if self.fnt_cfg_path.exists():
            self.fnt_cfg_path.unlink()
        self.fnt_cfg_path.write_text("\n".join(fnt_lines), encoding="utf8")

        logger.success("生成完成！")

    def _get_character_size(self, image_path: str) -> tuple[int, int]:
        character_image = Image.open(image_path)
        return character_image.size


def main():
    character_data = [
        {"image_path": "D:\\work\\arts\\slots一版切图\\上架素材\\火箭2\\切图\\wz_tip_0.png", "value": "0"},
        {"image_path": "D:\\work\\arts\\slots一版切图\\上架素材\\火箭2\\切图\\wz_tip_1.png", "value": "1"},
        {"image_path": "D:\\work\\arts\\slots一版切图\\上架素材\\火箭2\\切图\\wz_tip_2.png", "value": "2"},
        {"image_path": "D:\\work\\arts\\slots一版切图\\上架素材\\火箭2\\切图\\wz_tip_3.png", "value": "3"},
        {"image_path": "D:\\work\\arts\\slots一版切图\\上架素材\\火箭2\\切图\\wz_tip_4.png", "value": "4"},
        {"image_path": "D:\\work\\arts\\slots一版切图\\上架素材\\火箭2\\切图\\wz_tip_5.png", "value": "5"},
        {"image_path": "D:\\work\\arts\\slots一版切图\\上架素材\\火箭2\\切图\\wz_tip_6.png", "value": "6"},
        {"image_path": "D:\\work\\arts\\slots一版切图\\上架素材\\火箭2\\切图\\wz_tip_7.png", "value": "7"},
        {"image_path": "D:\\work\\arts\\slots一版切图\\上架素材\\火箭2\\切图\\wz_tip_8.png", "value": "8"},
        {"image_path": "D:\\work\\arts\\slots一版切图\\上架素材\\火箭2\\切图\\wz_tip_9.png", "value": "9"},
        {"image_path": "D:\\work\\arts\\slots一版切图\\上架素材\\火箭2\\切图\\wz_tip_10.png", "value": ","},
        {"image_path": "D:\\work\\arts\\slots一版切图\\上架素材\\火箭2\\切图\\wz_tip_11.png", "value": "."},
        {"image_path": "D:\\work\\arts\\slots一版切图\\上架素材\\火箭2\\切图\\wz_tip_x.png", "value": "x"},
    ]

    generator = FontGenerator(
        character_data=character_data, output_folder="D:\\work\\client-game\\assets\\images", name="wz_tw"
    )
    generator.generate_font()


if __name__ == "__main__":
    main()
