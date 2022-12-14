# -*- coding: utf-8 -*-
"""model_selection

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1X8B2ADmyxpJ66yy8lXCnsENsJ8SmMWw-
"""

# Commented out IPython magic to ensure Python compatibility.
# %load_ext autoreload
# %aimport data_creater
# %autoreload 1

from data_creater import *

stocks = companies()
tickers = stocks.values.tolist()

#Select stock to perform tests
ticker = tickers[2][1]

print("Stock ticker selected for testing: {}".format(ticker))

import numpy as np
import pandas as pd

from keras.models import Sequential
from keras.layers import Dense, LSTM, Dropout, Bidirectional
from keras.optimizers import RMSprop

def fixed_model(X,y, learn_rate):
    model = Sequential()
    model.add(LSTM(5,input_shape=(X.shape[1:])))
    model.add(Dense(y.shape[1], activation='tanh'))
      
    # compile the model
    optimizer = RMSprop(lr=learn_rate)
    model.compile(loss='mean_squared_error', optimizer=optimizer)
    return model

def dynamic_model(X,y, learn_rate):
    model = Sequential()
    model.add(LSTM(X.shape[1],input_shape=(X.shape[1:])))
    model.add(Dense(y.shape[1], activation='tanh'))
      
    # compile the model
    optimizer = RMSprop(lr=learn_rate)
    model.compile(loss='mean_squared_error', optimizer=optimizer)
    return model

def bidirectional_model(X,y, learn_rate):
    model = Sequential()
    model.add(Bidirectional(LSTM(X.shape[1],return_sequences=False), input_shape=(X.shape[1:])))
    model.add(Dense(X.shape[1]))
    model.add(Dense(y.shape[1], activation='tanh'))
      
    # compile the model
    optimizer = RMSprop(lr=learn_rate)
    model.compile(loss='mean_squared_error', optimizer=optimizer)
    return model

def stacked_model(X,y, learn_rate):
    model = Sequential()
    model.add(LSTM(10,return_sequences=True, input_shape=(X.shape[1:])))
    model.add(LSTM(5))
    model.add(Dense(y.shape[1], activation='tanh'))
      
    # compile the model
    optimizer = RMSprop(lr=learn_rate)
    model.compile(loss='mean_squared_error', optimizer=optimizer)
    return model

#Create list of our models for use by the testing function.
models =[]
models.append(("Fixed",fixed_model))
models.append(("Dynamic",dynamic_model))
models.append(("Bidirectional",bidirectional_model))
models.append(("Stacked",stacked_model))

from collections import OrderedDict

def test_model(ticker,epochs,models,seq,window_sizes):
    #test result data
    sizes = []
    #seq_name = []
    model_name = []
    train_errors = []
    test_errors = []
    param_count = []
    
    for window_size in window_sizes:
        print("\nWindow size: {}".format(window_size))
        print('----------------')
        for model_item in models:
            seq_obj = seq[1](ticker,window_size,1)
            X_train,y_train,X_test,y_test = split_data(seq_obj)
            model = model_item[1](X_train,y_train,0.001)
            
            # fit model!
            model.fit(X_train, y_train, epochs=epochs, batch_size=50, verbose=0)

            # print out training and testing errors
            training_error = model.evaluate(X_train, y_train, verbose=0)
            testing_error = model.evaluate(X_test, y_test, verbose=0)
            msg = " > Model: {0:<15} Param count: {1:} \tTraining error: {2:.4f}\tTesting error: {3:.4f}"
            print(msg.format(model_item[0],model.count_params(),training_error,testing_error))

            #update result variables
            param_count.append(model.count_params())
            sizes.append(window_size)
            #seq_name.append(seq[0])
            model_name.append(model_item[0])
            train_errors.append(float("{0:.4f}".format(training_error)))
            test_errors.append(float("{0:.4f}".format( testing_error)))

    table= OrderedDict()
    table['Window Size'] = sizes
    table['Sequence Name'] =  [seq[0] for _ in range(len(sizes))]
    table['Model Name'] = model_name
    table['Ticker'] = [ticker for _ in range(len(sizes))]
    table['Training Error'] = train_errors
    table['Testing Error'] = test_errors
    table['Param Count'] = param_count
        
    return table


def update_test_table(*argv):
    file_path = "./data/model_test.csv"
    
    table = pd.read_csv(file_path)
    tickers = set( table['Ticker'].values.tolist())
    
    for item in argv:

        #first check if already exist 
        check = item['Ticker'][0]
        if check in tickers:
            #drop items
            idx = table[(table['Ticker']== check)  &  (table['Sequence Name']== item['Sequence Name'][0])].index
            table =  table.drop(idx)

        #append current test
        table = table.append(pd.DataFrame(item))

    table = table.reset_index(drop=True)
    table.to_csv(file_path, index = False)

