# Dynamic Code Generator Templates

## Description
Templates that Claude uses to generate executable code based on parsed skill definitions.

## Purpose
- Convert skill definitions into executable Python/JavaScript code
- Generate conditional logic from decision matrices
- Create response templates and workflows
- Enable runtime code generation

## Code Generation Process

### 1. Conditional Logic Generator
**Template Input:** Decision Matrix from skill parser
**Generated Output:** If-else statements or switch cases

```python
def process_email(email_content):
    # Parsed from decision matrix
    if condition1:
        action1()
        log_to(location1)
        approval_needed = False
    elif condition2:
        action2()
        log_to(location2)
        approval_needed = True
    else:
        default_action()
        log_to(default_location)
        approval_needed = False
```

### 2. Response Template Generator
**Template Input:** Response templates from skill parser
**Generated Output:** String formatting functions

```python
def generate_reply(sender_name, subject_topic, urgency_level):
    # Generated from response templates
    reply = f"""
    Subject: Re: {subject_topic}

    Dear {sender_name},

    Thank you for your email regarding "{subject_topic}".

    Our team has received your request and will review it promptly.
    {specific_acknowledgment_based_on_content}

    Timeline: {expected_response_time_based_on_urgency}

    Best regards,
    AI Employee System
    """
    return reply
```

### 3. Analysis Process Generator
**Template Input:** Analysis process steps from skill parser
**Generated Output:** Step-by-step analysis functions

```python
def analyze_email(email):
    # Step 1: Sender Verification
    sender_status = verify_sender(email.sender)

    # Step 2: Subject Analysis
    subject_analysis = analyze_subject(email.subject)

    # Step 3: Content Examination
    content_analysis = examine_content(email.body)

    # Step 4: Urgency Assessment
    urgency_level = assess_urgency(email.body, email.subject)

    return {
        'sender_verified': sender_status,
        'subject_analysis': subject_analysis,
        'content_analysis': content_analysis,
        'urgency_level': urgency_level
    }
```

### 4. Approval Workflow Generator
**Template Input:** Approval checker skill definition
**Generated Output:** Financial approval workflow

```python
def process_approval_request(amount, request_type):
    # Generated from approval checker skill
    if amount < 50:
        # Auto-approve under $50
        return {'approved': True, 'approver': 'system'}
    elif 50 <= amount <= 500:
        # Manager approval needed
        return {'approved': False, 'approver': 'manager', 'escalate': True}
    elif amount > 500:
        # Executive approval needed
        return {'approved': False, 'approver': 'executive', 'escalate': True}
```

## Template Placeholders

### Variable Substitution
- `{SKILL_NAME}` → Actual skill name
- `{TRIGGERS}` → Trigger conditions
- `{CONDITIONS}` → If/elif conditions
- `{ACTIONS}` → Action functions to call
- `{TEMPLATES}` → Response templates
- `{LOG_LOCATIONS}` → Logging destinations

### Function Name Generator
```python
def generate_function_name(skill_name, action_type):
    # Convert "Email Handler" to "handle_email"
    # Convert "Approval Checker" to "check_approval"
    normalized = skill_name.lower().replace(' ', '_').replace('-', '_')
    if action_type == 'main':
        return f"execute_{normalized}"
    else:
        return f"{action_type}_{normalized}"
```

## Code Safety Patterns

### Input Validation Wrapper
```python
def safe_execute(skill_func, *args, **kwargs):
    try:
        # Validate inputs
        validated_args = validate_inputs(*args, **kwargs)
        # Execute skill
        result = skill_func(*validated_args)
        # Validate output
        return validate_output(result)
    except Exception as e:
        log_error(f"Skill execution failed: {str(e)}")
        return handle_skill_error(e)
```

### Error Recovery Template
```python
def recover_from_error(error_context, recovery_options):
    # Generated from error handling section
    error_type = classify_error(error_context)

    if error_type == "invalid_format":
        return handle_invalid_format(recovery_options)
    elif error_type == "missing_data":
        return handle_missing_data(recovery_options)
    elif error_type == "permission_denied":
        return handle_permission_error(recovery_options)
    else:
        return escalate_error(error_context)
```

## Runtime Generation Parameters

### Configuration Variables
- `MAX_CODE_LENGTH`: Maximum allowed generated code size
- `ALLOWED_IMPORTS`: List of allowed Python imports
- `SANDBOX_ENABLED`: Whether to run in sandbox mode
- `VALIDATION_LEVEL`: Strictness of code validation
- `EXECUTION_TIMEOUT`: Maximum execution time

### Security Constraints
- No system command execution
- Limited file system access
- Restricted network access
- Input/output sanitization
- Activity logging

## Integration Hooks

### Dashboard Update Hook
```python
def update_dashboard_after_execution(skill_name, result, duration):
    # Generated template for dashboard updates
    dashboard_data = {
        'skill': skill_name,
        'result': result,
        'duration': duration,
        'timestamp': datetime.now(),
        'status': 'completed' if result.success else 'failed'
    }
    update_dashboard(dashboard_data)
```

### Logging Hook Template
```python
def log_skill_execution(skill_name, inputs, outputs, errors=None):
    # Generated from logging process section
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'skill': skill_name,
        'action_type': extract_action_type(inputs),
        'sender': extract_sender(inputs),
        'subject_summary': extract_subject(inputs),
        'urgency_level': extract_urgency(inputs),
        'action_taken': extract_action(outputs),
        'result': 'success' if not errors else 'failure',
        'next_steps': extract_next_steps(outputs)
    }
    write_log_entry(log_entry)
```

## Template Validation

### Syntax Validation
- Check generated code syntax
- Verify proper indentation
- Validate bracket/parentheses matching
- Confirm variable name validity

### Logic Validation
- Ensure all branches have returns
- Verify decision matrix completeness
- Check for unreachable code
- Validate template placeholder substitution

This template system enables Claude to generate safe, validated code dynamically based on your skill definitions while maintaining security and reliability.