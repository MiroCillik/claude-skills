# Addressing Review Comments on Your PR

Every comment from a person gets an answer, including nits and comments on outdated lines. Replies use the Comment Shape from `SKILL.md`.

1. List what needs an answer:
   ```bash
   bash <this skill dir>/scripts/collect-comments.sh <PR URL>
   ```
   It skips resolved threads, threads where you wrote last, and bot comments. A `SELF` item is your own thread or review body (usually a self-review finding); answer it like the others. A review body that only approves or says LGTM needs no answer.
2. For each one, check that it is correct before acting on it. **REQUIRED SUB-SKILL:** superpowers:receiving-code-review
3. Then do one of these:
   - **Fix it.** If the comment is about behavior (a bug, a missing check, a setting that does not work), first write a test that fails because of the problem, then fix it and run the test. Reply with a short note and the commit SHA only after the test passes. **REQUIRED SUB-SKILL:** superpowers:test-driven-development
   - **Disagree**, then reply with one line saying why, plus bullets with the facts.
   - **Defer it**, then reply with where it will be handled. The reply may name the follow-up ticket; the code gets no TODO with the ticket ID.
4. Draft the replies and show them to the user. After they confirm, push the fixes and post the replies: inside each inline thread (the script prints the command), and one conversation comment for review bodies and conversation comments.
5. Run the script again. You are done when it lists no threads, and each review body or conversation comment you had to answer is marked "you commented after this".
