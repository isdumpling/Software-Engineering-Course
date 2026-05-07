# ============================================================
# Zhike Agent - Copy source files for software copyright submission
# Usage: Run this script in PowerShell
# Output: _submission/ folder with source_code/ and docs/
# ============================================================

$PROJ = "Z:\home\scvsalsgn\se_practice"
$DEST = "$PROJ\_submission"
$SOURCE_CODE = "$DEST\source_code"
$DOC = "$DEST\docs"

# Clean and recreate
if (Test-Path $DEST) { Remove-Item $DEST -Recurse -Force }

# Create directory structure
$dirs = @(
    "$SOURCE_CODE\backend\routers",
    "$SOURCE_CODE\backend\services",
    "$SOURCE_CODE\backend\course_management",
    "$SOURCE_CODE\frontend\src\router",
    "$SOURCE_CODE\frontend\src\store",
    "$SOURCE_CODE\frontend\src\api",
    "$SOURCE_CODE\frontend\src\views\admin",
    "$DOC"
)
foreach ($d in $dirs) { New-Item -ItemType Directory -Force -Path $d | Out-Null }

# ===== Backend source files =====
$BACKEND = @(
    "backend\main.py",
    "backend\config.py",
    "backend\database.py",
    "backend\models.py",
    "backend\schemas.py",
    "backend\auth.py",
    "backend\ai_service.py",
    "backend\requirements.txt",
    "backend\init_db.py",
    "backend\start.py",
    "backend\routers\__init__.py",
    "backend\routers\auth.py",
    "backend\routers\chat.py",
    "backend\routers\admin.py",
    "backend\services\__init__.py",
    "backend\services\knowledge_service.py",
    "backend\course_management\__init__.py",
    "backend\course_management\course_config.py",
    "backend\course_management\build_course_knowledge.py",
    "backend\course_management\build_all_courses.py",
    "backend\.env.example"
)

# ===== Frontend source files =====
$FRONTEND = @(
    "frontend\package.json",
    "frontend\vue.config.js",
    "frontend\src\main.js",
    "frontend\src\App.vue",
    "frontend\src\router\index.js",
    "frontend\src\store\index.js",
    "frontend\src\api\index.js",
    "frontend\src\views\Login.vue",
    "frontend\src\views\Register.vue",
    "frontend\src\views\Home.vue",
    "frontend\src\views\Chat.vue",
    "frontend\src\views\History.vue",
    "frontend\src\views\ForgotPassword.vue",
    "frontend\src\views\ResetPassword.vue",
    "frontend\src\views\admin\AdminLayout.vue",
    "frontend\src\views\admin\AdminDashboard.vue",
    "frontend\src\views\admin\AdminCourses.vue",
    "frontend\src\views\admin\AdminRetrievalTest.vue",
    "frontend\src\views\admin\AdminSystem.vue"
)

function Copy-Files($files, $label) {
    Write-Host "== $label ==" -ForegroundColor Cyan
    foreach ($f in $files) {
        $src = Join-Path $PROJ $f
        $dst = Join-Path $SOURCE_CODE $f
        $dir = Split-Path $dst -Parent
        if (!(Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
        if (Test-Path $src) {
            Copy-Item $src $dst -Force
            Write-Host "  OK  $f"
        } else {
            Write-Host "  MISS $f" -ForegroundColor Yellow
        }
    }
}

Copy-Files $BACKEND "Backend (20 files)"
Copy-Files $FRONTEND "Frontend (19 files)"

# Copy README to docs
$readme = Join-Path $PROJ "README.md"
if (Test-Path $readme) {
    Copy-Item $readme $DOC -Force
    Write-Host "  OK  README.md -> docs/"
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host " Done! Output: $DEST" -ForegroundColor Green
Write-Host "  - source_code/  (39 source files)" -ForegroundColor White
Write-Host "  - docs/         (README.md)" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Put the user manual PDF into: $DOC" -ForegroundColor White
Write-Host "  2. Zip the _submission/ folder for submission" -ForegroundColor White
