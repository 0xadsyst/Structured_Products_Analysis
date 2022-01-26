# Structure Product Analysis

## Overview

This repository provides the tools to backtest covered call and covered put vaults using data from GVol.

Note: The raw data retrieved from GVol is not included in this repository.

## Combining Files

The combine_skew_data.py script is designed to combine historical skew csv files downloaded from GVol. It retreives the open and expiry prices from FTX, and calculates theoretical (Black Scholes) option pricing and delta for each strike.

Files to be combined must be stored in *data/[token name]/skew*. All files in the folder will be processed in alphabetical order, and must be regularly spaced apart.

If using data from another source, the csv files must be formatted with the following data:

* expirationDate : Time of expiry (integer ms from Unix Epoch)
* weightedIv : Implied volatility (decimal number)
* strike : Strike price (integer)

In the script, the following parameters should be set according to the files to be processed:

* token: The name of the token (eg. eth, btc).
* open_date: The date of the first file.
* days_between_files : Number of days between each file to be processed.

## Calculating Vault Performance

The backtest_vault.py script calculates how a user deposit would performed for covered call and covered put vaults. The script is designed to calculate the performance for a number of tokens and different deltas in a single run. Each combination of token/delta will be output to a seperate file and saved as follows: *data/[token name]/output/[token_name]_[delta].csv*.

In the script, the following parameters should be set according to the files to be processed:

* tokens : The names of the tokens to be processed in a list (eg. ['eth', 'btc']).
* deltas : A list of deltas to run the backtest on as integers (eg. [10, 20, 30]).
* days_to_expiry : The number of days between the opening date of a position and the option expiry date.
* start_date : Date of first position open to start the backtest.
* end_date : Date of last position open to end the backtest.

The script will search for options positions that match the delta and expiry date.
The file with the input data must be stored in *data/[token name]/skew/combined/combined_skew_data.csv*. If the combine_skew_data script is used to generate the files, this will be done automatically.

The output data of the script has the following format:

* open_date : Starting date of the position (when the option is sold).
* open_price : Price at the time of position opening.
* expiry_date : Expiry date for the sold option.
* expiry_price : Price at the time of option expiry.
* strike_price_call : The strike price of the call option sold for the covered call.
* delta_call : The delta of the sold call option.
* premium_call : The premium received for the sold call option (in tokens).
* option_loss_call : The loss on the sold call option (in tokens). Zero if price is below strike price.
* percentage_profit_loss_call : The percentage profit/loss of the covered call position in decimal format (eg. 0.05 = 5% profit).
* vault_total_profit_loss_call : The total percentage profit/loss if a deposit is made and left in the vault until the end of the backtest.
* vault_apy_call : The annualized percentage gain/loss of the covered call vault if a deposit is made and left in the vault until the end of the backtest.
* strike_price_put : The strike price of the put option sold for the covered put.
* delta_put : The delta of the sold put option.
* premium_put : The premium received for the sold put option (in dollars). This is per single token option sold, for example, if ETH is $3000 at the time of opening, this will be the premium received per $3000 of stablecoins deposited.
* option_loss_put : The loss on the sold put option (in dollars). Zero if price is above strike price. This is per single token option sold, for example, if ETH is $3000 at the time of opening, this will be the loss per $3000 of stablecoins deposited.
* percentage_profit_loss_put : The percentage profit/loss of the covered put position in decimal format (eg. 0.05 = 5% profit).
* vault_total_profit_loss_put : The total percentage profit/loss if a deposit is made and left in the vault until the end of the backtest.
* vault_apy_put : The annualized percentage gain/loss of the covered put vault if a deposit is made and left in the vault until the end of the backtest.
