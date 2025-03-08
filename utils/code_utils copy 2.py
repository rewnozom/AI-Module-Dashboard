
# ./utils/code_utils.py
import os
import re
import ast
import time
import json
from pathlib import Path
from datetime import datetime

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
                        # Extrahera funktion med parametrar
                        params = []
                        for arg in node.args.args:
                            if hasattr(arg, 'annotation') and arg.annotation:
                                if isinstance(arg.annotation, ast.Name):
                                    params.append(f"{arg.arg}: {arg.annotation.id}")
                                else:
                                    params.append(arg.arg)
                            else:
                                params.append(arg.arg)
                        
                        functions.append({
                            'name': node.name,
                            'code': function_code,
                            'lineno': node.lineno,
                            'params': params,
                            'has_docstring': ast.get_docstring(node) is not None
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
                    methods = {}
                    class_vars = {}
                    
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            # Extrahera metod med parametrar
                            params = []
                            for arg in item.args.args:
                                if hasattr(arg, 'annotation') and arg.annotation:
                                    if isinstance(arg.annotation, ast.Name):
                                        params.append(f"{arg.arg}: {arg.annotation.id}")
                                    else:
                                        params.append(arg.arg)
                                else:
                                    params.append(arg.arg)
                            
                            methods[item.name] = {
                                'lineno': item.lineno,
                                'params': params,
                                'has_docstring': ast.get_docstring(item) is not None
                            }
                        elif isinstance(item, ast.Assign):
                            # Hitta klassvariabler
                            for target in item.targets:
                                if isinstance(target, ast.Name):
                                    class_vars[target.id] = {
                                        'lineno': item.lineno
                                    }
                    
                    if class_code:
                        classes.append({
                            'name': node.name,
                            'code': class_code,
                            'methods': methods,
                            'properties': class_vars,
                            'lineno': node.lineno,
                            'has_docstring': ast.get_docstring(node) is not None,
                            'base_classes': [base.id for base in node.bases if isinstance(base, ast.Name)]
                        })
            
            return classes
        except SyntaxError:
            # Om koden inte är giltig Python
            return []
    
    @staticmethod
    def extract_javascript_functions(code):
        """
        Extrahera JavaScript-funktioner från given kod med hjälp av reguljära uttryck.
        Detta är en enkel implementering som inte hanterar alla fall.
        """
        functions = []
        
        # Reguljära uttryck för olika funktionstyper
        patterns = [
            # Traditionella funktioner
            r'function\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\(([^)]*)\)',
            # Arrow-funktioner (med variabeldeklarationer)
            r'(?:const|let|var)\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*(?:\(([^)]*)\)|([a-zA-Z_$][a-zA-Z0-9_$]*))\s*=>',
            # Funktionsuttryck
            r'(?:const|let|var)\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*function\s*\(([^)]*)\)'
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, code):
                func_name = match.group(1)
                params_str = match.group(2) if len(match.groups()) > 1 and match.group(2) else ""
                params = [p.strip() for p in params_str.split(',') if p.strip()]
                
                # Hitta radnummer
                line_no = code[:match.start()].count('\n') + 1
                
                # Försök att extrahera funktionskroppen
                end_pos = None
                if "{" in code[match.end():]:
                    open_braces = 0
                    for i, char in enumerate(code[match.end():]):
                        if char == '{':
                            open_braces += 1
                        elif char == '}':
                            open_braces -= 1
                            if open_braces == 0:
                                end_pos = match.end() + i + 1
                                break
                
                function_code = ""
                if end_pos:
                    function_code = code[match.start():end_pos]
                
                functions.append({
                    'name': func_name,
                    'params': params,
                    'lineno': line_no,
                    'code': function_code
                })
        
        return functions
    
    @staticmethod
    def extract_javascript_classes(code):
        """
        Extrahera JavaScript-klasser från given kod.
        Detta är en enkel implementering med reguljära uttryck.
        """
        classes = []
        
        # Reguljärt uttryck för klassdeklarationer
        class_pattern = r'class\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*(?:extends\s+([a-zA-Z_$][a-zA-Z0-9_$]*))?\s*\{'
        
        for match in re.finditer(class_pattern, code):
            class_name = match.group(1)
            extends = match.group(2)
            
            line_no = code[:match.start()].count('\n') + 1
            
            bases = [extends] if extends else []
            
            # Hitta slut på klassen
            class_start = match.start()
            brace_count = 0
            class_end = class_start
            
            for i, char in enumerate(code[class_start:]):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        class_end = class_start + i + 1
                        break
            
            class_code = code[class_start:class_end]
            
            # Hitta metoder och egenskaper
            methods = {}
            properties = {}
            
            # Hitta metoder
            method_pattern = r'(?:async\s+)?(?:static\s+)?(?:get\s+|set\s+)?([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\(([^)]*)\)'
            for m_match in re.finditer(method_pattern, class_code):
                method_name = m_match.group(1)
                params_str = m_match.group(2)
                params = [p.strip() for p in params_str.split(',') if p.strip()]
                
                local_line_no = class_code[:m_match.start()].count('\n') + 1
                method_line_no = code[:class_start].count('\n') + local_line_no
                
                methods[method_name] = {
                    'lineno': method_line_no,
                    'params': params
                }
            
            # Hitta egenskaper/fält
            property_pattern = r'this\.([a-zA-Z_$][a-zA-Z0-9_$]*)\s*='
            for p_match in re.finditer(property_pattern, class_code):
                prop_name = p_match.group(1)
                
                local_line_no = class_code[:p_match.start()].count('\n') + 1
                prop_line_no = code[:class_start].count('\n') + local_line_no
                
                properties[prop_name] = {
                    'lineno': prop_line_no
                }
            
            classes.append({
                'name': class_name,
                'code': class_code,
                'methods': methods,
                'properties': properties,
                'lineno': line_no,
                'base_classes': bases
            })
        
        return classes
    
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
                                'line': f"import {alias.name}" + (f" as {alias.asname}" if alias.asname else ""),
                                'lineno': node.lineno
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
                                'line': f"from {level}{module} import {alias.name}" + (f" as {alias.asname}" if alias.asname else ""),
                                'lineno': node.lineno
                            })
                
                return imports
            except SyntaxError:
                return []
        
        elif language == "javascript":
            # Enkel regex för JavaScript-imports (endast för typiska ES6-imports)
            imports = []
            
            # Olika mönster för JS-imports
            patterns = [
                # import { x, y } from 'module';
                (r'import\s+\{([^}]+)\}\s+from\s+[\'"]([^\'"]*)[\'"]\s*;?\s*', 'destructuring'),
                # import x from 'module';
                (r'import\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s+from\s+[\'"]([^\'"]*)[\'"]\s*;?\s*', 'default'),
                # import * as x from 'module';
                (r'import\s+\*\s+as\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s+from\s+[\'"]([^\'"]*)[\'"]\s*;?\s*', 'namespace')
            ]
            
            for pattern, import_type in patterns:
                for match in re.finditer(pattern, code):
                    line_no = code[:match.start()].count('\n') + 1
                    
                    if import_type == 'destructuring':
                        items = [item.strip() for item in match.group(1).split(',')]
                        module = match.group(2)
                        
                        for item in items:
                            # Hantera "as" alias inom destructuring
                            if " as " in item:
                                name, alias = item.split(" as ", 1)
                                name = name.strip()
                                alias = alias.strip()
                            else:
                                name = item.strip()
                                alias = None
                            
                            imports.append({
                                'type': 'import_destructuring',
                                'name': name,
                                'alias': alias,
                                'module': module,
                                'line': match.group(0).strip(),
                                'lineno': line_no
                            })
                    
                    elif import_type == 'default':
                        name = match.group(1)
                        module = match.group(2)
                        
                        imports.append({
                            'type': 'import_default',
                            'name': name,
                            'module': module,
                            'line': match.group(0).strip(),
                            'lineno': line_no
                        })
                    
                    elif import_type == 'namespace':
                        name = match.group(1)
                        module = match.group(2)
                        
                        imports.append({
                            'type': 'import_namespace',
                            'name': name,
                            'module': module,
                            'line': match.group(0).strip(),
                            'lineno': line_no
                        })
            
            return imports
        
        else:
            return []
    
    @staticmethod
    def extract_variables(code, language="python"):
        """
        Extrahera globala variabler från koden.
        """
        if language == "python":
            try:
                tree = ast.parse(code)
                variables = []
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Assign) and all(isinstance(target, ast.Name) for target in node.targets):
                        # Försök få värdetext
                        value_text = ast.get_source_segment(code, node.value) if hasattr(ast, 'get_source_segment') else ""
                        
                        for target in node.targets:
                            variables.append({
                                'name': target.id,
                                'value': value_text,
                                'lineno': node.lineno
                            })
                
                return variables
            except SyntaxError:
                return []
        
        elif language == "javascript":
            # Regex för JavaScript-variabeldeklarationer
            variables = []
            
            # Mönster för JS-variabler
            patterns = [
                # const x = value;
                r'const\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*([^;]*);',
                # let x = value;
                r'let\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*([^;]*);',
                # var x = value;
                r'var\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*([^;]*);'
            ]
            
            for pattern in patterns:
                for match in re.finditer(pattern, code):
                    name = match.group(1)
                    value = match.group(2).strip()
                    line_no = code[:match.start()].count('\n') + 1
                    
                    variables.append({
                        'name': name,
                        'value': value,
                        'lineno': line_no
                    })
            
            return variables
        
        else:
            return []
    
    @staticmethod
    def format_python_code(code):
        """
        Formatera Python-kod för bättre läsbarhet.
        Detta är en enkel implementering utan external dependencies.
        """
        try:
            # Parsea koden för att verifiera att den är korrekt
            tree = ast.parse(code)
            
            lines = code.split('\n')
            formatted_lines = []
            
            indent_level = 0
            for line in lines:
                stripped = line.strip()
                
                # Skip tomma rader
                if not stripped:
                    formatted_lines.append("")
                    continue
                
                # Justera indenteringsnivå
                if stripped.startswith(('else:', 'elif ', 'except:', 'finally:', 'except ')):
                    indent_level = max(0, indent_level - 1)
                
                formatted_lines.append('    ' * indent_level + stripped)
                
                # Uppdatera indentering för nästa rad
                if stripped.endswith(':') and not stripped.startswith('#'):
                    indent_level += 1
                elif stripped in ('break', 'continue', 'raise', 'return', 'pass'):
                    # Inget speciellt här, behåll indentering
                    pass
            
            return '\n'.join(formatted_lines)
        except SyntaxError:
            # Om det är ogiltigt Python, returnera oformaterad kod
            return code
    
    @staticmethod
    def format_javascript_code(code):
        """
        Formatera JavaScript-kod för bättre läsbarhet.
        Detta är en enkel implementering utan external dependencies.
        """
        try:
            lines = code.split('\n')
            formatted_lines = []
            
            indent_level = 0
            for line in lines:
                stripped = line.strip()
                
                # Skip tomma rader
                if not stripped:
                    formatted_lines.append("")
                    continue
                
                # Justera indentering för slutkrullparanteser
                if stripped.startswith('}'):
                    indent_level = max(0, indent_level - 1)
                
                formatted_lines.append('  ' * indent_level + stripped)
                
                # Uppdatera indentering för nästa rad baserat på öppna krullparanteser
                if stripped.endswith('{'):
                    indent_level += 1
            
            return '\n'.join(formatted_lines)
        except Exception:
            # Vid fel, returnera oformaterat
            return code
    
    @staticmethod
    def detect_language(file_path):
        """
        Upptäck programmeringsspråk baserat på filändelse.
        """
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        if ext in ['.py']:
            return 'python'
        elif ext in ['.js', '.jsx']:
            return 'javascript'
        elif ext in ['.html', '.htm']:
            return 'html'
        elif ext in ['.css']:
            return 'css'
        elif ext in ['.java']:
            return 'java'
        elif ext in ['.cpp', '.c', '.h', '.hpp']:
            return 'cpp'
        else:
            return 'unknown'

