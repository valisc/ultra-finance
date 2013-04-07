'''
Created on Dec 18, 2011

@author: ppa
'''
import unittest
from datetime import datetime
from ultrafinance.backTest.tradingCenter import TradingCenter
from ultrafinance.backTest.accountManager import AccountManager
from ultrafinance.model import Tick, Order, Side
from ultrafinance.backTest.account import Account
from ultrafinance.lib.errors import UfException
import mox

class testTradingCenter(unittest.TestCase):
    def setUp(self):
        self.mock = mox.Mox()

    def tearDown(self):
        pass

    def testIsOrderMet(self):
        tc = TradingCenter()
        tick1 = Tick(datetime.now(), 30.0, 35.0, 13.20, 13.20, 100000)
        order1 = Order(accountId = None, side = Side.BUY, symbol = 'symbol', price = 13.25, share = 10)
        order2 = Order(accountId = None, side = Side.BUY, symbol = 'symbol', price = 13.15, share = 10)
        order3 = Order(accountId = None, side = Side.SELL, symbol = 'symbol', price = 13.25, share = 10)
        order4 = Order(accountId = None, side = Side.SELL, symbol = 'symbol', price = 13.15, share = 10)

        self.assertEquals(True, tc.isOrderMet(tick1, order1))
        self.assertEquals(False, tc.isOrderMet(tick1, order2))
        self.assertEquals(False, tc.isOrderMet(tick1, order3))
        self.assertEquals(True, tc.isOrderMet(tick1, order4))

    def testValidOrder(self):
        tc = TradingCenter()
        account = Account(1000, 10)
        accountId = tc.accountManager.addAccount(account)

        order1 = Order(accountId = accountId, side = Side.BUY, symbol = 'symbol', price = 13.25, share = 10)
        order2 = Order(accountId = 'unknowAccount', side = Side.BUY, symbol = 'symbol', price = 13.25, share = 10)

        self.assertEquals(False, tc.validateOrder(order2) ) # invalid account id
        self.assertEquals(True, tc.validateOrder(order1) ) # True
        #TODO Find out why this test exists
        #self.assertEquals(False, tc.validateOrder(order1) ) # False

    def testPlaceOrder_existedOrder(self):
        tc = TradingCenter()

        accountId = 'accountId'
        order1 = Order(accountId = accountId, side = Side.BUY, symbol = 'symbol', price = 13.25, share = 10, orderId = 'orderId1')
        self.assertRaises(UfException, tc.placeOrder, order1)

    def testPlaceOrder_invalidAccountId(self):
        tc = TradingCenter()

        order2 = Order(accountId = 'unknowAccount', side = Side.BUY, symbol = 'symbol', price = 13.25, share = 10)

        self.mock.ReplayAll()
        self.assertEquals(None, tc.placeOrder(order2) ) # invalid account id
        self.mock.VerifyAll()

    def testPlaceOrder_OK(self):
        tc = TradingCenter()
        
        account = Account(1000, 0)
        self.mock.StubOutWithMock(account, "validate")
        accountId = tc.accountManager.addAccount(account)

        order1 = Order(accountId = accountId, side = Side.BUY, symbol = 'symbol', price = 13.25, share = 10)
        account.validate(order1).AndReturn(True)

        self.mock.ReplayAll()
        self.assertNotEquals(None, tc.placeOrder(order1) ) # True
        self.mock.VerifyAll()

    def testPlaceOrder_failed(self):
        tc = TradingCenter()

        account = Account(1000, 0)
        self.mock.StubOutWithMock(account, "validate")
        accountId = tc.accountManager.addAccount(account)
        
        order1 = Order(accountId = accountId, side = Side.BUY, symbol = 'symbol', price = 13.25, share = 10)
        account.validate(order1).AndReturn(False)

        self.mock.ReplayAll()
        self.assertEquals(None, tc.placeOrder(order1) ) # True
        self.mock.VerifyAll()

    def testGetOpenOrdersByOrderId(self):
        order1 = Order(accountId = 'accountId', side = Side.BUY, symbol = 'symbol1', price = 13.2, share = 10, orderId = 'id1')
        order2 = Order(accountId = 'accountId', side = Side.BUY, symbol = 'symbol1', price = 13.25, share = 10, orderId = 'id2')

        tc = TradingCenter()
        tc._TradingCenter__openOrders = {'symbol1': [order1, order2]}
        order = tc.getOpenOrderByOrderId('id1')
        self.assertEquals(order1, order)

        order = tc.getOpenOrderByOrderId('id1sdfasdf')
        self.assertEquals(None, order)

    def testGetOpenOrdersBySymbol(self):
        order1 = Order(accountId = 'accountId', side = Side.BUY, symbol = 'symbol1', price = 13.2, share = 10, orderId = 'id1')
        order2 = Order(accountId = 'accountId', side = Side.BUY, symbol = 'symbol1', price = 13.25, share = 10, orderId = 'id2')

        tc = TradingCenter()
        tc._TradingCenter__openOrders = {'symbol1': [order1, order2]}
        orders = tc.getOpenOrdersBySymbol('symbol1')
        self.assertEquals([order1, order2], orders)

    def testCancelOrder(self):
        order1 = Order(accountId = 'accountId', side = Side.BUY, symbol = 'symbol1', price = 13.2, share = 10, orderId = 'id1')
        order2 = Order(accountId = 'accountId', side = Side.BUY, symbol = 'symbol1', price = 13.25, share = 10, orderId = 'id2')

        tc = TradingCenter()
        tc._TradingCenter__openOrders = {'symbol1': [order1, order2]}

        tc.cancelOrder('id1')
        self.assertEquals({'symbol1': [order2]}, tc._TradingCenter__openOrders)
        self.assertEquals({'id1': order1}, tc._TradingCenter__closedOrders)
        self.assertEquals(Order.CANCELED, order1.status)

        tc.cancelOrder('id2')
        self.assertEquals({}, tc._TradingCenter__openOrders)
        self.assertEquals({'id1': order1, 'id2': order2}, tc._TradingCenter__closedOrders)

    def testCancelAllOpenOrders(self):
        order1 = Order(accountId = 'accountId', side = Side.BUY, symbol = 'symbol1', price = 13.2, share = 10, orderId = 'id1')
        order2 = Order(accountId = 'accountId', side = Side.BUY, symbol = 'symbol1', price = 13.25, share = 10, orderId = 'id2')

        tc = TradingCenter()
        tc._TradingCenter__openOrders = {'symbol1': [order1, order2]}

        tc.cancelAllOpenOrders()
        self.assertEquals({}, tc._TradingCenter__openOrders)
        self.assertEquals({'id1': order1, 'id2': order2}, tc._TradingCenter__closedOrders)

    def testConsume(self):
        pass

    def testPostConsume(self):
        pass

    def testCreateAccountWithMetrix(self):
        pass
