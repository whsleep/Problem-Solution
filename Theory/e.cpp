// 从长度为 2 开始计算
for (int L = 2; L <= n; ++L)
{
    for (int i = 0; i <= n - L; i++)
    {
        int j = i + L - 1; // 计算右边界

        if (s[i] != s[j])
        {
            dp[i][j] = false;
#if DEBUG
            printf("--当前为 [%d,%d] 直接false即可\n", i, j);
            dis_dp(dp);
#endif
        }
        else
        {
#if DEBUG
            printf("当前为 [%d,%d] 需要判断 [%d,%d]\n", i, j, i + 1, j - 1);
            dis_dp(dp);
#endif
            // 根据子串长度处理,子串长度为2，且字符内容相同
            if (L <= 3)
            {
                dp[i][j] = true;
            }
            else
            {
                dp[i][j] = dp[i + 1][j - 1]; // 状态转移
            }
        }

        // 更新最长回文子串记录
        if (dp[i][j] && L > len)
        {
            len = L;
            begin = i;
        }
    }
}