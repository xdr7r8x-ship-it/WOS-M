# WOS-M
### Advanced Whiteout Survival Management Bot

![WOS-M Banner](assets/banner.png)

## 🎮 Overview

WOS-M is a comprehensive Discord bot designed for Whiteout Survival game management, featuring alliance management, player tracking, gift code redemption, event management, and more.

**© MANSOUR — WOS-M. All rights reserved for original code, branding, UI, documentation, custom features, automation systems, and project identity.**

## ✨ Features

### 📊 Dashboard
- **Single Command Access**: Everything through `/wos` slash command
- **Interactive Buttons**: Navigation via buttons, select menus, modals
- **Multi-language Support**: Full Arabic and English support

### 🏰 Management Modules
- **Alliances**: Complete alliance management with sync settings
- **Players**: Player tracking, FID management, alliance transfers
- **Gift Codes**: Auto redemption system with batch processing
- **Events**: Event creation and management
- **Attendance**: Track player attendance with reports
- **Bear Tracking**: Hunt damage tracking with leaderboards
- **Ministers**: Position management and scheduling
- **Notifications**: Scheduled notifications system

### 👑 Owner Panel
- **Language Management**: Switch between Arabic and English
- **Button Management**: Customize dashboard buttons
- **Text Management**: Edit all visible texts
- **Icon Management**: Customize icons and emojis
- **Branding**: Theme colors, bot name, signature
- **Feature Registry**: Enable/disable features dynamically

### 🔐 Security
- **Permission System**: Owner, Admin, Member levels
- **Audit Logging**: Track all sensitive operations
- **Permission Guards**: Secure action validation

### ⚙️ Technical
- **Process Queue**: Background task processing with priorities
- **Feature Registry**: Extensible feature system
- **SQLite/PostgreSQL**: Database with migration support
- **Captcha Integration**: Anti-bot protection
- **OCR Support**: Image text extraction

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Discord Bot Token
- Discord application with bot enabled

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/xdr7r8x-ship-it/wos-m.git
cd wos-m
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your credentials
```

5. **Run the bot**
```bash
python main.py
```

### Using Docker

```bash
# Build image
docker build -t wos-m .

# Run container
docker run -d --env-file .env wos-m
```

### Using Docker Compose

```bash
docker-compose up -d
```

## 📁 Project Structure

```
wos-m/
├── main.py              # Entry point
├── requirements.txt     # Dependencies
├── config/
│   └── settings.py      # Configuration
├── core/
│   ├── bot.py           # Bot core
│   ├── database.py      # Database system
│   ├── i18n.py          # Internationalization
│   ├── permissions.py   # Permission system
│   ├── audit_log.py     # Audit logging
│   ├── process_queue.py # Background tasks
│   └── feature_registry.py
├── modules/
│   ├── dashboard/       # Main dashboard
│   ├── owner_panel/     # Owner controls
│   ├── alliances/       # Alliance management
│   ├── players/         # Player management
│   ├── gift_codes/      # Gift code system
│   ├── events/          # Event management
│   ├── attendance/      # Attendance tracking
│   ├── bear_tracking/   # Bear hunt tracking
│   ├── notifications/   # Notification system
│   ├── ministers/       # Minister management
│   ├── themes/          # Theme customization
│   └── maintenance/     # Maintenance tools
├── integrations/
│   ├── wos_api_client.py
│   ├── gift_code_client.py
│   ├── captcha_service.py
│   └── ocr_service.py
├── views/
│   ├── base.py          # Base view classes
│   ├── buttons.py        # Button components
│   ├── modals.py        # Modal components
│   └── selects.py       # Select menu components
├── locales/
│   ├── ar.json          # Arabic translations
│   └── en.json          # English translations
└── database/
    ├── migrations/
    └── seed.py           # Initial data
```

## 🎯 Usage

### Slash Commands
| Command | Description |
|---------|-------------|
| `/wos` | Main dashboard - access all features |

### Navigation
- All navigation is done through **Buttons** and **Select Menus**
- Every page has **Back** (🔙) and **Home** (🏠) buttons
- Use **Modals** for data input

## 🔧 Configuration

Edit `.env` file:

```env
DISCORD_BOT_TOKEN=your_bot_token
DISCORD_APPLICATION_ID=your_app_id
OWNER_DISCORD_ID=your_user_id
DEFAULT_LANGUAGE=ar
DATABASE_URL=sqlite:///data/wosm.sqlite
```

## 📝 License

**© MANSOUR — WOS-M. All rights reserved for original code, branding, UI, documentation, custom features, automation systems, and project identity.**

This project is proprietary software. Unauthorized copying, distribution, or use is strictly prohibited.

## 🤝 Support

- **Owner**: MANSOUR
- **Discord**: DANGER_600

## 📜 Changelog

### v1.0.0
- Initial release
- Full feature implementation
- Arabic and English support
- Owner panel
- Gift code auto-redemption
- Process queue system
- Feature registry

---

**WOS-M** - Built for Whiteout Survival Excellence
