import ast
import os
from robot.parsing.model import ResourceFile

class func_info(object):
    def __init__(self, func_name, lineno, alias=None):
        self.func_name = func_name
        self.call_name = func_name.replace('_', ' ').title()
        self.alias = alias
        self.lineno = lineno
        self.marker = False
    
    def robot_wrap(self):
        end_call_name = "  " + str(self.call_name).lower()
        end_alias = "  " + str(self.alias).lower()
        in_line_call_name = "  " + str(self.call_name).lower() + "  "
        in_line_alias = "  " + str(self.alias).lower() + "  "
        return end_call_name, end_alias, in_line_call_name, in_line_alias
    
    def py_wrap(self):
        return '.' + str(self.func_name) + '('

class pyparse(object):
    def __init__(self, path):
        self._file_path = path
        self.all_func_info = []

    def build(self, method):
        if not isinstance(method, ast.FunctionDef):
            raise Exception('Method is not function')
        if len(method.decorator_list):
            for deco in method.decorator_list:
                if type(deco) == ast.Call:
                    if deco.args:
                        return func_info(method.name, method.lineno, deco.args[0].s)
                    if deco.keywords:
                        return func_info(method.name, method.lineno, deco.keywords[0].value.s)
        return func_info(method.name, method.lineno)
    
    def do(self):
        with open(self._file_path, "r") as f:
            module = ast.parse(f.read())
            for node in module.body:
                if isinstance(node, ast.FunctionDef):
                    self.all_func_info.append( self.build(node) )
                
                if isinstance(node, ast.ClassDef):
                    for method in node.body:
                        if isinstance(method, ast.FunctionDef):
                            self.all_func_info.append( self.build(method) )

if __name__ == "__main__":
    import sys
    root = os.getcwd()
    py_path = os.path.join(root, sys.argv[1])
    if not os.path.exists(py_path) or not sys.argv[1].endswith(".py"):
        exit(1)
    p = pyparse(py_path)
    p.do()

    robot_files, py_files, filtered_files = [], [], []
    for subdir, dirs, files in os.walk(root):
        for f in files:
            path = subdir + os.sep + f
            if path.endswith('.robot') or path.endswith('.txt'):
                robot_files.append(path)
            elif path.endswith('.txt'):
                try:
                    r = ResourceFile(path).populate()
                    robot_files.append(path)
                except:
                    filtered_files.append(path)
            elif path.endswith('.py'):
                py_files.append(path)
            else:
                filtered_files.append(path)

    for robot_file in robot_files:
        with open(robot_file, 'r', encoding='utf-8') as rf:
            for line in rf:
                if not line.startswith('#'):
                    for i in range(len(p.all_func_info)):
                        end_call_name, end_alias, in_line_call_name, in_line_alias = p.all_func_info[i].robot_wrap()
                        if line.lower().strip('\n').endswith(end_call_name) or line.lower().strip('\n').endswith(end_alias):
                            p.all_func_info[i].marker = True
                        elif in_line_call_name in line.lower() or in_line_alias in line.lower():
                            p.all_func_info[i].marker = True

    for py_file in py_files:
        with open(py_file, 'r', encoding='utf-8') as pf:
            for line in pf:
                if not line.startswith('#'):
                    for i in range(len(p.all_func_info)):
                        func_name = p.all_func_info[i].py_wrap()
                        if func_name in line:
                            p.all_func_info[i].marker = True

    for afi in p.all_func_info:
        if not afi.marker:
            print("Unused keyword '{}' at line {}".format(afi.func_name, afi.lineno))