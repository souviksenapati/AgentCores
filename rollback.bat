@echo off
echo 🔄 Rolling back AgentCores to previous state...

:: Stop any running containers
docker-compose down

:: Restore backup files
echo 📁 Restoring backup files...
copy "backup\.env.backup" "backend\.env"
copy "backup\database.py.backup" "backend\app\database.py"  
copy "backup\main.py.backup" "backend\app\main.py"
copy "backup\docker-compose.yml.backup" "docker-compose.yml"

echo ✅ Rollback complete! 
echo 🚀 You can now run the original setup with: docker-compose up -d
pause