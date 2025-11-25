import math
import re

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
IMPLICIT_OPERATOR = "*"

FUNCTIONS = ["sin", "cos", "tan"]
FUNCTION_FUNCTIONS = {
    "sin": lambda x: math.sin(x),
    "cos": lambda x: math.cos(x),
    "tan": lambda x: math.tan(x),
}

CONSTANTS = ["e", "pi"]
CONSTANT_CALUES = {
    "e": math.e,
    "pi": math.pi,
    "tau": math.tau,
}

class Node:
    
    def __init__(self, value):
        self.value = value
        self.left_child = None
        self.right_child = None
    
    def post_order_traversal(self, l = []):
        """
        traverses left node, traverses right node, takes value of root.
        """
        if self.left_child: l = self.left_child.post_order_traversal(l)
        
        if self.right_child: l = self.right_child.post_order_traversal(l)
        
        l.append(self.value)
        
        return l
    
    def __repr__(self):
        try:
            return f" {self.value}: {self.left_child.value}, {self.right_child.value}"
        except:
            return f" {self.value}"
    
    def add_left_child(self, value):
        self.left_child = Node(value)
    
    def add_right_child(self, value):
        self.right_child = Node(value)
    
    def set_value(self, value):
        self.value = value
    
    def __contains__(self, value:int):
        if value == self.value:
            return True
        
        elif value > self.value and self.right_child:
            return value in self.right_child
        
        elif value < self.value and self.left_child:
            return value in self.left_child
        
        else: return False


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
        print("inner")
        print(root.value)
        e = root.value
        # check for function wrapping the entire expression:
        
        functions = ''+'|'.join(FUNCTIONS) + ''
        regex = f"^({functions})\\("
        m = re.match(regex, e[0])
        if m is not None and check_fully_bracketed(e):
            print("fully bracketed")
            print(m.group()[:-1])
            print("====")
            root.value = m.group()[:-1]
            
            if len(e) == 1:
                root.value = m.group()[:-1]
                argument = e[0][len(m.group()):-1]
                print("HIIII")
                print(root.value, argument)
                
                root.add_left_child(argument)
                
            else:
                print("OTHER HI")
                print(m.group()[:-1])
                print(remove_outer_brackets(e, function=m.group()[:-1]))
                root.value = m.group()[:-1]
                
                root.add_left_child(remove_outer_brackets(e, function=m.group()[:-1]))
                print(root.left_child.value)
                
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
    print("EVALUATING")
    print(expression)
    
    stack = []
    for item in expression:
        print(stack)
        
        stack.append(item)
        
        if type(item) == float or type(item) == int:
            pass
        else:
            # check for function:
            if item in FUNCTIONS:
                function = stack.pop(-1)
                operand = stack.pop(-1)
                stack.append(FUNCTION_FUNCTIONS[function](operand))
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
    
    return expression


def space_out_numbers(expression:str):
    regex = "[\\d.]+|[()]"
    new_expression = ""
    for found in re.findall(regex, expression):
        partition = expression.partition(found)
        new_expression += partition[0] + " " + partition[1] + " "
        expression = partition[2]
    return new_expression.strip()


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
        clean_brackets,
        preserve_function_spacing,
    ]
    
    for op in operations:
        expression = op(expression)
    
    return expression


def rpn(expression):
    cleaned = preprocess(expression)
    rpn = convert_numbers(infix_to_rpn(cleaned))
    return rpn

tests = ["sin(30)", "40+sin(20)tan(30*2)", "sin(pi/2)", "sin(2*pi)"]

for e in tests:
    print("=================")
    print(preprocess(e))
    # print(evaluate(rpn(e)))