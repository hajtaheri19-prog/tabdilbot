import math
import re
from typing import Dict, List, Optional, Any, Union
import logging

logger = logging.getLogger(__name__)

class AdvancedCalculator:
    """Advanced calculator with scientific functions"""
    
    def __init__(self):
        # Mathematical constants
        self.constants = {
            "pi": math.pi,
            "e": math.e,
            "tau": math.tau,
            "inf": math.inf,
            "nan": math.nan
        }
        
        # Supported functions
        self.functions = {
            # Basic arithmetic
            "+": lambda x, y: x + y,
            "-": lambda x, y: x - y,
            "*": lambda x, y: x * y,
            "/": lambda x, y: x / y if y != 0 else math.inf,
            "%": lambda x, y: x % y if y != 0 else math.nan,
            "**": lambda x, y: x ** y,
            "^": lambda x, y: x ** y,
            
            # Trigonometric functions
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "asin": math.asin,
            "acos": math.acos,
            "atan": math.atan,
            "atan2": math.atan2,
            
            # Hyperbolic functions
            "sinh": math.sinh,
            "cosh": math.cosh,
            "tanh": math.tanh,
            "asinh": math.asinh,
            "acosh": math.acosh,
            "atanh": math.atanh,
            
            # Logarithmic functions
            "log": math.log,
            "log10": math.log10,
            "log2": math.log2,
            "log1p": math.log1p,
            "exp": math.exp,
            "expm1": math.expm1,
            
            # Power functions
            "sqrt": math.sqrt,
            "cbrt": lambda x: x ** (1/3),
            "pow": math.pow,
            
            # Rounding functions
            "ceil": math.ceil,
            "floor": math.floor,
            "trunc": math.trunc,
            "round": round,
            
            # Other functions
            "abs": abs,
            "fabs": math.fabs,
            "factorial": math.factorial,
            "gcd": math.gcd,
            "lcm": lambda x, y: abs(x * y) // math.gcd(x, y) if x != 0 and y != 0 else 0,
            "degrees": math.degrees,
            "radians": math.radians,
            "copysign": math.copysign,
            "fmod": math.fmod,
            "remainder": math.remainder,
            "isclose": math.isclose,
            "isfinite": math.isfinite,
            "isinf": math.isinf,
            "isnan": math.isnan,
            
            # Statistical functions
            "sum": sum,
            "min": min,
            "max": max,
            "mean": lambda *args: sum(args) / len(args) if args else 0,
            "median": lambda *args: sorted(args)[len(args)//2] if args else 0,
            "std": lambda *args: math.sqrt(sum((x - sum(args)/len(args))**2 for x in args) / len(args)) if args else 0,
            
            # Bitwise operations
            "&": lambda x, y: int(x) & int(y),
            "|": lambda x, y: int(x) | int(y),
            "^": lambda x, y: int(x) ^ int(y),
            "<<": lambda x, y: int(x) << int(y),
            ">>": lambda x, y: int(x) >> int(y),
            "~": lambda x: ~int(x)
        }
        
        # Operator precedence
        self.precedence = {
            "(": 0, ")": 0,
            "+": 1, "-": 1,
            "*": 2, "/": 2, "%": 2,
            "**": 3, "^": 3,
            "&": 4, "|": 4, "<<": 4, ">>": 4,
            "~": 5
        }
    
    def calculate(self, expression: str) -> Dict[str, Any]:
        """Calculate mathematical expression"""
        try:
            # Clean and validate expression
            cleaned_expr = self._clean_expression(expression)
            if not cleaned_expr:
                return {
                    "success": False,
                    "error": "Invalid expression"
                }
            
            # Parse and evaluate
            result = self._evaluate_expression(cleaned_expr)
            
            return {
                "success": True,
                "expression": expression,
                "result": result,
                "formatted": self._format_result(result)
            }
            
        except Exception as e:
            logger.error(f"Calculation error: {e}")
            return {
                "success": False,
                "error": f"Calculation failed: {str(e)}",
                "expression": expression
            }
    
    def _clean_expression(self, expression: str) -> str:
        """Clean and validate mathematical expression"""
        # Remove whitespace
        expr = expression.replace(" ", "")
        
        # Replace common symbols
        expr = expr.replace("×", "*").replace("÷", "/")
        expr = expr.replace("π", "pi").replace("τ", "tau")
        
        # Validate characters
        allowed_chars = set("0123456789+-*/.()^%&|~<>abcdefghijklmnopqrstuvwxyz")
        if not all(c in allowed_chars for c in expr.lower()):
            return ""
        
        return expr
    
    def _evaluate_expression(self, expression: str) -> float:
        """Evaluate mathematical expression using shunting yard algorithm"""
        # Convert to postfix notation
        postfix = self._infix_to_postfix(expression)
        
        # Evaluate postfix expression
        stack = []
        
        for token in postfix:
            if self._is_number(token):
                stack.append(float(token))
            elif token in self.constants:
                stack.append(self.constants[token])
            elif token in self.functions:
                if len(stack) >= 2:
                    if token in ["+", "-", "*", "/", "%", "**", "^", "&", "|", "<<", ">>"]:
                        b = stack.pop()
                        a = stack.pop()
                        result = self.functions[token](a, b)
                        stack.append(result)
                    elif token in ["atan2"]:
                        b = stack.pop()
                        a = stack.pop()
                        result = self.functions[token](a, b)
                        stack.append(result)
                elif len(stack) >= 1:
                    if token in ["sin", "cos", "tan", "asin", "acos", "atan", "sinh", "cosh", "tanh",
                               "asinh", "acosh", "atanh", "log", "log10", "log2", "log1p", "exp",
                               "expm1", "sqrt", "cbrt", "ceil", "floor", "trunc", "round", "abs",
                               "fabs", "factorial", "degrees", "radians", "~"]:
                        a = stack.pop()
                        result = self.functions[token](a)
                        stack.append(result)
        
        if len(stack) != 1:
            raise ValueError("Invalid expression")
        
        return stack[0]
    
    def _infix_to_postfix(self, expression: str) -> List[str]:
        """Convert infix expression to postfix notation"""
        output = []
        operators = []
        
        i = 0
        while i < len(expression):
            char = expression[i]
            
            if char.isdigit() or char == '.':
                # Parse number
                num = ""
                while i < len(expression) and (expression[i].isdigit() or expression[i] == '.'):
                    num += expression[i]
                    i += 1
                output.append(num)
                i -= 1
            
            elif char.isalpha():
                # Parse function or constant
                token = ""
                while i < len(expression) and expression[i].isalpha():
                    token += expression[i]
                    i += 1
                
                if token in self.constants:
                    output.append(token)
                elif token in self.functions:
                    operators.append(token)
                else:
                    raise ValueError(f"Unknown token: {token}")
                i -= 1
            
            elif char == '(':
                operators.append(char)
            
            elif char == ')':
                while operators and operators[-1] != '(':
                    output.append(operators.pop())
                if operators:
                    operators.pop()  # Remove '('
            
            elif char in self.precedence:
                while (operators and 
                       operators[-1] != '(' and 
                       self.precedence.get(operators[-1], 0) >= self.precedence[char]):
                    output.append(operators.pop())
                operators.append(char)
            
            i += 1
        
        # Pop remaining operators
        while operators:
            output.append(operators.pop())
        
        return output
    
    def _is_number(self, token: str) -> bool:
        """Check if token is a number"""
        try:
            float(token)
            return True
        except ValueError:
            return False
    
    def _format_result(self, result: float) -> str:
        """Format calculation result"""
        if math.isnan(result):
            return "NaN"
        elif math.isinf(result):
            return "∞" if result > 0 else "-∞"
        elif result == int(result):
            return str(int(result))
        else:
            return f"{result:.10g}"
    
    def get_supported_functions(self) -> Dict[str, str]:
        """Get list of supported functions with descriptions"""
        return {
            "Basic": {
                "+": "Addition",
                "-": "Subtraction", 
                "*": "Multiplication",
                "/": "Division",
                "%": "Modulo",
                "**": "Power",
                "^": "Power (alternative)"
            },
            "Trigonometric": {
                "sin": "Sine",
                "cos": "Cosine",
                "tan": "Tangent",
                "asin": "Arcsine",
                "acos": "Arccosine",
                "atan": "Arctangent"
            },
            "Logarithmic": {
                "log": "Natural logarithm",
                "log10": "Base-10 logarithm",
                "log2": "Base-2 logarithm",
                "exp": "Exponential"
            },
            "Other": {
                "sqrt": "Square root",
                "abs": "Absolute value",
                "ceil": "Ceiling",
                "floor": "Floor",
                "factorial": "Factorial"
            },
            "Constants": {
                "pi": "π (3.14159...)",
                "e": "Euler's number (2.71828...)",
                "tau": "τ (2π)"
            }
        }
    
    def calculate_statistics(self, numbers: List[float]) -> Dict[str, Any]:
        """Calculate statistical measures"""
        if not numbers:
            return {
                "success": False,
                "error": "No numbers provided"
            }
        
        try:
            n = len(numbers)
            total = sum(numbers)
            mean = total / n
            
            # Calculate variance
            variance = sum((x - mean) ** 2 for x in numbers) / n
            std_dev = math.sqrt(variance)
            
            # Calculate median
            sorted_nums = sorted(numbers)
            if n % 2 == 0:
                median = (sorted_nums[n//2 - 1] + sorted_nums[n//2]) / 2
            else:
                median = sorted_nums[n//2]
            
            return {
                "success": True,
                "count": n,
                "sum": total,
                "mean": mean,
                "median": median,
                "min": min(numbers),
                "max": max(numbers),
                "range": max(numbers) - min(numbers),
                "variance": variance,
                "std_deviation": std_dev
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Statistical calculation failed: {str(e)}"
            }
    
    def solve_equation(self, equation: str) -> Dict[str, Any]:
        """Solve simple linear equations"""
        try:
            # Parse equation (simple linear: ax + b = c)
            if "=" not in equation:
                return {
                    "success": False,
                    "error": "Equation must contain '='"
                }
            
            left, right = equation.split("=", 1)
            
            # Simple parsing for linear equations
            # This is a basic implementation
            return {
                "success": False,
                "error": "Equation solving not fully implemented"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Equation solving failed: {str(e)}"
            }
    
    def convert_base(self, number: str, from_base: int, to_base: int) -> Dict[str, Any]:
        """Convert number between different bases"""
        try:
            # Convert to decimal first
            decimal = int(number, from_base)
            
            # Convert to target base
            if to_base == 10:
                result = str(decimal)
            else:
                result = self._decimal_to_base(decimal, to_base)
            
            return {
                "success": True,
                "original": number,
                "from_base": from_base,
                "to_base": to_base,
                "result": result,
                "decimal": decimal
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Base conversion failed: {str(e)}"
            }
    
    def _decimal_to_base(self, decimal: int, base: int) -> str:
        """Convert decimal number to any base"""
        if decimal == 0:
            return "0"
        
        digits = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        result = ""
        
        while decimal > 0:
            result = digits[decimal % base] + result
            decimal //= base
        
        return result
    
    def format_calculation_result(self, result: Dict[str, Any]) -> str:
        """Format calculation result for display"""
        if not result["success"]:
            return f"❌ {result['error']}"
        
        return f"🧮 **محاسبه:** {result['expression']}\n" \
               f"📊 **نتیجه:** {result['formatted']}\n" \
               f"✅ **وضعیت:** موفق"

