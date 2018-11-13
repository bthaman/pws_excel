"""
author: bill thaman
"""
from pws_list_v3 import *
import xlwings as xw
import msgbox


@xw.sub
def pws_names(cnty_name, sht_name='Sheet1', sort=True):
    sht = xw.Book.caller().sheets[sht_name]
    sht.book.app.screen_updating = False
    county_pws = CountyPWS()
    # get the pws names for the selected county
    d = county_pws.get_pws_names(cnty_name.upper())
    sht.range((6, 1), (6, 3)).expand().clear_contents()
    # clear_sheets()
    if sort:
        # sorted func returns a list
        d_ordered = sorted(d.items(), reverse=False)
        lst_names = [i[0] for i in d_ordered]
        lst_detail_urls = [i[1][0] for i in d_ordered]
        lst_summary_urls = [i[1][2] for i in d_ordered]
    else:
        # create lists from dict
        lst_names = list(d.keys())
        lst_urls = list(d.values())
        lst_detail_urls = [i[0] for i in lst_urls]
        lst_summary_urls = [i[2] for i in lst_urls]
    sht.range(6, 1).options(transpose=True).value = lst_names
    sht.range(6, 2).options(transpose=True).value = lst_detail_urls
    sht.range(6, 3).options(transpose=True).value = lst_summary_urls


@xw.sub
def pws_detail(url_detail, url_summary, detail='Detail', buyers='Buyers', purchases='Purchases',
               wells='Wells', sources='Sources'):
    """
    Called from Excel when user clicks hyperlink for a PWS
    :param url_detail:
    :param url_summary:
    :param detail:
    :param buyers:
    :param purchases:
    :param wells
    :param sources:
    :return:
    """
    get_buyers_and_purchases = True
    sht_detail = xw.Book.caller().sheets[detail]
    sht_sources = xw.Book.caller().sheets[sources]
    sht_wells = xw.Book.caller().sheets[wells]
    sht_buyers = xw.Book.caller().sheets[buyers]
    sht_purchases = xw.Book.caller().sheets[purchases]
    sht_detail.book.app.screen_updating = False
    pwsd = PWS_Detail()
    try:
        pwsd.get_detail(url_detail, url_summary, buyers=True, purchases=True)
    except Exception as e:
        msgbox.show_error('Python Error in get_detail', e)
    try:
        lrow_detail = sht_detail.range('A1').end('down').last_cell.row
        lrow_sources = sht_sources.range('A1').end('down').last_cell.row
        lrow_wells = sht_wells.range('A1').end('down').last_cell.row
        lrow_buyers = sht_buyers.range('A1').end('down').last_cell.row
        lrow_purchases = sht_purchases.range('A1').end('down').last_cell.row
        lrow_detail = lrow_detail if lrow_detail < 2**20 else 0
        lrow_sources = lrow_sources if lrow_sources < 2**20 else 0
        lrow_wells = lrow_wells if lrow_wells < 2**20 else 0
        lrow_buyers = lrow_buyers if lrow_buyers < 2**20 else 0
        lrow_purchases = lrow_purchases if lrow_purchases < 2**20 else 0

        sht_detail.range(lrow_detail + 1, 1).options(index=False, header=not lrow_detail).value = \
            pwsd.get_basic_detail()
        sht_sources.range(lrow_sources + 1, 1).options(index=False, header=not lrow_sources).value = \
            pwsd.get_sources()
        sht_wells.range(lrow_wells + 1, 1).options(index=False, header=not lrow_wells).value = \
            pwsd.get_wells()
        if get_buyers_and_purchases:
            sht_buyers.range(lrow_buyers + 1, 1).options(index=False, header=not lrow_buyers).value = \
                pwsd.get_buyers()
            sht_purchases.range(lrow_purchases + 1, 1).options(index=False, header=not lrow_purchases).value = \
                pwsd.get_purchases()
    except Exception as e:
        msgbox.show_error('Python Error', e)
    sht_detail.book.app.screen_updating = True


def clear_sheets():
    sht_detail = xw.Book.caller().sheets['Detail']
    sht_sources = xw.Book.caller().sheets['Sources']
    sht_wells = xw.Book.caller().sheets['Wells']
    sht_buyers = xw.Book.caller().sheets['Buyers']
    sht_purchases = xw.Book.caller().sheets['Purchases']
    sht_detail.range((1, 1), (1, 50)).expand().clear_contents()
    sht_sources.range((1, 1), (1, 50)).expand().clear_contents()
    sht_wells.range((1, 1), (1, 50)).expand().clear_contents()
    sht_buyers.range((1, 1), (1, 50)).expand().clear_contents()
    sht_purchases.range((1, 1), (1, 50)).expand().clear_contents()


def testit(cnty_name):
    county_pws = CountyPWS()
    pws_detail = PWS_Detail()
    # get the pws names for the selected county
    d_names = county_pws.get_pws_names(cnty_name.upper())
    # create lists from dict
    lst_urls = list(d_names.values())
    for u in lst_urls[:5]:
        pws_detail.get_detail(u)
    df_basic = pws_detail.get_basic_detail()
    print(df_basic)

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 2:
        wkbk_name = sys.argv[1]
        xw.Book(wkbk_name).set_mock_caller()
        if sys.argv[2] == 'pws_names':
            cnty_nm = sys.argv[3]
            sht_nm = sys.argv[4]
            pws_names(cnty_name=cnty_nm, sht_name=sht_nm)
        elif sys.argv[2] == 'pws_detail':
            url_det = sys.argv[3]
            url_summ = sys.argv[4]
            pws_detail(url_detail=url_det, url_summary=url_summ)
        elif sys.argv[2] == 'clear_sheets':
            clear_sheets()
