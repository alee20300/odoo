# Salon Appointment Module for Odoo 19 Community

Complete salon appointment management system running on Docker.

## Features

✅ **Appointment Management** - Full CRUD with state workflow  
✅ **Overlap Prevention** - No double-booking for confirmed appointments  
✅ **Service Integration** - Uses Products (type=service)  
✅ **Barber Assignment** - Assigns appointments to users  
✅ **Multiple Views** - List, Form, Calendar, Kanban  
✅ **Buffer Times** - Before/after appointment buffers  
✅ **Source Tracking** - Walk-in, Instagram, Call, Website  
✅ **Status Workflow** - Requested → Confirmed → In Service → Completed  
✅ **Auto Reference Numbers** - SAL/2025/00001 format  

## Quick Start

### 1. Start Docker Containers

```bash
cd /Users/aliabdulla/odoo
docker compose up -d
```

Wait 30-60 seconds for Odoo to initialize.

### 2. Access Odoo

Open browser: **http://localhost:8069**

Create your database:
- Database name: `salon_db` (or any name)
- Email: your admin email
- Password: your admin password
- Language: English
- Country: Your country

### 3. Install the Module

1. Enable **Developer Mode**:
   - Settings → Activate Developer Mode (at bottom)

2. Update Apps List:
   - Apps → Update Apps List (top-right menu)

3. Install Module:
   - Apps → Remove "Apps" filter
   - Search: **Salon Appointment**
   - Click **Install**

### 4. Configure

#### Add Services (Required)
1. Go to **Sales → Products → Products**
2. Create services (e.g., "Haircut", "Hair Coloring"):
   - Product Type: **Service**
   - Sales Price: Set your price
   - Save

#### Add Barbers
- Use existing users or create new ones
- Settings → Users & Companies → Users

### 5. Create Appointments

1. **Salon → Appointments → Create**
2. Fill in:
   - Customer (create if needed)
   - Service (select from products)
   - Barber/Stylist
   - Start time
   - Duration (default 30 min)
   - Buffer times (optional)
3. Click **Confirm** to activate overlap prevention

## Views

- **List View** - All appointments sorted by start time
- **Form View** - Detailed appointment with workflow buttons
- **Calendar View** - Visual schedule (color-coded by barber)
- **Kanban View** - Today's appointments grouped by barber

## Workflow States

1. **Requested** - Initial state (can overlap)
2. **Confirmed** - Appointment confirmed (overlap prevention active)
3. **In Service** - Customer is being served
4. **Completed** - Service finished
5. **Cancelled** - Appointment cancelled
6. **No Show** - Customer didn't show up

## Overlap Prevention

- Only applies to **Confirmed** and **In Service** states
- **Requested** appointments can overlap (for tentative bookings)
- Includes buffer times in overlap calculation
- Error message if double-booking attempted

## File Structure

```
odoo/
├── docker-compose.yml
└── custom_addons/
    └── salon_appointment/
        ├── __init__.py
        ├── __manifest__.py
        ├── models/
        │   ├── __init__.py
        │   └── salon_appointment.py
        ├── views/
        │   ├── menu.xml
        │   └── salon_appointment_views.xml
        ├── security/
        │   ├── security.xml
        │   └── ir.model.access.csv
        └── data/
            └── sequence.xml
```

## Security Groups

- **Salon User** - Can create, read, write appointments
- **Salon Manager** - Full access including delete

Assign groups: Settings → Users & Companies → Users → Edit user → Access Rights

## Troubleshooting

### Module not showing in Apps
- Check volume path in docker-compose.yml matches your directory
- Verify `--addons-path` includes `/mnt/extra-addons`
- Update Apps List again

### Restart Odoo
```bash
docker compose restart odoo
```

### View logs
```bash
docker compose logs -f odoo
```

### Reset everything
```bash
docker compose down -v
docker compose up -d
```

## Next Steps (Optional Extensions)

These can be added later:

1. **"Any Barber" option** - Auto-assign based on availability
2. **Find next slot** - Button to suggest next available time
3. **Working hours** - Define business hours + breaks per barber
4. **Website booking** - Self-service appointment requests
5. **SMS/Email reminders** - Automated notifications
6. **Recurring appointments** - Weekly/monthly bookings

Let me know which feature you'd like to add next!

## Support

For issues or questions, check:
- Odoo logs: `docker compose logs odoo`
- Module files in `custom_addons/salon_appointment/`
- Odoo documentation: https://www.odoo.com/documentation/19.0/

---

Built for **Odoo 19 Community Edition**  
License: AGPL-3
