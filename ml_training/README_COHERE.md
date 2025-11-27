# Cohere Training for Sisi Lola

## Quick Commands

### Windows
```cmd
cd c:\Users\POK28\Dropbox\Sisi_Lola
run_cohere_training.bat
```

### Linux/Mac
```bash
cd ~/Dropbox/Sisi_Lola
chmod +x run_cohere_training.sh
./run_cohere_training.sh
```

### Test Integration
```bash
python test_cohere_integration.py
```

## What This Does

1. ✅ Loads Cohere API key from `.env`
2. ✅ Installs required dependencies
3. ✅ Prepares Sisi Lola personality dataset
4. ✅ Uploads dataset to Cohere
5. ✅ Creates fine-tuning job
6. ✅ Triggers GitHub Actions workflow
7. ✅ Generates training report

## Files Created

- `scripts/cohere_training.py` - Training script
- `datasets/sisi_lola_personality.txt` - Training data
- `../ansible/playbooks/cohere_training.yml` - Automation
- `../sisi_lola_api/app/services/cohere_service.py` - API service

## Monitor Training

- **Cohere Dashboard**: https://dashboard.cohere.com/fine-tuning
- **Local Logs**: `logs/cohere_training_*.md`
- **GitHub Actions**: Check your repository's Actions tab

## Configuration

API key is stored in `../sisi_lola_api/.env`:
```
COHERE_API_KEY=RABGythRT0Pd58wLABvi2NYp1PNtHigKWOHlELIv
COHERE_MODEL=command-r-plus
```

## Next Steps

1. Run training: `run_cohere_training.bat`
2. Monitor in Cohere dashboard
3. Test with: `python test_cohere_integration.py`
4. Deploy when ready

## Support

See `../COHERE_SETUP_GUIDE.md` for detailed documentation.
