def differences(results, filename):
    """
    Just a quick function to see if the results parsed from the XML Trickle file are
    matching the EOD collated sales in the SQLServer database.

    :param results:
    :param filename:
    :return:
    """
    PLU = slice(25, 47)
    WEIGHTED = slice(97, 108)
    QUANTITY = slice(130, 154)
    SALES = slice(108, 130)

    holding_cell = dict()

    with file(filename) as f:
        headers = f.next()
        _ = f.next()
        for line in f:
            if '2014' in line:
                plu = line[PLU].strip()[1:]
                weighted = int(line[WEIGHTED].strip())
                quantity = float(line[QUANTITY].strip())
                sales = float(line[SALES].strip())

                if  weighted and quantity > 0:
                    result_total = sum([x["weight"] for x in results if x["product"] == plu.zfill(14)])/1000.0

                    if result_total != quantity:
                        print 'MISS {}.  Trickle={}, ISS45={}: Diff={}'.format(
                            plu, result_total, quantity, result_total-quantity
                        )