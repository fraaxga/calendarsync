#!/bin/bash
if [ ! -f "src/config/yandex_token.json" ]; then
    echo "Токен Яндекс.Календаря не найден в src/config/"
    exit 1
fi
echo "Токен Яндекс.Календаря найден"
if [ ! -f "src/config/google_token.pickle" ]; then
    echo "Токен Google не найден"
fi

echo ""
echo "запуск синхронизации"
python src/main.py
if [ -f "scripts/check_db.py" ]; then
    echo ""
    echo "проверка результата"
    python scripts/check_db.py
fi