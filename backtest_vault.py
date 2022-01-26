import numpy
from datetime import datetime, timezone, timedelta
import csv

tokens = ['btc', 'eth']
deltas = [10, 20, 30]
days_to_expiry = 14
start_date = datetime(2020, 1, 3, tzinfo=timezone.utc)
end_date = datetime(2021, 12, 31, tzinfo=timezone.utc)

for token, delta in [(token, delta) for token in tokens for delta in deltas]:
    f_in = 'data/' + token + '/skew/combined/combined_skew_data.csv'

    with open(f_in, 'r', encoding='utf-8-sig') as csv_file:
        dict_reader = csv.DictReader(csv_file)
        data_list = list(dict_reader)

    open_date = start_date
    summary = []
    first_position = True

    while open_date < end_date:
        open_date_string = open_date.strftime("%Y-%m-%d")
        filtered_list = [x for x in data_list if x['open_date'] == open_date_string and x['days_to_expiry'] == str(days_to_expiry)]
        position_call = min(filtered_list, key=lambda x : abs((delta / 100) - float(x['delta'])))
        position_put = min(filtered_list, key=lambda x : abs(1 - (delta / 100) - float(x['delta'])))

        print('Call: ' + str(position_call))
        print('Put: ' + str(position_put))

        open_price = float(position_call['open_price'])
        expiry_price = float(position_call['expiry_price'])

        strike_price_call = float(position_call['strike'])
        strike_price_put = float(position_put['strike'])

        delta_call = float(position_call['delta'])
        delta_put = float(position_put['delta'])

        premium_call = float(position_call['call_price']) / open_price
        premium_put = float(position_put['put_price'])
        
        option_loss_call = (max(expiry_price, strike_price_call) - strike_price_call) / expiry_price
        option_loss_put = strike_price_put - min(expiry_price, strike_price_put)

        percentage_profit_loss_call = premium_call - option_loss_call
        percentage_profit_loss_put = (premium_put - option_loss_put) / open_price


        summary.append({
            'open_date' : open_date_string,
            'open_price' : open_price,
            'expiry_date' : position_call['expiry_date'],
            'expiry_price' : expiry_price,
            'strike_price_call' : strike_price_call,
            'delta_call' : delta_call,
            'premium_call' : premium_call,
            'option_loss_call' : option_loss_call,
            'percentage_profit_loss_call' : percentage_profit_loss_call,
            'vault_total_profit_loss_call' : 0,
            'vault_apy_call' : 0,
            'strike_price_put' : strike_price_put,
            'delta_put' : delta_put,
            'premium_put' : premium_put,
            'option_loss_put' : option_loss_put,
            'percentage_profit_loss_put' : percentage_profit_loss_put,
            'vault_total_profit_loss_put' : 0,
            'vault_apy_put' : 0,
            'days_to_end_date' : (end_date - open_date).days
        })

        open_date += timedelta(days = days_to_expiry)

    for p in summary:
        sub_list_call = [1 + x['percentage_profit_loss_call'] for x in summary if x['open_date'] >= p['open_date']]
        vault_total_profit_loss_call = numpy.prod(sub_list_call) - 1
        p['vault_total_profit_loss_call'] = vault_total_profit_loss_call
        p['vault_apy_call'] = vault_total_profit_loss_call * 365 / p['days_to_end_date']

        sub_list_put = [1 + x['percentage_profit_loss_put'] for x in summary if x['open_date'] >= p['open_date']]
        vault_total_profit_loss_put = numpy.prod(sub_list_put) - 1
        p['vault_total_profit_loss_put'] = vault_total_profit_loss_put
        p['vault_apy_put'] = vault_total_profit_loss_put * 365 / p['days_to_end_date']

    f_out = 'data/' + token + '/output/' + token + '_' + str(delta) + '.csv'

    with open(f_out, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=summary[0].keys())
        writer.writeheader()
        for r in summary:
            writer.writerow(r)

