import math
import re
from tree import Node

OPERATORS = [("+", "-"), ("//", "*", "/", "%"), ("^")] # least to highest precedence
OPERATOR_FUNCTIONS = {
    "^": lambda x, y: x ** y,
    "*": lambda x, y: x * y,
    "/": lambda x, y: x / y,
    "%": lambda x, y: x % y,
    "//": lambda x, y: x // y,
    "+": lambda x, y: x + y,
    "-": lambda x, y: x - y,
}
IMPLICIT_OPERATOR = "*" # must be in OPERATORS (duh)

FUNCTIONS = [
    "sin",
    "cos",
    "tan",
    "sec",
    "testinge",
    ]

FUNCTION_FUNCTIONS = {
    "sin": lambda x: math.sin(x),
    "cos": lambda x: math.cos(x),
    "tan": lambda x: math.tan(x),
    "sec": lambda x: 1/math.cos(x),
}

CONSTANTS = ["e", "pi"]
CONSTANT_VALUES = {
    "e": math.e,
    "pi": math.pi,
    "tau": math.tau,
}

# OVERLAPS = {}
# # for func in FUNCTIONS:
# #     OVERLAPS.update({func:[]})
# #     to_check = [const for const in CONSTANTS if func.find(const) != -1]
# #     for item in to_check:
# #         temp = func
# #         while True:
# #             i = item.index(item)
# #             OVERLAPS[temp].append(i)
# #             temp = item[i+len(item):]
# #             if not temp:
# #                 break

# for func in FUNCTIONS:
#     OVERLAPS.update({func:[]})
#     for const in CONSTANTS:
#         re.
#         print(const, func, re.search(const, func))
#         OVERLAPS[func].append((const,re.search(const, func)))


# print(OVERLAPS)

def remove_outer_brackets(expression:list, function=""):
    if expression[0].startswith(function+"("):
        
        skip = expression[0].count("(")
        triggered = False
        
        for i in range(1, len(expression)):
            if triggered:
                pass
            elif "(" in expression[i]:
                skip += expression[i].count("(")
            elif ")" in expression[i]:
                skip -= expression[i].count(")")
            
            if skip == 0 and i != len(expression) - 1:
                triggered = True            
        if not triggered:
            # remove
            expression[0] = expression[0][1+len(function):]
            expression[-1] = expression[-1][:-1]
                    
    return expression


def find_lowest_precendence_operator(expression:list):
    """where expr is written in infix notation list"""
    
    # from least precedence to most
    for operator_group in OPERATORS:
        
        #flag
        skip = 0
        grouped = []
        for i in range(len(expression)-1, -1, -1):
            if ")" in expression[i] or "(" in expression[i]:
                skip += expression[i].count(")")
                skip -= expression[i].count("(")
                
            elif expression[i] in operator_group and not skip:
                return i
            
            if not skip:
                if grouped:
                    grouped.append(expression[i:-1*len(grouped[-1])])
                else:
                    grouped.append(expression[i:])
                    
    
    raise ValueError("Expression invalid due to unknown operators")


def check_fully_bracketed(expr:list[str]):
    current = 0
    for section in expr[:-1]:
        current += section.count("(")
        current -= section.count(")")
        if current == 0:
            return False
    
    current += expr[-1].count("(")
    current -= expr[-1].count(")")
    
    if current != 0:
        raise ValueError(f"Expression {" ".join(expr)} is not correctly bracketed")

    return True


def infix_to_rpn(expr):
    
    def inner(root):
        # print("inner")
        # print(root.value)
        e = root.value
        # check for function wrapping the entire expression:
        
        functions = ''+'|'.join(FUNCTIONS) + ''
        regex = f"^({functions})\\("
        m = re.match(regex, e[0])
        if m is not None and check_fully_bracketed(e):
            # print("fully bracketed")
            # print(m.group()[:-1])
            # print("====")
            root.value = m.group()[:-1]
            
            if len(e) == 1:
                root.value = m.group()[:-1]
                argument = e[0][len(m.group()):-1]
                # print("HIIII")
                # print(root.value, argument)
                
                root.add_left_child(argument)
                
            else:
                # print("OTHER HI")
                # print(m.group()[:-1])
                # print(remove_outer_brackets(e, function=m.group()[:-1]))
                root.value = m.group()[:-1]
                
                root.add_left_child(remove_outer_brackets(e, function=m.group()[:-1]))
                # print(root.left_child.value)
                
                inner(root.left_child)
        
        else:
            if len(e) == 1:
                root.set_value(e[0])
            else:
                
                operator_index = find_lowest_precendence_operator(e)
                
                root.set_value(e[operator_index])
                
                root.add_left_child(remove_outer_brackets(e[:operator_index]))
                root.add_right_child(remove_outer_brackets(e[operator_index + 1:]))
                
                inner(root.left_child)
                inner(root.right_child)
    
    expression = remove_outer_brackets(expr.split(" "))
    tree = Node(expression)

    inner(tree)
    
    return tree.post_order_traversal(l=[])

