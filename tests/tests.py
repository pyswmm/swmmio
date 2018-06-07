#test modules
import unittest
import sys
sys.path.append(r'P:\06_Tools\swmmio')
from swmmio import swmm_headers

#check that header match and replace somethig in the file
class sectionheadersTest(unittest.TestCase):
    def test(self):
        with open(r'sample_models\sample.inp') as f:
            #print f.read(1000)
            text = f.read()
            for hpair in swmm_headers.inpHeaderList:
                print(hpair[0][:200])
                matched_an_inp_header = False
                #hpair[0]
                if hpair[0] in text:
                    matched_an_inp_header = True

        self.assertTrue(matched_an_inp_header)

class RptHeadersTest(unittest.TestCase):
    def test(self):
        with open(r'sample_models\sample.rpt') as f:
            #print f.read(1000)
            text = f.read()
            for hpair in swmm_headers.rptHeaderList:
                #print hpair[0][20:]
                matched_an_rpt_header = False
                #hpair[0]
                if hpair[0] in text:
                    matched_an_rpt_header = True

        self.assertTrue(matched_an_rpt_header)

if __name__ == '__main__':
    unittest.main()
