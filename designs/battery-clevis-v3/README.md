# 电池底座与双耳支架一体件 v3：板厚2 mm（最新版）

相对v2仅修改电池板厚度，由1 mm改为2 mm，向上加厚1 mm。底面仍为Z=0，上表面由Z=1变为Z=2。底座外形112×54 mm不变，整件总高由33变为34 mm。

中央三个细槽继续填实；其他孔槽形状和位置不变，继续贯通。没有叠加加强底座；双耳直接从电池板底面延伸。双耳、耳根圆角、销孔方向及位置均不变。销轴沿短边左右方向，hook前后摆动。

双耳内净距15，外宽28，各厚6.5，耳宽20，销孔直径10；孔中心距底板下表面22 mm，最低点距下表面32 mm。坐标中心X=0、Y=-2.300636 mm。

- battery_with_clevis.step：单实体STEP模型。
- battery_with_clevis.stl：单位mm，100%比例切片打印。
- preview.png / review_drawing.pdf：外形核对图。
- build.py：CadQuery建模脚本。运行需要同目录source_battery.step及inputs中的hook_review.step和battery_v2.step。
- clearance_check.json：hook离散姿态检查数据，单位mm3。
- source_battery.step：原始1 mm输入备份，并非本版成品。

验证：板厚2 mm；与v2作布尔差验证，原有材料全部保留，唯一新增材料位于Z=1至2，体积等于原已填槽板的一层体积；单实体有效；STEP导出重新导入通过；hook前后±90度每5度采样无重叠。

未进行承重、疲劳、实际打印配合及整机安装空间验证。
