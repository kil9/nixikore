import yaml


class Category:
    def __init__(self, filename):
        self.category = self.load_category(filename)

    def load_category(self, filename):
        with open(filename, 'r') as stream:
            category = yaml.load(stream)

        return category

    def find_node(self, name):
        root = self.category
        return self.search_children(root, name)

    def search_children(self, node, name):
        if node['name'] == name:
            return node
        elif 'children' not in node:
            return None
        else:
            for child in node['children']:
                answer = self.search_children(child, name)
                if answer:
                    return answer
            return None

    def all_children(self, node):
        result = []
        result.append(node['name'])
        if 'children' in node:
            for child in node['children']:
                result += self.all_children(child)
        return result


Categories = Category('data/category.yaml')

if __name__ == "__main__":
    cat = Category('data/category.yaml')

    __import__('pprint').pprint(cat.find_node('사람'))
    __import__('pprint').pprint(cat.all_children(cat.find_node('동물')))
