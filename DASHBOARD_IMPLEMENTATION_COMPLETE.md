# Dashboard Role-Based Implementation - Complete Guide

## Overview

This implementation creates different dashboard experiences based on user roles and permissions within the PACIFICO workflow system. The system now automatically routes users to the appropriate dashboard based on their Django group membership and permissions.

## 🚀 Key Features Implemented

### 1. **Smart Dashboard Router**
- **Location**: `workflow/dashboard_views.py` - `dashboard_router()` function
- **Purpose**: Automatically determines which dashboard to show based on user role
- **Fallback**: Defaults to operational dashboard for users without specific roles

### 2. **Role-Based Dashboards**

#### 📊 **Dashboard de Negocios** (Business Officers)
- **Target Users**: Members of "Oficial de Negocio" Django group
- **Template**: `dashboard_negocios.html`
- **URL**: `/workflow/dashboard-negocios/`
- **Features**:
  - Personal solicitudes and cotizaciones metrics
  - Performance tracking (completion times)
  - Notas y recordatorios management
  - Temporal evolution charts (6-month view)
  - Individual KPIs and achievements

#### 🏛️ **Dashboard de Comité Enhanced** (Credit Committee)
- **Target Users**: Members of groups containing "Comité" or "Comite"
- **Template**: `dashboard_comite_enhanced.html`
- **URL**: `/workflow/dashboard-comite-enhanced/`
- **Features**:
  - Committee escalation statistics
  - Personal voting status (pending/completed)
  - Resolution time analytics
  - Level-based distribution analysis
  - Committee performance metrics

#### 📋 **Dashboard Bandeja de Trabajo** (Group Work Queue)
- **Target Users**: Users with `PermisoBandeja` access to group queues
- **Template**: `dashboard_bandeja.html`
- **URL**: `/workflow/dashboard-bandeja/`
- **Features**:
  - Real-time queue status
  - Unassigned vs assigned requests distribution
  - SLA violation tracking
  - Team productivity metrics
  - Stage-specific processing times

#### 📈 **Dashboard Operativo** (Operational - Default)
- **Target Users**: All other users and superuser default
- **Template**: `dashboard.html` (existing, enhanced)
- **URL**: `/workflow/dashboard-operativo/`
- **Features**: System-wide operational metrics

### 3. **Superuser Dashboard Selector**
- **Feature**: Dropdown menu for superusers to switch between dashboard views
- **Implementation**: Query parameter `?type=` (operativo|negocios|comite|bandeja)
- **Usage**: Allows administrators to test and view all dashboard types

## 🔧 Technical Implementation

### URL Structure
```python
# Main entry point - smart routing
path('', dashboard_views.dashboard_router, name='dashboard')

# Specific dashboards
path('dashboard-negocios/', dashboard_views.dashboard_negocios, name='dashboard_negocios')
path('dashboard-bandeja/', dashboard_views.dashboard_bandeja_trabajo, name='dashboard_bandeja')
path('dashboard-comite-enhanced/', dashboard_views.dashboard_comite_enhanced, name='dashboard_comite_enhanced')
```

### User Role Detection Logic
```python
def dashboard_router(request):
    user = request.user
    
    # Superuser can choose via ?type= parameter
    if user.is_superuser:
        dashboard_type = request.GET.get('type', 'operativo')
        # Route to appropriate dashboard
    
    # Check for Oficial de Negocio
    if user.groups.filter(name='Oficial de Negocio').exists():
        return dashboard_negocios(request)
    
    # Check for Committee member
    if user.groups.filter(name__icontains='Comité').exists():
        return dashboard_comite_enhanced(request)
    
    # Check for bandeja access
    if has_bandeja_access(user):
        return dashboard_bandeja_trabajo(request)
    
    # Default to operational
    return dashboard_operativo(request)
```

## 📊 Dashboard Features Breakdown

### Dashboard de Negocios
- **Personal Metrics**: Solicitudes created by user
- **Cotizaciones Tracking**: User's quotations with status
- **Performance KPIs**:
  - Total solicitudes created
  - Active vs completed requests
  - Personal completion times
- **Reminders**: Upcoming notes and tasks
- **Temporal Analysis**: 6-month evolution charts

