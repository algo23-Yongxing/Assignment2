import pandas as pd
import rqdatac as rq
from rqdatac import *
rq.init('17827067076','123456')
print(rq.user.get_quota())
data = rq.get_price('601318.XSHG','20100101','20230520',frequency='1m')
df = pd.DataFrame(data)
df.to_csv(r'D:\CUHK\23Term2\MFE 5210\Project\marketdata\pingan_1min.csv')