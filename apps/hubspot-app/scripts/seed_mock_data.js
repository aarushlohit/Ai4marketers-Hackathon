const fs = require('fs');
const path = require('path');
const os = require('os');

// Helper to extract access token from HubSpot CLI config
function getHubSpotToken() {
  const paths = [
    path.join(os.homedir(), '.hscli', 'config.yml'),
    path.join(os.homedir(), 'hubspot.config.yml'),
    path.join(os.homedir(), '.hubspot.config.yml')
  ];
  for (const configPath of paths) {
    if (fs.existsSync(configPath)) {
      const content = fs.readFileSync(configPath, 'utf-8');
      const lines = content.split(/\r?\n/);
      
      // Try to find accessToken
      let foundAccessToken = false;
      let tokenLines = [];
      for (let line of lines) {
        if (line.includes('accessToken:')) {
          foundAccessToken = true;
          const after = line.split('accessToken:')[1].trim();
          if (after && after !== '>-') {
            return after;
          }
          continue;
        }
        if (foundAccessToken) {
          if (line.match(/^\s*[a-zA-Z0-9_]+:/) || line.trim() === '') {
            break;
          }
          tokenLines.push(line.trim());
        }
      }
      if (tokenLines.length > 0) {
        return tokenLines.join('');
      }

      // Try to find personalAccessKey
      let foundPat = false;
      let patLines = [];
      for (let line of lines) {
        if (line.includes('personalAccessKey:')) {
          foundPat = true;
          const after = line.split('personalAccessKey:')[1].trim();
          if (after && after !== '>-') {
            return after;
          }
          continue;
        }
        if (foundPat) {
          if (line.match(/^\s*[a-zA-Z0-9_]+:/) || line.trim() === '') {
            break;
          }
          patLines.push(line.trim());
        }
      }
      if (patLines.length > 0) {
        return patLines.join('');
      }
    }
  }
  return process.env.HUBSPOT_ACCESS_TOKEN;
}

const token = getHubSpotToken();
console.log('EXTRACTED TOKEN:', token);
if (!token) {
  console.error('Error: Could not find HubSpot access token in ~/.hubspot.config.yml or HUBSPOT_ACCESS_TOKEN env variable.');
  process.exit(1);
}

// Medium level mock data: Contacts with more details
const mockContacts = [
  { properties: { email: 'emily.chen@tech-innovators.com', firstname: 'Emily', lastname: 'Chen', company: 'Tech Innovators', jobtitle: 'VP of Marketing', phone: '555-0101', city: 'San Francisco' } },
  { properties: { email: 'marcus.johnson@globex.com', firstname: 'Marcus', lastname: 'Johnson', company: 'Globex Corp', jobtitle: 'Sales Director', phone: '555-0102', city: 'New York' } },
  { properties: { email: 'sarah.connor@cyberdyne.net', firstname: 'Sarah', lastname: 'Connor', company: 'Cyberdyne Systems', jobtitle: 'Operations Manager', phone: '555-0103', city: 'Los Angeles' } },
  { properties: { email: 'liam.neeson@stark.com', firstname: 'Liam', lastname: 'Neeson', company: 'Stark Industries', jobtitle: 'Chief Security Officer', phone: '555-0104', city: 'Chicago' } },
  { properties: { email: 'zara.khan@wayne.com', firstname: 'Zara', lastname: 'Khan', company: 'Wayne Enterprises', jobtitle: 'CFO', phone: '555-0105', city: 'Gotham' } }
];

// Sales data: Deals
const mockDeals = [
  { properties: { dealname: 'Tech Innovators Q3 Enterprise License', amount: '45000', dealstage: 'appointmentscheduled', pipeline: 'default' } },
  { properties: { dealname: 'Globex Corp Software Upgrade', amount: '12500', dealstage: 'presentationscheduled', pipeline: 'default' } },
  { properties: { dealname: 'Cyberdyne Maintenance Contract', amount: '85000', dealstage: 'contractsent', pipeline: 'default' } },
  { properties: { dealname: 'Stark Industries Cloud Migration', amount: '150000', dealstage: 'closedwon', pipeline: 'default' } },
  { properties: { dealname: 'Wayne Ent Security Audit', amount: '35000', dealstage: 'decisionmakerboughtin', pipeline: 'default' } }
];

async function createObject(endpoint, objectData, objectType) {
  try {
    const response = await fetch(`https://api.hubapi.com/crm/v3/objects/${endpoint}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(objectData)
    });

    if (response.ok) {
      const data = await response.json();
      const displayName = objectType === 'contact' 
        ? `${objectData.properties.firstname} ${objectData.properties.lastname}`
        : objectData.properties.dealname;
      console.log(`✅ Created ${objectType}: ${displayName} (ID: ${data.id})`);
    } else {
      const error = await response.json();
      const errorContext = objectType === 'contact' ? objectData.properties.email : objectData.properties.dealname;
      console.error(`❌ Failed to create ${objectType} (${errorContext}):`, error.message);
    }
  } catch (err) {
    console.error(`Request failed for ${objectType}:`, err);
  }
}

async function seedData() {
  console.log('🌱 Seeding medium-level mock Contacts...');
  for (const contact of mockContacts) {
    await createObject('contacts', contact, 'contact');
  }
  
  console.log('\n💼 Seeding Sales Data (Deals)...');
  for (const deal of mockDeals) {
    await createObject('deals', deal, 'deal');
  }
  
  console.log('\n🎉 Done seeding mock data and sales data!');
}

seedData();
