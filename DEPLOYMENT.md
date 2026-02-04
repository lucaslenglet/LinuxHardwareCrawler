# Ubuntu VPS Deployment Guide

## Deployment Architecture

This document outlines how to deploy the Linux Hardware Crawler to an Ubuntu VPS using Docker and cron for scheduling.

## Prerequisites

1. Ubuntu VPS (20.04 LTS or later recommended)
2. Docker installed on the VPS
3. SSH access to the VPS
4. Discord Server (for webhook setup - optional)

## Step 1: Set Up Discord Webhook (Optional)

If you want Discord notifications when new devices are found:

1. Go to your Discord Server Settings → Integrations → Webhooks
2. Click "New Webhook"
3. Name it "Hardware Crawler" and copy the webhook URL
4. Save the URL for later use

## Step 2: SSH into Your VPS

```bash
ssh user@your-vps-ip
```

## Step 3: Install Docker

If Docker is not already installed:

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

Log out and back in for group changes to take effect.

## Step 4: Clone the Repository

```bash
cd /opt
sudo git clone https://github.com/lucaslenglet/LinuxHardwareCrawler.git
cd LinuxHardwareCrawler
sudo chown -R $USER:$USER .
```

## Step 5: Build the Docker Image

```bash
docker build -t linux-hardware-crawler:latest .
```

## Step 6: Set Up Data Directory

```bash
mkdir -p /var/lib/linux-hardware-crawler
chmod 755 /var/lib/linux-hardware-crawler
```

This directory will persist the `devices.json` file between runs.

## Step 7: Set Up Systemd Timer

Create `/etc/systemd/system/hardware-crawler.service`:

```ini
[Unit]
Description=Linux Hardware Crawler
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
User=your-username
WorkingDirectory=/opt/LinuxHardwareCrawler
Environment="DISCORD_WEBHOOK_URL=YOUR_WEBHOOK_URL"
ExecStart=/usr/bin/docker run --rm \
  -v /var/lib/linux-hardware-crawler:/app/output \
  -e DISCORD_WEBHOOK_URL=${DISCORD_WEBHOOK_URL} \
  linux-hardware-crawler:latest
StandardOutput=journal
StandardError=journal
```

Create `/etc/systemd/system/hardware-crawler.timer`:

```ini
[Unit]
Description=Run Linux Hardware Crawler every 12 hours
Requires=hardware-crawler.service

[Timer]
OnBootSec=5min
OnUnitActiveSec=12h
Unit=hardware-crawler.service

[Install]
WantedBy=timers.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable hardware-crawler.timer
sudo systemctl start hardware-crawler.timer
```

Check status:
```bash
sudo systemctl status hardware-crawler.timer
sudo systemctl list-timers
```

## Step 8: Environment Variables

Set the Discord webhook URL in the systemd service file (if needed):

Edit `/etc/systemd/system/hardware-crawler.service` and replace `YOUR_WEBHOOK_URL` with your actual Discord webhook URL.

| Variable | Description | Optional | Example |
|----------|-------------|----------|---------|
| `DISCORD_WEBHOOK_URL` | Discord webhook for notifications | Yes | `https://discordapp.com/api/webhooks/...` |

After making changes to the service file, reload and restart:
```bash
sudo systemctl daemon-reload
sudo systemctl restart hardware-crawler.timer
```

## Step 9: Monitor Logs

### Systemd Timer Logs
```bash
sudo journalctl -u hardware-crawler.service -f
```

View execution history:
```bash
sudo journalctl -u hardware-crawler.service --no-pager
```

Check timer status:
```bash
sudo systemctl status hardware-crawler.timer
sudo systemctl list-timers --all
```

## Step 10: Data Persistence

The `devices.json` file is stored in `/var/lib/linux-hardware-crawler/` and persists between runs.

Backup your data:
```bash
cp /var/lib/linux-hardware-crawler/devices.json /backup/devices-backup.json
```

## Troubleshooting

### Docker command not found in systemd
Ensure you're using the absolute path `/usr/bin/docker` in the service file (already configured above).

### Permission denied errors
Ensure your user is in the docker group:
```bash
sudo usermod -aG docker $USER
# Log out and back in
```

### Timer not running
Check the timer is enabled and started:
```bash
sudo systemctl status hardware-crawler.timer
sudo systemctl enable hardware-crawler.timer
sudo systemctl start hardware-crawler.timer
```

### Discord notifications not working
1. Verify `DISCORD_WEBHOOK_URL` is set correctly in the service file
2. Check logs for webhook errors: `sudo journalctl -u hardware-crawler.service`
3. Ensure webhook URL is still valid

### Docker image build failed
Make sure you're in the correct directory and Dockerfile exists:
```bash
ls -la /opt/LinuxHardwareCrawler/Dockerfile
docker build -t linux-hardware-crawler:latest /opt/LinuxHardwareCrawler/
```

## Cost Estimation

- **VPS:** $5-20/month depending on provider and specs
- **Bandwidth:** Minimal (mostly local)
- **Total:** $5-20/month

## Updating the Application

When you update the code:

```bash
cd /opt/LinuxHardwareCrawler
git pull origin main
docker build -t linux-hardware-crawler:latest .
```

The next cron execution will use the new image.

## Quick Start Reference

```bash
# Build
docker build -t linux-hardware-crawler:latest .

# Test run
docker run --rm \
  -v /var/lib/linux-hardware-crawler:/app/output \
  -e DISCORD_WEBHOOK_URL="YOUR_WEBHOOK_URL" \
  linux-hardware-crawler:latest

# View result
cat /var/lib/linux-hardware-crawler/devices.json
```
