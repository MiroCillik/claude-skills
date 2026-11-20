#!/usr/bin/env bash
# Usage: bash collect-comments.sh <PR URL | owner/repo#number>
# Lists the review comments on a PR that still need an answer from you.
set -euo pipefail

ref="${1:?Usage: collect-comments.sh <PR URL | owner/repo#number>}"
if [[ "$ref" =~ github\.com/([^/]+)/([^/]+)/pull/([0-9]+) ]] || [[ "$ref" =~ ^([^/]+)/([^#]+)#([0-9]+)$ ]]; then
  owner=${BASH_REMATCH[1]}; repo=${BASH_REMATCH[2]}; number=${BASH_REMATCH[3]}
else
  echo "Cannot read the PR reference: $ref" >&2
  exit 1
fi

me=$(gh api user --jq .login)

query='query($o:String!,$r:String!,$n:Int!){repository(owner:$o,name:$r){pullRequest(number:$n){
  reviewThreads(first:100){nodes{isResolved isOutdated path line originalLine
    comments(first:100){nodes{databaseId author{login __typename} body}}}}
  reviews(first:100){nodes{author{login __typename} state body submittedAt}}
  comments(first:100){nodes{author{login __typename} body createdAt}}}}}'

gh api graphql -F o="$owner" -F r="$repo" -F n="$number" -f query="$query" \
| jq -r --arg me "$me" --arg pr "$owner/$repo#$number" --arg api "repos/$owner/$repo/pulls/$number" '
  def bot: . != null and (.__typename == "Bot" or (.login | test("bot$"; "i")));
  def indent: split("\n") | map("    " + .) | join("\n");
  def after($t; $last): if $last != null and $last > $t then " (you commented after this)" else "" end;

  .data.repository.pullRequest as $p
  | ([$p.comments.nodes[] | select(.author.login == $me) | .createdAt] | max) as $myLast
  | [$p.reviewThreads.nodes[]
      | select((.isResolved | not) and (.comments.nodes[0].author | bot | not))
      | . + {status: (if .comments.nodes[-1].author.login != $me then "OPEN"
                      elif (.comments.nodes | length) == 1 then "SELF"
                      else "REPLIED" end)}] as $threads
  | [$p.reviews.nodes[] | select((.body | length) > 0 and (.author | bot | not))] as $reviews
  | [$p.comments.nodes[] | select(.author.login != $me and (.author | bot | not))] as $conv

  | "PR \($pr), you are \($me)", "",
    "== Inline threads to answer",
    ( $threads[] | select(.status != "REPLIED")
      | "[\(.status)] \(.path):\(.line // .originalLine)\(if .isOutdated then " (outdated)" else "" end), reply to comment \(.comments.nodes[0].databaseId)",
        (.comments.nodes[] | "  \(.author.login):", (.body | indent)),
        "" ),
    "== Review bodies",
    ( $reviews[] | "[\(.state)\(if .author.login == $me then ", SELF" else "" end)] \(.author.login) \(.submittedAt[:10])\(after(.submittedAt; $myLast))", (.body | indent), "" ),
    "== Conversation comments",
    ( $conv[] | "\(.author.login) \(.createdAt[:10])\(after(.createdAt; $myLast))", (.body | indent), "" ),
    "== Count",
    "threads: \([$threads[] | select(.status == "OPEN")] | length) OPEN (someone else wrote last), \([$threads[] | select(.status == "SELF")] | length) SELF (only your comment), \([$threads[] | select(.status == "REPLIED")] | length) already replied (not listed)",
    "review bodies: \($reviews | length), \([$reviews[] | select(.author.login == $me)] | length) of them SELF (an APPROVED one needs an answer only if it asks for something)",
    "conversation comments: \($conv | length)",
    "skipped: \([$p.reviewThreads.nodes[] | select(.isResolved)] | length) resolved threads, all bot comments",
    "",
    "Reply in a thread: gh api \($api)/comments/<comment id>/replies -f body=\"...\""
'
