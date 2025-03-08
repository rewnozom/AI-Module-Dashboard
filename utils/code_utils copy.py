# ./utils/code_utils.py
import re
import os
import ast

class CodeAnalyzer:
    """
    Verktyg för att analysera och extrahera information från kod.
    """
    
    @staticmethod
    def extract_python_functions(code):
        """
        Extrahera Python-funktioner från given kod.
        Returnerar en lista med funktionsdefinitioner, med både dekoratorer och docstrings.
        """
        try:
            tree = ast.parse(code)
            functions = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Hämta funktionskoden genom att extrahera raderna från källkoden
                    function_code = ast.get_source_segment(code, node)
                    if function_code:
                        functions.append({
                            'name': node.name,
                            'code': function_code,
                            'lineno': node.lineno
                        })
            
            return functions
        except SyntaxError:
            # Om koden inte är giltig Python
            return []
    
    @staticmethod
    def extract_python_classes(code):
        """
        Extrahera Python-klasser från given kod.
        Returnerar en lista med klassdefinitioner och deras metoder.
        """
        try:
            tree = ast.parse(code)
            classes = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Hämta klasskoden genom att extrahera raderna från källkoden
                    class_code = ast.get_source_segment(code, node)
                    
                    # Hitta metoder i klassen
                    methods = []
                    for child in node.body:
                        if isinstance(child, ast.FunctionDef):
                            methods.append(child.name)
                    
                    if class_code:
                        classes.append({
                            'name': node.name,
                            'code': class_code,
                            'methods': methods,
                            'lineno': node.lineno
                        })
            
            return classes
        except SyntaxError:
            # Om koden inte är giltig Python
            return []
    
    @staticmethod
    def extract_js_functions(code):
        """
        Extrahera JavaScript-funktioner från given kod med hjälp av reguljära uttryck.
        Detta är en enkel implementering som inte hanterar alla fall.
        """
        # Reguljärt uttryck för traditionella JavaScript-funktioner
        traditional_func_pattern = r'function\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\([^)]*\)\s*\{(?:[^{}]|(?:\{[^{}]*\}))*\}'
        traditional_funcs = re.findall(traditional_func_pattern, code)
        
        # Reguljärt uttryck för ES6 arrow functions
        arrow_func_pattern = r'(?:const|let|var)\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*(?:\([^)]*\)|\w+)\s*=>\s*\{[^}]*\}'
        arrow_funcs = re.findall(arrow_func_pattern, code)
        
        # Kombinera alla hittade funktioner
        all_functions = traditional_funcs + arrow_funcs
        
        return all_functions
    
    @staticmethod
    def extract_imports(code, language="python"):
        """
        Extrahera importsatser baserat på programmeringsspråk.
        """
        if language == "python":
            try:
                tree = ast.parse(code)
                imports = []
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append({
                                'type': 'import',
                                'name': alias.name,
                                'alias': alias.asname,
                                'line': f"import {alias.name}" + (f" as {alias.asname}" if alias.asname else "")
                            })
                    
                    elif isinstance(node, ast.ImportFrom):
                        module = node.module or ''
                        level = '.' * node.level if node.level > 0 else ''
                        for alias in node.names:
                            imports.append({
                                'type': 'importfrom',
                                'module': module,
                                'name': alias.name,
                                'alias': alias.asname,
                                'level': node.level,
                                'line': f"from {level}{module} import {alias.name}" + (f" as {alias.asname}" if alias.asname else "")
                            })
                
                return imports
            except SyntaxError:
                return []
        
        elif language == "javascript":
            # Enkel regex för JavaScript-imports (endast för typiska ES6-imports)
            import_patterns = [
                r'import\s+\{([^}]+)\}\s+from\s+[\'"]([^\'"]*)[\'"]\s*;?\s*',  # import { x, y } from 'module';
                r'import\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s+from\s+[\'"]([^\'"]*)[\'"]\s*;?\s*'  # import x from 'module';
            ]
            
            imports = []
            for pattern in import_patterns:
                for match in re.finditer(pattern, code):
                    imports.append({
                        'type': 'import',
                        'line': match.group(0).strip()
                    })
            
            return imports
        
        else:
            return []
    
    @staticmethod
    def format_python_code(code):
        """
        Formatera Python-kod för bättre läsbarhet.
        Detta är en enkel implementering som kan utökas med black/autopep8 eller liknande.
        """
        try:
            # Parsea koden för att verifiera att den är korrekt
            tree = ast.parse(code)
            
            lines = code.split('\n')
            formatted_lines = []
            
            indent_level = 0
            for line in lines:
                stripped = line.strip()
                
                # Justera indenteringsnivå baserat på raden
                if stripped.endswith(':') and not stripped.startswith(('else', 'elif', 'except', 'finally')):
                    # Raderna som ökar indenteringen (def, class, if, etc.)
                    formatted_lines.append('    ' * indent_level + stripped)
                    indent_level += 1
                elif stripped.startswith(('else:', 'elif', 'except:', 'finally:')):
                    # Raderna som behåller tidigare indentering (else, elif, etc.)
                    indent_level = max(0, indent_level - 1)
                    formatted_lines.append('    ' * indent_level + stripped)
                    indent_level += 1
                elif stripped == '' and indent_level > 0:
                    # Tomma rader behåller indentering
                    formatted_lines.append('')
                else:
                    # De flesta andra rader
                    if stripped and stripped[0] == '}' and indent_level > 0:
                        indent_level -= 1
                    formatted_lines.append('    ' * indent_level + stripped)
                    if stripped and stripped[-1] == '{':
                        indent_level += 1
            
            return '\n'.join(formatted_lines)
        except SyntaxError:
            # Om det är ogiltigt Python, returnera oformaterad kod
            return code

