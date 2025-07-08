# PWA Setup Guide - Pacífico Workflow

## Overview
This guide explains how to set up, test, and deploy the Progressive Web App (PWA) functionality for the Pacífico Workflow system.

## ✅ Completed Setup

### 1. Service Worker Configuration
- **Location**: `workflow/static/workflow/sw.js`
- **Features**: 
  - Offline caching with multiple cache strategies
  - Network-first for dynamic content
  - Cache-first for static assets
  - Background sync capability
  - Push notification support (prepared for future use)

### 2. Manifest Configuration
- **Endpoint**: `/workflow/manifest.json`
- **Features**:
  - App name: "Pacífico Workflow"
  - Theme color: #009c3c (Pacífico green)
  - Display mode: standalone
  - Icons: Complete set from 16x16 to 512x512
  - Shortcuts: Dashboard, Bandeja, Nueva Solicitud

### 3. PWA Icons
- **Location**: `workflow/static/workflow/icons/`
- **Available sizes**: 16x16, 32x32, 72x72, 96x96, 128x128, 144x144, 152x152, 192x192, 384x384, 512x512
- **Format**: PNG with RGBA support
- **Special**: Apple touch icon (180x180) and favicon included

### 4. PWA Middleware
- **Location**: `workflow/middleware.py`
- **Features**:
  - Proper cache headers for PWA resources
  - Service worker scope configuration
  - Static asset caching optimization

### 5. Base Template Integration
- **Location**: `workflow/templates/workflow/base.html`
- **Features**:
  - Manifest link and meta tags
  - Service worker registration
  - Install prompt handling
  - Offline detection
  - Update notifications

## 🧪 Testing the PWA

### Test Page
Visit `/workflow/pwa-test/` to access the comprehensive PWA test page that includes:
- Connection status monitoring
- Service worker registration status
- Installation status checking
- Offline functionality testing
- Cache testing
- Notification testing

### Manual Testing Steps

1. **Basic PWA Features**:
   ```bash
   # Check manifest
   curl http://localhost:8000/workflow/manifest.json
   
   # Check service worker
   curl http://localhost:8000/workflow/sw.js
   
   # Check offline page
   curl http://localhost:8000/workflow/offline/
   ```

2. **Browser Testing**:
   - Open Chrome DevTools > Application > Service Workers
   - Check if service worker is registered
   - Test offline mode in Network tab
   - Look for install prompts in address bar

3. **Installation Testing**:
   - Chrome: Look for install icon in address bar
   - Edge: Check for "Install app" option in menu
   - Mobile browsers: Check for "Add to Home Screen"

## 🚀 Production Deployment

### HTTPS Requirement
**⚠️ CRITICAL**: PWAs require HTTPS in production for:
- Service worker registration
- Install prompts
- Push notifications
- Secure context features

### Production Checklist

1. **SSL Certificate**:
   ```python
   # In settings.py for production
   SECURE_SSL_REDIRECT = True
   SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
   ```

2. **Domain Configuration**:
   ```python
   # Update ALLOWED_HOSTS
   ALLOWED_HOSTS = ['your-domain.com', 'www.your-domain.com']
   
   # Update CSRF_TRUSTED_ORIGINS
   CSRF_TRUSTED_ORIGINS = [
       'https://your-domain.com',
       'https://www.your-domain.com',
   ]
   ```

3. **Static Files**:
   ```bash
   # Collect static files
   python manage.py collectstatic
   
   # Ensure icons are accessible
   # Check: https://your-domain.com/static/workflow/icons/icon-192x192.png
   ```

4. **Security Headers**:
   ```python
   # Add to settings.py
   SECURE_CONTENT_TYPE_NOSNIFF = True
   SECURE_BROWSER_XSS_FILTER = True
   SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
   ```

## 📱 PWA Features Available

### Core Features
- ✅ **Offline Access**: Works without internet connection
- ✅ **Installable**: Can be installed on devices
- ✅ **App-like Experience**: Runs in standalone mode
- ✅ **Responsive Design**: Works on all screen sizes
- ✅ **Fast Loading**: Cached resources load instantly

### Advanced Features
- ✅ **Background Sync**: Queues actions when offline
- ✅ **Update Notifications**: Alerts users of new versions
- ✅ **Network Status**: Shows connection state
- 🔄 **Push Notifications**: Prepared for future implementation
- 🔄 **Background Tasks**: Framework ready for expansion

## 🔧 Configuration Options

### PWA Settings (settings.py)
```python
# PWA Configuration
PWA_APP_NAME = 'Pacífico Workflow'
PWA_APP_DESCRIPTION = 'Sistema de Workflow - Financiera Pacífico'
PWA_APP_THEME_COLOR = '#009c3c'
PWA_APP_BACKGROUND_COLOR = '#ffffff'
PWA_APP_DISPLAY = 'standalone'
PWA_APP_SCOPE = '/workflow/'
PWA_APP_START_URL = '/workflow/'
```

### Cache Strategy Configuration
Edit `workflow/static/workflow/sw.js` to modify:
- Cache names and versions
- URLs to cache
- Cache strategies (network-first, cache-first, etc.)
- Cache expiration times

## 🐛 Troubleshooting

### Common Issues

1. **Service Worker Not Registering**:
   - Check browser console for errors
   - Ensure HTTPS in production
   - Verify service worker path is correct

2. **Install Prompt Not Showing**:
   - PWA criteria must be met (manifest, service worker, HTTPS)
   - Some browsers have different timing for prompts
   - Check DevTools > Application > Manifest

3. **Offline Mode Not Working**:
   - Verify service worker is active
   - Check cache storage in DevTools
   - Ensure offline page exists

4. **Icons Not Loading**:
   - Check static file serving
   - Verify icon paths in manifest
   - Ensure proper MIME types

### Debug Commands
```bash
# Check service worker status
curl -I http://localhost:8000/workflow/sw.js

# Validate manifest
curl -H "Accept: application/json" http://localhost:8000/workflow/manifest.json

# Test offline page
curl http://localhost:8000/workflow/offline/

# Check PWA test page
curl http://localhost:8000/workflow/pwa-test/
```

## 📊 Performance Optimization

### Cache Optimization
- Static assets: 1 year cache (31536000 seconds)
- Dynamic content: Network-first with fallback
- API responses: No cache for fresh data

### Load Time Optimization
- Critical CSS inlined
- Non-critical resources lazy-loaded
- Service worker pre-caches essential resources

## 🔮 Future Enhancements

### Planned Features
- **Push Notifications**: Real-time updates for workflow changes
- **Background Sync**: Offline form submissions
- **App Shortcuts**: More quick actions
- **Advanced Caching**: Smarter cache invalidation
- **Analytics**: PWA usage tracking

### Implementation Ready
The PWA framework is prepared for these features with:
- Service worker message handling
- Notification permission framework
- Background sync event listeners
- Extensible cache strategies

## 📞 Support

For PWA-related issues:
1. Check the PWA test page: `/workflow/pwa-test/`
2. Review browser console for errors
3. Verify all requirements are met
4. Check network tab for service worker activity

## 🎯 Success Metrics

A successful PWA deployment should show:
- ✅ Service worker registered and active
- ✅ Manifest properly loaded
- ✅ Install prompt available
- ✅ Offline functionality working
- ✅ Fast load times (< 2 seconds)
- ✅ Responsive design on all devices

---

*Last updated: January 2025*
*Version: 1.0.1* 