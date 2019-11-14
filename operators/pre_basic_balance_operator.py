'''
barra beta因子计算程序
'''
from common import db
from operators.operator import Operator
from utils.data_util import *
import time

class PreBasicBalanceOperator(Operator):
    schema= 'basicdb'
    table = 'basic_balance'

    @classmethod
    def load_data(cls, date, code_list=None):
        tuple_str = "("
        for s in report_period_generator(period=32):
            tuple_str += "'" + s + "',"
        tuple_str = tuple_str[:-1]
        tuple_str += ")"
        print(tuple_str)
        sql = '''
                SELECT
                    S_INFO_WINDCODE,
                    REPORT_PERIOD,
                    ACTUAL_ANN_DT,
                    STATEMENT_TYPE,
                    TOT_ASSETS AS total_assets,
                    TOT_SHRHLDR_EQY_EXCL_MIN_INT AS total_equities_exc_min,
                    TOT_SHRHLDR_EQY_INCL_MIN_INT AS total_equities_inc_min 
                FROM
                    wind.ASHAREBALANCESHEET
                WHERE
                    SUBSTR(S_INFO_WINDCODE, 1, 1) != 'A'
                    AND STATEMENT_TYPE in (408001000, 408004000, 408005000, 408050000)
                    AND REPORT_PERIOD in {}
        	'''.format(tuple_str)
        df = db.query_by_SQL("wind", sql)
        pd.set_option("display.max_columns", None)
        df = pd.merge(df, get_listed_stocks(), on="s_info_windcode")
        df.sort_values(by=["s_info_windcode", "report_period", "actual_ann_dt", "statement_type"], inplace=True)
        current_df = df.groupby(by="s_info_windcode").last()
        print(current_df.shape[0])
        snapshot_df = pd.DataFrame()
        for snapshot_date in report_period_generator(period=20):
            print(snapshot_date)
            df_slice = df[(df["actual_ann_dt"] <= snapshot_date) & (df["report_period"] <= snapshot_date)].copy()
            df_slice.sort_values(by=["s_info_windcode", "report_period", "actual_ann_dt", "statement_type"], inplace=True)
            df_slice = df_slice.groupby(by="s_info_windcode").last()
            print(df_slice.shape[0])


        print("Program Stoped!")
        time.sleep(100000)
        # whole_df = pd.DataFrame(columns=["trade_date", "code"])
        # end_date = datetime.datetime.strftime(datetime.datetime.strptime(date, "%Y%m%d") + datetime.timedelta(10), "%Y%m%d")
        # # print(date, end_date)
        # # for factor in ['total_assets', 'total_equities_exc_min', 'total_equities_inc_min',
        # #             'noncur_liabilities', 'total_liabilities',
        # #             'longterm_loan', 'bonds_payable', 'longterm_payable', 'preferred_stock',
        # #             "cash", "tradable_financialasset", "notes_receiveable", "accounts_receivable",
        # #             "inventory", "fixed_asset", "construction_inprogress", "intangible_asset",
        # #             "development_expenditure", "goodwill", "notes_payable", "accounts_payable"]:
        # for factor in ['total_assets', 'total_equities_exc_min', 'total_equities_inc_min',
        #             'noncur_liabilities']:
        # # for factor in ["goodwill",]:
        #     df=  make_financial_factor(date, end_date, factor, test_mode=True)
        #     df.rename(columns={'tradeday': 'trade_date', 'ticker': 'code'}, inplace=True)
        #     df = df[df["trade_date"] == date]
        #     whole_df = pd.merge(whole_df, df, how="outer")
        #     pd.set_option("display.max_columns", None)
        # print(whole_df)
        # return whole_df

    @classmethod
    def fit(cls, datas):
        return datas

    @classmethod
    def dump_data(cls, datas):
        '''
        数据存储默认方法，如有不同存储方式，子类可重写该方法。
        :param datas: dataframe 待存储数据，必须有trade_date字段，且不为空
        :return:
        '''
        print(datas)