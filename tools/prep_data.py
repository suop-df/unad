import pandas as pd
import json

df = pd.read_excel(r'E:\empenho\exportar.xlsx', engine='openpyxl')
for col in ['NOUG', 'NUNE', 'NOEVENTO']:
    df[col] = df[col].str.strip()

df['VADOCUMENTO'] = df['VADOCUMENTO'].round(2)

data = df[['COUG','NOUG','NUNE','COFONTE','INDESTINACAO','CONATUREZA','GND','NOEVENTO','VADOCUMENTO']].to_dict(orient='records')

with open(r'E:\empenho\dados.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, separators=(',',':'))

ugs = df.groupby(['COUG','NOUG']).size().reset_index()[['COUG','NOUG']].sort_values('NOUG').to_dict(orient='records')
fontes = sorted([int(x) for x in df['COFONTE'].unique().tolist()])

with open(r'E:\empenho\meta.json', 'w', encoding='utf-8') as f:
    json.dump({'ugs': ugs, 'fontes': fontes}, f, ensure_ascii=False)

print('done', len(data), 'records')
