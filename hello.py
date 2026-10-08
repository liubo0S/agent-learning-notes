# 用 for 循环计算 1 加到 100 的总和，并打印结果。（提示：先设一个变量 total = 0，然后 for i in range(1, 101): total = total + i）

# 有一个列表 scores = [88, 92, 78, 60, 45, 73]，用 for 循环遍历它，并打印出及格（>=60）的分数和不及格的分数，格式如：88 及格、45 不及格。


# total = 0

total = sum(range(1,101))

print(total)


source = [88, 92, 78, 60, 45, 73]

for i in source:
    if(i >= 60):
        print(i,"及格")
    else :
        print(i,"不及格")