class CodeGenerator:
    """
    Verktyg för att generera kod baserat på mallar.
    """
    
    @staticmethod
    def generate_python_class(class_name, methods=None, base_classes=None):
        """
        Generera en Python-klassmall.
        
        Args:
            class_name (str): Namnet på klassen
            methods (list): Lista med metodnamn att inkludera
            base_classes (list): Lista med basklasser
        
        Returns:
            str: Genererad Python-klasskod
        """
        if methods is None:
            methods = ["__init__"]
        
        if base_classes is None:
            base_classes = []
        
        inheritance = f"({', '.join(base_classes)})" if base_classes else ""
        
        code = [f"class {class_name}{inheritance}:"]
        code.append(f'    """')
        code.append(f'    {class_name} - Beskrivning av klassen.')
        code.append(f'    """')
        code.append("")
        
        for method in methods:
            if method == "__init__":
                code.append("    def __init__(self):")
                code.append('        """Initialisera {class_name}."""')
                code.append("        pass")
            else:
                code.append(f"    def {method}(self):")
                code.append(f'        """Implementera {method}."""')
                code.append("        pass")
            code.append("")
        
        return "\n".join(code)
    
    @staticmethod
    def generate_python_function(function_name, params=None, return_type=None):
        """
        Generera en Python-funktionsmall.
        
        Args:
            function_name (str): Namnet på funktionen
            params (list): Lista med parametrar
            return_type (str): Returtyp för funktionen
        
        Returns:
            str: Genererad Python-funktionskod
        """
        if params is None:
            params = []
        
        param_str = ", ".join(params)
        type_hint = f" -> {return_type}" if return_type else ""
        
        code = [f"def {function_name}({param_str}){type_hint}:"]
        code.append(f'    """')
        code.append(f'    {function_name} - Beskrivning av funktionen.')
        
        if params:
            code.append(f'    ')
            code.append(f'    Args:')
            for param in params:
                param_name = param.split(':')[0].strip() if ':' in param else param.strip()
                code.append(f'        {param_name}: Beskrivning av parameter')
        
        if return_type:
            code.append(f'    ')
            code.append(f'    Returns:')
            code.append(f'        {return_type}: Beskrivning av returvärde')
        
        code.append(f'    """')
        code.append("    pass")
        
        return "\n".join(code)
    
    @staticmethod
    def generate_js_class(class_name, methods=None):
        """
        Generera en JavaScript ES6-klassmall.
        
        Args:
            class_name (str): Namnet på klassen
            methods (list): Lista med metodnamn att inkludera
        
        Returns:
            str: Genererad JavaScript-klasskod
        """
        if methods is None:
            methods = ["constructor"]
        
        code = [f"class {class_name} {{"]
        
        for method in methods:
            if method == "constructor":
                code.append("  constructor() {")
                code.append("    // Initialisering här")
                code.append("  }")
            else:
                code.append(f"  {method}() {{")
                code.append(f"    // Implementera {method}")
                code.append("  }")
        
        code.append("}")
        
        return "\n".join(code)

