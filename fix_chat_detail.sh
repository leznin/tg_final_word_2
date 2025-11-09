#!/bin/bash

# Подключаемся к серверу и исправляем ChatDetail.tsx

sshpass -p '696578As!!!!' ssh root@45.147.196.229 << 'ENDSSH'
cd /root/tg_final_word_2/frontend/src/pages

# Создаем backup
cp ChatDetail.tsx ChatDetail.tsx.backup

# 1. Добавляем импорт useCurrentUser
sed -i "4 a import { useCurrentUser } from '../hooks/useAdminUsers';" ChatDetail.tsx

# 2. Добавляем хук useCurrentUser после addModeratorFromTelegramMutation
sed -i '/const addModeratorFromTelegramMutation = useAddModeratorFromTelegram();/a\  \n  // Get current user\n  const { data: currentUser } = useCurrentUser();' ChatDetail.tsx

# 3. Заменяем функцию handleAddModeratorFromTelegram
sed -i '/const handleAddModeratorFromTelegram = async (admin: any)/,/const user = JSON\.parse(userStr);/{
  /const userStr = localStorage.getItem/c\      // Check if current user is available\n      if (!currentUser) {
  /if (!userStr) {/d
  /const user = JSON\.parse/d
}' ChatDetail.tsx

# 4. Заменяем added_by_user_id: user.id на added_by_user_id: currentUser.id
sed -i 's/added_by_user_id: user\.id/added_by_user_id: currentUser.id/' ChatDetail.tsx

echo "Файл ChatDetail.tsx обновлен"

# Пересобираем фронтенд
cd /root/tg_final_word_2/frontend
echo "Начинаю сборку фронтенда..."
npm run build

# Перезапускаем nginx
echo "Перезапускаю nginx..."
systemctl reload nginx

echo "Готово!"
ENDSSH
