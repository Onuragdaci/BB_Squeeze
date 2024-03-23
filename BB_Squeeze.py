import pandas as pd
import pandas_ta as ta
import ssl
from urllib import request
import requests
import matplotlib.pyplot as plt

def Hisse_Temel_Veriler():
    url1="https://www.isyatirim.com.tr/tr-tr/analiz/hisse/Sayfalar/Temel-Degerler-Ve-Oranlar.aspx#page-1"
    context = ssl._create_unverified_context()
    response = request.urlopen(url1, context=context)
    url1 = response.read()
    df = pd.read_html(url1,decimal=',', thousands='.')                         #Tüm Hisselerin Tablolarını Aktar
    df=df[6]
    Hisseler=df['Kod'].values.tolist()
    return Hisseler

def Stock_Prices(Hisse,period=120,Bar=100):
    url = f"https://www.isyatirim.com.tr/_Layouts/15/IsYatirim.Website/Common/ChartData.aspx/IntradayDelay?period={period}&code={Hisse}.E.BIST&last={Bar}"
    r1 = requests.get(url).json()
    data = pd.DataFrame.from_dict(r1)
    data[['Volume', 'Close']] = pd.DataFrame(data['data'].tolist(), index=data.index)
    data.drop(columns=['data'], inplace=True)
    return data

def BBands_Squeeze(data,length=20,stdev=2,perct=2.5):
    df=data.copy()
    stdev=float(stdev)
    BBands=ta.bbands(df['Close'],length=20)
    BBands['Band_Width'] = BBands['BBU_'+str(length)+'_'+str(stdev)] - BBands['BBL_'+str(length)+'_'+str(stdev)]
    BBands['Band_Width_Percentage'] = (BBands['Band_Width'] / BBands['BBM_'+str(length)+'_'+str(stdev)]) * 100
    BBands['Squeeze'] = BBands.apply(lambda x: 1 if x['Band_Width_Percentage'] < perct else 0, axis=1)
    return BBands

def Plot_BBands_with_Squeze(Hisse,data,BBands,length=20,stdev=2):
    plt.close()
    stdev=float(stdev)
    last_10_squeeze = BBands['Squeeze'].iloc[-10:].tolist()
    last_perct=BBands['Band_Width_Percentage'].iloc[-1:].tolist()
    
    if 1 in last_10_squeeze:
        # Verileri ve Bollinger bantlarını çiz
        plt.figure(figsize=(10, 5))
        plt.plot(data.index, data['Close'], label='Close Price')
        plt.plot(BBands.index, BBands['BBU_'+str(length)+'_'+str(stdev)], label='Upper Band', color='green',linestyle='--')
        plt.plot(BBands.index, BBands['BBL_'+str(length)+'_'+str(stdev)], label='Lower Band', color='red',linestyle='--')
        plt.plot(BBands.index, BBands['BBM_'+str(length)+'_'+str(stdev)], label='Middle Band', color='blue',linestyle='--')
        last_squeeze_point = BBands[BBands['Squeeze'] == 1].index[-1]
        plt.axvline(x=last_squeeze_point, color='orange', linestyle='--', alpha=0.5)
        plt.legend()
        plt.title(f'{Hisse} Bollinger Bands Sıkışması')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.grid()
        plt.savefig(f'{Hisse}_BB_Sıkışması.png', bbox_inches='tight', dpi=200)
    else:
        return
    return
Hisseler=Hisse_Temel_Veriler()

for i in range(0,len(Hisseler)):
    print(Hisseler[i])
    try:
        P=240
        B=100
        L=20
        S=2
        Perc=2.5
        data=Stock_Prices(Hisseler[i],period=P,Bar=B)
        BBands=BBands_Squeeze(data,length=L,stdev=S,perct=Perc)
        Plot_BBands_with_Squeze(Hisseler[i],data,BBands,length=L,stdev=S)
    except:
        pass


