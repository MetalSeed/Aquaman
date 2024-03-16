# table_recognizer采集的OCR信息 在hands_converter里不同stage交叉校验
# 交叉校验数据集


IR = table()
RD = round()
HD = hand()

dict = table.get_table_dict()
RD.table2round(dict)

hands.add_round(RD)

dicision = get_decision(hands)

hands.add_hero_decision(dicision)


