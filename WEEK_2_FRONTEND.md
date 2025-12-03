# WEEK 2: FRONTEND DASHBOARD

## Day 1-2: Setup & Deploy

```bash
cd control_center_frontend

# Install dependencies
npm install

# Run locally
npm run dev
# Visit http://localhost:3000

# Test login with admin@sisilola.io / SisiLola2025!
```

## Day 3: Build Production

```bash
# Create .env.production
echo "NEXT_PUBLIC_API_URL=https://api.sisilola.io/api/v2" > .env.production

# Build
npm run build

# Deploy to Vercel (easiest)
npm install -g vercel
vercel login
vercel --prod

# Or deploy to server
npm run build
scp -r .next out package.json ubuntu@YOUR_SERVER:/var/www/sisilola-app/
```

## Day 4-5: Add Features

Create content management page:
