import json

from utility import save_json

class TreeNode:
    '''
    TreeNode class to store a node data. It has three 
    '''
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None

def input_tree():
    data = input("Enter the root node data: ").strip()
    if not data:
        return None
    
    root = TreeNode(data.lower())
    queue = [root]
    
    while queue:
        current = queue.pop(0)
        
        left_data = input(f"Enter the left child of {current.data} (or press Enter if no left child): ").strip()
        if left_data:
            current.left = TreeNode(left_data.lower()) # type: ignore
            queue.append(current.left) # type: ignore
        else:
            current.left = None
        
        right_data = input(f"Enter the right child of {current.data} (or press Enter if no right child): ").strip()
        if right_data:
            current.right = TreeNode(right_data.lower()) # type: ignore
            queue.append(current.right) # type: ignore
        else:
            current.right = None

    return root

def tree_to_dict(node):
    if node is None:
        return None
    
    return {
        "data": node.data,
        "left": tree_to_dict(node.left),
        "right": tree_to_dict(node.right)
    }

def tree_to_json(root):
    tree_dict = tree_to_dict(root)
    return json.dumps(tree_dict, indent=4)

def load_tree_from_json(json_data):
    def dict_to_tree(d):
        if d is None:
            return None
        
        node = TreeNode(d["data"])
        node.left = dict_to_tree(d["left"]) # type: ignore
        node.right = dict_to_tree(d["right"]) # type: ignore
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

def main():
    # print("Enter the binary tree in level-order traversal format.")
    # root = input_tree()
    
    # if root is None:
    #     print("The tree is empty.")
    # else:
    #     json_output = tree_to_json(root)
    #     save_json(tree_to_dict(root), 'education.json')
    #     print("Tree in JSON format:")
    #     print(json_output)

    loaded_root = load_tree_from_json("education.json")
        
    if loaded_root is None:
        print("The loaded tree is empty.")
    else:
        print("Loaded tree in JSON format:")
        print(tree_to_json(loaded_root))

if __name__ == "__main__":
    main()