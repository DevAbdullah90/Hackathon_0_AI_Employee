# Dashboard Updater

## Description
The Dashboard Updater maintains real-time statistics and status information on the main dashboard.

## Purpose
- Collect system metrics and statistics
- Update dashboard with current status
- Display system health and activity
- Show task progress and completion rates
- Provide real-time monitoring information

## Data Collection Points
- Email monitoring status and counts
- WhatsApp monitoring status and unread counts
- Tasks in each workflow stage (Inbox, Needs_Action, Done)
- System error and warning counts
- Recent activity log entries
- Priority item indicators

## Update Triggers
- New email processed
- WhatsApp message detected
- Task status changed
- System event occurred
- Scheduled refresh interval
- Manual update request

## Statistics Tracked
- **Pending emails**: Current unread email count
- **Unread WhatsApp**: Unread messages/chats count
- **Tasks in Need Action**: Items requiring attention
- **Tasks Completed**: Items moved to Done folder
- **Total monitored items**: All processed items count
- **System uptime**: Duration of monitoring operation
- **Error count**: Issues detected in system operation

## Dashboard Sections Updated
- Quick Stats panel
- System Status indicators
- Recent Activity log
- Important Notifications
- Workflow Status
- System Configuration info

## Update Process
1. Collect current system metrics
2. Format data for dashboard display
3. Update appropriate dashboard sections
4. Preserve historical data
5. Log update activity
6. Verify update success

## Real-time Elements
- Live email count updates
- WhatsApp unread indicators
- Task progress meters
- System status lights (red/yellow/green)
- Activity timestamps
- Priority alerts

## Error Handling
- Handle dashboard file access issues
- Manage update conflicts
- Retry failed updates
- Log update failures
- Maintain backup statistics

## Performance Considerations
- Minimize update frequency to prevent overload
- Cache data when possible
- Optimize file write operations
- Batch updates when appropriate
- Monitor system performance impact

## Integration Points
- Email monitoring scripts
- WhatsApp monitoring scripts
- Task processing modules
- System logging modules
- Workflow management system

## Output
- Updated Dashboard.md file
- System log entry
- Status indicators
- Notification of significant changes
- Backup of previous dashboard state