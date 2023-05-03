import pandas as pd
from tqdm import tqdm
import argparse

def parser_args():
    parser = argparse.ArgumentParser(description='Preprocess')
    parser.add_argument(
        '--condition', 
        type = str, 
        default = 'orderDone', 
        help = 'orderDone / orderSheet'
    )

    args = parser.parse_args()

    return args
    

def make_sequence(df, condition):
    df_seq_done = pd.DataFrame(columns=df.columns)
    seq_num = 1
    for kmid in tqdm(df.KMID.unique().tolist()):
        kmid_data = df[df.KMID == kmid].sort_values('Time_Stamp')
        seq_logs = []
        prev_time = None
            
        for i, row in kmid_data.iterrows():
            if prev_time and (pd.to_datetime(row['Time_Stamp']) - pd.to_datetime(prev_time)).seconds > 180:
                if any([log['URL'].str.contains(condition).any() for log in seq_logs]):
                    seq_df = pd.concat(seq_logs, ignore_index=True)
                    seq_df['seq'] = seq_num
                    df_seq_done = pd.concat([df_seq_done, seq_df], ignore_index=True)
                    seq_num += 1
                seq_logs = []
            seq_logs.append(row.to_frame().T)
            prev_time = row['Time_Stamp']
            
        if any([log['URL'].str.contains(condition).any() for log in seq_logs]):
            seq_df = pd.concat(seq_logs, ignore_index=True)
            seq_df['seq'] = seq_num
            df_seq_done = pd.concat([df_seq_done, seq_df], ignore_index=True)
    
    return df_seq_done


def main():
    print('# Takes about 1 minute to load the data')

    args = parser_args()
    df = pd.read_csv('labeling.csv')
    df = df.drop_duplicates() 
    df['Time_Stamp'] = pd.to_datetime(df['Time_Stamp'])
    df = df.sort_values(['KMID', 'Time_Stamp']).reset_index().iloc[:,1:]

    pay_u = df[df['URL'].str.contains('pay.naver')].KMID.unique().tolist()
    df = df.query('KMID in @pay_u').reset_index().iloc[:,1:]
    print('## Data Load Complete')

    print('## Start to Preprocess Data')
    df_preprocessed = make_sequence(df, args.condition)
    df_preprocessed.to_csv(args.condition + '.csv', index = False)


if __name__=='__main__':
    main()