class CodeModuleManager:
    """
    Hanterare för kodmoduler, ansvarig för att läsa, skriva och organisera moduler.
    """
    
    def __init__(self, base_directory="./modules/"):
        self.base_directory = base_directory
        
        # Säkerställ att baskatalogen existerar
        os.makedirs(self.base_directory, exist_ok=True)
        
        # Skapa kataloger för olika språk om de inte finns
        language_dirs = ["python", "javascript", "typescript", "cpp", "html", "css", "java"]
        self.language_directories = {}
        
        for lang in language_dirs:
            lang_dir = os.path.join(self.base_directory, lang)
            os.makedirs(lang_dir, exist_ok=True)
            self.language_directories[lang] = lang_dir
    
    def get_language_from_extension(self, extension):
        """
        Returnera språk baserat på filändelse.
        """
        extension = extension.lower()
        extension_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".cpp": "cpp",
            ".c": "cpp",
            ".h": "cpp",
            ".hpp": "cpp",
            ".html": "html",
            ".css": "css",
            ".java": "java"
        }
        
        return extension_map.get(extension, "other")
    
    def save_module(self, module_name, code, extension=".py"):
        """
        Spara en kodmodul till lämplig katalog baserat på filändelse.
        """
        if not extension.startswith('.'):
            extension = '.' + extension
        
        language = self.get_language_from_extension(extension)
        if language in self.language_directories:
            target_dir = self.language_directories[language]
        else:
            target_dir = os.path.join(self.base_directory, "other")
            os.makedirs(target_dir, exist_ok=True)
        
        file_path = os.path.join(target_dir, f"{module_name}{extension}")
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(code)
            return True, file_path
        except Exception as e:
            return False, str(e)
    
    def load_module(self, file_path):
        """
        Ladda en kodmodul från en fil.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            module_name = os.path.splitext(os.path.basename(file_path))[0]
            extension = os.path.splitext(file_path)[1]
            
            return {
                "name": module_name,
                "extension": extension,
                "code": code,
                "path": file_path
            }
        except Exception as e:
            return None
    
    def list_modules(self, language=None):
        """
        Lista alla tillgängliga moduler, eventuellt filtrerat per språk.
        """
        modules = []
        
        if language and language in self.language_directories:
            # Lista endast moduler för ett specifikt språk
            lang_dir = self.language_directories[language]
            for file_name in os.listdir(lang_dir):
                file_path = os.path.join(lang_dir, file_name)
                if os.path.isfile(file_path):
                    module = self.load_module(file_path)
                    if module:
                        modules.append(module)
        else:
            # Lista alla moduler
            for lang, lang_dir in self.language_directories.items():
                if os.path.exists(lang_dir):
                    for file_name in os.listdir(lang_dir):
                        file_path = os.path.join(lang_dir, file_name)
                        if os.path.isfile(file_path):
                            module = self.load_module(file_path)
                            if module:
                                module["language"] = lang
                                modules.append(module)
        
        return modules