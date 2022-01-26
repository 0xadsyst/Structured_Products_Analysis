import csv
import os
from datetime import datetime, timedelta, timezone
import mibian as mb
import ftx

token = 'btc'
open_date = datetime(2020, 1, 3, tzinfo=timezone.utc)
days_between_files = 7

def get_price(date: datetime):
    
    t = date.timestamp()
    
    for p in price_data:
        p_time = p['time'] / 1000
        if p_time == t:
            return p['open']

    return None

ftx_client = ftx.FtxClient()

skew_data = []

price_data = ftx_client.get_historical_data(token + '/usd', 86400 * 7, start_time = open_date.timestamp())

directory = 'data/' + token + '/skew'
for filename in os.listdir(directory):
    f = os.path.join(directory, filename)

    if os.path.isfile(f):
        with open(f, 'r', encoding='utf-8-sig') as input_file:
            
            csv_reader = csv.DictReader(input_file)

            for row in csv_reader:
                
                
                expiry_date = datetime.fromtimestamp(int(row['expirationDate'])/1000, tz=timezone.utc)
                
                print('Calculating: Open Date = ' + str(open_date) + ' Expiry Date = ' + str(expiry_date))

                days_to_expiry = int((expiry_date - open_date).days)
                open_price = get_price(open_date)
                expiry_price = get_price(expiry_date)
                strike_price = float(row['strike'])
                vol = row['weightedIv']

                if not open_price is None and not expiry_price is None and float(vol) > 0:
                    option = mb.BS([open_price, strike_price, 0, days_to_expiry + (1/3)], volatility=vol)

                    skew_data.append({
                            'open_date' : open_date.strftime('%Y-%m-%d'),
                            'open_price' : open_price,
                            'expiry_date' : expiry_date.strftime('%Y-%m-%d'),
                            'expiry_price' : expiry_price,
                            'days_to_expiry' : days_to_expiry,
                            'strike' : strike_price,
                            'iv' : row['weightedIv'],
                            'call_price' : option.callPrice,
                            'put_price' : option.putPrice,
                            'delta' : option.callDelta
                    })
                else:
                    print('Error: Open Date = ' + str(open_date) + ' Expiry Date = ' + str(expiry_date))

        open_date += timedelta(days=days_between_files)

f = os.path.join(directory, 'combined/combined_skew_data.csv')
with open(f, 'w', newline='', encoding='utf-8-sig') as csvfile:
    fieldnames = skew_data[0].keys()
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for d in skew_data:
        writer.writerow(d)


