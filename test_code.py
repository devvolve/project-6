import unittest
from assembler import Code  

class TestCodeModule(unittest.TestCase):
    def setUp(self):
        self.code = Code()
    
    def test_comp_mnemonics(self):
        # Test a few comp mnemonics
        self.assertEqual(self.code.comp("0"), "0101010")
        self.assertEqual(self.code.comp("1"), "0111111")
        self.assertEqual(self.code.comp("-1"), "0111010")
        self.assertEqual(self.code.comp("D"), "0001100")
        self.assertEqual(self.code.comp("A"), "0110000")
        self.assertEqual(self.code.comp("M"), "1110000")
        self.assertEqual(self.code.comp("D+1"), "0011111")
        # Add more test cases as needed
        
    def test_dest_mnemonics(self):
        # Test a few dest mnemonics
        self.assertEqual(self.code.dest(""), "000")  # or self.code.dest(None)
        self.assertEqual(self.code.dest("M"), "001")
        self.assertEqual(self.code.dest("D"), "010")
        self.assertEqual(self.code.dest("MD"), "011")
        self.assertEqual(self.code.dest("A"), "100")
        self.assertEqual(self.code.dest("AM"), "101")
        self.assertEqual(self.code.dest("AD"), "110")
        self.assertEqual(self.code.dest("AMD"), "111")
        
    def test_jump_mnemonics(self):
        # Test a few jump mnemonics
        self.assertEqual(self.code.jump(""), "000")  # or self.code.jump(None)
        self.assertEqual(self.code.jump("JGT"), "001")
        self.assertEqual(self.code.jump("JEQ"), "010")
        self.assertEqual(self.code.jump("JGE"), "011")
        self.assertEqual(self.code.jump("JLT"), "100")
        self.assertEqual(self.code.jump("JNE"), "101")
        self.assertEqual(self.code.jump("JLE"), "110")
        self.assertEqual(self.code.jump("JMP"), "111")

if __name__ == '__main__':
    unittest.main()
