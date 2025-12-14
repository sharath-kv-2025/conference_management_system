# Conference Management System

An enterprise-grade Conference Management System built with Frappe Framework, featuring clean architecture, service-oriented design, and professional UI/UX.

## 🏗️ Architecture Overview

The system follows a clean, modular architecture:

```
conference_management_system/
├── conference_management_system/
│   ├── doctype/                    # Core business entities
│   │   ├── conference/
│   │   ├── session/
│   │   ├── attendee/
│   │   ├── registration/
│   │   └── api_log/
│   ├── services/                   # Business logic layer
│   │   ├── conference_service.py
│   │   └── registration_service.py
│   ├── controllers/                # Event handlers
│   │   ├── registration_controller.py
│   │   └── attendee_controller.py
│   ├── utils/                      # Helper utilities
│   │   └── api_logger.py
│   ├── api/v1/                     # REST API endpoints
│   │   ├── conferences.py
│   │   └── registrations.py
│   └── report/                     # Business reports
│       ├── conference_report/
│       └── session_analysis_report/
├── www/                            # Web pages
├── fixtures/                       # Sample data
└── tasks.py                        # Scheduled tasks
```

## 🚀 Features

### Core Functionality
- **Conference Management**: Create and manage conferences with automatic status updates
- **Session Scheduling**: Advanced session management with overlap detection
- **Attendee Registration**: Streamlined registration process with email verification
- **Payment Processing**: Mock payment system with invoice generation
- **Capacity Management**: Automatic capacity enforcement and waitlist handling

### Business Logic
- **Validation Rules**: Comprehensive validation for dates, times, and capacity
- **Event-Driven Architecture**: Automated email notifications and status updates
- **Recommendation Engine**: AI-powered session recommendations based on preferences
- **Conflict Detection**: Prevents double-booking and session overlaps

### User Experience
- **Minimal UI**: Clean, enterprise-grade interface
- **Responsive Design**: Mobile-friendly layouts
- **Multi-Step Registration**: Guided registration with verification
- **Real-Time Updates**: Dynamic content loading and status updates

## 📋 User Roles & Access Control

### 1. Administrator / Conference Admin
- **Access**: Full system access via Frappe Desk
- **Capabilities**:
  - Create/edit conferences and sessions
  - View all registrations and payments
  - Access analytics and reports
  - Manage attendee data
  - API access and logs

### 2. Attendee (Public + Logged-in)
- **Access**: Public web interface
- **Capabilities**:
  - Browse conferences and sessions
  - Register for sessions
  - Email verification with OTP
  - Payment processing
  - View personal registrations and invoices

## 🔧 Installation & Setup

### Prerequisites
- Frappe Framework (v14+)
- Python 3.8+
- MariaDB/MySQL

### Installation Steps

1. **Install the app**:
   ```bash
   bench get-app https://github.com/your-repo/conference_management_system
   bench install-app conference_management_system
   ```

2. **Create sample data**:
   ```bash
   bench execute conference_management_system.fixtures.sample_data.create_sample_data
   ```

3. **Set up permissions**:
   ```bash
   bench migrate
   ```

4. **Start the server**:
   ```bash
   bench start
   ```

## 🌐 API Documentation

### Base URL
```
https://your-site.com/api/method/conference_management_system.api.v1
```

### Endpoints

#### 1. Get Upcoming Conferences
```http
GET /conferences.get_upcoming_conferences
```

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "name": "conf-001",
      "conference_name": "Tech Summit 2024",
      "start_date": "2024-06-15",
      "end_date": "2024-06-17",
      "location": "San Francisco",
      "sessions": [...]
    }
  ]
}
```

#### 2. Register for Session
```http
POST /registrations.register_for_session
Content-Type: application/json

{
  "attendee_name": "John Doe",
  "email": "john@example.com",
  "phone_number": "+1-555-0123",
  "organization": "TechCorp",
  "session_id": "session-001"
}
```

#### 3. Process Payment
```http
POST /registrations.process_payment
Content-Type: application/json