### Dashboard Bandeja de Trabajo
- **Queue Management**:
  - Total requests in accessible queues
  - Unassigned requests requiring attention
  - SLA violations across queues
- **Team Analytics**:
  - Most active users in queues
  - Processing time averages by stage
  - 30-day productivity metrics
- **Access Control**: Only shows queues user has permission to view

### Dashboard Comité Enhanced
- **Committee Metrics**:
  - Total escalations by level
  - Pending votes requiring attention
  - Approval/rejection ratios
- **Personal Participation**:
  - User's pending votes
  - Resolution time performance
  - Historical participation
- **Level Analysis**: Distribution and performance by committee level

## 🛠️ Setup and Configuration

### 1. Required Django Groups
Create these groups in Django Admin:
- `Oficial de Negocio`
- `Comité de Crédito` (or any group containing "Comité"/"Comite")

### 2. Bandeja Permissions
Configure `PermisoBandeja` objects for users who should access group queues:
```python
# Example: Give user access to group queue
PermisoBandeja.objects.create(
    etapa=etapa_grupal,
    usuario=user,
    puede_ver=True,
    puede_tomar=True
)
```

### 3. Test Users (Created by test script)
- `oficial_test` - Oficial de Negocio dashboard
- `comite_test` - Committee dashboard  
- `bandeja_test` - Group queue dashboard
- Password: `test123`

## 🎯 Usage Instructions

### For End Users
1. **Login**: Users automatically see their role-appropriate dashboard
2. **Navigation**: Dashboard includes role-specific action buttons
3. **Filtering**: Each dashboard includes relevant date/criteria filters

### For Superusers
1. **Dashboard Selection**: Use dropdown in header to switch views
2. **Testing**: Can access any dashboard type via dropdown
3. **URL Parameters**: Can use `?type=negocios` etc. for direct access

### For Administrators
1. **User Assignment**: Add users to appropriate Django groups
2. **Permissions**: Configure `PermisoBandeja` for queue access
3. **Monitoring**: Use operational dashboard for system-wide view

## 🔍 Key Files Modified/Created

### New Files
- `workflow/templates/workflow/dashboard_negocios.html`
- `workflow/templates/workflow/dashboard_bandeja.html`
- `workflow/templates/workflow/dashboard_comite_enhanced.html`
- `test_dashboard.py` (testing utilities)

### Modified Files
- `workflow/dashboard_views.py` - Added new dashboard functions
- `workflow/urls_workflow.py` - Added new URL patterns
- `workflow/templates/workflow/dashboard.html` - Added superuser selector

## 🧪 Testing

Run the test script to verify implementation:
```bash
python test_dashboard.py
```

The test script:
- Verifies group configurations
- Tests user routing logic
- Creates sample users for testing
- Validates permissions and access

## 🎨 UI/UX Features

### Visual Design
- **Color-coded KPIs**: Different colors for different metric types
- **Progress indicators**: Visual representation of percentages
- **Responsive layout**: Works on desktop and mobile
- **Auto-refresh**: Some dashboards auto-refresh for real-time data

### User Experience
- **Smart routing**: Users automatically see their relevant dashboard
- **Contextual actions**: Role-appropriate buttons and links
- **Clear navigation**: Easy access to related workflow functions
- **Performance indicators**: Visual feedback on user/team performance

## 🚦 Success Metrics

The implementation successfully addresses all requirements:

✅ **Negocios Dashboard**: Personal tracking for business officers
✅ **Comité Dashboard**: Committee-specific metrics and participation
✅ **Bandeja Dashboard**: Group queue management and team analytics  
✅ **Superuser Toggle**: Administrative access to all dashboard types
✅ **Smart Routing**: Automatic role-based dashboard selection
✅ **Responsive Design**: Modern, mobile-friendly interface
✅ **Real-time Data**: Live metrics and auto-refresh capabilities

## 🔮 Future Enhancements

Potential improvements could include:
- Dashboard personalization/customization
- More granular role-based permissions
- Advanced analytics and reporting
- Push notifications for critical metrics
- Export functionality for reports
- Integration with external BI tools

---

**Implementation Complete** ✅  
All requested dashboard functionalities have been successfully implemented and tested.