class CodeGenerator:
    """
    Verktyg för att generera kod baserat på mallar.
    """
    
    @staticmethod
    def generate_python_class(class_name, methods=None, base_classes=None, doc=None):
        """
        Generera en Python-klassmall.
        
        Args:
            class_name (str): Namnet på klassen
            methods (list): Lista med metodnamn att inkludera
            base_classes (list): Lista med basklasser
            doc (str): Dokumentationstext för klassen
        
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
        code.append(f'    {doc or class_name + " - Beskrivning av klassen."}')
        code.append(f'    """')
        code.append("")
        
        for method in methods:
            if method == "__init__":
                code.append("    def __init__(self):")
                code.append(f'        """Initialisera {class_name}."""')
                code.append("        pass")
            else:
                code.append(f"    def {method}(self):")
                code.append(f'        """Implementera {method}."""')
                code.append("        pass")
            code.append("")
        
        return "\n".join(code)
    
    @staticmethod
    def generate_python_function(function_name, params=None, return_type=None, doc=None):
        """
        Generera en Python-funktionsmall.
        
        Args:
            function_name (str): Namnet på funktionen
            params (list): Lista med parametrar
            return_type (str): Returtyp för funktionen
            doc (str): Dokumentationstext för funktionen
        
        Returns:
            str: Genererad Python-funktionskod
        """
        if params is None:
            params = []
        
        param_str = ", ".join(params)
        type_hint = f" -> {return_type}" if return_type else ""
        
        code = [f"def {function_name}({param_str}){type_hint}:"]
        code.append(f'    """')
        code.append(f'    {doc or function_name + " - Beskrivning av funktionen."}')
        
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
    def generate_javascript_class(class_name, methods=None, extends=None, doc=None):
        """
        Generera en JavaScript ES6-klassmall.
        
        Args:
            class_name (str): Namnet på klassen
            methods (list): Lista med metodnamn att inkludera
            extends (str): Klass att ärva från
            doc (str): Dokumentationstext för klassen
        
        Returns:
            str: Genererad JavaScript-klasskod
        """
        if methods is None:
            methods = ["constructor"]
        
        extends_str = f" extends {extends}" if extends else ""
        
        code = []
        
        # Lägg till JSDoc för klassen
        code.append("/**")
        code.append(f" * {doc or class_name + ' - Beskrivning av klassen'}")
        if extends:
            code.append(f" * @extends {extends}")
        code.append(" */")
        
        code.append(f"class {class_name}{extends_str} {{")
        
        for method in methods:
            if method == "constructor":
                code.append("  /**")
                code.append(f"   * Skapa en instans av {class_name}")
                code.append("   */")
                code.append("  constructor() {")
                code.append("    // Initiera klassen")
                if extends:
                    code.append("    super();")
                code.append("  }")
            else:
                code.append("  /**")
                code.append(f"   * {method} - Metodbeskrivning")
                code.append("   */")
                code.append(f"  {method}() {{")
                code.append(f"    // Implementera {method}")
                code.append("  }")
            
            # Lägg till blank rad efter metod
            code.append("")
        
        code.append("}")
        
        return "\n".join(code)
    
    @staticmethod
    def generate_javascript_function(function_name, params=None, doc=None, arrow=False):
        """
        Generera en JavaScript-funktionsmall.
        
        Args:
            function_name (str): Namnet på funktionen
            params (list): Lista med parametrar
            doc (str): Dokumentationstext för funktionen
            arrow (bool): Om arrow-funktion ska användas
        
        Returns:
            str: Genererad JavaScript-funktionskod
        """
        if params is None:
            params = []
        
        param_str = ", ".join(params)
        
        code = []
        
        # Lägg till JSDoc
        code.append("/**")
        code.append(f" * {doc or function_name + ' - Beskrivning av funktionen'}")
        
        if params:
            for param in params:
                param_name = param.split('=')[0].strip() if '=' in param else param.strip()
                code.append(f" * @param {{{param_name}}} {param_name} - Parameterbeskrivning")
        
        code.append(" * @returns {*} Returvärde")
        code.append(" */")
        
        if arrow:
            code.append(f"const {function_name} = ({param_str}) => {{")
        else:
            code.append(f"function {function_name}({param_str}) {{")
        
        code.append("  // Funktionsimplementering")
        code.append("  return null;")
        code.append("}")
        
        return "\n".join(code)

