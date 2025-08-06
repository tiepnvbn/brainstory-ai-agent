#!/usr/bin/env pwsh

# Script thiết lập Ollama với model nhẹ cho BrainStory AI Agent

Write-Host "🧠 BrainStory AI Agent - Ollama Setup" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

# Kiểm tra Ollama đã cài chưa
Write-Host "1. Kiểm tra Ollama..." -ForegroundColor Yellow
try {
    $version = ollama --version
    Write-Host "✅ Ollama đã cài đặt: $version" -ForegroundColor Green
} catch {
    Write-Host "❌ Ollama chưa được cài đặt!" -ForegroundColor Red
    Write-Host "Vui lòng tải từ: https://ollama.ai/download" -ForegroundColor Yellow
    Write-Host "Sau khi cài xong, chạy lại script này." -ForegroundColor Yellow
    exit 1
}

# Danh sách model nhẹ theo thứ tự ưu tiên
$models = @(
    @{name="qwen2:1.5b"; size="0.9GB"; desc="Nhẹ nhất, hiệu quả"},
    @{name="llama3.2:1b"; size="1.3GB"; desc="Meta, rất nhẹ"},
    @{name="gemma2:2b"; size="1.6GB"; desc="Google, cân bằng"},
    @{name="phi3:mini"; size="2.3GB"; desc="Microsoft, tối ưu"}
)

Write-Host "`n2. Tải model AI..." -ForegroundColor Yellow
Write-Host "Chọn model để tải (khuyến nghị bắt đầu với model nhẹ nhất):"

for ($i = 0; $i -lt $models.Count; $i++) {
    $model = $models[$i]
    Write-Host "$($i+1). $($model.name) - $($model.size) - $($model.desc)" -ForegroundColor Cyan
}

do {
    $choice = Read-Host "`nNhập số (1-$($models.Count)) hoặc 'all' để tải tất cả"
    
    if ($choice -eq "all") {
        foreach ($model in $models) {
            Write-Host "`n📥 Đang tải $($model.name)..." -ForegroundColor Yellow
            try {
                ollama pull $model.name
                Write-Host "✅ Tải thành công $($model.name)" -ForegroundColor Green
            } catch {
                Write-Host "❌ Lỗi khi tải $($model.name): $($_.Exception.Message)" -ForegroundColor Red
            }
        }
        break
    } elseif ([int]$choice -ge 1 -and [int]$choice -le $models.Count) {
        $selectedModel = $models[[int]$choice - 1]
        Write-Host "`n📥 Đang tải $($selectedModel.name)..." -ForegroundColor Yellow
        try {
            ollama pull $selectedModel.name
            Write-Host "✅ Tải thành công $($selectedModel.name)" -ForegroundColor Green
        } catch {
            Write-Host "❌ Lỗi khi tải $($selectedModel.name): $($_.Exception.Message)" -ForegroundColor Red
        }
        break
    } else {
        Write-Host "Lựa chọn không hợp lệ!" -ForegroundColor Red
    }
} while ($true)

# Kiểm tra model đã tải
Write-Host "`n3. Kiểm tra model đã tải..." -ForegroundColor Yellow
try {
    $installedModels = ollama list
    Write-Host "✅ Model đã cài đặt:" -ForegroundColor Green
    Write-Host $installedModels
} catch {
    Write-Host "❌ Không thể kiểm tra model đã cài" -ForegroundColor Red
}

Write-Host "`n🎉 Hoàn tất! Bây giờ bạn có thể chạy BrainStory AI Agent" -ForegroundColor Green
Write-Host "Chạy: streamlit run app/main.py" -ForegroundColor Cyan
