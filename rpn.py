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


def remove_outer_brackets(expression:list):
    if expression[0][0] == "(":
        
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
            expression[0] = expression[0][1:]
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

def infix_to_rpn(expr):
    
    def inner(root):
        e = root.value
        # print(e)
        
        if len(e) == 1:
            root.value = e[0]
        else:
            operator = find_lowest_precendence_operator(e)
            
            root.set_value(e[operator])
            
            root.add_left_child(remove_outer_brackets(e[:operator]))
            root.add_right_child(remove_outer_brackets(e[operator + 1:]))
            
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
    print(expression)
    
    functions = functions = ''+'|'.join(FUNCTIONS) + ''
    stack = []
    for item in expression:
        print(stack)
        # check for function:
        func = False
        if isinstance(item, str) and re.match(f"^({functions})", item) is not None:
            func, arg = item.split("(")
            arg = arg[:-1]
            stack.append(FUNCTION_FUNCTIONS[func](float(arg)))
            func = True
        else:
            stack.append(item)
        
        if type(item) == float or type(item) == int:
            pass
        elif not func:
            operator = stack.pop(-1)
            operand1 = stack.pop(-2)
            operand2 = stack.pop(-1)
            stack.append(OPERATOR_FUNCTIONS[operator](operand1, operand2))
    
    return stack[0]


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
    return expression


def space_out_numbers(expression:str):
    regex = "[\\d.]+|[()]"
    new_expression = ""
    for found in re.findall(regex, expression):
        partition = expression.partition(found)
        new_expression += partition[0] + " " + partition[1] + " "
        expression = partition[2]
    return new_expression.strip()


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


def collapse_spaces(expression:str):
    return expression.replace(" ", "")

def convert_numbers(expression:list[str]):
    """expression is in rpn"""
    for item in range(len(expression)):
        if expression[item].isnumeric():
            expression[item] = int(expression[item])
        elif expression[item].count(".") == 1 and expression[item].replace(".",'').isnumeric():
            expression[item] = float(expression[item])
    return expression

def preprocess(expression):
    return preserve_function_spacing(
        clean_brackets(
            space_out_numbers(
                handle_implicit_operations(
                    collapse_spaces(
                        expression.lower()
                        )
                    )
                )
            )
        )
    

def rpn(expression):
    cleaned = preprocess(expression)
    rpn = convert_numbers(infix_to_rpn(cleaned))
    return rpn


tests = ["(1-2)/3+22//2(9 +10)", "40+sin(20)tan(30)", "20.9(10)"]

# print(evaluate(rpn(e)))
for e in tests:
    print("=================")
    print(preprocess(e))
    print(evaluate(rpn(preprocess(e))))