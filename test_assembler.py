import unittest
import tempfile
import os
from assembler import Code, Parser, CommandType

# ---------------------------
# Code Module Tests
# ---------------------------
class TestCodeComp(unittest.TestCase):
    def setUp(self):
        self.code = Code()
    
    def test_comp_mnemonics(self):
        test_data = [
            ("0", "0101010"),
            ("1", "0111111"),
            ("-1", "0111010"),
            ("D", "0001100"),
            ("A", "0110000"),
            ("M", "1110000"),
            ("!D", "0001101"),
            ("!A", "0110001"),
            ("!M", "1110001"),
            ("-D", "0001111"),
            ("-A", "0110011"),
            ("-M", "1110011"),
            ("D+1", "0011111"),
            ("A+1", "0110111"),
            ("M+1", "1110111"),
            ("D-1", "0001110"),
            ("A-1", "0110010"),
            ("M-1", "1110010"),
            ("D+A", "0000010"),
            ("D+M", "1000010"),
            ("D-A", "0010011"),
            ("D-M", "1010011"),
            ("A-D", "0000111"),
            ("M-D", "1000111"),
            ("D&A", "0000000"),
            ("D&M", "1000000"),
            ("D|A", "0010101"),
            ("D|M", "1010101")
        ]
        for mnemonic, expected in test_data:
            self.assertEqual(self.code.comp(mnemonic), expected)

class TestCodeDest(unittest.TestCase):
    def setUp(self):
        self.code = Code()
    
    def test_dest_mnemonics(self):
        test_data = [
            ("", "000"),
            ("M", "001"),
            ("D", "010"),
            ("MD", "011"),
            ("A", "100"),
            ("AM", "101"),
            ("AD", "110"),
            ("AMD", "111")
        ]
        for mnemonic, expected in test_data:
            self.assertEqual(self.code.dest(mnemonic), expected)

class TestCodeJump(unittest.TestCase):
    def setUp(self):
        self.code = Code()
    
    def test_jump_mnemonics(self):
        test_data = [
            ("", "000"),
            ("JGT", "001"),
            ("JEQ", "010"),
            ("JGE", "011"),
            ("JLT", "100"),
            ("JNE", "101"),
            ("JLE", "110"),
            ("JMP", "111")
        ]
        for mnemonic, expected in test_data:
            self.assertEqual(self.code.jump(mnemonic), expected)

# ---------------------------
# Parser Module Tests
# ---------------------------
class TestParserCommands(unittest.TestCase):
    def setUp(self):
        # Create a temporary test file with several commands.
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.asm')
        # Write test data similar to the Java tests.
        self.temp_file.write("(LOOP)\n")
        self.temp_file.write("@acommand\n")
        self.temp_file.write("D=M\n")
        self.temp_file.write("(END)\n")
        self.temp_file.write("@variable\n")
        self.temp_file.write("AMD=D|A;JLE\n")
        self.temp_file.close()
        self.file_path = self.temp_file.name

    def tearDown(self):
        os.remove(self.file_path)

    def test_command_types(self):
        parser = Parser(self.file_path)
        expected_types = [
            CommandType.L_COMMAND,
            CommandType.A_COMMAND,
            CommandType.C_COMMAND,
            CommandType.L_COMMAND,
            CommandType.A_COMMAND,
            CommandType.C_COMMAND
        ]
        types = []
        while parser.has_more_commands():
            parser.advance()
            types.append(parser.command_type())
        parser.close()
        self.assertEqual(types, expected_types)

    def test_parser_fields(self):
        parser = Parser(self.file_path)
        # First command: Label (LOOP)
        parser.advance()
        self.assertEqual(parser.command_type(), CommandType.L_COMMAND)
        self.assertEqual(parser.symbol(), "LOOP")
        # Second command: A-command (@acommand)
        parser.advance()
        self.assertEqual(parser.command_type(), CommandType.A_COMMAND)
        self.assertEqual(parser.symbol(), "acommand")
        # Third command: C-command ("D=M")
        parser.advance()
        self.assertEqual(parser.command_type(), CommandType.C_COMMAND)
        self.assertEqual(parser.dest(), "D")
        self.assertEqual(parser.comp(), "M")
        self.assertIsNone(parser.jump())
        # Fourth command: Label (END)
        parser.advance()
        self.assertEqual(parser.command_type(), CommandType.L_COMMAND)
        self.assertEqual(parser.symbol(), "END")
        # Fifth command: A-command (@variable)
        parser.advance()
        self.assertEqual(parser.command_type(), CommandType.A_COMMAND)
        self.assertEqual(parser.symbol(), "variable")
        # Sixth command: C-command ("AMD=D|A;JLE")
        parser.advance()
        self.assertEqual(parser.command_type(), CommandType.C_COMMAND)
        self.assertEqual(parser.dest(), "AMD")
        self.assertEqual(parser.comp(), "D|A")
        self.assertEqual(parser.jump(), "JLE")
        parser.close()

class TestParserHasMoreCommands(unittest.TestCase):
    def test_empty_file(self):
        with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.asm') as tf:
            file_path = tf.name
        parser = Parser(file_path)
        self.assertFalse(parser.has_more_commands())
        parser.close()
        os.remove(file_path)

    def test_non_empty_file(self):
        with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.asm') as tf:
            tf.write("D=M\n")
            file_path = tf.name
        parser = Parser(file_path)
        self.assertTrue(parser.has_more_commands())
        parser.close()
        os.remove(file_path)

class TestParserInitialization(unittest.TestCase):
    def test_none_file_raises_exception(self):
        with self.assertRaises(TypeError):
            Parser(None)

    def test_nonexistent_file_raises_exception(self):
        with self.assertRaises(FileNotFoundError):
            Parser("nonexistent_file.asm")

# ---------------------------
# Suite for Parser Tests (optional)
# ---------------------------
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestCodeComp))
    suite.addTest(unittest.makeSuite(TestCodeDest))
    suite.addTest(unittest.makeSuite(TestCodeJump))
    suite.addTest(unittest.makeSuite(TestParserCommands))
    suite.addTest(unittest.makeSuite(TestParserHasMoreCommands))
    suite.addTest(unittest.makeSuite(TestParserInitialization))
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
