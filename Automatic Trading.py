# -*- coding: utf-8 -*-
"""
Spyder Editor

# This is a short Python project I completed for a graduate level course. 

# Here a factor investing strategy designed by myself is bact-tested, with real market data from Yahoo Finance API 
# and automatic rebalancing methods.
 
"""
import numpy as np
import pandas as pd
import os
from pandas_datareader import data
from sklearn import linear_model
import random
import csv

class Get_Data:
    def __init__(self):
        pass
   
    def get_data(self):
        df = pd.read_csv('./ticker_universe.csv')
        ticker_u = df['ticker'].values.tolist()
        for i in range(len(ticker_u)):

            temp = ticker_u[i]

            if "SH" in temp:

                ticker_u[i] = ticker_u[i].replace("SH", "ss")
                
            else:
                pass

        myarray = np.asarray(ticker_u)
        p1 = data.DataReader(name=myarray, data_source="yahoo", start="2010-12-1", end="2014-10-31")
        p = p1.dropna(axis=2, how='all')
        return p


class Sell_Equities:
    def  __init__(self, initialPortfolio, equitiesToBeSold, datadictionary, i,frequency):
        self.initialPortfolio = initialPortfolio
        self.equitiesToBeSold = equitiesToBeSold
        self.datadictionary = datadictionary
        self.i = i
        self.frequency = freq
       
        
    def sellEquities(self):
    
        gain = 0    
        k =0 
    
        self.initialPortfolio = self.initialPortfolio.reset_index(drop=True)
    
        for ticker in self.initialPortfolio['Ticker']:
            if ticker in self.equitiesToBeSold:
                try:
                    currentPrice = self.datadictionary[ticker]['Close'][self.i]
                except:
                    currentPrice = self.datadictionary[ticker]['Close'][self.i-self.frequency]
                gain = gain + (currentPrice * self.initialPortfolio['Amount'][k])
            
            #Delete where No Ticker Exists
                self.initialPortfolio = self.initialPortfolio[self.initialPortfolio['Ticker'] != ticker]
            k = k + 1
    
        return gain, self.initialPortfolio
       
        
    
class Buy_Equities:
    def  __init__(self,initialPortfolio, equitiesToBeBought, datadictionary, i, portfolioFactor):
        self.initialPortfolio = initialPortfolio
        self.equitiesToBeBought = equitiesToBeBought
        self.datadictionary = datadictionary
        self.i = i
        self.portfolioFactor = portfolioFactor


    def buyEquities(self):
    #Cash Flow Profits
        loss = 0    
    
        self.initialPortfolio = self.initialPortfolio.reset_index(drop=True)
        for ticker in self.equitiesToBeBought:
        
        #Calculate all the Current Values
            currentPrice = self.datadictionary[ticker]['Close'][i]
            shares = (1/100)*self.portfolioFactor/currentPrice
            loss = loss + (1/100)*self.portfolioFactor
            temp = [ticker,currentPrice,shares]
        
        #Assign to the End
            self.initialPortfolio.loc[len(self.initialPortfolio)] = temp
        
        return loss, self.initialPortfolio

class result:
        
    def  __init__(self, initialPortfolio, datadictionary, i, portfolioFactor):
        self.initialPortfolio = initialPortfolio
        self.datadictionary = datadictionary
        self.i = i
        self.portfolioFactor = portfolioFactor    
   
    def rebalance(self):
    
        self.initialPortfolio = self.initialPortfolio.reset_index(drop= True)
        count=0    
        lossInRebalance = 0
        gainInRebalance = 0
    
        for ticker in self.initialPortfolio['Ticker']:
            currentPrice = self.initialPortfolio['Close'][count]
            oldShares = self.initialPortfolio['Amount'][count]
       
            new_shares = (1/100)*self.portfolioFactor/currentPrice
            diff = new_shares - oldShares
       
            if diff > 0:
                lossInRebalance = lossInRebalance + diff *currentPrice
                temp = [ticker, currentPrice, new_shares]
                self.initialPortfolio.loc[count] = temp
            if diff < 0:
                gainInRebalance = gainInRebalance + abs(diff)*currentPrice
                temp = [ticker, currentPrice, new_shares]
                self.initialPortfolio.loc[count] = temp
            else: pass
        
            count=count+1
   
        return lossInRebalance, gainInRebalance, self.initialPortfolio



