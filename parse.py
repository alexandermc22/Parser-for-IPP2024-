import getopt
import sys
import re
import codecs
import xml.etree.ElementTree as ET

###################################################
#########--Declaration and defenition--############
###################################################

first_read = False
eof_found = False


class Command:
    def __init__(self, name, arg_types):
        self.name = name
        self.types = arg_types
        self.args = []

    def set_name(self, name):
        self.name = name

    def add_arg(self, arg):
        self.args.append(arg)

    def add_type(self, type):
        self.types.append(type)

    def is_command(self, commands): # Checking if the received command corresponds to the defined commands 
        for command in commands:
            if self.name != command.name:
                continue
            if len(self.types) != len(command.types):
                sys.exit(23)
            for type, expected_type in zip(self.types, command.types):
                if expected_type == "symb":
                    if not (is_keyword(type) or type == "var"):
                        sys.exit(23)
                elif expected_type == "label":
                    if not (is_keyword(type) or type == "label"):
                        sys.exit(23)
                elif not type == expected_type:
                    sys.exit(23)
            return True
        sys.exit(22)


def declarations(commands):
    #
    commands.append(Command("MOVE", ["var", "symb"]))
    commands.append(Command("CREATEFRAME", []))
    commands.append(Command("PUSHFRAME", []))
    commands.append(Command("POPFRAME", []))
    commands.append(Command("DEFVAR", ["var"]))
    commands.append(Command("CALL", ["label"]))
    commands.append(Command("RETURN", []))
    #
    commands.append(Command("PUSHS", ["symb"]))
    commands.append(Command("POPS", ["var"]))
    #
    commands.append(Command("ADD", ["var", "symb", "symb"]))
    commands.append(Command("SUB", ["var", "symb", "symb"]))
    commands.append(Command("MUL", ["var", "symb", "symb"]))
    commands.append(Command("IDIV", ["var", "symb", "symb"]))
    commands.append(Command("GT", ["var", "symb", "symb"]))
    commands.append(Command("EQ", ["var", "symb", "symb"]))
    commands.append(Command("LT", ["var", "symb", "symb"]))
    commands.append(Command("AND", ["var", "symb", "symb"]))
    commands.append(Command("NOT", ["var", "symb"]))
    commands.append(Command("OR", ["var", "symb", "symb"]))
    commands.append(Command("INT2CHAR", ["var", "symb"]))
    commands.append(Command("STRI2INT", ["var", "symb", "symb"]))
    #
    commands.append(Command("READ", ["var", "type"]))
    commands.append(Command("WRITE", ["symb"]))
    #
    commands.append(Command("CONCAT", ["var", "symb", "symb"]))
    commands.append(Command("STRLEN", ["var", "symb"]))
    commands.append(Command("GETCHAR", ["var", "symb", "symb"]))
    commands.append(Command("SETCHAR", ["var", "symb", "symb"]))
    #
    commands.append(Command("TYPE", ["var", "symb"]))
    #
    commands.append(Command("LABEL", ["label"]))
    commands.append(Command("JUMP", ["label"]))
    commands.append(Command("JUMPIFEQ", ["label", "symb", "symb"]))
    commands.append(Command("JUMPIFNEQ", ["label", "symb", "symb"]))
    commands.append(Command("EXIT", ["symb"]))
    #
    commands.append(Command("DPRINT", ["symb"]))
    commands.append(Command("BREAK", []))


###################################################
#############--String conversion--#################
###################################################

def parse_ippcode24():
    global eof_found
    global first_read

    source_code = sys.stdin.readline()
    # check end of file
    if (not source_code):
        if first_read:
            eof_found = True
            return
        else:
            sys.exit(21)

    instruction = source_code.strip()  # string without space
    # skip spaces and comments
    while source_code.isspace() or instruction[0] == '#':
        source_code = sys.stdin.readline()
        instruction = source_code.strip()
        if not source_code:
            if first_read:
                eof_found = True
                return
            else:
                sys.exit(21)
    # separate instruction / comment
    parts = instruction.split('#')
    if len(parts) > 1:
        instruction = parts[0].strip()
    # first read check
    if not first_read:
        if instruction.casefold() != ".ippcode24".casefold():
            sys.exit(21)
    if instruction.casefold() == ".ippcode24".casefold():
        if not first_read:
            first_read = True
            return ".IPPcode24"
        elif first_read:
            sys.exit(23)
        else:
            sys.exit(21)
    return instruction


###################################################
#############--Token creation--####################
###################################################

def analyze_ippcode24(instruction, parsed_instruction):
    words_buffer = instruction.split() # splitting the string into a instruction name and its arguments 
    if len(words_buffer) >= 5:
        sys.exit(22)
    parsed_instruction.set_name(words_buffer[0].upper()) # set name of instruction
    for word in words_buffer[1:]:
        variable_check(word, parsed_instruction)


