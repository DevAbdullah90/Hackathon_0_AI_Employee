"""
Dynamic Plan Creator generated from plan_creator.md skill definition
"""
import os
import json
import datetime
import re
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from pathlib import Path

class PriorityLevel(Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class PlanStatus(Enum):
    DRAFT = "Draft"
    APPROVED = "Approved"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    ON_HOLD = "On Hold"

@dataclass
class PlanComponent:
    """Data class for plan components"""
    executive_summary: str
    objectives: List[str]
    action_steps: List[Dict[str, Any]]
    resource_allocation: Dict[str, Any]
    timeline: Dict[str, str]
    success_metrics: List[str]
    risk_assessment: List[Dict[str, str]]
    review_schedule: List[str]

class PlanCreator:
    """
    The Plan Creator generates structured action plans based on incoming requests, tasks, and identified opportunities.
    """

    def __init__(self):
        # Configuration variables from skill definition
        self.PLAN_FOLDER = "Plans"
        self.INPUT_SOURCES = [
            "Needs_Action",  # Email opportunities and proposals
            "Inbox",         # Incoming items
        ]
        self.KEYWORD_INDICATORS = [
            "opportunity", "proposal", "project", "initiative",
            "strategic", "plan", "develop", "implement", "launch"
        ]

        # Create plans folder if it doesn't exist
        os.makedirs(self.PLAN_FOLDER, exist_ok=True)

    def analyze_request_content(self, content: str, source: str = "unknown") -> Dict[str, Any]:
        """
        Analyze request content and requirements
        """
        analysis = {
            'source': source,
            'content': content,
            'has_opportunity_keywords': any(kw in content.lower() for kw in self.KEYWORD_INDICATORS),
            'estimated_complexity': self.estimate_complexity(content),
            'required_resources': self.identify_required_resources(content),
            'timeline_indicators': self.extract_timeline_indicators(content),
            'risks_identified': self.identify_risks(content),
            'stakeholders_mentioned': self.extract_stakeholders(content),
            'priority_level': self.determine_priority(content),
            'feasibility_score': self.assess_feasibility(content)
        }

        return analysis

    def estimate_complexity(self, content: str) -> str:
        """Estimate the complexity of the request"""
        complexity_indicators = {
            'simple': ['basic', 'simple', 'straightforward', 'easy'],
            'moderate': ['complex', 'involved', 'multiple steps', 'several components'],
            'complex': ['large scale', 'enterprise', 'comprehensive', 'multi-phase']
        }

        content_lower = content.lower()
        for level, indicators in complexity_indicators.items():
            if any(indicator in content_lower for indicator in indicators):
                return level

        return 'moderate'  # Default complexity

    def identify_required_resources(self, content: str) -> List[str]:
        """Identify resources that might be required"""
        resource_indicators = [
            'personnel', 'staff', 'team', 'budget', 'funding', 'equipment',
            'software', 'tools', 'time', 'expertise', 'consultant', 'contractor'
        ]

        content_lower = content.lower()
        resources = []
        for indicator in resource_indicators:
            if indicator in content_lower:
                resources.append(indicator)

        return list(set(resources))  # Remove duplicates

    def extract_timeline_indicators(self, content: str) -> List[str]:
        """Extract timeline-related indicators from content"""
        timeline_pattern = r'(within\s+\w+\s+(days?|weeks?|months?|years?)|by\s+\w+\s+\d{1,2}(st|nd|rd|th)?|before\s+\w+)'
        matches = re.findall(timeline_pattern, content, re.IGNORECASE)
        return [match[0] if isinstance(match, tuple) else match for match in matches]

    def identify_risks(self, content: str) -> List[str]:
        """Identify potential risks in the content"""
        risk_indicators = [
            'risk', 'challenge', 'obstacle', 'difficulty', 'concern',
            'potential issue', 'barrier', 'threat', 'uncertainty'
        ]

        content_lower = content.lower()
        risks = []
        for indicator in risk_indicators:
            if indicator in content_lower:
                # Extract the sentence containing the risk
                sentences = content.split('.')
                for sentence in sentences:
                    if indicator in sentence.lower():
                        risks.append(sentence.strip())

        return risks

    def extract_stakeholders(self, content: str) -> List[str]:
        """Extract stakeholder names or roles from content"""
        # Look for common stakeholder references
        stakeholder_patterns = [
            r'(manager|director|lead|supervisor|team lead)',
            r'(client|customer|partner|vendor)',
            r'([A-Z][a-z]+\s+[A-Z][a-z]+)'  # Proper names
        ]

        stakeholders = []
        for pattern in stakeholder_patterns:
            matches = re.findall(pattern, content)
            stakeholders.extend(matches)

        return list(set(stakeholders))

    def determine_priority(self, content: str) -> PriorityLevel:
        """Determine priority level based on content"""
        content_lower = content.lower()

        # Critical: Immediate action required (within 24 hours)
        if any(word in content_lower for word in ['urgent', 'immediate', 'asap', 'today', 'within 24 hours']):
            return PriorityLevel.CRITICAL

        # High: Important tasks (within 1 week)
        if any(word in content_lower for word in ['important', 'high priority', 'within a week', 'next week']):
            return PriorityLevel.HIGH

        # Medium: Standard priority (within 1 month)
        if any(word in content_lower for word in ['standard', 'normal', 'within a month', 'month', 'regular']):
            return PriorityLevel.MEDIUM

        # Default to Low: Long-term initiatives (ongoing)
        return PriorityLevel.LOW

    def assess_feasibility(self, content: str) -> float:
        """
        Assess plan feasibility (score from 0.0 to 1.0)
        """
        # Simple heuristic: more specific details = higher feasibility
        positive_indicators = [
            'specific', 'detailed', 'clear', 'defined', 'measurable',
            'realistic', 'achievable', 'resources', 'timeline', 'steps'
        ]

        negative_indicators = [
            'maybe', 'perhaps', 'possibly', 'if possible', 'somehow',
            'magically', 'automatically'
        ]

        content_lower = content.lower()
        positive_count = sum(1 for indicator in positive_indicators if indicator in content_lower)
        negative_count = sum(1 for indicator in negative_indicators if indicator in content_lower)

        # Calculate feasibility score (0.0 to 1.0)
        total_indicators = positive_count + negative_count
        if total_indicators == 0:
            return 0.5  # Neutral if no indicators

        score = positive_count / total_indicators
        return min(1.0, max(0.0, score))  # Clamp between 0 and 1

    def assess_resources_and_constraints(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess available resources and constraints
        """
        resources = {
            'available': analysis['required_resources'],
            'constraints': self.identify_constraints(analysis['content']),
            'capacity': self.assess_capacity(analysis['required_resources']),
            'dependencies': self.identify_dependencies(analysis['content'])
        }

        return resources

    def identify_constraints(self, content: str) -> List[str]:
        """Identify constraints from content"""
        constraint_indicators = [
            'limited', 'restricted', 'constrained', 'under budget',
            'short staffed', 'time constraint', 'deadline', 'fixed'
        ]

        content_lower = content.lower()
        constraints = []
        for indicator in constraint_indicators:
            if indicator in content_lower:
                sentences = content.split('.')
                for sentence in sentences:
                    if indicator in sentence.lower():
                        constraints.append(sentence.strip())

        return constraints

    def assess_capacity(self, required_resources: List[str]) -> str:
        """Assess capacity based on required resources"""
        if not required_resources:
            return 'adequate'

        resource_count = len(required_resources)
        if resource_count <= 2:
            return 'adequate'
        elif resource_count <= 5:
            return 'limited'
        else:
            return 'constrained'

    def identify_dependencies(self, content: str) -> List[str]:
        """Identify dependencies from content"""
        dependency_indicators = [
            'dependent on', 'requires', 'needs', 'awaiting',
            'precondition', 'prerequisite', 'before we can'
        ]

        content_lower = content.lower()
        dependencies = []
        for indicator in dependency_indicators:
            if indicator in content_lower:
                sentences = content.split('.')
                for sentence in sentences:
                    if indicator in sentence.lower():
                        dependencies.append(sentence.strip())

        return dependencies

    def define_objectives_and_success_criteria(self, content: str) -> Dict[str, List[str]]:
        """
        Define objectives and success criteria
        """
        objectives = self.extract_objectives(content)
        success_criteria = self.define_success_criteria(content)

        return {
            'objectives': objectives,
            'success_criteria': success_criteria
        }

    def extract_objectives(self, content: str) -> List[str]:
        """Extract objectives from content"""
        objective_indicators = [
            'objective', 'goal', 'aim', 'purpose', 'intended outcome',
            'we want to', 'our goal is', 'we aim to', 'the purpose is'
        ]

        content_lower = content.lower()
        objectives = []
        sentences = content.split('.')

        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(indicator in sentence_lower for indicator in objective_indicators):
                objectives.append(sentence.strip())

        # If no explicit objectives found, use the main topic
        if not objectives:
            # Extract the main subject/topic from content
            words = content.split()
            # Take first few meaningful words as objective
            main_topic = ' '.join(words[:10])
            objectives.append(f"Address or implement: {main_topic}")

        return objectives

    def define_success_criteria(self, content: str) -> List[str]:
        """Define success criteria based on content"""
        success_indicators = [
            'success', 'successful', 'achieved', 'completed', 'delivered',
            'met the requirements', 'fulfilled the objective', 'accomplished'
        ]

        content_lower = content.lower()
        criteria = []
        sentences = content.split('.')

        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(indicator in sentence_lower for indicator in success_indicators):
                criteria.append(sentence.strip())

        # If no explicit success criteria found, create generic ones
        if not criteria:
            criteria = [
                "Requirements clearly understood and documented",
                "Stakeholder expectations managed",
                "Deliverables completed on time",
                "Budget constraints respected",
                "Quality standards met"
            ]

        return criteria

    def break_down_tasks(self, content: str) -> List[Dict[str, Any]]:
        """
        Break down tasks into actionable steps
        """
        # Look for numbered lists or step indicators
        step_patterns = [
            r'(\d+\.\s*[A-Za-z][^.]*?)\.',
            r'(Step\s+\d+\s*:.*)',
            r'(Phase\s+\d+\s*:.*)',
            r'(First,\s*.*)',
            r'(Next,\s*.*)',
            r'(Finally,\s*.*)'
        ]

        steps = []
        for pattern in step_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if match.strip():
                    steps.append({
                        'id': len(steps) + 1,
                        'description': match.strip(),
                        'estimated_duration': self.estimate_duration_for_step(match),
                        'dependencies': [],
                        'responsible_party': 'TBD'
                    })

        # If no explicit steps found, create generic ones
        if not steps:
            steps = [
                {
                    'id': 1,
                    'description': 'Analyze requirements in detail',
                    'estimated_duration': '1-2 days',
                    'dependencies': [],
                    'responsible_party': 'Project Lead'
                },
                {
                    'id': 2,
                    'description': 'Develop detailed plan and timeline',
                    'estimated_duration': '2-3 days',
                    'dependencies': ['1'],
                    'responsible_party': 'Planning Team'
                },
                {
                    'id': 3,
                    'description': 'Execute primary activities',
                    'estimated_duration': '1-2 weeks',
                    'dependencies': ['2'],
                    'responsible_party': 'Implementation Team'
                },
                {
                    'id': 4,
                    'description': 'Review and finalize deliverables',
                    'estimated_duration': '1-2 days',
                    'dependencies': ['3'],
                    'responsible_party': 'Quality Assurance'
                }
            ]

        return steps

    def estimate_duration_for_step(self, step_description: str) -> str:
        """Estimate duration for a specific step"""
        # Simple heuristics based on keywords
        if any(word in step_description.lower() for word in ['analyze', 'research', 'study']):
            return '2-3 days'
        elif any(word in step_description.lower() for word in ['develop', 'create', 'build']):
            return '1-2 weeks'
        elif any(word in step_description.lower() for word in ['review', 'evaluate', 'assess']):
            return '1-2 days'
        else:
            return '3-5 days'

    def estimate_timeline_and_resources(self, steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Estimate timeline and resource needs
        """
        total_duration = self.calculate_total_duration(steps)
        required_resources = self.aggregate_resources(steps)

        timeline = {
            'start_date': datetime.date.today().isoformat(),
            'estimated_end_date': (datetime.date.today() + datetime.timedelta(days=total_duration)).isoformat(),
            'milestones': self.create_milestones(steps),
            'critical_path': self.identify_critical_path(steps)
        }

        return {
            'timeline': timeline,
            'resource_needs': required_resources,
            'total_estimated_duration': total_duration
        }

    def calculate_total_duration(self, steps: List[Dict[str, Any]]) -> int:
        """Calculate total estimated duration in days"""
        # Simple calculation: assume each step takes its estimated duration
        # In reality, this would consider parallel vs sequential tasks
        total_days = 0
        for step in steps:
            # Extract number from duration string (e.g., "1-2 days" -> average of 1.5 days)
            duration_str = step.get('estimated_duration', '5 days')
            numbers = re.findall(r'\d+', duration_str)
            if numbers:
                # Take the highest number as conservative estimate
                avg = sum(int(num) for num in numbers) / len(numbers)
                total_days += int(avg)

        return max(total_days, 1)  # At least 1 day

    def aggregate_resources(self, steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate resource needs from all steps"""
        resources = {}
        for step in steps:
            party = step.get('responsible_party', 'TBD')
            if party in resources:
                resources[party] += 1
            else:
                resources[party] = 1

        return resources

    def create_milestones(self, steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create milestones from steps"""
        milestones = []
        for i, step in enumerate(steps):
            if i % 2 == 0:  # Every other step as milestone
                milestones.append({
                    'id': f"M{i//2 + 1}",
                    'name': f"Milestone: {step['description'][:30]}...",
                    'target_date': self.calculate_milestone_date(i, steps),
                    'completed': False
                })

        # Add final milestone
        milestones.append({
            'id': f"M{len(milestones) + 1}",
            'name': "Project Completion",
            'target_date': self.calculate_milestone_date(len(steps) - 1, steps),
            'completed': False
        })

        return milestones

    def calculate_milestone_date(self, step_index: int, steps: List[Dict[str, Any]]) -> str:
        """Calculate target date for a milestone"""
        # Simple calculation based on cumulative duration up to this point
        days_passed = 0
        for i in range(step_index + 1):
            if i < len(steps):
                duration_str = steps[i].get('estimated_duration', '5 days')
                numbers = re.findall(r'\d+', duration_str)
                if numbers:
                    avg = sum(int(num) for num in numbers) / len(numbers)
                    days_passed += int(avg)

        target_date = datetime.date.today() + datetime.timedelta(days=int(days_passed))
        return target_date.isoformat()

    def identify_critical_path(self, steps: List[Dict[str, Any]]) -> List[str]:
        """Identify the critical path of the project"""
        # For simplicity, assume linear sequence as critical path
        return [str(step['id']) for step in steps]

    def identify_risks_and_mitigation(self, content: str) -> List[Dict[str, str]]:
        """
        Identify risks and mitigation strategies
        """
        risks = self.identify_risks(content)
        mitigation_strategies = []

        for risk in risks:
            mitigation_strategies.append({
                'risk': risk,
                'likelihood': self.assess_risk_likelihood(risk),
                'impact': self.assess_risk_impact(risk),
                'mitigation_strategy': self.propose_mitigation(risk)
            })

        # Add some generic risks if none were identified
        if not risks:
            mitigation_strategies = [
                {
                    'risk': 'Scope creep or changing requirements',
                    'likelihood': 'medium',
                    'impact': 'high',
                    'mitigation_strategy': 'Establish clear requirements baseline and change control process'
                },
                {
                    'risk': 'Resource unavailability',
                    'likelihood': 'medium',
                    'impact': 'medium',
                    'mitigation_strategy': 'Identify backup resources and cross-training opportunities'
                },
                {
                    'risk': 'Timeline delays',
                    'likelihood': 'medium',
                    'impact': 'high',
                    'mitigation_strategy': 'Build buffer time and identify parallel processing opportunities'
                }
            ]

        return mitigation_strategies

    def assess_risk_likelihood(self, risk: str) -> str:
        """Assess likelihood of a risk occurring"""
        risk_lower = risk.lower()
        if any(word in risk_lower for word in ['likely', 'probable', 'expected']):
            return 'high'
        elif any(word in risk_lower for word in ['possible', 'might', 'could']):
            return 'medium'
        else:
            return 'low'

    def assess_risk_impact(self, risk: str) -> str:
        """Assess impact of a risk if it occurs"""
        risk_lower = risk.lower()
        if any(word in risk_lower for word in ['critical', 'major', 'severe', 'significant']):
            return 'high'
        elif any(word in risk_lower for word in ['moderate', 'some', 'minor']):
            return 'medium'
        else:
            return 'low'

    def propose_mitigation(self, risk: str) -> str:
        """Propose mitigation strategy for a risk"""
        # Generic mitigation suggestions based on risk keywords
        risk_lower = risk.lower()
        if 'delay' in risk_lower or 'late' in risk_lower:
            return 'Build buffer time and identify parallel processing opportunities'
        elif 'resource' in risk_lower or 'staff' in risk_lower:
            return 'Identify backup resources and cross-training opportunities'
        elif 'scope' in risk_lower or 'requirement' in risk_lower:
            return 'Establish clear requirements baseline and change control process'
        else:
            return 'Establish monitoring process and contingency plans'

    def create_structured_plan_document(self, analysis: Dict[str, Any],
                                     resources: Dict[str, Any],
                                     objectives: Dict[str, List[str]],
                                     steps: List[Dict[str, Any]],
                                     timeline_data: Dict[str, Any],
                                     risks: List[Dict[str, str]]) -> PlanComponent:
        """
        Create structured plan document with all components
        """
        # Create executive summary
        exec_summary = f"""
Plan for: {analysis['source']}
Priority: {analysis['priority_level'].value}
Complexity: {analysis['estimated_complexity']}
Feasibility Score: {analysis['feasibility_score']:.2f}

This plan addresses the identified opportunity/request in the source material.
It outlines the approach, timeline, and resources required for successful implementation.
        """.strip()

        plan_component = PlanComponent(
            executive_summary=exec_summary,
            objectives=objectives['objectives'],
            action_steps=steps,
            resource_allocation={
                'required': analysis['required_resources'],
                'available': resources['available'],
                'constraints': resources['constraints'],
                'capacity': resources['capacity']
            },
            timeline=timeline_data['timeline'],
            success_metrics=objectives['success_criteria'],
            risk_assessment=risks,
            review_schedule=self.create_review_schedule()
        )

        return plan_component

    def create_review_schedule(self) -> List[str]:
        """Create a default review schedule"""
        today = datetime.date.today()
        return [
            f"Weekly review: {(today + datetime.timedelta(weeks=1)).isoformat()}",
            f"Milestone review: {(today + datetime.timedelta(weeks=2)).isoformat()}",
            f"Mid-project review: {(today + datetime.timedelta(weeks=4)).isoformat()}",
            f"Final review: {(today + datetime.timedelta(weeks=8)).isoformat()}"
        ]

    def set_up_tracking_and_monitoring(self, plan_id: str) -> Dict[str, Any]:
        """
        Set up tracking and monitoring for the plan
        """
        tracking_setup = {
            'plan_id': plan_id,
            'tracking_file': f"{self.PLAN_FOLDER}/{plan_id}_tracking.json",
            'monitoring_frequency': 'weekly',
            'reporting_schedule': ['weekly', 'monthly'],
            'status_updates_enabled': True,
            'progress_milestones': []
        }

        # Create tracking file
        tracking_data = {
            'plan_id': plan_id,
            'created_date': datetime.datetime.now().isoformat(),
            'status': PlanStatus.DRAFT.value,
            'progress': 0,
            'completed_steps': [],
            'current_phase': 'Initial Planning',
            'last_updated': datetime.datetime.now().isoformat()
        }

        with open(tracking_setup['tracking_file'], 'w', encoding='utf-8') as f:
            json.dump(tracking_data, f, indent=2)

        return tracking_setup

    def save_plan_to_file(self, plan_component: PlanComponent, plan_id: str) -> str:
        """
        Save the plan to a file
        """
        plan_filename = f"{self.PLAN_FOLDER}/{plan_id}.md"

        plan_content = f"""# Plan: {plan_id}

## Executive Summary
{plan_component.executive_summary}

## Objectives and Goals
{chr(10).join(f"- {obj}" for obj in plan_component.objectives)}

## Action Steps and Milestones
{chr(10).join(f"{step['id']}. {step['description']} ({step['estimated_duration']})" for step in plan_component.action_steps)}

## Resource Allocation
### Required Resources
{chr(10).join(f"- {resource}" for resource in plan_component.resource_allocation['required']) if plan_component.resource_allocation['required'] else "- No specific resources identified"}

### Constraints
{chr(10).join(f"- {constraint}" for constraint in plan_component.resource_allocation['constraints']) if plan_component.resource_allocation['constraints'] else "- No constraints identified"}

### Capacity Assessment
- Status: {plan_component.resource_allocation['capacity']}

## Timeline and Deadlines
- Start Date: {plan_component.timeline['start_date']}
- Estimated End Date: {plan_component.timeline['estimated_end_date']}
- Critical Path: {', '.join(plan_component.timeline['critical_path'])}

### Milestones
{chr(10).join(f"- {milestone['name']} ({milestone['target_date']})" for milestone in plan_component.timeline['milestones'])}

## Success Metrics
{chr(10).join(f"- {metric}" for metric in plan_component.success_metrics)}

## Risk Assessment
{chr(10).join(f"- **{risk['risk']}** ({risk['likelihood']} likelihood, {risk['impact']} impact): {risk['mitigation_strategy']}" for risk in plan_component.risk_assessment)}

## Review Schedule
{chr(10).join(f"- {review}" for review in plan_component.review_schedule)}

---
*Created: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        with open(plan_filename, 'w', encoding='utf-8') as f:
            f.write(plan_content)

        return plan_filename

    def generate_plan_from_content(self, content: str, source: str = "manual") -> Dict[str, Any]:
        """
        Main method to generate a plan from content following the planning process
        """
        try:
            # Step 1: Analyze request content and requirements
            analysis = self.analyze_request_content(content, source)

            # Step 2: Assess available resources and constraints
            resources = self.assess_resources_and_constraints(analysis)

            # Step 3: Define objectives and success criteria
            objectives = self.define_objectives_and_success_criteria(content)

            # Step 4: Break down tasks into actionable steps
            steps = self.break_down_tasks(content)

            # Step 5: Estimate timeline and resource needs
            timeline_data = self.estimate_timeline_and_resources(steps)

            # Step 6: Identify risks and mitigation strategies
            risks = self.identify_risks_and_mitigation(content)

            # Step 7: Create structured plan document
            plan_component = self.create_structured_plan_document(
                analysis, resources, objectives, steps, timeline_data, risks
            )

            # Step 8: Set up tracking and monitoring
            plan_id = f"PLAN_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
            tracking_setup = self.set_up_tracking_and_monitoring(plan_id)

            # Create the plan file
            plan_file = self.save_plan_to_file(plan_component, plan_id)

            result = {
                'success': True,
                'plan_id': plan_id,
                'plan_file': plan_file,
                'tracking_setup': tracking_setup,
                'priority_level': analysis['priority_level'].value,
                'feasibility_score': analysis['feasibility_score'],
                'estimated_duration': timeline_data['total_estimated_duration'],
                'message': f'Plan {plan_id} created successfully'
            }

            return result

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Plan creation failed due to error'
            }

    def scan_input_sources_for_planning_opportunities(self) -> List[Dict[str, Any]]:
        """
        Scan input sources for planning opportunities
        """
        opportunities = []

        # Check Needs_Action folder for opportunities
        needs_action_path = "Needs_Action"
        if os.path.exists(needs_action_path):
            for filename in os.listdir(needs_action_path):
                if filename.endswith('.md'):
                    filepath = os.path.join(needs_action_path, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Check if this item has planning opportunity indicators
                    if any(keyword in content.lower() for keyword in self.KEYWORD_INDICATORS):
                        opportunities.append({
                            'source': f"Needs_Action/{filename}",
                            'content': content,
                            'filename': filename,
                            'priority': self.determine_priority(content)
                        })

        # Check Inbox folder for opportunities
        inbox_path = "Inbox"
        if os.path.exists(inbox_path):
            for filename in os.listdir(inbox_path):
                if filename.endswith('.md'):
                    filepath = os.path.join(inbox_path, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Check if this item has planning opportunity indicators
                    if any(keyword in content.lower() for keyword in self.KEYWORD_INDICATORS):
                        opportunities.append({
                            'source': f"Inbox/{filename}",
                            'content': content,
                            'filename': filename,
                            'priority': self.determine_priority(content)
                        })

        # Sort by priority
        opportunities.sort(key=lambda x: x['priority'].value, reverse=True)
        return opportunities

    def process_planning_opportunities(self) -> Dict[str, Any]:
        """
        Process all identified planning opportunities
        """
        opportunities = self.scan_input_sources_for_planning_opportunities()
        results = []

        for opportunity in opportunities:
            result = self.generate_plan_from_content(
                opportunity['content'],
                opportunity['source']
            )
            results.append({
                **result,
                'opportunity_source': opportunity['source']
            })

        return {
            'opportunities_found': len(opportunities),
            'plans_created': len([r for r in results if r['success']]),
            'results': results
        }


# Example usage:
if __name__ == "__main__":
    # Initialize the plan creator
    creator = PlanCreator()

    # Example content for a plan
    sample_content = """
    We need to develop a new customer onboarding process. This is a strategic initiative that should be completed within 2 months.
    The process needs to include document verification, account setup, and initial training. We'll need IT support, customer service team,
    and possibly external consultants for best practices. The budget is approximately $50,000.
    Success will be measured by customer satisfaction scores and onboarding completion rates.
    """

    # Generate a plan from the content
    result = creator.generate_plan_from_content(sample_content, "Sample Request")

    print("Plan Creation Result:")
    print(json.dumps(result, indent=2, default=str))

    # Also process any existing opportunities in the system
    opportunity_results = creator.process_planning_opportunities()
    print("\nOpportunity Processing Results:")
    print(json.dumps(opportunity_results, indent=2, default=str))