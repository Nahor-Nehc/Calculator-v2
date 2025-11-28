


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

