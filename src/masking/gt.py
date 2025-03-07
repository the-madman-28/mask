import json
import math

class TreeNode:
    def __init__(self, data):
        self.data = data
        self.children = []

def input_tree():
    data = input("Enter the root node data: ").strip()
    if not data:
        return None
    
    root = TreeNode(data)
    queue = [root]
    
    while queue:
        current = queue.pop(0)
        
        while True:
            child_data = input(f"Enter a child for {current.data} (or press Enter to finish): ").strip()
            if not child_data:
                break
            child_node = TreeNode(child_data)
            current.children.append(child_node)
            queue.append(child_node)
    
    return root

def tree_to_dict(node):
    if node is None:
        return None
    
    return {
        "data": node.data,
        "children": [tree_to_dict(child) for child in node.children]
    }

def tree_to_json(root):
    tree_dict = tree_to_dict(root)
    return json.dumps(tree_dict, indent=4)

def load_tree_from_json(json_data):
    def dict_to_tree(d):
        if d is None:
            return None
        
        node = TreeNode(d["data"])
        for child_dict in d["children"]:
            child_node = dict_to_tree(child_dict)
            if child_node:
                node.children.append(child_node)
        return node
    
    # Load JSON data from a string or file
    if isinstance(json_data, str):
        if json_data.startswith("{") and json_data.endswith("}"):
            # It's a JSON string
            tree_dict = json.loads(json_data)
        else:
            # Assume it's a file path
            with open(json_data, 'r') as file:
                tree_dict = json.load(file)
    else:
        # Assume it's a dictionary
        tree_dict = json_data
    
    return dict_to_tree(tree_dict)

def print_tree(root):
    if root is None:
        print("The tree is empty.")
        return
    
    def print_tree_recursive(node, prefix="", is_last=True):
        # Print the current node
        print(prefix + ("└── " if is_last else "├── ") + node.data)
        
        # Determine the prefix for the children
        child_prefix = prefix + ("    " if is_last else "│   ")
        
        # Print the children
        for i, child in enumerate(node.children):
            print_tree_recursive(child, child_prefix, i == len(node.children) - 1)
    
    print_tree_recursive(root)

def find_node_at_height(root, leaf_data, target_height):
    def find_leaf_node(node, data):
        if node is None:
            return None
        if not node.children and node.data == data:
            return node
        for child in node.children:
            result = find_leaf_node(child, data)
            if result:
                return result
        return None

    def calculate_height(node, data, current_height):
        if node is None:
            return -1
        if node.data == data:
            return current_height
        for child in node.children:
            result = calculate_height(child, data, current_height + 1)
            if result != -1:
                return result
        return -1

    def find_node_at_target_height(node, current_height, target_height):
        if node is None:
            return None
        if current_height == target_height:
            return node
        for child in node.children:
            result = find_node_at_target_height(child, current_height + 1, target_height)
            if result:
                return result
        return None

    # Step 1: Find the leaf node with the given data
    leaf_node = find_leaf_node(root, leaf_data)
    if not leaf_node:
        return None  # Leaf node not found

    # Step 2: Calculate the height of the leaf node from the root
    leaf_height = calculate_height(root, leaf_node.data, 0)

    # Step 3: Calculate the target height from the leaf node
    target_height_from_leaf = leaf_height - math.ceil(target_height)
    print(f'Leaf height: {leaf_height}, target height: {target_height_from_leaf}')

    # Step 4: Find the node at the target height from the root
    target_node = find_node_at_target_height(root, 0, target_height_from_leaf)

    return target_node

def find_node_at_height_in_path(root, leaf_data, target_height):
    def find_leaf_node_and_path(node, data, path):
        if node is None:
            return None, []
        if not node.children and node.data == data:
            return node, path + [node]
        for child in node.children:
            result_node, result_path = find_leaf_node_and_path(child, data, path + [node])
            if result_node:
                return result_node, result_path
        return None, []
    
    def calculate_height(node, data, current_height):
        if node is None:
            return -1
        if node.data == data:
            return current_height
        for child in node.children:
            result = calculate_height(child, data, current_height + 1)
            if result != -1:
                return result
        return -1

    # Step 1: Find the leaf node with the given data and the path from root to leaf
    leaf_node, path = find_leaf_node_and_path(root, leaf_data, [])
    if not leaf_node:
        return None  # Leaf node not found

    # Step 2: Calculate the target height from the leaf node
    leaf_height = calculate_height(root, leaf_node.data, 0)
    target_height_from_leaf = leaf_height - math.ceil(target_height)

    # Step 3: Find the node at the target height in the path
    if target_height_from_leaf < 0 or target_height_from_leaf >= len(path):
        return None  # Target height is out of bounds

    return path[target_height_from_leaf]
# Example usage:
# Assuming you have a tree created using the previous code
# root = input_tree()
# leaf_data = "some_leaf_data"
# target_height = 2.5
# result_node = find_node_at_height(root, leaf_data, target_height)
# if result_node:
#     print(f"Node at ceil({target_height}) height from leaf node '{leaf_data}': {result_node.data}")
# else:
#     print("Node not found.")

def main():
    # print("Enter the tree in level-order traversal format.")
    # root = input_tree()
    
    # if root is None:
    #     print("The tree is empty.")
    # else:
    #     json_output = tree_to_json(root)
    #     print("Tree in JSON format:")
    #     print(json_output)
        
    #     # Save the JSON to a file
    #     with open("tree.json", "w") as file:
    #         file.write(json_output)
        
        # Load the tree from the saved JSON file
    loaded_root = load_tree_from_json("tree.json")
    
    if loaded_root is None:
        print("The loaded tree is empty.")
    else:
        print("Loaded tree in JSON format:")
        print(print_tree(loaded_root))
        # print(tree_to_json(loaded_root))

    leaf_data = "14"
    target_height = 1.5
    result_node = find_node_at_height_in_path(loaded_root, leaf_data, target_height)
    if result_node:
        print(f"Node at ceil({target_height}) height from leaf node '{leaf_data}': {result_node.data}")
    else:
        print("Node not found.")

if __name__ == "__main__":
    main()