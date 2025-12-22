# MODAL DEPLOYMENT - MANUAL STEPS REQUIRED

## ISSUE
Modal CLI requires browser-based authentication which cannot be completed in Codespaces terminal.

## SOLUTION: Deploy from Local Machine or use Modal Secrets

### Option 1: Deploy from Your Local Machine

1. **Clone the repository locally**:
   ```bash
   git clone https://github.com/BAMG-Studio/sisi-lola-project.git
   cd sisi-lola-project
   ```

2. **Install Modal CLI**:
   ```bash
   pip install modal
   ```

3. **Authenticate Modal** (this will open browser):
   ```bash
   modal token new
   ```
   Follow the browser prompts to complete authentication.

4. **Deploy the optimized service**:
   ```bash
   modal deploy ml_training/modal_inference_optimized.py
   ```

5. **Copy the endpoint URL** from the output:
   ```
   Web endpoints:
   ├─ generate_text => https://bamg-studio--sisi-lola-inference-generate-text.modal.run
   └─ health => https://bamg-studio--sisi-lola-inference-health.modal.run
   ```

### Option 2: Use Modal Web Interface

1. Go to https://modal.com/apps/bamg-studio
2. Click "New App"
3. Upload `ml_training/modal_inference_optimized.py`
4. Deploy directly from web interface

### Option 3: Use GitHub Actions (Recommended for CI/CD)

I'll create a GitHub Actions workflow for automatic deployment.

