# AI Employee Dashboard - Enterprise Edition

Welcome to the AI Employee Dashboard, an enterprise-grade dashboard system designed to automate and manage business operations across multiple platforms including email, WhatsApp, social media, and file processing pipelines.

## 🚀 Features

- **Real-time Monitoring**: Live dashboard with system health, file processing stats, and activity feeds
- **File Processing Pipeline**: Visual representation of document workflow (Inbox → Needs Action → Pending Approval → Approved → Done)
- **Email Management**: Integrated email processing and management system
- **WhatsApp Hub**: Real-time WhatsApp messaging interface
- **Social Media Integration**: LinkedIn, Twitter, and Instagram management
- **Approval Workflows**: Centralized approval request system
- **System Logs**: Comprehensive logging with filtering and search capabilities
- **Command Center**: Direct system command execution
- **Settings Management**: Theme, layout, and integration configuration
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Dark/Light Mode**: User preference-based theming
- **WebSocket Integration**: Real-time updates for all dashboard elements
- **MCP Integration**: Model Context Protocol support for AI employee systems
- **File System Watcher**: Automatic monitoring of vault folders
- **Cross-platform Compatibility**: Works on Windows, macOS, and Linux

## 📋 Prerequisites

- Node.js (v14 or higher)
- npm or yarn package manager

## 🛠️ Installation

1. Clone or download this repository
2. Navigate to the project directory
3. Install dependencies:

```bash
npm install
```

4. Start the server:

```bash
npm start
```

Or for development mode:

```bash
npm run dev
```

5. Open your browser and navigate to `http://localhost:3000`

## 🏗️ Project Structure

```
AI_Employee_vault/
├── server.js              # Main server application with WebSocket support
├── package.json          # Dependencies and scripts
├── enhanced_dashboard.html # Main dashboard UI with all features
├── dashboard.html       # Basic dashboard (legacy)
├── brain.md             # Technical reference and MCP integration details
├── test_dashboard.js    # Comprehensive test suite
├── Inbox/              # Incoming files
├── Needs_Action/       # Files requiring attention
├── Pending_Approval/   # Files awaiting approval
├── Approved/           # Approved files ready for processing
├── Done/               # Completed files
├── Failed/             # Failed processing attempts
├── Logs/               # System logs
├── Plans/              # Strategic plans and documentation
└── README.md           # This file
```

## 🔧 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/status` | Get system status and statistics |
| GET | `/api/activity` | Get recent activity feed |
| GET | `/api/pipeline` | Get file processing pipeline status |
| GET | `/api/email` | Get email messages |
| GET | `/api/whatsapp/contacts` | Get WhatsApp contacts |
| GET | `/api/whatsapp/messages/:contactId` | Get messages for a contact |
| GET | `/api/social/stats` | Get social media statistics |
| GET | `/api/approvals` | Get approval requests |
| GET | `/api/vault/files` | Get vault files |
| GET | `/api/vault/file/:folder/:filename` | Get specific file content |
| GET | `/api/logs` | Get system logs |
| POST | `/api/command` | Execute system commands |
| POST | `/api/logs` | Add log entry |

## ⚡ Available Commands

The system supports the following commands via the Command Center:

- `start-all`: Start all services
- `stop-all`: Stop all services
- `check-status`: Check system status
- `backup-system`: Create system backup
- `restart-services`: Restart services
- `run-diagnostic`: Run system diagnostic

## 🎨 Customization

### Themes
The dashboard supports three themes:
- Light theme (default)
- Dark theme
- Auto (follows system preference)

### Layout Options
- Compact: Dense layout for more information
- Spacious: Relaxed spacing for easier reading
- Minimal: Clean layout with essential elements

## 🔌 WebSocket Integration

The dashboard uses WebSocket for real-time updates:
- System status updates every 5 seconds
- Real-time log entries
- File change notifications
- Activity updates
- Command execution results

## 🧪 Testing

Run the comprehensive test suite:

```bash
node test_dashboard.js
```

This will verify all dashboard functionality including API endpoints, WebSocket connectivity, and UI components.

## 🚀 Production Deployment

1. Ensure all dependencies are installed
2. Configure environment variables (optional)
3. Build the application: `npm run build`
4. Start the production server: `npm start`

## 🤖 MCP (Model Context Protocol) Integration

This dashboard integrates with the MCP system as documented in `brain.md`, allowing for seamless interaction with AI employee systems and Claude Code command execution. The system includes:

- Email MCP server for automated email processing
- LinkedIn MCP server for social media management
- WhatsApp MCP server for messaging automation
- Twitter MCP server for tweet management

## 📊 Data Flow

1. File changes in the vault trigger chokidar watchers
2. Events are broadcast to all connected WebSocket clients
3. Dashboard updates in real-time with new information
4. User actions can trigger system commands
5. All activity is logged and displayed in the dashboard
6. MCP servers process specialized tasks based on file types

## 🔒 Security Features

- Rate limiting (100 requests per 15 minutes per IP)
- Helmet.js security headers
- CORS protection
- Input validation for command execution
- Secure API endpoints
- Environment-based configuration

## 🛡️ Error Handling

- Graceful degradation when API is unavailable
- Reconnection logic for WebSocket
- Comprehensive error messages
- Fallback to simulated data when needed
- Retry logic with exponential backoff
- Service failure detection and recovery

## 💡 Best Practices

1. Monitor system logs regularly
2. Keep the vault organized with proper folder structure
3. Regularly review approval requests
4. Use the command center for system maintenance
5. Customize notifications to avoid information overload
6. Implement proper security measures for production use
7. Regular backups of the vault and configuration

## 🆘 Support

For issues or questions, please refer to the `brain.md` file for technical details and troubleshooting information. The file contains:

- MCP server configurations
- Python watcher scripts for email, WhatsApp, and auto-processing
- Claude Code integration commands
- Testing methodologies
- Error handling implementations
- Deployment scripts

## 📈 Advanced Features

### File Processing Automation
- Monitors the vault for new files in different stages
- Processes files based on type and approval status
- Moves files between folders automatically
- Generates logs for all processing activities

### Real-time Monitoring
- Live dashboard updates via WebSocket
- System health monitoring
- Performance metrics tracking
- Activity feed with timestamps

### Multi-platform Integration
- Email processing and response
- WhatsApp message handling
- Social media posting automation
- Cross-platform notification system

---

Built with ❤️ for enterprise automation and productivity

This system represents a complete AI employee solution that can handle multiple business operations simultaneously, reducing manual workload and increasing efficiency.