def get_test_table():
    file_path = "./data/model_test.csv"
    return pd.read_csv(file_path)

seed = 7
np.random.seed(seed)

#Model testing variables
epochs =100
window_sizes =[5,7,10,20]

print("*** Simple Sequence Model Test for {} ***".format(ticker))
print("=" * 45)

seq_name = ('Simple',SimpleSequence)

test_1  = test_model(ticker,epochs,models,seq_name,window_sizes)
update_test_table(test_1)

print("*** Multi Sequence Model Test for {} ***".format(ticker))
print("=" * 45)

seq_name = ('Multi',MultiSequence)

test_2  = test_model(ticker,epochs,models,seq_name,window_sizes)
update_test_table(test_2)

table = get_test_table()

pd.pivot_table(table, values=['Training Error','Testing Error'], index=['Sequence Name']
               ,aggfunc={'Training Error':np.mean, 'Testing Error':np.mean} )

pd.pivot_table(table, values=['Training Error','Testing Error'], index=['Ticker','Window Size']
               ,aggfunc={'Training Error':np.mean, 'Testing Error':np.mean} )

pd.pivot_table(table, values=['Training Error','Testing Error'], index=['Sequence Name','Window Size']
               ,aggfunc={'Training Error':np.mean, 'Testing Error':np.mean} )

pd.pivot_table(table, values=['Training Error','Testing Error'], index=['Model Name']
               ,aggfunc={'Training Error':np.mean, 'Testing Error':np.mean} )

pd.pivot_table(table, values=['Training Error','Testing Error'], index=['Sequence Name' ,'Model Name']
               ,aggfunc={'Training Error':np.mean, 'Testing Error':np.mean} )

pd.pivot_table(table, values='Param Count', index=['Sequence Name','Model Name'], columns=['Window Size'])

def live_model(X,y, learn_rate,dropout):
    model = Sequential()
    model.add(Bidirectional(LSTM(X.shape[1],return_sequences=False), input_shape=(X.shape[1:])))
    model.add(Dense(X.shape[1]))
    model.add(Dropout(dropout))
    model.add(Dense(y.shape[1], activation='tanh'))
    
    # compile the model
    optimizer = RMSprop(lr=learn_rate)
    model.compile(loss='mean_squared_error', optimizer=optimizer)
    return model

# Commented out IPython magic to ensure Python compatibility.
# %matplotlib inline
import matplotlib.pyplot as plt

window_size = 10
dropouts =  [0.0,0.25,0.4,0.50]
learn_rates = [0.01,0.001,0.0001]
batch_size = 50
epochs_live = 100

def test_live(X_train,y_train,X_test,y_test):
    best_model = None
    lowest_test_error = 2.0
    best_learn_rate = 0.0
    best_dropout_rate = 0.0
    for rate in learn_rates:
        print("\nLearn rate: {0:.4f}".format(rate))
        print('---------------------')
        lengend = []
        for dropout in dropouts:
            model = live_model(X_train,y_train,rate,dropout)
            history = model.fit(X_train, y_train, epochs=epochs_live, batch_size=batch_size, verbose=0)

            # print out training and testing errors
            training_error = model.evaluate(X_train, y_train, verbose=0)
            testing_error = model.evaluate(X_test, y_test, verbose=0)
            msg = " > Dropout: {0:.2f} Training error: {1:.4f}\tTesting error: {2:.4f}"
            print(msg.format(dropout, training_error,testing_error))
            
            #check if test error
            if lowest_test_error > testing_error:
                best_model = model
                lowest_test_error = testing_error
                best_learn_rate = rate
                best_dropout_rate = dropout
                
            #plot loss function
            plt.plot(history.history['loss'])
            lengend.append("Drop {0:.4f}".format(dropout)) 
    
        plt.title("Learn rate {0:.4f}".format(rate))
        plt.xlabel('epochs')
        plt.ylabel('loss')
        plt.legend(lengend,loc='center left', bbox_to_anchor=(1, 0.5))
        plt.show()
    
    return (best_model,lowest_test_error,best_learn_rate,best_dropout_rate)


seq_obj = MultiSequence(ticker,window_size,1)
dataset = seq_obj.original_data
X_train,y_train,X_test,y_test = split_data(seq_obj)

print("*** Live Model Testing ***")
print("=" * 40)        
results = test_live(X_train,y_train,X_test,y_test)


print("*** Best Live Model Summary***")
print("=" * 40) 
print("Testing error: {0:.4f}".format(results[1]))
print("Best learning rate: {}".format(results[2]))
print("Best dropout rate: {}".format(results[3]))

#get fourt tickers to perform out epoch test
ticker_epochs = [tickers[i][1] for i in range(4)]

