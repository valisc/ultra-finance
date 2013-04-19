'''
Created on Jan 18, 2011

@author: ppa
'''
import mox
import unittest
from datetime import datetime
from ultrafinance.backTest.constant import TRADE_TYPE, TICK, QUOTE
from ultrafinance.backTest.tickSubscriber import TickSubsriber
from ultrafinance.dam.baseDAM import BaseDAM
from ultrafinance.model import Tick, Quote
from ultrafinance.backTest.appGlobal import appGlobal
from ultrafinance.backTest.tickFeeder import TickFeeder
from ultrafinance.lib.errors import UfException

class testTickFeeder(unittest.TestCase):
    def setUp(self):
        self.mock = mox.Mox()

    def tearDown(self):
        pass

    def testAddSource(self):
        dam = self.mock.CreateMockAnything('dam')
        dam.symbol = 's1'

        tf = TickFeeder()
        tf.addSource(dam)

        self.assertEquals({'s1': dam}, tf._TickFeeder__source)

    def testValidate_Normal(self):
        sub = self.mock.CreateMock(TickSubsriber)
        sub.subRules().AndReturn(['s1', 'mockRule'])

        tf = TickFeeder()
        tf._TickFeeder__source = {'s1': 'dam1', 's11': 'dam2', 's2': 'dam3'}

        self.mock.ReplayAll()
        symbols, sub = tf.validate(sub)
        self.mock.VerifyAll()

    def testValidate_Exception(self):
        sub = self.mock.CreateMock(TickSubsriber)
        sub.subRules().AndReturn(['s3', 'mockRule'])

        tf = TickFeeder()
        tf._TickFeeder__source = {'s1': 'dam1', 's11': 'dam2', 's2': 'dam3'}

        self.mock.ReplayAll()
        self.assertRaises(UfException, tf.validate, sub)
        self.mock.VerifyAll()

    def testRegister_Normal(self):
        sub = self.mock.CreateMock(TickSubsriber)
        sub.subRules().AndReturn(['s1', 'mockRule'])

        tf = TickFeeder()
        tf._TickFeeder__source = {'s1': 'dam1', 's11': 'dam2', 's2': 'dam3'}

        self.mock.ReplayAll()
        tf.register(sub)
        self.mock.VerifyAll()

        subs = tf.getSubs()
        self.assertEquals({sub: {'symbols': ['s1'], 'fail': 0} },
                          subs)

    def testRegister_Exception(self):
        sub = self.mock.CreateMock(TickSubsriber)
        sub.subRules().AndReturn(['s3', 'mockRule'])

        tf = TickFeeder()
        tf._TickFeeder__source = {'s1': 'dam1', 's11': 'dam2', 's2': 'dam3'}

        self.mock.ReplayAll()
        self.assertRaises(UfException, tf.register, sub)
        self.mock.VerifyAll()


    def testLoadTicks_quote(self):
        time1 = datetime.now()
        time2 = datetime.now()
        quoteTime1Dam1 = Quote(time1, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0)
        quoteTime2Dam1 = Quote(time2, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0)
        quoteTime1Dam2 = Quote(time1, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0)
        quoteTime2Dam2 = Quote(time2, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0)

        dam1 = self.mock.CreateMock(BaseDAM)
        dam1.readQuotes(mox.IgnoreArg(), mox.IgnoreArg()).AndReturn([quoteTime1Dam1, quoteTime2Dam1])

        dam2 = self.mock.CreateMock(BaseDAM)
        dam2.readQuotes(mox.IgnoreArg(), mox.IgnoreArg()).AndReturn([quoteTime1Dam2, quoteTime2Dam2])

        tf = TickFeeder()
        tf.inputType = QUOTE
        appGlobal[TRADE_TYPE] = QUOTE

        tf._TickFeeder__source = {'s1': dam1, 's2': dam2}

        self.mock.ReplayAll()
        timeTicks = tf.loadTicks()
        self.mock.VerifyAll()

        self.assertEquals({time1: {'s1': quoteTime1Dam1, 's2': quoteTime1Dam2},
                           time2: {'s1': quoteTime2Dam1, 's2': quoteTime2Dam2}},
                           timeTicks)


    def testLoadTicks_tick(self):
        time1 = datetime.now()
        time2 = datetime.now()
        tickTime1Dam1 = Tick(time1, 100.0, 100.0, 100.0, 100.0, 100.0)
        tickTime2Dam1 = Tick(time2, 100.0, 100.0, 100.0, 100.0, 100.0)
        tickTime1Dam2 = Tick(time1, 100.0, 100.0, 100.0, 100.0, 100.0)
        tickTime2Dam2 = Tick(time2, 100.0, 100.0, 100.0, 100.0, 100.0)

        dam1 = self.mock.CreateMock(BaseDAM)
        dam1.readTicks(mox.IgnoreArg(), mox.IgnoreArg()).AndReturn([tickTime1Dam1, tickTime2Dam1])

        dam2 = self.mock.CreateMock(BaseDAM)
        dam2.readTicks(mox.IgnoreArg(), mox.IgnoreArg()).AndReturn([tickTime1Dam2, tickTime2Dam2])

        tf = TickFeeder()
        tf._TickFeeder__source = {'s1': dam1, 's2': dam2}
        tf.inputType = TICK
        appGlobal[TRADE_TYPE] = TICK

        self.mock.ReplayAll()
        timeTicks = tf.loadTicks()
        self.mock.VerifyAll()

        self.assertEquals({time1: {'s1': tickTime1Dam1, 's2': tickTime1Dam2},
                           time2: {'s1': tickTime2Dam1, 's2': tickTime2Dam2}},
                           timeTicks)

    def testPubTicks(self):
        sub = self.mock.CreateMock(TickSubsriber)
        sub.tickUpdate(['ticks'])

        tf = TickFeeder()
        self.mock.ReplayAll()
        thread = tf.pubTicks(['ticks'], sub)
        self.mock.VerifyAll()

    #TODO, too lazy to write this one........
    def testExecute(self):
        pass