def variable_check(word, parsed_instruction):
    # split string
    buffer = word.split("@", 1)
    if len(buffer) == 2:
        type = buffer[0]  # Part before "@"
        arg = buffer[1]  # Part after "@"
    # if we have type or lable
    elif len(buffer) == 1:
        if is_keyword(word) and parsed_instruction.name == "READ":
            parsed_instruction.add_type("type")
            parsed_instruction.add_arg(word)
            return
        elif is_valid_name(word) and starts_with_allowed_char(word):
            parsed_instruction.add_type("label")
            parsed_instruction.add_arg(word)
            return
        else:
            sys.exit(23)

    # if we have constant or variable
    if type in {"GF", "LF", "TF"}:  # variable
        parsed_instruction.add_type("var")
        if is_valid_name(arg) and starts_with_allowed_char(arg):
            parsed_instruction.add_arg(word)
            return
    elif is_keyword(type):
        type_check(parsed_instruction, type, arg)
    else:
        sys.exit(23)


def type_check(parsed_instruction, type, arg): # check the argument type and its contents 
    if type == "nil":
        if arg == "nil":
            parsed_instruction.add_type(type)
            parsed_instruction.add_arg(arg)
            return
        else:
            sys.exit(23)
    if type == "bool":
        if not (arg in {"true", "false"}):
            sys.exit(23)
        else:
            parsed_instruction.add_type(type)
            parsed_instruction.add_arg(arg)
            return
    if type == "int":
        parsed_instruction.add_type(type)
        if check_octal_string(arg) or check_hex_string(arg) or is_dec_string(arg):
            parsed_instruction.add_arg(arg)
            return
        else:
            sys.exit(23)
    if type == "string":
        if (is_valid_string(arg)):
            parsed_instruction.add_arg(arg)
            parsed_instruction.add_type(type)
            return
        else:
            sys.exit(23)
    sys.exit(23)


###################################################
##############--Lexical check--####################
###################################################

def check_octal_string(s):
    pattern = r'^(-0o[0-7]+|0o[0-7]+)$'
    return bool(re.match(pattern, s))


def check_hex_string(s):
    pattern = r'^(-0x[0-9a-fA-F]+|0x[0-9a-fA-F]+)$'
    return bool(re.match(pattern, s))


def is_dec_string(s):
    return bool(re.match(r'^-?\d+$', s))


def is_keyword(s):
    if s in {"int", "bool", "string", "nil"}:
        return True
    else:
        return False


def is_valid_name(s):
    return bool(re.match(r'^[_$&%*!?0-9a-zA-Z-]+$', s))


def starts_with_allowed_char(s):
    return bool(re.match(r'^[_$&%*!?a-zA-Z-]', s))


def is_valid_string(input_string):
    invalid_characters = {' ', '#'} # the '\' character is not in invalid_characters because it is checked together with escape sequences.

    try:
        codecs.decode(input_string.encode('utf-8'), 'utf-8', 'strict')
    except UnicodeDecodeError:
        sys.exit(23)
    # looking for the number of escape sequences where 3 numbers are given and the number of free-form sequences
    escape_pattern = re.compile(r'\\(\d{3})')
    backslash_pattern = re.compile(r'\\')

    escape_matches = re.finditer(escape_pattern, input_string)
    backslash_matches = re.finditer(backslash_pattern, input_string)

    found_escape_count = 0
    found_backslash_count = 0

    for match in escape_matches:
        found_escape_count += 1

    for match in backslash_matches:
        found_backslash_count += 1
    # If their number is not the same, then the string contains sequences of the wrong format.
    if found_escape_count != found_backslash_count:
        sys.exit(23)

    return not any(char in invalid_characters for char in input_string)


###################################################
###########--XML code generation--#################
###################################################

def XML_generation(token_list):
    root = ET.Element("program")
    root.set("language", "IPPcode24")
    i = 1
    for token in token_list:
        instruction = ET.SubElement(root, "instruction")
        instruction.set("order", str(i))
        instruction.set("opcode", token.name)
        j = 1
        for type, argument in zip(token.types, token.args):
            arg = ET.SubElement(instruction, "arg" + str(j))
            arg.set("type", type)
            arg.text = argument
            j = j + 1
        i = i + 1
    tree = ET.ElementTree(root)
    tree.write(sys.stdout.buffer, encoding="UTF-8", xml_declaration=True)
    return


###################################################
##################--Main--#########################
###################################################
def main(argv):
    global eof_found

    # parsing arguments
    try:
        opts, args = getopt.getopt(argv, "h", ["help"])
    except getopt.GetoptError:
        sys.exit(10)
    if len(opts) > 1:
        sys.exit(10)
    elif len(opts) == 1:
        usage = "The filter script reads the source code in IPPcode24 from the standard input, checks the lexical and syntactic correctness of the code and prints the XML representation of the program to the standard output.\nError return codes specific to the analyzer:\n- 21 - wrong or missing header in the source code written in IPPcode24;\n- 22 - unknown or incorrect opcode in the source code written in IPPcode24;\n- 23 - other lexical or syntax error in the source code written in IPPcode24."
        print(usage)
        return 0

    # init lists
    commands = []
    declarations(commands)
    token_list = []

    # start reading code
    try:
        while True:
            instruction = parse_ippcode24() # get a instruction
            if instruction == ".IPPcode24":
                continue
            if eof_found:
                break
            parsed_instruction = Command("name", [])
            analyze_ippcode24(instruction, parsed_instruction) # create and check instruction
            parsed_instruction.is_command(commands)
            token_list.append(parsed_instruction)

    except Exception as e:
        sys.exit(99)

    XML_generation(token_list) # generate XML code
    return 0


main(sys.argv[1:])