def get_effecient_tickers(original_data):
    p_d = original_data.loc['Adj Close']
    ma = list(p_d.columns.values)
    return ma

def get_m_score(ticker, mkt_share, original_data):
    p = original_data.xs(ticker, axis=2)
    dframe = p.iloc[23:]
    
    dframe['Stock'] = ticker
    
    Returns = (p['Adj Close']/p['Adj Close'].shift(1))-1
    Returns = Returns.iloc[23:]
    dframe['Returns']=Returns
    
    Momentum = np.log((p['Adj Close'].shift(1)))-np.log((p['Adj Close'].shift(5)))
    Momentum = Momentum.iloc[23:]
    dframe['Momentum']= Momentum
    
    reversal = np.log((p['Adj Close'].shift(20)))-np.log((p['Adj Close'].shift(1)))
    reversal = reversal.iloc[23:]
    dframe['Reversal']= reversal
    
    Log_returns = np.log((p['Adj Close']))-np.log((p['Adj Close'].shift(1)))
    Volatility = pd.rolling_std(Log_returns, window=15)
    Volatility = Volatility.iloc[23:]
    dframe['Volatility']= Volatility
    
    average_volume = pd.rolling_mean(p['Volume'], window =15)
    average_volume = average_volume.iloc[23:]
    dframe['Average Volume'] = average_volume
    mkt_share = float(mkt_share.replace(",",""))
    dframe['Market Cap'] = dframe['Adj Close']*float(mkt_share)    
    
    if "SZ" in ticker:
        try:
            factors = pd.read_csv('./szss/sz/%s_factor.csv' %ticker,header=0)
            factors = factors.set_index('Date')
            
         
            dframe = dframe.merge(factors,left_index=True,right_index=True)
    
        except Exception as e:
            pass
            
            
    elif "SS" in ticker:
        try:
            factors = pd.read_csv('./szss/ss/%s_factor.csv' %ticker,header=0)
            factors = factors.set_index('Date')
            dframe = dframe.merge(factors,left_index=True,right_index=True)
        except Exception as e:
            pass
        
    else:
        pass

    Mscore = (0.1 * dframe['PB'] + 0.05*dframe['PCF'] + 0.25*dframe['PE'] 
    + 0.05*dframe['PS'] + 0.3*dframe['Momentum'] + 0.05*dframe['Reversal'] 
    + 0.2*dframe['Volatility'] )
    dframe['MScore']= Mscore
    return dframe
    

def construct_portfolio(t, data, PortVal):
    M_dframe = pd.DataFrame(columns = ['Ticker','MScore','Close','Amount', 'Average Volume', 'Market Cap'])
    g = [*data]
    M_dframe['Ticker']= g    
    for ind, ticker in enumerate(g):
        M_dframe ['MScore'][ind] = data[ticker]['MScore'][t]
        M_dframe ['Close'][ind]  = data[ticker]['Close'][t]
        M_dframe ['Amount'][ind] = (1/100)*PortVal/data[ticker]['Close'][t]
        M_dframe ['Average Volume'][ind]  = data[ticker]['Average Volume'][t]
        M_dframe ['Market Cap'][ind]  = data[ticker]['Market Cap'][t]
        
    M_dframe = M_dframe.sort_values('MScore', ascending=False)
    
    M_dframe = M_dframe[M_dframe['Average Volume']>1000000]
    
    M_dframe = M_dframe[M_dframe['Market Cap']>500000000]

    M_Portfolio = M_dframe[0:100]
    
    M_Portfolio = M_Portfolio.drop('MScore',1)
    M_Portfolio = M_Portfolio.drop('Average Volume',1)
    M_Portfolio = M_Portfolio.drop('Market Cap',1)
    M_Portfolio = M_Portfolio.fillna(0)

    return M_Portfolio


