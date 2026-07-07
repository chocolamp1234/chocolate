#!/usr/bin/env bash
# Local WP (Simply Static export) -> このリポジトリ -> GitHub -> Vercel への
# ワンコマンドデプロイスクリプト。
#
# 使い方:
#   ./deploy.sh                 # 同期 + コミット + プッシュ
#   ./deploy.sh --dry-run       # 実際には何も変更せず、同期される内容だけ確認
#
# 事前準備:
#   1. Local WP の管理画面で Simply Static プラグインを有効化する
#   2. Simply Static > Settings > General で
#        Delivery Method: Local Directory
#        Local Directory: 下記 SOURCE_DIR と同じパスを指定
#      にしておく(初回は下記デフォルトのままでOK)
#   3. Simply Static > Generate で静的サイトを書き出す

set -euo pipefail

# ---- 設定 (環境に合わせて変更してください) ----------------------------------
# Simply Static のエクスポート先 (Local WP の chocolamp サイト内)
SOURCE_DIR="${SOURCE_DIR:-$HOME/Local Sites/chocolamp/app/public/wp-content/uploads/simply-static/generated-files}"

# このリポジトリのルート (deploy.sh が置かれている場所)
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# push するブランチ
BRANCH="main"
# -----------------------------------------------------------------------------

DRY_RUN=false
if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=true
fi

if [[ ! -d "$SOURCE_DIR" ]]; then
  echo "エラー: エクスポート元フォルダが見つかりません: $SOURCE_DIR" >&2
  echo "Simply Static で静的サイトを Generate し、出力先を確認してください。" >&2
  exit 1
fi

echo "==> 同期元: $SOURCE_DIR"
echo "==> 同期先: $REPO_DIR"

RSYNC_OPTS=(-a --delete --exclude ".git" --exclude "deploy.sh" --exclude "README.md")
if $DRY_RUN; then
  RSYNC_OPTS+=(--dry-run -v)
fi

rsync "${RSYNC_OPTS[@]}" "$SOURCE_DIR"/ "$REPO_DIR"/

if $DRY_RUN; then
  echo "==> dry-run 完了。実際のファイルは変更していません。"
  exit 0
fi

cd "$REPO_DIR"

if [[ -z "$(git status --porcelain)" ]]; then
  echo "==> 変更なし。コミット/プッシュはスキップします。"
  exit 0
fi

git add -A

COMMIT_MSG="Deploy: $(date '+%Y-%m-%d %H:%M:%S')"
git commit -m "$COMMIT_MSG"

echo "==> $BRANCH ブランチへ push します..."
git push origin "$BRANCH"

echo "==> 完了。Vercel が自動でビルド/デプロイを開始します。"