class CodeModuleManager:
    """
    Hanterare för kodmoduler, ansvarig för att läsa, skriva och organisera moduler.
    """
    
    def __init__(self, base_directory="./modules/"):
        self.base_directory = Path(base_directory)
        
        # Säkerställ att baskatalogen existerar
        os.makedirs(self.base_directory, exist_ok=True)
        
        # Skapa kataloger för olika språk och kategorier
        self.language_dirs = {
            "python": self.base_directory / "python",
            "javascript": self.base_directory / "javascript",
            "html": self.base_directory / "html",
            "css": self.base_directory / "css",
            "java": self.base_directory / "java",
            "cpp": self.base_directory / "cpp"
        }
        
        self.category_dirs = {
            "ui": self.base_directory / "ui",
            "utils": self.base_directory / "utils",
            "data": self.base_directory / "data",
            "network": self.base_directory / "network",
            "db": self.base_directory / "db",
            "ai": self.base_directory / "ai",
            "algorithms": self.base_directory / "algorithms",
            "other": self.base_directory / "other"
        }
        
        # Skapa alla kataloger
        for dir_path in list(self.language_dirs.values()) + list(self.category_dirs.values()):
            os.makedirs(dir_path, exist_ok=True)
    
    def get_language_from_extension(self, extension):
        """
        Returnera språk baserat på filändelse.
        """
        extension = extension.lower()
        extension_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".jsx": "javascript",
            ".tsx": "typescript",
            ".cpp": "cpp",
            ".c": "cpp",
            ".h": "cpp",
            ".hpp": "cpp",
            ".html": "html",
            ".htm": "html",
            ".css": "css",
            ".java": "java"
        }
        
        return extension_map.get(extension, "other")
    
    def save_module(self, module_name, code, extension=".py", category="other"):
        """
        Spara en kodmodul till lämplig katalog baserat på filändelse och kategori.
        """
        if not extension.startswith('.'):
            extension = '.' + extension
        
        language = self.get_language_from_extension(extension)
        
        # Bestäm målkatalog, primärt efter kategori
        target_dir = self.category_dirs.get(category, self.category_dirs["other"])
        
        # Fallback till språkkatalog om kategorikatalogen inte finns
        if language in self.language_dirs:
            language_dir = self.language_dirs[language]
        else:
            language_dir = self.base_directory / "other"
        
        # Kontrollera om katalogen finns, annars skapa den
        os.makedirs(target_dir, exist_ok=True)
        
        # Säkerställ giltigt filnamn
        safe_name = re.sub(r'[^\w\-\.]', '_', module_name)
        file_path = target_dir / f"{safe_name}{extension}"
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(code)
            return True, str(file_path)
        except Exception as e:
            return False, str(e)
    
    def load_module(self, file_path):
        """
        Ladda en kodmodul från en fil.
        """
        path = Path(file_path)
        if not path.exists():
            return None
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            module_name = path.stem
            extension = path.suffix
            
            return {
                "name": module_name,
                "extension": extension,
                "code": code,
                "path": str(path),
                "language": self.get_language_from_extension(extension)
            }
        except Exception as e:
            print(f"Error loading module {file_path}: {e}")
            return None
    
    def list_modules(self, language=None, category=None):
        """
        Lista alla tillgängliga moduler, eventuellt filtrerat per språk/kategori.
        """
        modules = []
        search_dirs = []
        
        # Bestäm vilka kataloger som ska sökas igenom
        if language and language in self.language_dirs:
            search_dirs.append(self.language_dirs[language])
        elif category and category in self.category_dirs:
            search_dirs.append(self.category_dirs[category])
        else:
            # Sök igenom alla standard-kataloger om inget specifikt anges
            search_dirs.extend(list
    
    
    
# Sök igenom alla standard-kataloger om inget specifikt anges
            search_dirs.extend(list(self.language_dirs.values()))
            search_dirs.extend(list(self.category_dirs.values()))
        
        # Ta bort eventuella dubbletter i sökkataloger
        search_dirs = list(set(search_dirs))
        
        # Gå igenom varje katalog och leta efter filer
        for directory in search_dirs:
            if not directory.exists():
                continue
            
            # Lista alla filer med relevanta filändelser
            for ext in [".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".css", ".cpp", ".c", ".h", ".hpp", ".java"]:
                for file_path in directory.glob(f"*{ext}"):
                    module = self.load_module(file_path)
                    if module:
                        modules.append(module)
        
        # Ta bort dubletter baserat på filsökväg
        unique_modules = {}
        for module in modules:
            path = module.get("path", "")
            if path and path not in unique_modules:
                unique_modules[path] = module
        
        return list(unique_modules.values())
    
    def delete_module(self, file_path):
        """
        Ta bort en modulfilför permanent.
        """
        path = Path(file_path)
        if path.exists() and path.is_file():
            try:
                path.unlink()
                return True, f"Modulen {path.name} har tagits bort."
            except Exception as e:
                return False, str(e)
        else:
            return False, f"Filen {file_path} existerar inte."
    
    def rename_module(self, file_path, new_name, keep_extension=True):
        """
        Byt namn på en modulkod.
        """
        path = Path(file_path)
        if not path.exists():
            return False, f"Filen {file_path} existerar inte."
        
        try:
            # Säkerställ giltigt filnamn
            safe_name = re.sub(r'[^\w\-\.]', '_', new_name)
            
            # Behåll filändelsen om önskat
            new_path = path.parent / (safe_name + path.suffix if keep_extension else safe_name)
            
            # Kontrollera om målfilnamnet redan finns
            if new_path.exists():
                return False, f"En fil med namnet {new_path.name} finns redan."
            
            # Byt namn på filen
            path.rename(new_path)
            
            return True, str(new_path)
        except Exception as e:
            return False, str(e)
    
    def move_module(self, file_path, target_category=None, target_language=None):
        """
        Flytta en modul till en annan kategori eller språkkatalog.
        """
        path = Path(file_path)
        if not path.exists():
            return False, f"Filen {file_path} existerar inte."
        
        try:
            # Bestäm målkatalog
            target_dir = None
            
            if target_category and target_category in self.category_dirs:
                target_dir = self.category_dirs[target_category]
            elif target_language and target_language in self.language_dirs:
                target_dir = self.language_dirs[target_language]
            else:
                # Ingen giltig målkatalog angiven
                return False, "Ingen giltig målkatalog angiven."
            
            # Skapa katalogen om den inte finns
            os.makedirs(target_dir, exist_ok=True)
            
            # Definiera målfilsökväg
            target_path = target_dir / path.name
            
            # Kontrollera om målfilen redan finns
            if target_path.exists():
                # Generera unikt namn genom att lägga till suffix
                base_name = target_path.stem
                ext = target_path.suffix
                counter = 1
                
                while target_path.exists():
                    new_name = f"{base_name}_{counter}{ext}"
                    target_path = target_dir / new_name
                    counter += 1
            
            # Flytta filen
            path.rename(target_path)
            
            return True, str(target_path)
        except Exception as e:
            return False, str(e)
    
    def analyze_module(self, file_path_or_code, is_path=True):
        """
        Analysera en kodmodul och returnera struktur och statistik.
        
        Args:
            file_path_or_code (str): Sökväg till filen eller kodinnehåll
            is_path (bool): Om första parametern är en sökväg eller faktisk kod
        
        Returns:
            dict: Analysresultat inkluderande funktioner, klasser, etc.
        """
        if is_path:
            # Ladda modulen från fil
            module = self.load_module(file_path_or_code)
            if not module:
                return None
            
            code = module["code"]
            language = module["language"]
        else:
            # Använd angiven kod direkt
            code = file_path_or_code
            # Försök bestämma språk från kodinnehåll (enkel heuristik)
            if "def " in code and "import " in code:
                language = "python"
            elif "function " in code or "class " in code and "{" in code:
                language = "javascript"
            else:
                language = "unknown"
        
        result = {
            "language": language,
            "functions": [],
            "classes": [],
            "imports": [],
            "variables": [],
            "loc": len(code.split('\n')),  # Lines of Code
            "sloc": sum(1 for line in code.split('\n') if line.strip()),  # Source Lines of Code
            "blank_lines": sum(1 for line in code.split('\n') if not line.strip()),
            "comment_lines": 0  # Kommer att uppdateras för varje språk
        }
        
        # Språkspecifik analys
        if language == "python":
            # Räkna kommentarer
            result["comment_lines"] = sum(1 for line in code.split('\n') if line.strip().startswith('#'))
            
            # Analysera funktioner
            result["functions"] = CodeAnalyzer.extract_python_functions(code)
            
            # Analysera klasser
            result["classes"] = CodeAnalyzer.extract_python_classes(code)
            
            # Analysera imports
            result["imports"] = CodeAnalyzer.extract_imports(code, "python")
            
            # Analysera variabler
            result["variables"] = CodeAnalyzer.extract_variables(code, "python")
            
        elif language == "javascript":
            # Räkna kommentarer (enkel version)
            result["comment_lines"] = sum(
                1 for line in code.split('\n') 
                if line.strip().startswith('//') or line.strip().startswith('/*') or line.strip().startswith('*')
            )
            
            # Analysera funktioner
            result["functions"] = CodeAnalyzer.extract_javascript_functions(code)
            
            # Analysera klasser
            result["classes"] = CodeAnalyzer.extract_javascript_classes(code)
            
            # Analysera imports
            result["imports"] = CodeAnalyzer.extract_imports(code, "javascript")
            
            # Analysera variabler
            result["variables"] = CodeAnalyzer.extract_variables(code, "javascript")
        
        # Beräkna statistik
        result["function_count"] = len(result["functions"])
        result["class_count"] = len(result["classes"])
        result["import_count"] = len(result["imports"])
        result["variable_count"] = len(result["variables"])
        
        return result
    
    def suggest_improvements(self, file_path_or_code, is_path=True):
        """
        Analysera kod och föreslå förbättringar.
        
        Args:
            file_path_or_code (str): Sökväg till filen eller kodinnehåll
            is_path (bool): Om första parametern är en sökväg eller faktisk kod
        
        Returns:
            list: Lista med förbättringsförslag
        """
        analysis = self.analyze_module(file_path_or_code, is_path)
        if not analysis:
            return []
        
        suggestions = []
        language = analysis["language"]
        
        # Grundläggande förbättringsförslag oavsett språk
        if analysis["function_count"] > 10:
            suggestions.append({
                "type": "structure",
                "severity": "info",
                "message": f"Koden innehåller {analysis['function_count']} funktioner, överväg att dela upp i flera moduler för bättre hanterbarhet."
            })
        
        if analysis["blank_lines"] < analysis["sloc"] * 0.1:
            suggestions.append({
                "type": "readability",
                "severity": "low",
                "message": "Koden har få tomma rader. Överväg att lägga till fler för bättre läsbarhet."
            })
        
        # Språkspecifika förslag
        if language == "python":
            # Kontrollera docstrings för funktioner
            missing_docstrings = sum(1 for func in analysis["functions"] if not func.get("has_docstring", False))
            if missing_docstrings > 0:
                suggestions.append({
                    "type": "documentation",
                    "severity": "medium",
                    "message": f"{missing_docstrings} funktioner saknar docstrings. Lägg till för bättre dokumentation."
                })
            
            # Kontrollera docstrings för klasser
            missing_class_docs = sum(1 for cls in analysis["classes"] if not cls.get("has_docstring", False))
            if missing_class_docs > 0:
                suggestions.append({
                    "type": "documentation",
                    "severity": "medium",
                    "message": f"{missing_class_docs} klasser saknar docstrings. Lägg till för bättre dokumentation."
                })
            
            # Kontrollera importeringar
            if any(imp.get("name") == "*" for imp in analysis["imports"]):
                suggestions.append({
                    "type": "best_practice",
                    "severity": "medium",
                    "message": "Undvik wildcard-imports (from module import *). Importera explicit vad som behövs."
                })
        
        elif language == "javascript":
            # Kontrollera JSDoc för funktioner
            if analysis["comment_lines"] < analysis["function_count"]:
                suggestions.append({
                    "type": "documentation",
                    "severity": "medium",
                    "message": "En del funktioner verkar sakna JSDoc-kommentarer. Lägg till för bättre dokumentation."
                })
            
            # Kontrollera för console.log
            code = analysis.get("code", "")
            if "console.log" in code:
                suggestions.append({
                    "type": "debugging",
                    "severity": "low",
                    "message": "Det finns console.log-anrop i koden. Överväg att ta bort dessa före produktion."
                })
        
        return suggestions

# Hjälpfunktioner för kodhantering

def detect_duplicate_code(codes):
    """
    Identifiera potentiella dupliceringar av kod mellan olika moduler.
    
    Args:
        codes (list): Lista med kodsträngar att jämföra
    
    Returns:
        list: Lista med potentiella dupliceringar
    """
    # Förenkla implementeringen för prestanda
    # I en fullständig implementation skulle vi använda mer avancerade algoritmer
    
    duplicates = []
    for i, code1 in enumerate(codes):
        lines1 = [line.strip() for line in code1.split('\n') if line.strip() and not line.strip().startswith('#')]
        
        for j, code2 in enumerate(codes):
            if i >= j:  # Jämför bara olika koder och undvik dubbletter
                continue
            
            lines2 = [line.strip() for line in code2.split('\n') if line.strip() and not line.strip().startswith('#')]
            
            # Enkelt sätt att hitta dubbletter: kontrollera för längre sekvenser av rad-för-rad matchningar
            matches = []
            current_match = []
            
            for line1 in lines1:
                if line1 in lines2:
                    current_match.append(line1)
                else:
                    if len(current_match) >= 5:  # Minst 5 rader i rad för att räknas som dubblett
                        matches.append(current_match[:])
                    current_match = []
            
            # Kolla igen i slutet av loopen
            if len(current_match) >= 5:
                matches.append(current_match[:])
            
            if matches:
                duplicates.append({
                    "module1": i,
                    "module2": j,
                    "matches": matches
                })
    
    return duplicates

def extract_requirements_from_imports(imports):
    """
    Extrahera potentiella beroenden från importlistan.
    
    Args:
        imports (list): Lista med importdeklarationer
    
    Returns:
        list: Lista med potentiella paketberoenden
    """
    # Kända standardpaket som inte behöver installeras
    python_stdlib = [
        "os", "sys", "re", "math", "datetime", "time", "json", "ast", "random", 
        "argparse", "collections", "functools", "itertools", "pathlib"
    ]
    
    # Bearbeta alla imports och hitta externa beroenden
    requirements = []
    
    for imp in imports:
        name = imp.get("name", "")
        module = imp.get("module", "")
        
        # Kontrollera importnamn (för direkta importer)
        if name and "." in name:
            root_module = name.split('.')[0]
            if root_module not in python_stdlib and root_module not in requirements:
                requirements.append(root_module)
        elif name and name not in python_stdlib and name not in requirements:
            requirements.append(name)
        
        # Kontrollera modulnamn (för from-imports)
        if module and "." in module:
            root_module = module.split('.')[0]
            if root_module not in python_stdlib and root_module not in requirements:
                requirements.append(root_module)
        elif module and module not in python_stdlib and module not in requirements:
            requirements.append(module)
    
    # Sortera krav
    requirements.sort()
    
    return requirements