def port_value(oldPort, data, t,freq):
    
    value=0
    count=0
    
    for ticker in oldPort['Ticker']:
        if t <= freq:
            value = value + (data[ticker]['Close'][t] * oldPort['Amount'][count])
        else:
            value = value + (data[ticker]['Close'][t-freq] * oldPort['Amount'][count])
        count= count + 1
        
    return value 


def out_put(portV,transaction,profit,t,freq):
    csvlist = []

    j=0
    
    p_returns = []
    returns=0
    moving_mean=0
    sharpe =0
    md = 0
    highestPortVal = portV[0]
    
    for m in portV:
       #If at the First Scenario No RATIOS are Available
        if j!=0:
            returns=(m-portV[j-1])/portV[j-1]
            p_returns.append(returns)
            standard = np.std(p_returns)
            moving_mean = np.mean(p_returns)
            sharpe = (np.mean(p_returns)-0.03)/standard
        else:
            p_returns.append(returns)
            pass
        if m>highestPortVal:
            highestPortVal=m
            
        dd = (highestPortVal-m)/highestPortVal
        if dd>md:
            md=dd
        
        row = [t,portV[j],transaction[j],sharpe,profit[j],returns, moving_mean]
        
                
        t = t + freq
        
        
        csvlist.append(row)
        
        j=j+1
    
    
    csvlist.append(["Maximum Drawdown:",md])
    return csvlist    

    
datadict = {}

a1 = Get_Data()
a = a1.get_data()

df1 = pd.read_csv('./ticker_universe.csv')
all_ticker = df1['ticker'].values.tolist()
mkt_share = df1['mktshare'].values.tolist()


b = get_effecient_tickers(a)
 
mktshare_list = [0]*len(b)
i = 0
for index, item in enumerate(all_ticker):
    if item in b:        
        mktshare_list[i] = mkt_share[index]
        i = i+1


subsetData = random.sample(range(len(b)-1), 1000)


for i in subsetData:
    try:
        pDataFrame = get_m_score(b[i], mktshare_list[i], a)
        datadict[b[i]] = pDataFrame
    except:
        pass
     
t = 20

firstday = t

freq = 20

portV = 70000000


iport = construct_portfolio(t, datadict, portV)


portV_list =[]
portV_list.append(portV)
   
   
Balance_list = []
Balance_list.append(-portV-portV*0.007)
      
   
   
transaction_cost = []
transaction_cost.append(portV*0.007)


while t < 900:
    
    tempV = portV    
    t = t + 20
    oldPort = iport
    oldPort = oldPort.reset_index(drop=True)    
    
    portsum = port_value(oldPort, datadict, t,freq)
    portV=portsum
    select_equities = construct_portfolio(t, datadict, portV)
    
    sells = list(set(oldPort['Ticker']) - set(select_equities['Ticker']))

    AA = Sell_Equities(iport, sells, datadict, t,freq)
    earnings, iport = AA.sellEquities()

    buys = list(set(select_equities['Ticker']) - set(oldPort['Ticker']))

    BB = Buy_Equities(iport, buys, datadict, t, portV)
    spendings, iport = BB.buyEquities()
    
    RR = result(iport, datadict, t, portV)

    spending_r, earning_r, iport = RR.rebalance()

    portV_list.append(portV)

    transaction_c = (abs(earnings)+abs(spendings)+abs(spending_r)+abs(earning_r))*0.007
    transaction_cost.append(transaction_c)

    Balance = portV-tempV-transaction_c
    Balance_list.append(Balance)

    


data_f = out_put(portV_list,transaction_cost,Balance_list,firstday,freq)
data_f_df = pd.DataFrame(data_f, columns = ["Time","Portfolio Value",\
                         "Transaction Value", "Sharpe", "Profit/Loss", "One-Period Return", "Moving Average"])


data_f_df.to_csv('Table.csv', encoding='utf-8', index=False)
