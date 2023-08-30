import matplotlib.pyplot as plt
import numpy

import GenerateData

def plotOrderTimes(randomOrderTimes):
    plt.hist(randomOrderTimes, 13*6)
    plt.show() 

def plotOrdersPerMinute(openOrdersPerMinute):
    plotMinutes = []
    plotOrders = []
    for minute in openOrdersPerMinute:
        plotMinutes.append(minute[0])
        plotOrders.append(len(minute[1]))

    mymodel = numpy.poly1d(numpy.polyfit(plotMinutes, plotOrders, 10))

    myline = numpy.linspace(GenerateData.openTimeOffset, (GenerateData.openTimeOffset + GenerateData.openDuration), 100)
        
    plt.bar(plotMinutes, plotOrders)
    plt.plot(myline, mymodel(myline))
    plt.xlabel("Time in Minutes")
    plt.ylabel("Open Orders")
    plt.show() 
    plt.clf()

def plotOrderDelayPerOpenOrder(openOrdersPerMinute, orders):
    plotDelayTime = []
    plotOpenOrdersAtTime = []

    for order in orders:
        delaytime = GenerateData.calcDelayTime(order, openOrdersPerMinute)
    
        plotOpenOrdersAtTime.append(len(openOrdersPerMinute[order["orderTime"]-GenerateData.openTimeOffset][1]))
        plotDelayTime.append(delaytime)

        #print("OrderTime: " + str(order["orderTime"])
        #      +"\t[" + str(len(openOrdersPerMinute[order["orderTime"]-openTimeOffset][1]))
        #      + " , " + str(delaytime) + ']')


    plt.scatter(plotOpenOrdersAtTime, plotDelayTime)
    plt.ylabel("Order Delay Time")
    plt.xlabel("Open Orders")
    plt.show() 