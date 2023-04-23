import pandas as pd
from tqdm import tqdm

def make_sequence(df, df_n):
    df_seq_done = pd.DataFrame(columns=df.columns)
    seq_num = 1
    for kmid in tqdm(df_n.KMID.unique().tolist()):
        kmid_data = df_n[df_n.KMID == kmid].sort_values('Time_Stamp')
        seq_logs = []
        prev_time = None
            
        for i, row in kmid_data.iterrows():
            if prev_time and (pd.to_datetime(row['Time_Stamp']) - pd.to_datetime(prev_time)).seconds > 180:
                if any([log['URL'].str.contains('o/orderDone').any() for log in seq_logs]):
                    seq_df = pd.concat(seq_logs, ignore_index=True)
                    seq_df['seq'] = seq_num
                    df_seq_done = pd.concat([df_seq_done, seq_df], ignore_index=True)
                    seq_num += 1
                seq_logs = []
            seq_logs.append(row.to_frame().T)
            prev_time = row['Time_Stamp']
            
        if any([log['URL'].str.contains('o/orderDone').any() for log in seq_logs]):
            seq_df = pd.concat(seq_logs, ignore_index=True)
            seq_df['seq'] = seq_num
            df_seq_done = pd.concat([df_seq_done, seq_df], ignore_index=True)
    
    return df_seq_done


def main():
    df = pd.read_csv('labeling.csv')
    df = df.drop_duplicates() 
    df['Time_Stamp'] = pd.to_datetime(df['Time_Stamp'])
    df = df.sort_values(['KMID', 'Time_Stamp']).reset_index().iloc[:,1:]
    print('## 1')

    pay = df[df['URL'].str.contains('pay.naver')]
    u = pay.KMID.unique().tolist()
    user = pd.read_excel('dataset/Panel Infomation_KM.xlsx')
    user_pay = user.query('KMID in @u').reset_index().iloc[:,1:]
    df = df.query('KMID in @u').reset_index().iloc[:,1:]
    print('## 2')

    u_done = df[df['URL'].str.contains('orderDone')].KMID.unique().tolist() # 555명
    user_pay['결제여부'] = user_pay.KMID.apply(lambda x : '결제 O' if x in u_done else '결제 X')
    pay_n = pay.query('KMID not in @u_done').reset_index().iloc[:,1:]
    pay_y = pay.query('KMID in @u_done').reset_index().iloc[:,1:]
    print('## 3')

    q1 = pay_y[pay_y['URL'].str.contains('orderDone')].KMID.value_counts().quantile(0.25)
    q3 = pay_y[pay_y['URL'].str.contains('orderDone')].KMID.value_counts().quantile(0.75)
    iqr = q3 - q1
    user_outlier = pay_y[pay_y['URL'].str.contains('orderDone')].KMID.value_counts().reset_index().query('KMID > 18.5')['index'].values.tolist()
    df['outlier'] = df.KMID.apply(lambda x : '1' if x in user_outlier else '0')
    pay_y['outlier'] = pay_y.KMID.apply(lambda x : '1' if x in user_outlier else '0')
    print('## 4')

    df_n = pd.read_csv('df_y.csv')
    print('## 5')
    a = make_sequence(df, df_n)

    a.to_csv('이상치O_orderDoneO.csv', index = False)


if __name__=='__main__':
    main()
