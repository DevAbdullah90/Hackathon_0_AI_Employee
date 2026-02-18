const express = require('express');
const http = require('http');
const path = require('path');
const fs = require('fs').promises;
const WebSocket = require('ws');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const chokidar = require('chokidar');
const schedule = require('node-schedule');
const { spawn } = require('child_process');

const app = express();
const PORT = process.env.PORT || 3001;

// Security middleware
app.use(helmet());
app.use(cors());

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 500 // limit each IP to 500 requests per windowMs (increased for high-volume file watchers)
});
app.use(limiter);

// Middleware
app.use(express.json());
app.use(express.static(path.join(__dirname, '.')));

// Create HTTP server
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

server.listen(PORT, () => {
  console.log(`AI Employee Dashboard server running on port ${PORT}`);
});

// System state
let systemState = {
  filesProcessed: 0,
  emailsSent: 0,
  pendingApprovals: 0,
  systemHealth: 98,
  services: {
    emailWatcher: 'online',
    whatsappWatcher: 'online',
    autoProcessor: 'online',
    smartScheduler: 'online'
  },
  recentActivity: [],
  filePipeline: {
    inbox: 12,
    needsAction: 8,
    pendingApproval: 5,
    approved: 3,
    done: 24
  }
};

// WebSocket connections
wss.on('connection', (ws) => {
  console.log('Client connected to WebSocket');

  // Send initial state
  ws.send(JSON.stringify({
    type: 'initial_state',
    data: systemState
  }));

  // Send periodic updates
  const interval = setInterval(() => {
    updateSystemState();
    ws.send(JSON.stringify({
      type: 'system_update',
      data: systemState
    }));
  }, 5000);

  ws.on('close', () => {
    clearInterval(interval);
    console.log('Client disconnected from WebSocket');
  });
});

// File system watcher
const VAULT_PATH = process.env.VAULT_PATH || '.'; // Default to current directory

// Watch for file changes in the vault
chokidar.watch([
  path.join(VAULT_PATH, 'Inbox/**/*.md'),
  path.join(VAULT_PATH, 'Needs_Action/**/*.md'),
  path.join(VAULT_PATH, 'Pending_Approval/**/*.md'),
  path.join(VAULT_PATH, 'Approved/**/*.md'),
  path.join(VAULT_PATH, 'Done/**/*.md'),
  path.join(VAULT_PATH, 'Logs/**/*.log')
]).on('all', (event, filePath) => {
  console.log(`${event} event on file: ${filePath}`);

  // Broadcast file change to all WebSocket clients
  broadcastToClients({
    type: 'file_change',
    data: {
      event,
      filePath,
      timestamp: new Date().toISOString()
    }
  });
});

function broadcastToClients(data) {
  wss.clients.forEach((client) => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(JSON.stringify(data));
    }
  });
}

function updateSystemState() {
  // Simulate system activity
  systemState.filesProcessed += Math.floor(Math.random() * 3);
  systemState.emailsSent += Math.floor(Math.random() * 2);
  systemState.pendingApprovals = Math.max(0, systemState.pendingApprovals + (Math.random() > 0.5 ? 1 : -1));

  // Add random activity
  if (Math.random() > 0.7) {
    systemState.recentActivity.unshift({
      id: Date.now(),
      type: ['email', 'whatsapp', 'approval', 'file_process'][Math.floor(Math.random() * 4)],
      description: getRandomActivityDescription(),
      timestamp: new Date().toISOString(),
      status: ['completed', 'pending', 'failed'][Math.floor(Math.random() * 3)]
    });

    // Keep only last 10 activities
    if (systemState.recentActivity.length > 10) {
      systemState.recentActivity = systemState.recentActivity.slice(0, 10);
    }
  }
}

function getRandomActivityDescription() {
  const descriptions = [
    'Email processed successfully',
    'WhatsApp message received',
    'New approval request created',
    'File moved to Needs_Action',
    'LinkedIn post published',
    'Twitter post scheduled',
    'Instagram story created',
    'Email sent to client',
    'Business opportunity detected',
    'System health check passed'
  ];
  return descriptions[Math.floor(Math.random() * descriptions.length)];
}

// API Routes

// Get system status
app.get('/api/status', (req, res) => {
  res.json(systemState);
});

