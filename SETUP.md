# Conference Management System - Setup Guide

This guide provides step-by-step instructions to set up and run the Conference Management System on your local environment or server.

## Prerequisites

Before installing the Conference Management System, ensure you have the following installed:

- **Frappe Framework** (v14 or later)
- **Python** 3.8+
- **Node.js** 14+ and npm
- **MariaDB** 10.3+ or **MySQL** 8.0+
- **Redis** (for caching and background jobs)
- **Git** (for version control)

## Installation Steps

### 1. Setup Frappe Bench

If you don't have Frappe Bench installed, follow these steps:

```bash
# Install bench
pip3 install frappe-bench

# Create a new bench
bench init conference-bench --frappe-branch version-14
cd conference-bench

# Create a new site
bench new-site conference.local
```

### 2. Get the Conference Management System App

```bash
# Get the app from repository
bench get-app conference_management_system https://github.com/sharath-kv-2025/conference_management_system.git

# Or if you have the app locally
bench get-app conference_management_system /path/to/conference_management_system
```

### 3. Install the App

```bash
# Install the app on your site
bench --site conference.local install-app conference_management_system

# Start the development server
bench start
```

### 4. Access the Application

Once the installation is complete, you can access the application at:
- **Base URL**: `http://conference.local:8000`
- **Admin Dashboard**: `http://conference.local:8000/app/admin-dashboard`
- **Attendee Portal**: `http://conference.local:8000/app/attendee-portal`

## Default Users & Credentials

The system automatically creates test users during installation:

### Administrator Access
- **Username**: `Administrator`
- **Password**: `admin` (default Frappe password)
- **Access**: Full system access, all modules
- **Dashboard**: `http://conference.local:8000/app/admin-dashboard`

### Conference Admin
- **Username**: `admin@conference.com`
- **Password**: `confadmin`
- **Role**: Conference Admin, System Manager
- **Access**: Conference management, reports, admin functions
- **Dashboard**: `http://conference.local:8000/app/admin-dashboard`

### Test Attendee
- **Username**: `attendee@conference.com`
- **Password**: `confattendee`
- **Role**: Attendee
- **Access**: Conference registration, session booking, payments
- **Portal**: `http://conference.local:8000/app/attendee-portal`

## Application Features & Access Points

### 1. Admin Dashboard (`/app/admin-dashboard`)
**Access**: Conference Admin, System Manager

**Features**:
- Real-time statistics (conferences, sessions, registrations, revenue)
- Quick action buttons for creating conferences and sessions
- Revenue analytics with payment method breakdown
- System monitoring and API usage statistics

**Navigation**:
- Conference management
- Session scheduling
- Attendee management
- Payment tracking
- Reports and analytics

### 2. Attendee Portal (`/app/attendee-portal`)
**Access**: Attendee role, General users

**Features**:
- **Conferences Tab**: Browse and search upcoming conferences
- **Registrations Tab**: View registrations, make payments, access join links
- **Recommendations Tab**: Personalized session suggestions

**Workflow**:
1. Browse conferences and sessions
2. Register for sessions
3. Complete payment
4. Access join links for paid sessions
5. Manage preferences and get recommendations

### 3. Standard Frappe Interface (`/app`)
**Access**: All authenticated users

**Available Modules**:
- Conference Management System module
- Standard Frappe doctypes (Conference, Session, Registration, Attendee)
- Reports (Conference Report, Session Analysis Report, API Usage Report)
- System administration tools

## Sample Data

The application automatically generates comprehensive sample data including:

- **6 Conferences** with various statuses (Upcoming, Ongoing, Completed)
- **20+ Sessions** across different conferences with realistic scheduling
- **50 Attendees** with diverse profiles and preferences
- **100+ Registrations** with various payment statuses
- **Payment Records** with transaction details and processing fees
- **Email Logs** for registration and payment confirmations
- **API Logs** for system monitoring and debugging

## Configuration

### 1. Email Settings
Configure email settings in Frappe for notifications:
```bash
# Access email settings
http://conference.local:8000/app/email-account
```

### 2. Scheduled Tasks
The system includes automated tasks that run:
- **Daily**: Update conference status based on dates
- **Weekly**: Send session recommendations to attendees
- **Monthly**: Clean up old API logs

### 3. User Roles and Permissions
The system creates two main roles:
- **Conference Admin**: Full access to all conference management features
- **Attendee**: Limited access for registration and session management

## API Endpoints

The system provides RESTful APIs accessible at:

### Conference APIs
- `GET /api/method/conference_management_system.api.v1.conferences.get_upcoming_conferences`
- `GET /api/method/conference_management_system.api.v1.sessions.get_sessions_by_conference`

### Registration APIs
- `POST /api/method/conference_management_system.api.v1.registrations.register_for_session`
- `POST /api/method/conference_management_system.api.v1.registrations.process_payment`
- `GET /api/method/conference_management_system.api.v1.registrations.get_attendee_registrations`

### Admin APIs
- `GET /api/method/conference_management_system.api.v1.admin.get_dashboard_stats`
- `GET /api/method/conference_management_system.api.v1.admin.get_revenue_summary`

### Attendee APIs
- `GET /api/method/conference_management_system.api.v1.attendees.get_attendee_profile`
- `POST /api/method/conference_management_system.api.v1.attendees.update_preferences`

## Troubleshooting

### Common Issues

1. **Module Import Errors**
   ```bash
   bench --site conference.local migrate
   bench --site conference.local clear-cache
   ```

2. **Permission Errors**
   ```bash
   bench --site conference.local set-admin-password admin
   ```

3. **Database Issues**
   ```bash
   bench --site conference.local migrate
   bench --site conference.local reload-doc conference_management_system
   ```

4. **Static Files Not Loading**
   ```bash
   bench build
   bench --site conference.local clear-cache
   ```

### Development Mode

For development, run in development mode:
```bash
bench --site conference.local set-config developer_mode 1
bench start
```

### Production Deployment

For production deployment:
```bash
# Setup production
bench setup production

# Enable SSL (optional)
bench setup lets-encrypt conference.local

# Setup supervisor and nginx
sudo bench setup supervisor
sudo bench setup nginx
```

## Testing the Application

### 1. Test Conference Management
1. Login as Conference Admin (`admin@conference.com`)
2. Access Admin Dashboard
3. Create new conferences and sessions
4. Monitor statistics and analytics

### 2. Test Attendee Registration
1. Login as Attendee (`attendee@conference.com`)
2. Access Attendee Portal
3. Browse conferences and register for sessions
4. Complete payment process
5. Access join links for paid sessions

### 3. Test API Endpoints
Use tools like Postman or curl to test API endpoints:
```bash
# Get upcoming conferences
curl -X GET "http://conference.local:8000/api/method/conference_management_system.api.v1.conferences.get_upcoming_conferences"
```

## Support

For technical support:
- Check the main README.md for detailed documentation
- Review Frappe Framework documentation
- Create GitHub issues for bug reports
- Contact system administrators for deployment issues

## Next Steps

After successful setup:
1. Customize conference and session templates
2. Configure email notifications
3. Set up payment gateway integration (for production)
4. Customize user interfaces as needed
5. Configure backup and monitoring systems

---

**Note**: This setup creates a fully functional conference management system with sample data for immediate testing and evaluation.