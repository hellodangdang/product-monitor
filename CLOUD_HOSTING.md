# Running Monitor on Cloud Server

## Why Cloud Hosting?

✅ **True 24/7** - Server never sleeps  
✅ **No need to keep MacBook on** - Saves electricity  
✅ **More reliable** - Professional infrastructure  
✅ **Can run multiple monitors** - Monitor multiple products  

## Cloud Provider Options & Costs:

### Option 1: AWS EC2 (Amazon)
**Cost:** ~$5-10/month
- **t2.micro** (Free tier eligible for 12 months, then ~$8/month)
- **t3.micro** (~$7-8/month)
- 1 vCPU, 1GB RAM (enough for the monitor)
- Free tier: 750 hours/month for first year

### Option 2: DigitalOcean
**Cost:** ~$4-6/month
- **Basic Droplet** - $4/month (512MB RAM)
- **Basic Droplet** - $6/month (1GB RAM) - Recommended
- Very simple setup
- Great for beginners

### Option 3: Linode
**Cost:** ~$5/month
- **Nanode** - $5/month (1GB RAM)
- Similar to DigitalOcean

### Option 4: Google Cloud Platform
**Cost:** ~$5-10/month
- **e2-micro** - Free tier eligible, then ~$6/month
- 600 hours/month free for first 3 months

### Option 5: Vultr
**Cost:** ~$2.50-6/month
- **Regular Performance** - $2.50/month (512MB RAM)
- **Regular Performance** - $6/month (1GB RAM)
- Very affordable

### Option 6: Heroku (Easiest but more expensive)
**Cost:** ~$7/month
- **Eco Dyno** - $5/month (sleeps after 30min inactivity)
- **Basic Dyno** - $7/month (always on)
- Easiest deployment but more expensive

## Recommended: DigitalOcean ($6/month)

**Why:**
- Simple setup
- Good documentation
- Reliable
- $6/month for 1GB RAM (plenty for the monitor)

## Setup Steps (DigitalOcean Example):

### 1. Create Account
- Sign up at digitalocean.com
- Add payment method

### 2. Create Droplet
- Choose: Ubuntu 22.04
- Plan: Basic $6/month (1GB RAM)
- Region: Choose closest to you
- Add SSH key or use password

### 3. Connect to Server
```bash
ssh root@your-server-ip
```

### 4. Install Dependencies
```bash
# Update system
apt update && apt upgrade -y

# Install Python
apt install python3 python3-pip -y

# Install Chrome/Chromium for headless browsing
apt install chromium-browser chromium-chromedriver -y

# Or use Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt install ./google-chrome-stable_current_amd64.deb -y
```

### 5. Upload Your Code
```bash
# Option A: Use git
git clone your-repo-url
cd crawler

# Option B: Use scp from your Mac
# From your Mac:
scp -r /Users/yijiedang/Documents/GitHub/crawler root@your-server-ip:/root/crawler
```

### 6. Install Python Packages
```bash
cd crawler
pip3 install -r requirements.txt
```

### 7. Configure
```bash
# Edit config.json with your settings
nano config.json
```

### 8. Run in Background
```bash
# Use screen or tmux
apt install screen -y
screen -S monitor
python3 product_monitor.py
# Press Ctrl+A then D to detach
```

### 9. Keep Running on Reboot (Optional)
```bash
# Create systemd service
nano /etc/systemd/system/product-monitor.service
```

Add:
```ini
[Unit]
Description=Product Monitor
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/crawler
ExecStart=/usr/bin/python3 /root/crawler/product_monitor.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
systemctl enable product-monitor
systemctl start product-monitor
```

## Cost Comparison:

| Provider | Monthly Cost | RAM | Best For |
|----------|-------------|-----|----------|
| **Vultr** | $2.50 | 512MB | Budget |
| **DigitalOcean** | $6 | 1GB | **Recommended** |
| **AWS EC2** | $0-8 | 1GB | Free tier (first year) |
| **Linode** | $5 | 1GB | Alternative |
| **Heroku** | $7 | 512MB | Easiest setup |

## Total Cost Estimate:

- **Cheapest:** Vultr $2.50/month = **$30/year**
- **Recommended:** DigitalOcean $6/month = **$72/year**
- **Free (first year):** AWS EC2 = **$0 first year, then ~$96/year**

## Additional Considerations:

1. **Bandwidth:** Usually included (1TB+)
2. **Storage:** 25GB+ included (plenty for logs)
3. **Backups:** Optional, +$1-2/month
4. **Monitoring:** Usually free

## Setup Time:

- **First time:** 30-60 minutes
- **After that:** Just SSH in and update code

## Advantages Over MacBook:

✅ Never sleeps  
✅ Lower electricity cost  
✅ More reliable  
✅ Can monitor multiple products  
✅ Access from anywhere  
✅ Professional infrastructure  

## Disadvantages:

❌ Monthly cost ($3-7)  
❌ Need to learn basic Linux/SSH  
❌ Need to maintain server  

## Recommendation:

**Start with DigitalOcean ($6/month)** - Best balance of price, ease of use, and reliability.

Want help setting it up? I can guide you through the process step-by-step!

