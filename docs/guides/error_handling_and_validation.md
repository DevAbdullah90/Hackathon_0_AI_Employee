# Error Handling and Validation System

## Description
Comprehensive error handling and validation framework for the dynamic code generation system in the Silver tier architecture.

## Purpose
- Validate dynamically generated code for safety and correctness
- Handle errors gracefully during code generation and execution
- Provide recovery mechanisms for failed operations
- Maintain system stability during dynamic operations

## Validation Layers

### 1. Syntax Validation
```python
import ast
import re

def validate_syntax(code_string):
    """Validate Python syntax of generated code"""
    try:
        # Parse the code to check syntax
        ast.parse(code_string)
        return True, "Valid syntax"
    except SyntaxError as e:
        return False, f"Syntax error at line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, f"Parse error: {str(e)}"
```

### 2. Security Validation
```python
DANGEROUS_PATTERNS = [
    r'import\s+os\b',           # OS module import
    r'import\s+sys\b',          # System module import
    r'import\s+subprocess\b',   # Subprocess module
    r'eval\s*\(',               # eval() function
    r'exec\s*\(',               # exec() function
    r'compile\s*\([^,]+,[^,]+,"exec"\)',  # compile() with exec
    r'open\s*\([^)]*"[wrxa]"[^)]*\)',     # File write operations
    r'__import__\s*\(',         # Dynamic imports
    r'getattr\s*\([^,]+,[^,]+,?\s*exec\(\)',  # getattr with exec
]

def validate_security(code_string):
    """Check for dangerous code patterns"""
    issues = []

    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, code_string, re.IGNORECASE):
            issues.append(f"Dangerous pattern detected: {pattern}")

    # Check for system command execution
    system_calls = ['os.system', 'os.popen', 'subprocess.run', 'subprocess.call']
    for call in system_calls:
        if call in code_string:
            issues.append(f"System command execution detected: {call}")

    return len(issues) == 0, issues
```

### 3. Semantic Validation
```python
def validate_semantics(parsed_ast):
    """Validate code semantics and logic"""
    issues = []

    # Check for infinite loops
    for node in ast.walk(parsed_ast):
        if isinstance(node, ast.While):
            if isinstance(node.test, ast.Constant) and node.test.value == True:
                # Check if there's a break statement in the loop
                has_break = any(isinstance(n, ast.Break) for n in ast.walk(node))
                if not has_break:
                    issues.append("Potential infinite loop detected")

    # Check for undefined variables in function calls
    # (Simplified check - real implementation would be more complex)

    return len(issues) == 0, issues
```

## Error Categories and Handling

### 1. Parsing Errors
```python
class ParsingError(Exception):
    """Raised when code parsing fails"""
    def __init__(self, message, original_exception=None):
        self.message = message
        self.original_exception = original_exception
        super().__init__(self.message)

def handle_parsing_error(error_details):
    """Handle code parsing errors"""
    log_error({
        'type': 'parsing_error',
        'details': error_details,
        'timestamp': datetime.now(),
        'severity': 'high'
    })

    # Return safe fallback
    return generate_safe_fallback()
```

### 2. Security Violations
```python
class SecurityViolation(Exception):
    """Raised when security checks fail"""
    def __init__(self, violations):
        self.violations = violations
        super().__init__(f"Security violations detected: {violations}")

def handle_security_violation(violations):
    """Handle security violations"""
    alert_admin({
        'type': 'security_violation',
        'violations': violations,
        'timestamp': datetime.now(),
        'severity': 'critical'
    })

    # Block execution and log incident
    log_security_incident(violations)
    return False  # Execution blocked
```

### 3. Runtime Errors
```python
def handle_runtime_error(exception, context):
    """Handle errors during code execution"""
    error_info = {
        'exception_type': type(exception).__name__,
        'exception_message': str(exception),
        'context': context,
        'timestamp': datetime.now(),
        'stack_trace': traceback.format_exc()
    }

    log_error(error_info)

    # Attempt recovery
    recovery_result = attempt_recovery(context)
    if recovery_result:
        return recovery_result
    else:
        # Fall back to manual processing
        queue_manual_review(context)
        return generate_error_response()
```

## Validation Pipeline

### Complete Validation Process
```python
def validate_generated_code(code_string, skill_definition):
    """Complete validation pipeline for generated code"""
    validation_results = {
        'syntax_valid': False,
        'security_clean': False,
        'semantically_sound': False,
        'business_logic_compliant': False,
        'errors': [],
        'warnings': []
    }

    # Step 1: Syntax validation
    try:
        syntax_ok, syntax_msg = validate_syntax(code_string)
        validation_results['syntax_valid'] = syntax_ok
        if not syntax_ok:
            validation_results['errors'].append(f"Syntax: {syntax_msg}")
    except Exception as e:
        validation_results['errors'].append(f"Syntax validation failed: {str(e)}")

    # Step 2: Security validation
    try:
        security_ok, security_issues = validate_security(code_string)
        validation_results['security_clean'] = security_ok
        if not security_ok:
            validation_results['errors'].extend([f"Security: {issue}" for issue in security_issues])
    except Exception as e:
        validation_results['errors'].append(f"Security validation failed: {str(e)}")

    # Step 3: Semantic validation
    try:
        if validation_results['syntax_valid']:
            parsed_ast = ast.parse(code_string)
            semantic_ok, semantic_issues = validate_semantics(parsed_ast)
            validation_results['semantically_sound'] = semantic_ok
            if not semantic_ok:
                validation_results['errors'].extend([f"Semantic: {issue}" for issue in semantic_issues])
    except Exception as e:
        validation_results['errors'].append(f"Semantic validation failed: {str(e)}")

    # Step 4: Business logic compliance
    try:
        business_ok, business_issues = validate_business_logic(code_string, skill_definition)
        validation_results['business_logic_compliant'] = business_ok
        if not business_ok:
            validation_results['errors'].extend([f"Business: {issue}" for issue in business_issues])
    except Exception as e:
        validation_results['errors'].append(f"Business logic validation failed: {str(e)}")

    # Overall validation status
    validation_results['overall_valid'] = all([
        validation_results['syntax_valid'],
        validation_results['security_clean'],
        validation_results['semantically_sound'],
        validation_results['business_logic_compliant']
    ])

    return validation_results
```

