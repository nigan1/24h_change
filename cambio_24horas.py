#pip install python-binance
from binance.client import Client
import pandas as pd
import numpy as np
import os
import time
from datetime import datetime
import telegram_send

#fecha
def current_date_format(date):
    months = ("Enero", "Febrero", "Marzo", "Abri", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre")
    day = date.day
    month = months[date.month - 1]
    year = date.year
    messsage = "{} de {} del {}".format(day, month, year)

    return messsage



#direccion de raiz
path=os.path.abspath(os.path.dirname(__file__))

#conexion a binance
api_key=''
api_secret=''
client=Client(api_key=api_key, api_secret=api_secret)

#mostrar todas las columnas y filas
pd.set_option("display.max_rows", None, "display.max_columns", None)

while True:
    try:

        os.system('cls')
        print('Buscando cambios...')
        #cargar archivo con monedas anteriores
        oldcoin=pd.read_excel(f"{os.path.dirname(__file__)}\output.xlsx")
        #para formatear el volumen
        """
        oldcoin['Volumen'] = pd.to_numeric(oldcoin['Volumen'], downcast="float")
        oldcoin['Volumen']=oldcoin['Volumen'].apply(lambda x: f'{x//1000000000}B' if x/1000000000>=1 else f'{x//1000000}M' if x/1000000>=1 else f'{int(x//1000)}K' if x/10000>=1 else f'{x}')
        """           
        #monedas que cumplen los parametros
        newcoin=[]

        #consultar monedas de futuros
        futures_exchange_info = client.futures_ticker()

        #monedas que cumplen los parametros de volatidad para operar
        for element in futures_exchange_info:
            #Menos de 50M alerta al cambio de 10% en precio.
            if 'USDT' in element['symbol']:
                if any(chr.isdigit() for chr in element['symbol'])==False:


                    if float(element['quoteVolume'])<50000000:
                        if float(element['priceChangePercent'])>10 or float(element['priceChangePercent'])<-10:
                            newcoin.append(element)
                    
                    if 50000000<float(element['quoteVolume'])<100000000:
                        if float(element['priceChangePercent'])>7 or float(element['priceChangePercent'])<-7:
                            newcoin.append(element)

                    if float(element['quoteVolume'])>100000000:
                        if float(element['priceChangePercent'])>5 or float(element['priceChangePercent'])<-5:
                            newcoin.append(element)


        df = pd.DataFrame(newcoin)
        df=df[['symbol','lastPrice','quoteVolume','priceChangePercent']]
        df.columns=['Symbol', 'Precio','Volumen','Cambio']

        #insertar columna con la señal de compra/venta
        df['Cambio'] = pd.to_numeric(df['Cambio'],errors = 'coerce')
        df['Signal']=np.where(df['Cambio']<0,'BUY','SELL')

        #formateo el volumen para mejor visualizacion
        df['Volumen'] = pd.to_numeric(df['Volumen'], downcast="float")
        df['Volumen']=df['Volumen'].apply(lambda x: f'{x//1000000000}B' if x/1000000000>=1 else f'{x//1000000}M' if x/1000000>=1 else f'{int(x//1000)}K' if x/10000>=1 else f'{x}')

        #hallar diferente
        dfDif=df[-df['Symbol'].isin(oldcoin['Symbol'])]

        if len(dfDif)>0:
            now = datetime.now()
            #guardar en excel la tabla
            df.to_excel(f"{os.path.dirname(__file__)}\output.xlsx",index=False)
            
            for i,j in dfDif.iterrows():
                Symbol=j['Symbol']
                Precio=j['Precio']
                Volumen=j['Volumen']
                Cambio=j['Cambio']
                Signal=j['Signal']
                telegram_send.send(messages=[f"""⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️\n\n🪙: {Symbol}\n📈: {Signal}\n💶: {Precio}   \n🤯: {Cambio}\n🦾: {Volumen}\n{now.strftime('%H:%M:%S')}\n{current_date_format(now)}\nhttps://www.binance.com/es/futures/{Symbol} """])

        time.sleep(3)
    except KeyboardInterrupt:
        print('Programa detenido con exito!')
        break
        