# utility_code

## parse_regmap/parse_regmap_v1.0.py
- 这是一个半自动，需要人工参与的regmap解析文档
  - 1.使用`adobe acrobat pro dc`，先把regmap.pdf 转为 html
  - 2.去除html中的一些标签：\<style>, style=xx, \<p>, 再生成一份临时的temp-1.html文档，这2步可以自动实现
  - 3.手动打开temp-1.html文档，并全选复制，新建 temp-2.xlsx文档，粘贴复制内容
  - 4.再使用程序自动解析temp-2.xlsx文档，并生成寄存器结构体头文件
- 原因
  - 使用`adobe acrobat pro dc`直接生成excel文档，存在丢失字段的问题，且字段也都是通过合并单元格，来实现pdf文档的排版
  - 使用`adobe acrobat pro dc`直接生成html文档，存在丢失寄存器行的问题，且html上对寄存器table的组织，有可能通过2个或以上的table进行分配，或者一个table中填充多个空行
  - 结合上述2种方式的优缺点，通过先转成html文档，再处理html，再复制到excel文档中，可有效避免上述的2种坑
  - 这也是本程序的由来
