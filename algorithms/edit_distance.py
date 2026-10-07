"""
Levenshtein Edit Distance — bottom-up Dynamic Programming.

dp[i][j] = minimum number of insertions, deletions and substitutions needed
to turn A[:i] into B[:j]:

    dp[i][0] = i,  dp[0][j] = j
    dp[i][j] = dp[i-1][j-1]                         if A[i-1] == B[j-1]
             = 1 + min(dp[i-1][j],     # delete A[i-1]
                       dp[i][j-1],     # insert B[j-1]
                       dp[i-1][j-1])   # substitute A[i-1] -> B[j-1]

Where it is used: the "mutation distance" between two virus variants.

Complexity: O(n * m) time, O(n * m) space (full table kept for traceback).
"""


def edit_distance_table(a, b):
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        dp[i][0] = i
    for j in range(m + 1):
        dp[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])
    return dp


def edit_distance(a, b):
    return edit_distance_table(a, b)[len(a)][len(b)]


def edit_operations(a, b, dp=None):
    """Trace back one optimal edit script.

    Returns a list of tuples ``(op, char_a, char_b)`` where op is one of
    'match', 'sub', 'del', 'ins'. Useful for drawing an alignment.
    """
    dp = dp or edit_distance_table(a, b)
    i, j = len(a), len(b)
    ops = []
    while i > 0 or j > 0:
        if i > 0 and j > 0 and a[i - 1] == b[j - 1] and dp[i][j] == dp[i - 1][j - 1]:
            ops.append(("match", a[i - 1], b[j - 1]))
            i, j = i - 1, j - 1
        elif i > 0 and j > 0 and dp[i][j] == dp[i - 1][j - 1] + 1:
            ops.append(("sub", a[i - 1], b[j - 1]))
            i, j = i - 1, j - 1
        elif i > 0 and dp[i][j] == dp[i - 1][j] + 1:
            ops.append(("del", a[i - 1], "-"))
            i -= 1
        else:
            ops.append(("ins", "-", b[j - 1]))
            j -= 1
    ops.reverse()
    return ops