def evaluate(expression):
    '''
    Evaluates expression as a list in reverse polish notation.
    Accepted operators are +, -, *, /, ^, %, //
    '''
    # print("EVALUATING")
    # print(expression)
    
    stack = []
    for item in expression:
        # print(stack)
        
        stack.append(item)
        
        if type(item) == float or type(item) == int:
            pass
        else:
            # check for function:
            if item in FUNCTIONS:
                function = stack.pop(-1)
                operand = stack.pop(-1)
                stack.append(FUNCTION_FUNCTIONS[function](operand))
            
            elif item in CONSTANTS:
                stack.append(CONSTANT_VALUES[stack.pop(-1)])
            
            else:
                operator = stack.pop(-1)
                operand1 = stack.pop(-2)
                operand2 = stack.pop(-1)
                stack.append(OPERATOR_FUNCTIONS[operator](operand1, operand2))
    
    return stack[0]


def collapse_spaces(expression:str):
    return expression.replace(" ", "")


def handle_implicit_operations(expression:str):
    """do this before spacing out operators"""
    
    # either a digit or closed brackets before open brackets
    regex = "\\d\\(|\\)\\("
    for found in re.findall(regex, expression):
        expression = expression.replace(found, found[0]+IMPLICIT_OPERATOR+found[1])
        
    # functions
    functions = '\\)'+'|\\)'.join(FUNCTIONS)
    regex = f"{functions}"
    for found in (re.findall(regex, expression)):
        expression = expression.replace(found, found[0]+IMPLICIT_OPERATOR+found[1:])
        
    # constants
    post_multiply_constants = '[\\d)]'+'|[\\d)]'.join(CONSTANTS)
    pre_multiply_constants = '[\\d(]|'.join(CONSTANTS)+'[\\d(]'
    # print(post_multiply_constants)
    # print(pre_multiply_constants)
    regex = f"({post_multiply_constants})|({pre_multiply_constants})"
    for found in (re.findall(regex, expression)):
        # print(found)
        if found[0]:
            to_replace = found[0]
            before = found[0][0]
            after = found[0][1:]
        elif found[1]:
            to_replace = found[1]
            before = found[1][:-1]
            after = found[1][-1]
            
        expression = expression.replace(to_replace, before+IMPLICIT_OPERATOR+after)
    
    return expression


def space_out_numbers(expression:str):
    # print("--")
    regex = "[\\d.]+|[()]"
    new_expression = ""
    for found in re.findall(regex, expression):
        # print(found)
        partition = expression.partition(found)
        # print(partition)
        new_expression += partition[0] + " " + partition[1] + " "
        expression = partition[2]
    new_expression += expression
    # print("--")
    return new_expression.strip()

def space_out_constants(expression:str):
    new_expression = ""
    i = 0
    while i < len(expression):
        if expression.startswith(tuple(FUNCTIONS), i):
            for func in FUNCTIONS:
                if expression.startswith(func, i):
                    new_expression += func
                    i += len(func)
                    break
            
        elif expression.startswith(tuple(CONSTANTS), i):
            for const in CONSTANTS:
                if expression.startswith(const, i):
                    new_expression += " " + const + " "
                    i += len(const)
                    break
        else:
            new_expression += expression[i]
            i += 1
    return new_expression

def clean_brackets(expression:str):
    while True:
        pre_replace = expression
        replaced = expression.replace("( ", "(").replace(" )", ")").replace("  ", " ")
        if replaced == pre_replace:
            return replaced
        else:
            expression = replaced


def preserve_function_spacing(expression:str):
    functions = ''+'|'.join(FUNCTIONS) + ''
    regex = f"({functions})([ ])+([\\(\\[])"
    for found in re.findall(regex, expression):
        func = found[0]
        expression = expression.replace("".join(found), " " + func+found[2])
    return expression.strip()


def convert_numbers(expression:list[str]):
    """expression is in rpn"""
    for item in range(len(expression)):
        if expression[item].isnumeric():
            expression[item] = int(expression[item])
        elif expression[item].count(".") == 1 and expression[item].replace(".",'').isnumeric():
            expression[item] = float(expression[item])
    return expression


def preprocess(expression):
    
    operations = [
        str.lower,
        collapse_spaces,
        handle_implicit_operations,
        space_out_numbers,
        space_out_constants,
        clean_brackets,
        preserve_function_spacing,
    ]
    
    for op in operations:
        # print(op)
        expression = op(expression)
        # print(expression)
    
    return expression


def rpn(expression:str)->list:
    cleaned = preprocess(expression)
    rpn = convert_numbers(infix_to_rpn(cleaned))
    return rpn

tests = ["sin(pi/2)", "sin(2*pi)", "4*pi", "4pi", "pi(3*2)", "e^3"]

for e in tests:
    print("="*60)
    # print(preprocess(e))
    print(e)
    print(evaluate(rpn(e)))

