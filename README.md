# utility_code

## parse_regmap/parse_regmap_v1.0.py
- 这是一个半自动，需要人工参与的regmap解析文档
- 1.使用`adobe acrobat pro dc`，先把regmap.pdf 转为 html
- 2.去除html中的一些标签：\<style>, style=xx, \<p>, 再生成一份临时的temp-1.html文档，这2步可以自动实现
- 3.手动打开temp-1.html文档，并全选复制，新建 temp-2.xlsx文档，粘贴复制内容
- 4.再使用程序自动解析temp-2.xlsx文档，并生成寄存器结构体头文件
