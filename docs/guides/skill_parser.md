# Skill Parser

## Description
The Skill Parser reads and interprets skill definition files, extracting structured information that can be used to dynamically generate code or execute actions.

## Purpose
- Parse markdown skill definitions into structured data
- Extract triggers, conditions, actions, and responses
- Convert human-readable instructions into executable logic
- Enable dynamic skill execution by Claude

## Input Requirements
- Skill definition file in markdown format
- Properly structured sections with headers
- Standardized format for triggers, actions, and responses

## Parsing Process

### 1. File Reading
- Load skill definition markdown file
- Verify file exists and is readable
- Check for proper skill format

### 2. Structure Extraction
- Extract Description section
- Parse Trigger Conditions
- Extract Analysis Process steps
- Identify Response Actions
- Capture Decision Matrix
- Extract Templates and formats
- Gather Configuration variables

### 3. Data Transformation
- Convert markdown to structured JSON
- Map decision matrix to conditional logic
- Transform templates into code blocks
- Validate extracted parameters

## Output Format
```json
{
  "skill_name": "string",
  "description": "string",
  "triggers": ["condition1", "condition2"],
  "prerequisites": ["req1", "req2"],
  "analysis_process": [
    {
      "step": 1,
      "name": "step_name",
      "checks": ["check1", "check2"]
    }
  ],
  "response_actions": {
    "action_type": {
      "conditions": ["condition1"],
      "responses": ["response1", "response2"]
    }
  },
  "decision_matrix": [
    {
      "condition": "condition_text",
      "action": "action_text",
      "approval_required": "boolean",
      "log_location": "location_text"
    }
  ],
  "templates": {
    "reply_format": "template_text",
    "approval_request": "template_text"
  },
  "error_handling": {
    "issues": ["issue1", "issue2"],
    "recovery_actions": ["action1", "action2"]
  },
  "integration_points": ["point1", "point2"],
  "success_criteria": ["criteria1", "criteria2"],
  "configuration_variables": {
    "variable_name": "description"
  },
  "output_artifacts": ["artifact1", "artifact2"]
}
```

## Validation Process
- Verify all required sections exist
- Check for consistent formatting
- Validate decision matrix completeness
- Ensure trigger conditions are clear
- Confirm templates have proper placeholders

## Error Handling
- File not found
- Malformed markdown
- Missing required sections
- Invalid decision matrix
- Unrecognized formatting

## Integration Points
- Called by Claude when executing dynamic skills
- Interfaces with code generator module
- Connects to execution engine
- Updates dashboard with parsing status

## Security Considerations
- Validate file source
- Sanitize extracted content
- Limit parsing depth
- Prevent injection attacks
- Log parsing activities