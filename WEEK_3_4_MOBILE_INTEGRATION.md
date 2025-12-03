# WEEK 3-4: MOBILE APP & INTEGRATION

## Week 3: React Native Mobile App

### Day 1: Setup

```bash
npx react-native init SisiLolaControl
cd SisiLolaControl
npm install @react-navigation/native @react-navigation/stack axios react-native-keychain
```

### Day 2-3: Core Screens

**App.tsx**
```typescript
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import LoginScreen from './screens/LoginScreen';
import DashboardScreen from './screens/DashboardScreen';

const Stack = createStackNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="Login">
        <Stack.Screen name="Login" component={LoginScreen} />
        <Stack.Screen name="Dashboard" component={DashboardScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
```

**screens/LoginScreen.tsx**
```typescript
import React, { useState } from 'react';
import { View, TextInput, Button, StyleSheet } from 'react-native';
import * as Keychain from 'react-native-keychain';
import axios from 'axios';

export default function LoginScreen({ navigation }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = async () => {
    try {
      const { data } = await axios.post('https://api.sisilola.io/api/v2/auth/login', {
        email, password
      });
      await Keychain.setGenericPassword('token', data.access_token);
      navigation.navigate('Dashboard');
    } catch (error) {
      alert('Login failed');
    }
  };

  return (
    <View style={styles.container}>
      <TextInput
        style={styles.input}
        placeholder="Email"
        value={email}
        onChangeText={setEmail}
        autoCapitalize="none"
      />
      <TextInput
        style={styles.input}
        placeholder="Password"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
      />
      <Button title="Login" onPress={handleLogin} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', padding: 20 },
  input: { borderWidth: 1, padding: 10, marginBottom: 10, borderRadius: 5 }
});
```

### Day 4-5: Build & Deploy

```bash
# iOS
cd ios && pod install && cd ..
npx react-native run-ios

# Android
npx react-native run-android

# Production builds
# iOS: Use Xcode to archive
# Android: ./gradlew assembleRelease
```

## Week 4: Integration & Polish

### Day 1-2: Connect Asset Pipeline

**Integrate with existing scripts:**

```python
# 00_PROJECT_CORE/Scripts/control_center_sync.py
import requests
import os
from pathlib import Path

API_BASE = "https://api.sisilola.io/api/v2"
TOKEN = os.getenv("CONTROL_CENTER_TOKEN")

def sync_asset(category, subcategory, filename, url, metadata):
    response = requests.post(
        f"{API_BASE}/control/assets",
        headers={"Authorization": f"Bearer {TOKEN}"},
        json={
            "category": category,
            "subcategory": subcategory,
            "filename": filename,
            "url": url,
            "metadata": metadata
        }
    )
    return response.json()

def sync_all_assets():
    assets_dir = Path("assets/generated")
    for file in assets_dir.rglob("*"):
        if file.is_file():
            sync_asset(
                category="GENERATED",
                subcategory=file.parent.name,
                filename=file.name,
                url=f"https://storage.sisilola.io/{file}",
                metadata={"size": file.stat().st_size}
            )
```

### Day 3: Automate Content Publishing

```python
# 00_PROJECT_CORE/Scripts/auto_publish.py
import requests
import schedule
import time

API_BASE = "https://api.sisilola.io/api/v2"
TOKEN = os.getenv("CONTROL_CENTER_TOKEN")

def check_and_publish():
    # Get approved content
    response = requests.get(
        f"{API_BASE}/control/content/queue?status=approved",
        headers={"Authorization": f"Bearer {TOKEN}"}
    )
    
    for content in response.json()["queue"]:
        if content["scheduled_at"] <= datetime.now():
            # Publish
            requests.post(
                f"{API_BASE}/control/content/{content['id']}/publish",
                headers={"Authorization": f"Bearer {TOKEN}"}
            )
            print(f"Published: {content['title']}")

schedule.every(5).minutes.do(check_and_publish)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### Day 4-5: Testing & Documentation

**Test all workflows:**
1. Login → Dashboard → Create Asset
2. Add content → Approve → Publish
3. Trigger ML training
4. View analytics

**Update .env with control center token:**
```bash
CONTROL_CENTER_TOKEN=your_access_token_here
```

## Deliverables

Week 3:
- ✅ Mobile app (iOS + Android)
- ✅ Push notifications setup
- ✅ Biometric auth

Week 4:
- ✅ Asset pipeline integration
- ✅ Auto-publishing system
- ✅ ML training triggers
- ✅ Complete documentation
- ✅ User training materials

## Final Architecture

```
User Devices
    ↓
[Web: app.sisilola.io] ← → [Mobile App]
    ↓
[API: api.sisilola.io]
    ↓
    ├── PostgreSQL (data)
    ├── S3 (assets)
    ├── YouTube API
    ├── Instagram API
    ├── TikTok API
    ├── HeyGen API
    ├── ElevenLabs API
    └── ML Training Pipeline
```

## Go-Live Checklist

- [ ] API deployed and tested
- [ ] Frontend deployed to app.sisilola.io
- [ ] Mobile apps in TestFlight/Play Store Beta
- [ ] All integrations tested
- [ ] Team trained on system
- [ ] Documentation complete
- [ ] Monitoring active
- [ ] Backups configured
- [ ] Security audit passed
- [ ] Load testing complete

## Post-Launch (Week 5+)

1. Monitor usage and performance
2. Gather user feedback
3. Iterate on features
4. Scale infrastructure as needed
5. Add advanced features:
   - AI-powered content suggestions
   - Advanced analytics
   - Automated A/B testing
   - Multi-language support