## Recovery Strategies

### 1. Graceful Degradation
```python
def graceful_degradation(skill_name, error_context):
    """Fall back to simpler processing methods"""
    # Try alternative implementation
    alternative_methods = [
        'rule_based_processing',
        'template_matching',
        'manual_review_queue'
    ]

    for method in alternative_methods:
        try:
            result = execute_alternative_method(method, skill_name, error_context)
            if result:
                log_recovery_action(f"Recovered using {method} method")
                return result
        except:
            continue

    # If all alternatives fail, escalate to manual review
    return escalate_to_manual_review(skill_name, error_context)
```

### 2. State Management
```python
class ExecutionState:
    """Manage execution state for recovery"""
    def __init__(self):
        self.checkpoints = []
        self.variables = {}
        self.completed_steps = []

    def create_checkpoint(self, step_name, data):
        """Create execution checkpoint"""
        checkpoint = {
            'step': step_name,
            'data': copy.deepcopy(data),
            'timestamp': datetime.now()
        }
        self.checkpoints.append(checkpoint)

    def rollback_to_checkpoint(self, step_name):
        """Rollback to a previous checkpoint"""
        for checkpoint in reversed(self.checkpoints):
            if checkpoint['step'] == step_name:
                self.variables = checkpoint['data']
                # Remove checkpoints after this point
                self.checkpoints = [cp for cp in self.checkpoints
                                  if cp['timestamp'] <= checkpoint['timestamp']]
                return True
        return False
```

## Error Recovery Procedures

### 1. Temporary Failure Recovery
```python
def handle_temporary_failure(error, retry_count=0):
    """Handle temporary failures with retry logic"""
    if retry_count >= MAX_RETRIES:
        return handle_permanent_failure(error)

    # Wait before retry with exponential backoff
    wait_time = min(BASE_WAIT * (2 ** retry_count), MAX_WAIT_TIME)
    time.sleep(wait_time)

    # Retry the operation
    try:
        return retry_operation(error.context, retry_count + 1)
    except Exception as e:
        return handle_temporary_failure(e, retry_count + 1)
```

### 2. Permanent Failure Handling
```python
def handle_permanent_failure(error):
    """Handle permanent failures"""
    # Log the failure
    failure_record = {
        'error': str(error),
        'type': type(error).__name__,
        'context': error.context if hasattr(error, 'context') else None,
        'timestamp': datetime.now(),
        'attempted_fixes': error.attempted_fixes if hasattr(error, 'attempted_fixes') else []
    }
    log_permanent_failure(failure_record)

    # Move to manual review queue
    manual_review_item = {
        'original_input': error.original_input,
        'failed_operation': error.operation,
        'error_details': failure_record,
        'priority': 'high' if is_critical_operation(error.operation) else 'normal'
    }
    add_to_manual_review_queue(manual_review_item)

    # Generate appropriate response
    return generate_failure_response(error)
```

## Validation Configuration

### Validation Settings
```python
VALIDATION_CONFIG = {
    'syntax_check': True,
    'security_scan': True,
    'semantic_analysis': True,
    'business_logic_check': True,
    'resource_limits': {
        'max_lines': 1000,
        'max_functions': 10,
        'max_classes': 5
    },
    'allowed_imports': [
        'datetime', 'json', 're', 'urllib', 'collections',
        'math', 'random', 'string', 'itertools'
    ],
    'forbidden_patterns': [
        r'__.*__',
        r'importlib\.',
        r'pickle\.',
        r'exec\(',
        r'eval\('
    ]
}
```

## Logging and Monitoring

### Error Classification
```python
ERROR_SEVERITY_LEVELS = {
    'info': 0,      # Informational, no action needed
    'warning': 1,   # Potential issue, monitor
    'error': 2,     # Error occurred, needs attention
    'critical': 3,  # Critical failure, immediate action required
    'alert': 4      # Security alert, emergency response
}

def classify_error(error):
    """Classify error severity"""
    if isinstance(error, SecurityViolation):
        return 'alert'
    elif isinstance(error, ParsingError):
        return 'error'
    elif isinstance(error, ValueError):
        return 'warning'
    else:
        return 'error'
```

## Testing and Verification

### Validation Testing
```python
def test_validation_pipeline():
    """Test the validation pipeline with various inputs"""
    test_cases = [
        # Valid code
        ("def hello(): return 'world'", True),
        # Invalid syntax
        ("def hello(: return 'world'", False),
        # Security violation
        ("import os\nos.system('rm -rf /')", False),
        # Semantic issue
        ("while True: pass", False)  # Infinite loop
    ]

    results = []
    for code, expected in test_cases:
        result = validate_generated_code(code, {})
        results.append({
            'code': code[:50] + "..." if len(code) > 50 else code,
            'expected': expected,
            'actual': result['overall_valid'],
            'passed': result['overall_valid'] == expected
        })

    return results
```

This comprehensive error handling and validation system ensures that your dynamic code generation is safe, reliable, and robust, preventing security issues while maintaining system stability.