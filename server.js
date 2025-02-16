const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const fs = require('fs');
const path = require('path');
const os = require('os');

const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
    cors: {
        origin: "*",
        methods: ["GET", "POST"]
    },
    allowEIO3: true
});

// Paths to the JSON files
const VERIFIED_IPS_FILE = '/opt/verified_ips.json';
const CHROMECAST_FILE = '/opt/chromecast.json';

// Load existing verified IPs from the file
function loadVerifiedIps() {
    if (fs.existsSync(VERIFIED_IPS_FILE)) {
        return JSON.parse(fs.readFileSync(VERIFIED_IPS_FILE, 'utf8'));
    }
    return {};
}

// Save verified IPs to the file
function saveVerifiedIps(ips) {
    fs.writeFileSync(VERIFIED_IPS_FILE, JSON.stringify(ips, null, 4));
}

// Load Chromecast codes and IPs
function loadChromecastCodes() {
    if (fs.existsSync(CHROMECAST_FILE)) {
        return JSON.parse(fs.readFileSync(CHROMECAST_FILE, 'utf8'));
    }
    return {};
}

// Initialize verified IPs and Chromecast codes
let verifiedIps = loadVerifiedIps();
let chromecastCodes = loadChromecastCodes();

function getLocalIp() {
    const interfaces = os.networkInterfaces();
    for (const name of Object.keys(interfaces)) {
        for (const iface of interfaces[name]) {
            if (iface.family === 'IPv4' && !iface.internal) {
                return iface.address;
            }
        }
    }
    return '127.0.0.1';
}

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'sender.html'));
});

app.get('/websocket_test', (req, res) => {
    res.sendFile(path.join(__dirname, 'websocket_test.html'));
});

app.post('/verify_code', express.json(), (req, res) => {
    const code = req.body.code;
    const deviceIp = req.ip;

    if (!code) {
        return res.json({ success: false, message: 'No code provided' });
    }

    if (chromecastCodes[code]) {
        const chromecastIp = chromecastCodes[code];
        console.log(`Handshake successful - Device IP: ${deviceIp}, Code: ${code}, Chromecast IP: ${chromecastIp}`);

        if (!verifiedIps[chromecastIp]) {
            verifiedIps[chromecastIp] = [];
        }

        if (!verifiedIps[chromecastIp].some(device => device.ip === deviceIp)) {
            const macAddress = "00:00:00:00:00:00"; // Placeholder for MAC address
            verifiedIps[chromecastIp].push({
                ip: deviceIp,
                pair_time: new Date().toISOString(),
                mac_address: macAddress
            });
            console.log(`Verified IP: ${deviceIp}, MAC Address: ${macAddress}`);
            saveVerifiedIps(verifiedIps);

            io.emit('connection_update', {
                chromecast_ip: chromecastIp,
                connections: verifiedIps[chromecastIp].length
            });
        }

        return res.json({ success: true, message: 'Connected successfully' });
    } else {
        console.log(`Invalid code received from IP: ${deviceIp}`);
        return res.json({ success: false, message: 'Invalid code' });
    }
});

app.post('/disconnect', express.json(), (req, res) => {
    const deviceIp = req.ip;
    for (const chromecastIp in verifiedIps) {
        const devices = verifiedIps[chromecastIp];
        const index = devices.findIndex(device => device.ip === deviceIp);
        if (index !== -1) {
            devices.splice(index, 1);
            saveVerifiedIps(verifiedIps);
            console.log(`Device disconnected: ${deviceIp}`);

            io.emit('connection_update', {
                chromecast_ip: chromecastIp,
                connections: devices.length
            });

            return res.json({ success: true, message: 'Disconnected successfully' });
        }
    }
    return res.json({ success: false, message: 'Device not found' });
});

const PORT = 8000;
server.listen(PORT, () => {
    const localIp = getLocalIp();
    console.log(`\nHandshake server running at:`);
    console.log(`http://${localIp}:${PORT}`);
    console.log("\nTest code: 1234");
}); 