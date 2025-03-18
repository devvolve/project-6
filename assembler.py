#!/usr/bin/env python3
import sys
from enum import Enum

# ---------------------------
# CommandType Enum
# ---------------------------
class CommandType(Enum):
    A_COMMAND = 1  # e.g., @2 or @symbol
    C_COMMAND = 2  # e.g., dest=comp;jump
    L_COMMAND = 3  # e.g., (LOOP)

# ---------------------------
# Code Module
# ---------------------------
class Code:
    def __init__(self):
        # Jump mnemonics lookup table.
        self.jumpMnemonics = {
            "NULL": "000",
            "JGT": "001",
            "JEQ": "010",
            "JGE": "011",
            "JLT": "100",
            "JNE": "101",
            "JLE": "110",
            "JMP": "111"
        }
        # Comp mnemonics lookup table.
        self.compMnemonics = {
            "0": "0101010",
            "1": "0111111",
            "-1": "0111010",
            "D": "0001100",
            "A": "0110000",
            "M": "1110000",
            "!D": "0001101",
            "!A": "0110001",
            "!M": "1110001",
            "-D": "0001111",
            "-A": "0110011",
            "-M": "1110011",
            "D+1": "0011111",
            "A+1": "0110111",
            "M+1": "1110111",
            "D-1": "0001110",
            "A-1": "0110010",
            "M-1": "1110010",
            "D+A": "0000010",
            "D+M": "1000010",
            "D-A": "0010011",
            "D-M": "1010011",
            "A-D": "0000111",
            "M-D": "1000111",
            "D&A": "0000000",
            "D&M": "1000000",
            "D|A": "0010101",
            "D|M": "1010101"
        }
        # Dest mnemonics lookup table.
        self.destMnemonics = {
            "NULL": "000",
            "M": "001",
            "D": "010",
            "MD": "011",
            "A": "100",
            "AM": "101",
            "AD": "110",
            "AMD": "111"
        }

    def dest(self, mnemonic):
        if mnemonic is None or mnemonic == "":
            mnemonic = "NULL"
        return self.destMnemonics.get(mnemonic)

    def comp(self, mnemonic):
        return self.compMnemonics.get(mnemonic)

    def jump(self, mnemonic):
        if mnemonic is None or mnemonic == "":
            mnemonic = "NULL"
        return self.jumpMnemonics.get(mnemonic)

    def format_number_as_binary(self, number_str):
        # Formats a number as a 15-bit, zero-padded binary string.
        value = int(number_str)
        return format(value, '015b')

# ---------------------------
# Parser Module
# ---------------------------
class Parser:
    def __init__(self, filepath):
        self.filepath = filepath
        self.file = open(filepath, 'r')
        self.current_command = None
        self.next_line = self.get_next_line()

    def get_next_line(self):
        while True:
            line = self.file.readline()
            if not line:
                return None
            line = line.strip()
            # Remove inline comments.
            if '//' in line:
                line = line.split('//')[0].strip()
            if line != "":
                return line

    def has_more_commands(self):
        return self.next_line is not None

    def advance(self):
        self.current_command = self.next_line
        self.next_line = self.get_next_line()

    def command_type(self):
        if self.current_command.startswith('@'):
            return CommandType.A_COMMAND
        elif self.current_command.startswith('(') and self.current_command.endswith(')'):
            return CommandType.L_COMMAND
        else:
            return CommandType.C_COMMAND

    def symbol(self):
        ct = self.command_type()
        if ct == CommandType.A_COMMAND:
            return self.current_command[1:]
        elif ct == CommandType.L_COMMAND:
            return self.current_command[1:-1]
        else:
            return None

    def dest(self):
        if '=' in self.current_command:
            return self.current_command.split('=')[0].strip()
        return None

    def comp(self):
        comp_str = self.current_command
        if '=' in comp_str:
            comp_str = comp_str.split('=')[1]
        if ';' in comp_str:
            comp_str = comp_str.split(';')[0]
        return comp_str.strip()

    def jump(self):
        if ';' in self.current_command:
            return self.current_command.split(';')[1].strip()
        return None

    def close(self):
        self.file.close()

