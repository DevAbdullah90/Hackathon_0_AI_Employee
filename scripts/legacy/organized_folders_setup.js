/**
 * Organized Folder Structure Setup for AI Employee Dashboard
 * This script creates the proper vault structure for the AI Employee system
 */

const fs = require('fs').promises;
const path = require('path');

async function createOrganizedStructure() {
    console.log('🧹 Organizing AI Employee Dashboard folder structure...\n');

    // Define the core vault folders needed for the AI Employee system
    const coreFolders = [
        'Inbox',           // Incoming files
        'Needs_Action',    // Files requiring attention
        'Pending_Approval', // Files awaiting approval
        'Approved',        // Approved files ready for processing
        'Done',            // Completed files
        'Failed',          // Failed processing attempts
        'Logs',            // System logs
        'Plans',           // Strategic plans and documentation
        'Templates',       // Template files for automation
        'Reports',         // Generated reports
        'Skills',          // AI skills and capabilities
        'Scripts',         // Automation scripts
        'Config',          // Configuration files
        'State'            // System state files
    ];

    // Folders that can be safely removed (non-core)
    const removableFolders = [
        '.claude',
        '.obsidian',
        'ai-employee-dashboard',
        'approval',
        'Audit_Logs',
        'config',  // lowercase config (keeping uppercase Config)
        'facebook_instagram',
        'images',
        'instagram_session',
        'linkedin',
        'LinkedIn_Analytics',
        'LinkedIn_Leads',
        'LinkedIn_Posts',
        'linkedin_session',
        'mcp',
        'node_modules',    // This should be in parent or handled by package.json
        'reddit',
        'Reddit_Comments',
        'Reddit_Data',
        'Reddit_Posts',
        'Rejected',        // Different from core 'Failed'
        'Scheduled_Tasks',
        'Social_Media_Posts',
        'twitter',
        'watchers',
        'whatsapp_session',
        'xero_mcp',
        '__pycache__'
    ];

    // Create core folders
    console.log('📂 Creating core vault folders...');
    for (const folder of coreFolders) {
        const folderPath = path.join(__dirname, folder);
        try {
            await fs.mkdir(folderPath, { recursive: true });
            console.log(`  ✅ Created: ${folder}`);
        } catch (error) {
            console.log(`  ⚠️  Already exists: ${folder}`);
        }
    }

    // Identify which removable folders actually exist
    console.log('\n🗂️  Identifying folders for cleanup...');
    const existingRemovable = [];
    for (const folder of removableFolders) {
        const folderPath = path.join(__dirname, folder);
        try {
            await fs.access(folderPath);
            existingRemovable.push(folder);
            console.log(`  📍 Marked for removal: ${folder}`);
        } catch (error) {
            // Folder doesn't exist, that's fine
        }
    }

    // Show summary before proceeding
    console.log(`\n📋 Summary:`);
    console.log(`  - Core folders to keep: ${coreFolders.length}`);
    console.log(`  - Extra folders to remove: ${existingRemovable.length}`);

    if (existingRemovable.length > 0) {
        console.log(`\n⚠️  CAUTION: About to remove ${existingRemovable.length} folders:`);
        existingRemovable.forEach(folder => console.log(`   • ${folder}`));

        console.log(`\n🔄 Moving important files (if any) before removal...`);

        // Move important files from removable folders to core folders
        for (const folder of existingRemovable) {
            const folderPath = path.join(__dirname, folder);
            try {
                const items = await fs.readdir(folderPath);

                // Move any .md files to appropriate core folders
                for (const item of items) {
                    if (item.endsWith('.md')) {
                        const sourcePath = path.join(folderPath, item);
                        let targetFolder = 'Plans'; // Default

                        // Categorize based on filename
                        if (item.toLowerCase().includes('approval')) targetFolder = 'Pending_Approval';
                        else if (item.toLowerCase().includes('done') || item.toLowerCase().includes('completed')) targetFolder = 'Done';
                        else if (item.toLowerCase().includes('fail')) targetFolder = 'Failed';
                        else if (item.toLowerCase().includes('log')) targetFolder = 'Logs';

                        const targetPath = path.join(__dirname, targetFolder, item);

                        try {
                            await fs.copyFile(sourcePath, targetPath);
                            console.log(`    📄 Moved: ${item} -> ${targetFolder}/`);
                        } catch (copyError) {
                            console.log(`    ⚠️  Could not move: ${item}`);
                        }
                    }
                }
            } catch (error) {
                console.log(`  ⚠️  Could not read folder: ${folder}`);
            }
        }

        console.log(`\n🗑️  Removing extra folders...`);
        for (const folder of existingRemovable) {
            const folderPath = path.join(__dirname, folder);
            try {
                await fs.rm(folderPath, { recursive: true, force: true });
                console.log(`  ✅ Removed: ${folder}`);
            } catch (error) {
                console.log(`  ⚠️  Could not remove: ${folder} - ${error.message}`);
            }
        }
    } else {
        console.log(`\n✅ No extra folders to remove.`);
    }

    // Create sample files to demonstrate the system
    console.log(`\n📝 Creating sample files...`);

    // Sample email in Inbox
    const sampleEmail = `---
type: email
from: business@example.com
subject: Business Opportunity
received_at: ${new Date().toISOString()}
status: pending_review
priority: high
---

# Business Opportunity - Q1 2026

We have an interesting business opportunity that requires your attention.

## Details
- Investment required: $50,000
- Expected ROI: 200%
- Timeline: 3 months

---
## Actions Required
- [ ] Review opportunity details
- [ ] Assess financial viability
- [ ] Schedule meeting with stakeholders
- [ ] Respond by deadline
`;

    await fs.writeFile(path.join(__dirname, 'Inbox', 'BUSINESS_OPPORTUNITY_20260117.md'), sampleEmail);
    console.log(`  ✅ Created sample email in Inbox`);

    // Sample LinkedIn post in Needs_Action
    const samplePost = `---
type: linkedin_post
status: draft
category: business_update
audience: professionals
---

# Exciting Times Ahead!

Our team is working on innovative solutions to transform the industry.

## Key Points:
- AI-powered automation
- Streamlined processes
- Enhanced productivity

---
## Actions Required
- [ ] Review content
- [ ] Add hashtags
- [ ] Schedule publication
- [ ] Monitor engagement
`;

    await fs.writeFile(path.join(__dirname, 'Needs_Action', 'LINKEDIN_POST_DRAFT_20260117.md'), samplePost);
    console.log(`  ✅ Created sample LinkedIn post in Needs_Action`);

    console.log(`\n🎉 Organization complete!`);
    console.log(`\nThe AI Employee Dashboard vault is now properly organized with:`);
    coreFolders.forEach(folder => console.log(`  • ${folder}/`));

    console.log(`\n🚀 The system is ready to use with the organized structure!`);
}

// Run the organization process
createOrganizedStructure().catch(console.error);