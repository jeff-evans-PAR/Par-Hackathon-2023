# %%
import numpy
import random
import math

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

def generateDataForOneDay(baseNumofOrders):
    orderTimes = creatRandomOrderTimes(baseNumofOrders)
    orders = createOrders(len(orderTimes), 2)

    mapOrdersToTimes(orders, orderTimes)
    sortedOrders = sorted(orders, key=lambda x: x['orderTime'])
    openOrdersPerMinute = calcOpenOrdersPerMinute(sortedOrders)

    return sortedOrders, openOrdersPerMinute

def creatRandomOrderTimes(baseNumofOrders):
    randomLunchTimes = createRandomOrderTimesInMinutes(lunchStartTimeInMinutes, lunchDuration , baseNumofOrders, "normal")
    #print(randomLunchTimes)
    
    randomDinnerTimes = createRandomOrderTimesInMinutes(dinnerStartTimeInMinutes, DinnerDuration , math.ceil(baseNumofOrders * 1.5), "normal")
    #print(randomDinnerTimes)
    
    randomTimes = createRandomOrderTimesInMinutes(openTimeOffset, openDuration , baseNumofOrders, "uniform")
    #print(randomTimes)
    
    allTimes = randomLunchTimes + randomDinnerTimes + randomTimes

    timesToRemove = []
    for time in allTimes:
        if time < openTimeOffset or time > (openTimeOffset + openDuration):
            timesToRemove.append(time)
            
    for timeToRemove in timesToRemove:
        allTimes.remove(timeToRemove)

    return allTimes

def createRandomOrderTimesInMinutes(start, duration, numOrder, type):
    end = start + duration
    if type == "normal":
        middle = (start+end)/2
        randomTimesFloat = numpy.random.normal(middle, duration/2 , numOrder)
    if type == "uniform":
        randomTimesFloat = numpy.random.uniform(start, end , numOrder)
    randomTimesInt = []
    
    for time in randomTimesFloat:
        randomTimesInt.append(round(time))
    
    return randomTimesInt

def createOrders(numOrders, averageItems):
    numItemsFloat = numpy.random.normal(averageItems, averageItems/2 , math.ceil(numOrders))
    numItemsInt = []
    
    for num  in numItemsFloat:
        intNum = round(num)
        if intNum <= 0:
            intNum = 1
        numItemsInt.append(intNum)
        
    orders = []

    for num in numItemsInt:
        orderItems = []
        for i in range(num):
            itemToAdd = orderItemTypesAndTimes[random.randrange(0, 2)]
            orderItems.append(itemToAdd)
        orders.append({"orderNum": 0, 
                       "orderTime": 0, 
                       "orderItems": orderItems, 
                       "completedTime": 0, 
                       "expectedMinutesToComplete": 0,
                       "minutesWorkCompleted": 0, 
                       "estimatedCompletedTime": 0})

    return orders

def mapOrdersToTimes(orders, times):
    calculatePrepTimeEstimates(orders)
    numOrders = len(times)
    for i in range(numOrders):
        orders[i]["orderTime"] = times[i]
        orders[i]["orderNum"] = i
        orders[i]["estimatedCompletedTime"] = math.ceil(orders[i]["orderTime"] + orders[i]["expectedMinutesToComplete"])

def calculatePrepTimeEstimates(orders):
    itemsPerOrder = []
    for order in orders:
        itemsPerOrder.append(len(order["orderItems"]))
        timeTotal = 1 # this represents the flat time to bag an order
        for item in order["orderItems"]:
            timeTotal += item["time"]
    
        order["expectedMinutesToComplete"] = timeTotal
        #print(order["orderItems"])
        #print(order["expectedCompleteTime"])
    return itemsPerOrder

def calcDelayTime(orderToDelay, openOrdersPerMinute):
    delayTime = 0
    shortestOrderCompleteTime = 0
    ordersAtMinute = openOrdersPerMinute[orderToDelay["orderTime"]-openTimeOffset][1]
    for order in ordersAtMinute:
        if len(ordersAtMinute) < KitchenOrderLimit:
            break
        queuePos = ordersAtMinute.index(order) + 1
        possibleDelay = 0
        if queuePos < KitchenOrderLimit:
            possibleDelay = calcOrdersDelayContribution(order)
            if possibleDelay < shortestOrderCompleteTime or shortestOrderCompleteTime == 0:
                shortestOrderCompleteTime = possibleDelay
        else:
            possibleDelay = calcOrdersDelayContribution(order)
            delayTime += possibleDelay
    if shortestOrderCompleteTime != 0:
        delayTime += shortestOrderCompleteTime

    return delayTime

def calcOrdersDelayContribution(order):
    delaytime = 0
    if order["minutesWorkCompleted"] > order["expectedMinutesToComplete"]:
        delaytime += order["expectedMinutesToComplete"]
    else:
        delaytime += (order["expectedMinutesToComplete"] - order["minutesWorkCompleted"])
    return delaytime

def getOrdersOpen(time, orders):
    openOrders = []
    for order in orders:
        if order["minutesWorkCompleted"] >= order["expectedMinutesToComplete"] and order["completedTime"] == 0:
            order["completedTime"] = time
        if order["orderTime"] <= time and (order["completedTime"] > time or order["completedTime"] == 0):
            openOrders.append(order)
    return openOrders

def calcOpenOrdersPerMinute(orders):
    openOrdersPerMinute = []
    currentOpenOrders = []
    
    def KitchenTick(time):
        currentOpenOrders = getOrdersOpen(time, orders)
        #print(currentOpenOrders)
        for i in range(len(currentOpenOrders)):
            currentOpenOrders[i]["minutesWorkCompleted"] += 1
            if i >= KitchenOrderLimit:
                break
        #print('"' + str(time) + '"' + ':' + json.dumps(currentOpenOrders) + ',')
        return currentOpenOrders
    #print('{')
    for minute in range(openTimeOffset, openTimeOffset + openDuration+30, 1):
        currentOpenOrders = KitchenTick(minute)
        
        openOrdersPerMinute.append([minute, currentOpenOrders])
    #print('}')
    return openOrdersPerMinute

def createDataFrame(orders, openOrdersPerMinute):
    data = {#"orderNum": [], 
           #"orderTime": [], 
           "OpenOrdersWhenPlaced": [], 
           "expectedMinutesToComplete": [], 
           "ActualMinutesToComplete": []}
    
    #info only columns
    orderNum = []
    orderPlaceTime = []

    #variable columns
    ordersOpenWhenOrderPlaced = []
    orderCompleteTimeEstimate = []
    orderCompleteTimeActual = []

    for order in orders:
        orderNum.append(order["orderNum"])
        orderPlaceTime.append(order["orderTime"])
        ordersOpenWhenOrderPlaced.append(len(openOrdersPerMinute[order["orderTime"]-openTimeOffset][1]))
        #orderCompleteTimeEstimate.append(order["expectedMinutesToComplete"])
        orderCompleteTimeEstimate.append(calcDelayTime(order, openOrdersPerMinute)+order["expectedMinutesToComplete"])
        orderCompleteTimeActual.append(order["completedTime"] - order["orderTime"])

    #data["orderNum"] = orderNum
    #data["orderTime"] = orderPlaceTime
    data["OpenOrdersWhenPlaced"] = ordersOpenWhenOrderPlaced
    data["expectedMinutesToComplete"] = orderCompleteTimeEstimate
    data["ActualMinutesToComplete"] = orderCompleteTimeActual
    return data