window_size = 10
dropout_rate = 0.25
epochs_list = [50,100,200,500,1000]
batch_size = 50
learn_rate = 0.001

def test_epochs():
    """
    
    """
    for symbol in ticker_epochs:
        print("\nSymbol: {}".format(symbol))
        print('---------------------')
        seq_obj = MultiSequence(symbol,window_size,1)
        X_train,y_train,X_test,y_test = split_data(seq_obj)
        lowest_test_error = 2.0
        best_epoch = 0
        for epoch in epochs_list:
            model = live_model(X_train,y_train,learn_rate,dropout_rate)
            model.fit(X_train, y_train, epochs=epoch, batch_size=batch_size, verbose=0)

            # print out training and testing errors
            training_error = model.evaluate(X_train, y_train, verbose=0)
            testing_error = model.evaluate(X_test, y_test, verbose=0)
            msg = " > Epoch: {0:} \tTraining error: {1:.4f}\tTesting error: {2:.4f}"
            print(msg.format(epoch, training_error,testing_error))

            if lowest_test_error > testing_error:
                lowest_test_error = testing_error
                best_epoch = epoch
        
        #print best epoch for symbol
        print(" ==> Best epoch {0:} with testing error of {1:.4f}".format(best_epoch,lowest_test_error))

print("*** Epoch Model Testing ***")
print("=" * 40)        
test_epochs()

# Commented out IPython magic to ensure Python compatibility.
# %matplotlib inline
import matplotlib.pyplot as plt

ticker = tickers[0][1]
window_sizes = [5,7,10]
dropouts =  [0.0,0.25,0.4]
learn_rates = [0.01,0.001]
epochs = [100,200,500]
batch_size = 50

def best_model(ticker, window_sizes, learn_rates, dropouts, epochs, batch_size):
    """
    
    """
    #our best model variables
    best_model = None
    lowest_test_error = 2.0
    best_training_error =0.0
    best_learn_rate = 0.0
    best_dropout_rate = 0.0
    best_epoch = 0
    best_window_size = 0
    
    counter = 1
    
    for window_size in window_sizes:
        print("\nWindow size: {}".format(window_size))
        print('---------------------')
        
        #prepare our sequence data
        seq_obj = MultiSequence(ticker,window_size,1)
        X_train,y_train,X_test,y_test = split_data(seq_obj)    
    
        for rate in learn_rates:
            for dropout in dropouts:
                for epoch in epochs:
                    model = live_model(X_train,y_train,rate,dropout)
                    model.fit(X_train, y_train, epochs=epoch, batch_size=batch_size, verbose=0)

                    # print out training and testing errors
                    training_error = model.evaluate(X_train, y_train, verbose=0)
                    testing_error = model.evaluate(X_test, y_test, verbose=0)
                    msg = " > Learn rate: {0:.4f} Dropout: {1:.2f}"
                    msg += " Epoch: {2:} Training error: {3:.4f} Testing error: {4:.4f}"
                    msg = str(counter) + "   " +msg.format(rate,dropout, epoch, training_error, testing_error)
                    print(msg)

                    #check if test error 
                    if lowest_test_error > testing_error:
                        best_model = model
                        lowest_test_error = testing_error
                        best_learn_rate = rate
                        best_dropout_rate = dropout
                        best_epoch = epoch
                        best_training_error = training_error 
                        best_window_size = window_size
                    
                    #increase our print counter
                    counter += 1
                        
    best_dict ={}
    best_dict["ticker"] = ticker
    best_dict["model"] = best_model
    best_dict["test_error"] =   "{0:.4f}".format(lowest_test_error) 
    best_dict["learn_rate"] = best_learn_rate
    best_dict["dropout"] = best_dropout_rate
    best_dict["epoch"] = best_epoch
    best_dict["train_error"] =  "{0:.4f}".format(best_training_error)  
    best_dict["window_size"] = best_window_size
    
    return best_dict


print("*** Best Model Selection for {} ***".format(ticker))
print("=" * 40)      
results = best_model(ticker, window_sizes, learn_rates, dropouts, epochs, batch_size)

print("*** Best Model Selected Summary for {} ***".format(results["ticker"]))
print("=" * 40) 

print("Window size: {}".format(results["window_size"]))
print("Train error: {}".format(results["train_error"]))
print("Testing error: {}".format(results["test_error"]))
print("Learning rate: {}".format(results["learn_rate"]))
print("Dropout rate: {}".format(results["dropout"]))
print("Epochs: {}".format(results["epoch"]))

seq_obj = MultiSequence(results["ticker"],results["window_size"],1)
dataset = seq_obj.original_data
X_train,y_train,X_test,y_test = split_data(seq_obj)

graph_prediction(results["model"], X_train,X_test,dataset,results["window_size"])