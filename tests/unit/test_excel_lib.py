'''
Created on May 6, 2011

@author: ppa
'''
import unittest

import os
import tempfile
from shutil import rmtree
from ultrafinance.dam.excelLib import ExcelLib

class testExcelLib(unittest.TestCase):

    def setUp(self):
        self.targetPath = tempfile.mkdtemp()
      

    def tearDown(self):
        rmtree(self.targetPath)

    def testWriteExcel(self):
        targetFile = os.path.join(self.targetPath, "excel_lib_test.xls")
        sheetName = "testSheet"

        if os.path.exists(targetFile):
            os.remove(targetFile)

        with ExcelLib(fileName = targetFile,
                      mode = ExcelLib.WRITE_MODE ) as excel:
            excel.openSheet(sheetName)
            excel.writeRow(0, [1, 2, 3, "4", "5"])

        self.assertTrue(os.path.exists(targetFile))

    def testReadExcel(self):
        self.testWriteExcel()
        targetFile = os.path.join(self.targetPath, "excel_lib_test.xls")
        with ExcelLib( fileName = targetFile, mode = ExcelLib.READ_MODE ) as excel:
            excel.openSheet('testSheet')
            data = excel.readRow(0)
            self.assertNotEqual(0, len(data))

            data = excel.readCol(0, 0)
            self.assertNotEqual(0, len(data))