{
  "registration_id": "reg-001"
}
```

#### 4. Search Conferences
```http
POST /conferences.search_conferences
Content-Type: application/json

{
  "keyword": "AI technology"
}
```

#### 5. Get Attendee Registrations
```http
POST /registrations.get_attendee_registrations
Content-Type: application/json

{
  "email": "john@example.com"
}
```

## 📊 Business Reports

### 1. Conference Report
- Conference overview with attendee counts
- Revenue analysis
- Session statistics
- Status tracking

### 2. Session Analysis Report
- Session capacity utilization
- Registration trends
- Speaker performance
- Revenue by session

## 🔄 Scheduled Tasks

### Daily Tasks
- **Conference Status Updates**: Automatically update conference status based on dates
- **Reminder Emails**: Send session reminders to registered attendees

### Weekly Tasks
- **API Log Cleanup**: Remove old API logs (30+ days)

## 🎯 Business Logic Rules

### Session Management
- ❌ No overlapping sessions within the same conference
- ❌ End time must be after start time
- ✅ Automatic capacity enforcement
- ✅ Real-time availability updates

### Registration Rules
- ❌ No double-booking for attendees
- ❌ Registration blocked when capacity reached
- ✅ Automatic invoice generation
- ✅ Unique join link creation

### Payment Processing
- 🎲 Mock payment with 80% success rate
- 📧 Automatic email notifications
- 🧾 Invoice generation on success
- 🔗 Join link delivery

## 🧪 Testing

### Sample Test Cases

1. **Conference Creation**:
   ```python
   # Test conference with valid dates
   conference = frappe.new_doc("Conference")
   conference.update({
       "conference_name": "Test Conference",
       "start_date": "2024-06-15",
       "end_date": "2024-06-17"
   })
   conference.insert()
   ```

2. **Session Overlap Validation**:
   ```python
   # Should throw error for overlapping sessions
   session1 = create_session("09:00", "11:00")
   session2 = create_session("10:00", "12:00")  # Overlaps!
   ```

3. **Registration Capacity**:
   ```python
   # Should block registration when capacity reached
   session = create_session(max_attendees=2)
   register_attendee(session, "user1@example.com")
   register_attendee(session, "user2@example.com")
   register_attendee(session, "user3@example.com")  # Should fail
   ```

## 🔐 Security Features

- **Input Validation**: All API inputs validated
- **SQL Injection Prevention**: Parameterized queries
- **Access Control**: Role-based permissions
- **API Logging**: Complete request/response logging
- **Email Verification**: OTP-based email verification

## 🚀 Performance Optimizations

- **Database Indexing**: Optimized queries with proper indexes
- **Caching**: Frappe's built-in caching mechanisms
- **Lazy Loading**: Dynamic content loading
- **Batch Operations**: Efficient bulk operations

## 📈 Monitoring & Analytics

- **API Logs**: Complete API request/response tracking
- **Error Logging**: Comprehensive error tracking
- **Performance Metrics**: Built-in Frappe monitoring
- **Business Analytics**: Custom reports and dashboards

## 🛠️ Customization Guide

### Adding New Fields
1. Modify doctype JSON files
2. Update controllers if needed
3. Run `bench migrate`

### Creating Custom Reports
1. Create new report in `/report/` directory
2. Implement `execute()` function
3. Define columns and data logic

### Adding API Endpoints
1. Create new file in `/api/v1/`
2. Use `@frappe.whitelist()` decorator
3. Add `@log_api_call` for logging

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Follow coding standards
4. Add tests for new features
5. Submit pull request

## 📄 License

MIT License - see LICENSE file for details.

## 📞 Support

For support and questions:
- Email: support@conference-system.com
- Documentation: https://docs.conference-system.com
- Issues: GitHub Issues page