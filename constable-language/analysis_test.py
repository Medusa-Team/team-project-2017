import unittest
from analysis import special_comma_split


class Test(unittest.TestCase):
    def test_comma_split(self):
        a = 'T_str,END'
        ae = ['T_str', 'END']
        self.assertListEqual(special_comma_split(a), ae)

        b = "Pfuncdec,Pprogstart,T|'{',CMDS,T|'}',Pfuncend,END"
        be = ["Pfuncdec", "Pprogstart", "T|'{'", "CMDS", "T|'}'", "Pfuncend",
              "END"]
        self.assertListEqual(special_comma_split(b), be)

        c = "T|',',SA,END"
        ce = ["T|','", "SA", "END"]
        self.assertListEqual(special_comma_split(c), ce)

        d = "T|',',END"
        de = ["T|','", "END"]
        self.assertListEqual(special_comma_split(d), de)


if __name__ == '__main__':
    unittest.main()
