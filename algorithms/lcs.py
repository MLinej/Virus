"""
Longest Common Subsequence (LCS) — bottom-up Dynamic Programming.

Recurrence (dp[i][j] = LCS length of A[:i] and B[:j]):

    dp[i][j] = 0                                   if i == 0 or j == 0
             = dp[i-1][j-1] + 1                    if A[i-1] == B[j-1]
             = max(dp[i-1][j], dp[i][j-1])         otherwise

Where it is used: measuring how much genetic material two virus variants
share. ``similarity = LCS / max(len(A), len(B))``.

Complexity: O(n * m) time, O(n * m) space for the full table (needed for the
traceback that recovers the actual subsequence).
"""


def lcs_table(a, b):
    """Build the full (len(a)+1) x (len(b)+1) DP table."""
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp


def lcs_length(a, b):
    return lcs_table(a, b)[len(a)][len(b)]


def lcs_string(a, b, dp=None):
    """Recover one LCS by tracing back through the DP table."""
    dp = dp or lcs_table(a, b)
    i, j = len(a), len(b)
    out = []
    while i > 0 and j > 0:
        if a[i - 1] == b[j - 1]:
            out.append(a[i - 1])
            i -= 1
            j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    return "".join(reversed(out))


def lcs_similarity(a, b):
    """LCS length divided by the longer sequence length (0..1)."""
    if not a and not b:
        return 1.0
    return lcs_length(a, b) / max(len(a), len(b))