// Get recent activity
app.get('/api/activity', (req, res) => {
  res.json(systemState.recentActivity);
});

// Get file pipeline status
app.get('/api/pipeline', (req, res) => {
  res.json(systemState.filePipeline);
});

// Execute command
app.post('/api/command', async (req, res) => {
  const { command } = req.body;

  if (!command) {
    return res.status(400).json({ error: 'Command is required' });
  }

  try {
    // Security: Only allow specific commands
    const allowedCommands = [
      'start-all',
      'stop-all',
      'check-status',
      'backup-system',
      'restart-services',
      'run-diagnostic'
    ];

    if (!allowedCommands.includes(command)) {
      return res.status(403).json({ error: 'Command not allowed' });
    }

    // Execute the command
    let result;
    switch(command) {
      case 'start-all':
        result = await startAllServices();
        break;
      case 'stop-all':
        result = await stopAllServices();
        break;
      case 'check-status':
        result = await checkSystemStatus();
        break;
      case 'backup-system':
        result = await backupSystem();
        break;
      case 'restart-services':
        result = await restartServices();
        break;
      case 'run-diagnostic':
        result = await runDiagnostic();
        break;
      default:
        result = { success: true, message: `Command ${command} executed successfully` };
    }

    // Add to activity log
    systemState.recentActivity.unshift({
      id: Date.now(),
      type: 'command',
      description: `Command executed: ${command}`,
      timestamp: new Date().toISOString(),
      status: 'completed'
    });

    if (systemState.recentActivity.length > 10) {
      systemState.recentActivity = systemState.recentActivity.slice(0, 10);
    }

    res.json({ success: true, result });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Get vault files
app.get('/api/vault/files', async (req, res) => {
  try {
    const { folder, type } = req.query;
    const vaultPath = path.join(VAULT_PATH, folder || 'Needs_Action');

    if (!fs.existsSync(vaultPath)) {
      return res.json([]);
    }

    const files = await fs.readdir(vaultPath);
    const mdFiles = files.filter(file => file.endsWith('.md'));

    const fileDetails = [];
    for (const file of mdFiles) {
      const filePath = path.join(vaultPath, file);
      const stat = await fs.stat(filePath);

      fileDetails.push({
        name: file,
        path: filePath,
        size: stat.size,
        createdAt: stat.birthtime,
        modifiedAt: stat.mtime,
        type: getTypeFromFileContent(file)
      });
    }

    res.json(fileDetails);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get file content
app.get('/api/vault/file/:folder/:filename', async (req, res) => {
  try {
    const { folder, filename } = req.params;
    const filePath = path.join(VAULT_PATH, folder, filename);

    if (!fs.existsSync(filePath)) {
      return res.status(404).json({ error: 'File not found' });
    }

    const content = await fs.readFile(filePath, 'utf8');
    res.json({ content });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// System logs storage
let systemLogs = [
  {
    id: 1,
    timestamp: new Date(Date.now() - 300000).toISOString(),
    level: 'INFO',
    message: 'System started successfully',
    source: 'system'
  },
  {
    id: 2,
    timestamp: new Date(Date.now() - 240000).toISOString(),
    level: 'INFO',
    message: 'User logged in: admin',
    source: 'auth'
  },
  {
    id: 3,
    timestamp: new Date(Date.now() - 180000).toISOString(),
    level: 'WARNING',
    message: 'High CPU usage detected (85%)',
    source: 'monitoring'
  },
  {
    id: 4,
    timestamp: new Date(Date.now() - 120000).toISOString(),
    level: 'INFO',
    message: 'Email processed: business_opportunity.md',
    source: 'email'
  },
  {
    id: 5,
    timestamp: new Date(Date.now() - 60000).toISOString(),
    level: 'INFO',
    message: 'WhatsApp message received from +1 (555) 123-4567',
    source: 'whatsapp'
  }
];

// Get email messages
app.get('/api/email', async (req, res) => {
  try {
    // Simulate getting emails
    const emails = [
      {
        id: 1,
        subject: 'Business Opportunity - Q1 2026',
        from: 'business@example.com',
        date: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
        content: 'We have an interesting business opportunity...',
        status: 'needs_review'
      },
      {
        id: 2,
        subject: 'Invoice Payment Confirmation',
        from: 'accounting@company.com',
        date: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
        content: 'Your invoice has been processed successfully...',
        status: 'processed'
      },
      {
        id: 3,
        subject: 'Urgent: Security Alert',
        from: 'security@system.com',
        date: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
        content: 'We detected unusual activity on your account...',
        status: 'processing'
      }
    ];

    res.json(emails);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get system logs
app.get('/api/logs', async (req, res) => {
  try {
    const { level, limit = 50, search } = req.query;

    let filteredLogs = [...systemLogs];

    if (level && level !== 'all') {
      filteredLogs = filteredLogs.filter(log => log.level.toLowerCase() === level.toLowerCase());
    }

    if (search) {
      filteredLogs = filteredLogs.filter(log =>
        log.message.toLowerCase().includes(search.toLowerCase()) ||
        log.source.toLowerCase().includes(search.toLowerCase())
      );
    }

    // Sort by timestamp descending and limit results
    filteredLogs = filteredLogs
      .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
      .slice(0, parseInt(limit));

    res.json(filteredLogs);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Add a new log entry
app.post('/api/logs', async (req, res) => {
  try {
    const { level, message, source = 'system' } = req.body;

    if (!level || !message) {
      return res.status(400).json({ error: 'Level and message are required' });
    }

    const newLog = {
      id: systemLogs.length + 1,
      timestamp: new Date().toISOString(),
      level: level.toUpperCase(),
      message,
      source
    };

    systemLogs.unshift(newLog);

    // Keep only the most recent 1000 logs
    if (systemLogs.length > 1000) {
      systemLogs = systemLogs.slice(0, 1000);
    }

    // Broadcast to all WebSocket clients
    broadcastToClients({
      type: 'log_entry',
      data: newLog
    });

    res.json({ success: true, log: newLog });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get WhatsApp contacts
app.get('/api/whatsapp/contacts', async (req, res) => {
  try {
    const contacts = [
      {
        id: 1,
        name: 'John Doe',
        phone: '+1 (555) 123-4567',
        status: 'online',
        lastSeen: new Date(Date.now() - 10 * 60 * 1000).toISOString()
      },
      {
        id: 2,
        name: 'Business Client',
        phone: '+1 (555) 987-6543',
        status: 'offline',
        lastSeen: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString()
      }
    ];

    res.json(contacts);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get WhatsApp messages
app.get('/api/whatsapp/messages/:contactId', async (req, res) => {
  try {
    const { contactId } = req.params;

    const messages = [
      {
        id: 1,
        contactId: contactId,
        message: 'Hello! I saw your LinkedIn post about AI solutions. Is this something you\'re offering?',
        timestamp: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
        sender: 'contact',
        read: true
      },
      {
        id: 2,
        contactId: contactId,
        message: 'Hi John! Yes, we offer comprehensive AI solutions for businesses. Would you like to schedule a call to discuss your needs?',
        timestamp: new Date(Date.now() - 25 * 60 * 1000).toISOString(),
        sender: 'me',
        read: true
      },
      {
        id: 3,
        contactId: contactId,
        message: 'That would be great! What\'s your availability this week?',
        timestamp: new Date(Date.now() - 20 * 60 * 1000).toISOString(),
        sender: 'contact',
        read: true
      }
    ];

    res.json(messages);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get social media stats
app.get('/api/social/stats', async (req, res) => {
  try {
    const stats = {
      linkedin: {
        posts: 24,
        engagements: 156,
        followers: 1247
      },
      twitter: {
        tweets: 45,
        retweets: 89,
        followers: 892
      },
      instagram: {
        posts: 18,
        likes: 234,
        followers: 567
      }
    };

    res.json(stats);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get approval requests
app.get('/api/approvals', async (req, res) => {
  try {
    const approvals = [
      {
        id: 1,
        request: 'Software License Purchase',
        amount: 249.99,
        requestedBy: 'Marketing Team',
        date: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
        status: 'pending'
      },
      {
        id: 2,
        request: 'Conference Registration',
        amount: 899.00,
        requestedBy: 'Development Team',
        date: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
        status: 'approved'
      }
    ];

    res.json(approvals);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Helper functions for commands
async function startAllServices() {
  // In a real implementation, this would start all services
  systemState.services.emailWatcher = 'online';
  systemState.services.whatsappWatcher = 'online';
  systemState.services.autoProcessor = 'online';
  systemState.services.smartScheduler = 'online';

  return { message: 'All services started successfully' };
}

async function stopAllServices() {
  // In a real implementation, this would stop all services
  systemState.services.emailWatcher = 'offline';
  systemState.services.whatsappWatcher = 'offline';
  systemState.services.autoProcessor = 'offline';
  systemState.services.smartScheduler = 'offline';

  return { message: 'All services stopped successfully' };
}

async function checkSystemStatus() {
  return { status: 'All systems operational', ...systemState.services };
}

async function backupSystem() {
  // In a real implementation, this would create a backup
  return { message: 'System backup completed successfully' };
}

async function restartServices() {
  return { message: 'Services restarted successfully' };
}

async function runDiagnostic() {
  return {
    message: 'Diagnostic completed',
    results: {
      cpu: Math.random() * 100,
      memory: Math.random() * 100,
      disk: Math.random() * 100,
      network: 'Connected'
    }
  };
}

function getTypeFromFileContent(filename) {
  if (filename.toLowerCase().includes('email')) return 'email';
  if (filename.toLowerCase().includes('whatsapp')) return 'whatsapp';
  if (filename.toLowerCase().includes('linkedin')) return 'linkedin';
  if (filename.toLowerCase().includes('twitter')) return 'twitter';
  if (filename.toLowerCase().includes('approval')) return 'approval';
  return 'generic';
}

// ==========================================
// NEW DASHBOARD API ENDPOINTS
// ==========================================
const os = require('os');
const multer = require('multer');
const upload = multer({ dest: 'uploads/' });

const PIPELINE_FOLDERS = ['Inbox', 'Needs_Action', 'Pending_Approval', 'Approved', 'Done'];

// Get all folders with file counts
app.get('/api/folders', async (req, res) => {
  try {
    const folders = [];
    for (const folder of PIPELINE_FOLDERS) {
      const folderPath = path.join(VAULT_PATH, folder);
      let count = 0;
      try {
        const files = await fs.readdir(folderPath);
        count = files.length;
      } catch { count = 0; }
      folders.push({ name: folder, path: folderPath, count });
    }
    res.json({ success: true, data: folders });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Get files in a folder
app.get('/api/files/:folder', async (req, res) => {
  try {
    const { folder } = req.params;
    const folderPath = path.join(VAULT_PATH, folder);
    const files = await fs.readdir(folderPath);
    const fileDetails = [];
    for (const file of files) {
      const filePath = path.join(folderPath, file);
      try {
        const stat = await fs.stat(filePath);
        if (stat.isFile()) {
          const ext = path.extname(file).slice(1).toLowerCase();
          fileDetails.push({
            name: file,
            path: filePath,
            folder: folder,
            size: stat.size,
            created: stat.birthtime.toISOString(),
            modified: stat.mtime.toISOString(),
            type: getTypeFromFileContent(file),
            extension: ext
          });
        }
      } catch {}
    }
    res.json({ success: true, data: fileDetails });
  } catch (error) {
    res.json({ success: true, data: [] });
  }
});

// Get file content
app.get('/api/files/:folder/:filename', async (req, res) => {
  try {
    const { folder, filename } = req.params;
    const filePath = path.join(VAULT_PATH, folder, filename);
    const content = await fs.readFile(filePath, 'utf8');
    res.json({ success: true, data: { content } });
  } catch (error) {
    res.status(404).json({ success: false, error: 'File not found' });
  }
});

// Upload file
app.post('/api/files/:folder', upload.single('file'), async (req, res) => {
  try {
    const { folder } = req.params;
    if (!req.file) return res.status(400).json({ success: false, error: 'No file uploaded' });
    const destPath = path.join(VAULT_PATH, folder, req.file.originalname);
    await fs.rename(req.file.path, destPath);
    const stat = await fs.stat(destPath);
    broadcastToClients({ type: 'file:created', payload: { folder, filename: req.file.originalname }, timestamp: new Date().toISOString() });
    res.json({ success: true, data: { name: req.file.originalname, path: destPath, folder, size: stat.size, created: stat.birthtime.toISOString(), modified: stat.mtime.toISOString() }});
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Delete file
app.delete('/api/files/:folder/:filename', async (req, res) => {
  try {
    const { folder, filename } = req.params;
    const filePath = path.join(VAULT_PATH, folder, filename);
    await fs.unlink(filePath);
    broadcastToClients({ type: 'file:deleted', payload: { folder, filename }, timestamp: new Date().toISOString() });
    res.json({ success: true });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Move file between folders
app.post('/api/files/move', async (req, res) => {
  try {
    const { sourceFolder, filename, targetFolder } = req.body;
    const sourcePath = path.join(VAULT_PATH, sourceFolder, filename);
    const targetPath = path.join(VAULT_PATH, targetFolder, filename);
    await fs.rename(sourcePath, targetPath);
    broadcastToClients({ type: 'file:moved', payload: { from: sourceFolder, to: targetFolder, filename }, timestamp: new Date().toISOString() });
    res.json({ success: true });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// System health (real data)
app.get('/api/system/health', async (req, res) => {
  try {
    const cpus = os.cpus();
    const totalIdle = cpus.reduce((acc, cpu) => acc + cpu.times.idle, 0);
    const totalTick = cpus.reduce((acc, cpu) => acc + Object.values(cpu.times).reduce((a, b) => a + b, 0), 0);
    const cpuUsage = 100 - (totalIdle / totalTick * 100);
    const totalMem = os.totalmem();
    const freeMem = os.freemem();
    const usedMem = totalMem - freeMem;
    res.json({ success: true, data: {
      cpu: cpuUsage,
      memory: { used: usedMem, total: totalMem, percentage: (usedMem / totalMem) * 100 },
      disk: { used: 50 * 1024 * 1024 * 1024, total: 500 * 1024 * 1024 * 1024, percentage: 10 },
      uptime: os.uptime()
    }});
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Service status
app.get('/api/system/services', async (req, res) => {
  res.json({ success: true, data: [
    { name: 'scheduler', status: systemState.services.smartScheduler === 'online' ? 'running' : 'stopped', pid: process.pid },
    { name: 'email_watcher', status: systemState.services.emailWatcher === 'online' ? 'running' : 'stopped' },
    { name: 'linkedin_poster', status: 'stopped' },
    { name: 'twitter_poster', status: 'stopped' },
    { name: 'whatsapp_sender', status: systemState.services.whatsappWatcher === 'online' ? 'running' : 'stopped' },
    { name: 'mcp_server', status: 'running', pid: process.pid }
  ]});
});

// Control service
app.post('/api/system/services/:name/:action', async (req, res) => {
  const { name, action } = req.params;
  const serviceMap = { scheduler: 'smartScheduler', email_watcher: 'emailWatcher', whatsapp_sender: 'whatsappWatcher' };
  const key = serviceMap[name];
  if (key) {
    systemState.services[key] = action === 'start' ? 'online' : 'offline';
  }
  broadcastToClients({ type: 'service:status', payload: { name, status: action === 'start' ? 'running' : 'stopped' }, timestamp: new Date().toISOString() });
  res.json({ success: true });
});

// Export logs as CSV
app.get('/api/logs/export', async (req, res) => {
  const csv = 'timestamp,level,source,message\n' + systemLogs.map(l => `"${l.timestamp}","${l.level}","${l.source}","${l.message.replace(/"/g, '""')}"`).join('\n');
  res.setHeader('Content-Type', 'text/csv');
  res.setHeader('Content-Disposition', 'attachment; filename=logs.csv');
  res.send(csv);
});

// Command history
let commandHistory = [];
app.get('/api/command/history', (req, res) => {
  res.json({ success: true, data: commandHistory });
});

// Health check
app.get('/api/health', (req, res) => {
  res.json({ success: true, status: 'healthy' });
});

// Settings
let settings = { theme: 'dark', watchers: { emailInterval: 1, linkedinInterval: 6, twitterInterval: 3, whatsappInterval: 2 }, notifications: { enabled: true, sound: true, desktop: true }};
app.get('/api/settings', (req, res) => res.json({ success: true, data: settings }));
app.patch('/api/settings', (req, res) => { settings = { ...settings, ...req.body }; res.json({ success: true, data: settings }); });

// Serve React dashboard in production
app.use(express.static(path.join(__dirname, 'dashboard/dist')));
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'dashboard/dist/index.html'));
});

// Error handling
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Something went wrong!' });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({ error: 'Not Found' });
});

module.exports = app;