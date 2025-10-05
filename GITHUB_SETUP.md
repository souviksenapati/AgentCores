# 🚀 GitHub Actions Setup Guide

## 📋 Repository Admin Setup (One-time)

### 1. Enable GitHub Actions
- Go to **Settings** → **Actions** → **General**
- Set "Actions permissions" to: **Allow all actions and reusable workflows**
- Enable "Allow GitHub Actions to create and approve pull requests"

### 2. Branch Protection Rules
Go to **Settings** → **Branches** → **Add rule**:

**Rule for `main` branch:**
- Branch name pattern: `main`
- ✅ Require a pull request before merging
- ✅ Require approvals (1 approval minimum)
- ✅ Require status checks to pass before merging
  - ✅ backend-test
  - ✅ frontend-test  
  - ✅ security-scan
  - ✅ ci-success
- ✅ Require up-to-date branches
- ✅ Do not allow bypassing the above settings
- ✅ Restrict pushes that create files that match the target branch

**Rule for `dev` branch:**
- Branch name pattern: `dev`
- ✅ Require status checks to pass before merging
  - ✅ backend-test
  - ✅ frontend-test
  - ✅ security-scan

### 3. Required Secrets (Optional)
Go to **Settings** → **Secrets and variables** → **Actions**:

**Repository Secrets:**
- `CODECOV_TOKEN` (for coverage reporting) - Optional
- `STAGING_DEPLOY_KEY` (if deploying to staging) - Optional
- `PROD_DEPLOY_KEY` (if deploying to production) - Optional

### 4. Environment Setup (Optional)
Go to **Settings** → **Environments**:

**Create environments:**
- `staging` (for dev branch deployments)
- `production` (for main branch deployments, require reviews)

---

## 👥 Team Member Workflow

### 🔄 Daily Development Process

#### **Step 1: Create Feature Branch**
```bash
# Pull latest changes
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/your-feature-name
```

#### **Step 2: Make Changes & Test Locally**
```bash
# Run local tests to catch issues early
.\run-tests.bat    # Windows
# OR
./run-tests.sh     # Linux/Mac

# Make your changes...
# Add files
git add .
git commit -m "feat: add new feature"
```

#### **Step 3: Push & Create Pull Request**
```bash
# Push feature branch
git push origin feature/your-feature-name

# Go to GitHub and create Pull Request
# GitHub Actions will automatically run all tests
```

#### **Step 4: Address CI Failures**
If tests fail, you'll see:
- ❌ Red X next to commit
- 📝 Detailed comment on your PR
- 🔗 Links to view logs

**Common fixes:**
```bash
# Fix formatting
cd backend && black . && isort .
cd frontend && npm run format

# Fix linting
cd backend && flake8 app/

# Run tests
pytest tests/ -v
npm test
```

#### **Step 5: Code Review & Merge**
- ✅ All checks must pass (green checkmarks)
- 👀 Get team member approval
- 🔀 Use "Squash and Merge" to keep history clean

---

## 🎯 Quick Reference - What Triggers Checks?

### **Every Push/PR:**
- 🔍 Code quality (Black, flake8, ESLint)
- 🧪 Unit tests (backend + frontend)
- 🔒 Security scanning
- 🐳 Docker build test

### **Pull Requests Only:**
- 🔗 Integration tests
- 📊 Coverage reporting
- 📝 Automated PR comments

### **Branch-Specific:**
- `dev` branch → 🚀 Auto-deploy to staging
- `main` branch → 🌟 Auto-deploy to production

---

## 🔧 Troubleshooting

### **Common Issues:**

**❌ "backend-test failed"**
```bash
cd backend
pip install -r requirements.txt
pytest tests/ -v
# Fix any failing tests
```

**❌ "Code formatting failed"**
```bash
cd backend
black .
isort .

cd frontend  
npm run format
```

**❌ "Coverage too low"**
- Current requirement: 46% minimum
- Add more tests to increase coverage
- Check coverage report in CI logs

**❌ "Docker build failed"**
- Check Dockerfile syntax
- Ensure all dependencies are in requirements.txt
- Test locally: `docker-compose build`

### **Local Testing Commands:**
```bash
# Complete CI simulation
.\run-tests.bat

# Individual checks
cd backend
black --check .
isort --check-only .
flake8 app/
pytest tests/ -v --cov=app

cd frontend
npm run lint
npm run test
npm run build
```

---

## 📊 Pipeline Status Dashboard

Your GitHub repository will show:

### **Repository Homepage:**
- 🟢 Green badge: All checks passing
- 🔴 Red badge: Some checks failing
- 📊 Coverage percentage display

### **Pull Request Page:**
- ✅ Individual check status
- 📝 Automated comments with results
- 🚫 Merge blocked until all green

### **Actions Tab:**
- 📈 Full workflow history
- 📋 Detailed logs for debugging
- ⏱️ Performance metrics

---

## 🎉 Benefits for Your Team

### **Automated Quality Assurance:**
- 🚫 No broken code reaches main branch
- 📏 Consistent code formatting across team
- 🔒 Automatic security vulnerability detection
- 📊 Code coverage tracking

### **Developer Experience:**
- 🔄 Immediate feedback on every change
- 📝 Clear error messages and fix suggestions
- 🎯 Pre-commit validation reduces CI failures
- 📱 GitHub mobile notifications

### **Team Collaboration:**
- 👀 Required code reviews
- 📋 Standardized merge process
- 📊 Transparent quality metrics
- 🚀 Automated deployments

---

## 🔗 Next Steps

1. **Admin**: Configure branch protection rules (above)
2. **Team**: Clone repository and run `.\run-tests.bat` locally
3. **Practice**: Create a test PR to see the workflow
4. **Customize**: Adjust coverage requirements or add more checks
5. **Monitor**: Review Actions tab regularly for insights

**Your pipeline is production-ready!** 🎉