# ---------------------------
# SymbolTable Module
# ---------------------------
class SymbolTable:
    def __init__(self):
        self.symbolAddressMap = {}
        # Initialize with predefined symbols.
        self.symbolAddressMap["SP"] = 0
        self.symbolAddressMap["LCL"] = 1
        self.symbolAddressMap["ARG"] = 2
        self.symbolAddressMap["THIS"] = 3
        self.symbolAddressMap["THAT"] = 4
        for i in range(16):
            self.symbolAddressMap[f"R{i}"] = i
        self.symbolAddressMap["SCREEN"] = 16384
        self.symbolAddressMap["KBD"] = 24576

        # Pointers for label and variable allocation.
        self.programAddress = 0  # for ROM addresses (labels)
        self.dataAddress = 16    # for variables

    def contains(self, symbol):
        return symbol in self.symbolAddressMap

    def add_entry(self, symbol, address):
        self.symbolAddressMap[symbol] = address

    def get_address(self, symbol):
        return self.symbolAddressMap[symbol]

    def get_program_address(self):
        return self.programAddress

    def increment_program_address(self):
        self.programAddress += 1

    def get_data_address(self):
        return self.dataAddress

    def increment_data_address(self):
        self.dataAddress += 1

# ---------------------------
# Assembler Module
# ---------------------------
class Assembler:
    def __init__(self, source_file, target_file):
        self.source_file = source_file
        self.target_file = target_file
        self.code = Code()
        self.symbol_table = SymbolTable()

    def record_label_address(self):
        """First pass: record all label (L_COMMAND) addresses into the symbol table."""
        parser = Parser(self.source_file)
        while parser.has_more_commands():
            parser.advance()
            ct = parser.command_type()
            if ct == CommandType.L_COMMAND:
                symbol = parser.symbol()
                address = self.symbol_table.get_program_address()
                self.symbol_table.add_entry(symbol, address)
            else:
                self.symbol_table.increment_program_address()
        parser.close()

    def parse(self):
        """Second pass: parse each instruction, translate to binary, and write output."""
        parser = Parser(self.source_file)
        output_lines = []
        while parser.has_more_commands():
            parser.advance()
            ct = parser.command_type()
            instruction = None
            if ct == CommandType.A_COMMAND:
                symbol = parser.symbol()
                if symbol.isdigit():
                    address = int(symbol)
                else:
                    if not self.symbol_table.contains(symbol):
                        # New variable: assign the next available data address.
                        address = self.symbol_table.get_data_address()
                        self.symbol_table.add_entry(symbol, address)
                        self.symbol_table.increment_data_address()
                    else:
                        address = self.symbol_table.get_address(symbol)
                instruction = self.format_a_instruction(address)
            elif ct == CommandType.C_COMMAND:
                comp = parser.comp()
                dest = parser.dest()
                jump = parser.jump()
                instruction = self.format_c_instruction(comp, dest, jump)
            # L_COMMANDs are not translated into machine code.
            if ct != CommandType.L_COMMAND:
                output_lines.append(instruction)
        parser.close()
        with open(self.target_file, 'w') as f:
            for line in output_lines:
                f.write(line + "\n")

    def format_a_instruction(self, address):
        # Format: "0" + 15-bit binary representation of the address.
        binary_address = format(address, '015b')
        return "0" + binary_address

    def format_c_instruction(self, comp, dest, jump):
        comp_bits = self.code.comp(comp)
        if comp_bits is None:
            raise ValueError("Unknown comp mnemonic: " + comp)
        dest_bits = self.code.dest(dest)
        jump_bits = self.code.jump(jump)
        return "111" + comp_bits + dest_bits + jump_bits

    def translate(self):
        self.record_label_address()
        self.parse()

# ---------------------------
# Main Program (entry point)
# ---------------------------
def main():
    if len(sys.argv) != 3:
        print("Usage: python assembler.py <inputfile.asm> <outputfile.hack>")
        sys.exit(1)
    source_file = sys.argv[1]
    target_file = sys.argv[2]
    assembler = Assembler(source_file, target_file)
    assembler.translate()
    print(f"Translation completed. Output written to {target_file}")

if __name__ == "__main__":
    main()
