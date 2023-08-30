# %%
import numpy
import matplotlib.pyplot as plt
import random
from sklearn import linear_model 
from sklearn.preprocessing import PolynomialFeatures
import pandas as pd
import json
import math

# %%
#define Store params
openTimeOffset = (10 * 60) #10am * 60 minutes
openDuration = (13 * 60) # 13 hours * 60 minutes (11pm)
lunchDuration = 3 * 60 # 3 hours in minutes
DinnerDuration = 4 * 60 # 4 hours in minutes
lunchStartTimeInMinutes = openTimeOffset + (1* 60) #1 hour after open * 60 minutes (11am)
dinnerStartTimeInMinutes = openTimeOffset + (7 * 60) #7 hour after open * 60 minutes (5pm)
KitchenOrderLimit = 5
delayFactor = 1
baseNumofOrders = 150

orderItemTypesAndTimes = [
    {"item":"burger", "time":.5},
    {"item":"burger2", "time":.75},
    {"item":"wrap", "time":1},
    {"item":"salad", "time":1},
    {"item":"fries", "time":.25},
    {"item":"orings", "time":.35},
    {"item":"poppers", "time":.35},
    {"item":"drink", "time":.15},
    {"item":"bottledDrink", "time":.1},
    {"item":"shake", "time":1},
 ]

# %%
def plotOrderTimes(randomOrderTimes):
    plt.hist(randomOrderTimes, 13*6)
    plt.show() 

# %%
def plotOrdersPerMinute(openOrdersPerMinute):
    plotMinutes = []
    plotOrders = []
    for minute in openOrdersPerMinute:
        plotMinutes.append(minute[0])
        plotOrders.append(len(minute[1]))

    mymodel = numpy.poly1d(numpy.polyfit(plotMinutes, plotOrders, 10))

    myline = numpy.linspace(openTimeOffset, (openTimeOffset + openDuration), 100)
        
    plt.bar(plotMinutes, plotOrders)
    plt.plot(myline, mymodel(myline))
    plt.xlabel("Time in Minutes")
    plt.ylabel("Open Orders")
    plt.show() 
    plt.clf()

# %%
def plotOrderDelayPerOpenOrder(openOrdersPerMinute, orders):
    plotDelayTime = []
    plotOpenOrdersAtTime = []

    for order in orders:
        delaytime = GenerateData.calcDelayTime(order, openOrdersPerMinute)
    
        plotOpenOrdersAtTime.append(len(openOrdersPerMinute[order["orderTime"]-openTimeOffset][1]))
        plotDelayTime.append(delaytime)

        #print("OrderTime: " + str(order["orderTime"])
        #      +"\t[" + str(len(openOrdersPerMinute[order["orderTime"]-openTimeOffset][1]))
        #      + " , " + str(delaytime) + ']')


    plt.scatter(plotOpenOrdersAtTime, plotDelayTime)
    plt.ylabel("Order Delay Time")
    plt.xlabel("Open Orders")
    plt.show() 

# %%
orderTimes = creatRandomOrderTimes(baseNumofOrders)
orders = createOrders(len(orderTimes), 3)

mapOrdersToTimes(orders, orderTimes)

# %%
#openOrdersPerMinute = calcOpenOrdersPerMinute(orders)

#plotOrdersPerMinute(openOrdersPerMinute)

#plotOrderDelayPerOpenOrder(openOrdersPerMinute, orders)

# %%
weekOrders = []
weekOpenOrdersPerMinute = []

for i in range(7):
    dayOrders, dayOpenOrdersPerMinute = GenerateData.generateDataForOneDay(baseNumofOrders)
    weekOrders += dayOrders
    weekOpenOrdersPerMinute += dayOpenOrdersPerMinute

# %%
plotOrdersPerMinute(weekOpenOrdersPerMinute)

plotOrderDelayPerOpenOrder(weekOpenOrdersPerMinute, weekOrders)

for i in range(len(weekOrders)):
    timeEstimate = weekOrders[i]["completedTime"] - weekOrders[i]["estimatedCompletedTime"]
    #if len(weekOpenOrdersPerMinute[i][1]) < KitchenOrderLimit and timeEstimate > 0:
        #print("Time: " + str(i+openTimeOffset) + "\tOrder: " + str(weekOrders[i]))

df = pd.DataFrame(createDataFrame(weekOrders, weekOpenOrdersPerMinute))

#print(df.to_string())

# %%
#X = df[['OpenOrdersWhenPlaced', 'expectedMinutesToComplete']]
#X = df.iloc[:, :-1].values
#y = df["ActualMinutesToComplete"] 
#y = df.iloc[:, -1].values
X = []
y= []

#poly = PolynomialFeatures(degree=2)
#X_poly = poly.fit_transform(X)

#print(df.iloc[:, -1].values)

#regr = linear_model.LinearRegression()
#regr.fit(X_poly, y) 
#regr.fit(X, y) 

predictions = []
answers = []
deviations = []

testCount = 50
testOpenOrdersPerMinute = []
testOrders = createOrders(testCount, 3)
calculatePrepTimeEstimates(testOrders)

for i in range(testCount):
    randOrdersInProcess = random.randrange(0,15)
    testOrdersInProcess = createOrders(randOrdersInProcess, 3)
    testOrdersInProcess.append(testOrders[i])
    testOrders[i]["orderTime"] = i+openTimeOffset
    testOpenOrdersPerMinute.append([i+openTimeOffset, testOrdersInProcess])

    X.append(len(testOrdersInProcess))
    y.append(GenerateData.calcDelayTime(testOrders[i], testOpenOrdersPerMinute))

mymodel = numpy.poly1d(numpy.polyfit(X, y, 4))

for i in range(testCount):
    testOperOrders = len(testOpenOrdersPerMinute[i][1])
    #testEstimate = testOrders[i]["expectedMinutesToComplete"]

    #new_data_poly = poly.transform([[testOperOrders, testEstimate]])
    
    #predictedCompleteTime = regr.predict(new_data_poly)
    #predictedCompleteTime = regr.predict([[testOperOrders, testEstimate]])
    predictedCompleteTime = mymodel(testOperOrders)
    predictions.append(predictedCompleteTime)
    answer = GenerateData.calcDelayTime(testOrders[i], testOpenOrdersPerMinute)
    answers.append(answer)
    deviations.append(round(predictedCompleteTime-answer, 6))
    
    print("Test #: " + str(i) +
         " \ttestOrderCount: " + str(testOperOrders) +
         #" \ttestOrderEst: " + str(testEstimate) +
         " \tpredictedCompleteTime: " + str(predictedCompleteTime) +
         " \tanswer: " + str(answer) +
         " \tDeviation: " + str(round(predictedCompleteTime-answer, 6)))
    
    #predictionsmodel = numpy.poly1d(numpy.polyfit(range(25), predictions, 10))
    #answersmodel = numpy.poly1d(numpy.polyfit(range(25), answers, 10))

    #predictionsline = numpy.linspace(1, 25, 25)
    #answersline = numpy.linspace(1, 25, 25)
print("Average deviation from answer: " + str(sum(deviations)/len(deviations)))
plt.figure().set_figwidth(15)        
plt.plot(predictions, color='blue', label="Predictions")
plt.plot(answers, color='orange', label="Answers")
plt.show() 
plt.clf()



