#!/bin/bash

# ����Ƿ��� Git �ֿ�Ŀ¼��
if [ -d ".git" ]; then
  echo "Git �ֿ��ѳ�ʼ�������� 'git init' ���衣"
else
  echo "��ʼ�� Git �ֿ�..."
  git init
fi

# ��������� .gitignore �ļ�
GITIGNORE_FILE=".gitignore"
IGNORE_CONTENT="

# ������־�ļ�
*.log

# ������ʱ�ļ�
*.tmp
*.swp
*.bak

# ���Բ���ϵͳ���ɵ��ļ�
.DS_Store
Thumbs.db

# ���Ա������ɵ��ļ�
*.o
*.obj
*.class
*.pyc
*.pyo
*.exe

# ���������ļ���
node_modules/
vendor/
__pycache__/

# ���Ի����ļ�
.env
.env.local
*.env

# ���� IDE �ͱ༭�������ļ�
.idea/
.vscode/
*.sublime-*

"

echo "���� .gitignore �ļ�..."
if [ ! -f "$GITIGNORE_FILE" ]; then
  touch "$GITIGNORE_FILE"
fi

# �����Թ�����ӵ� .gitignore �ļ��������ظ���ӣ�
echo "$IGNORE_CONTENT" | while read -r line; do
  if ! grep -Fxq "$line" "$GITIGNORE_FILE"; then
    echo "$line" >> "$GITIGNORE_FILE"
  fi
done

echo ".gitignore �ļ���������ɣ�"

# ���� pre-commit ����
PRE_COMMIT_FILE=".git/hooks/pre-commit"
echo "���� pre-commit ����..."
cat <<'EOF' > "$PRE_COMMIT_FILE"
#!/bin/sh

# ��������ļ���С�����磺50MB��
max_size=52428800  # 50MB����λ���ֽ�

# �������н����ύ���ļ�
for file in $(git diff --cached --name-only); do
    if [ -f "$file" ]; then
        file_size=$(stat -c %s "$file")
        if [ $file_size -gt $max_size ]; then
            echo "Error: File $file is larger than 50MB and will not be committed."
            exit 1
        fi
    fi
done

exit 0
EOF

# ���� pre-commit �ļ���ִ��Ȩ��
chmod +x "$PRE_COMMIT_FILE"
echo "pre-commit ������������ɣ�"

# ��ʾ���
echo "��ʼ����ɣ���������Ŀ��ǰ״̬��"
git status
