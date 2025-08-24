def Calc(current, target):
    # 计算所需经验值和套数
    total_exp = 0
    total_sets = 0

    for level in range(current, target):
        # 计算当前等级区间 (每10级一个区间)
        interval = level // 10
        # 每级需要的经验 = (区间数 + 1) * 100
        exp_per_level = (interval + 1) * 100
        total_exp += exp_per_level
        total_sets += interval + 1  # 每级需要的套数 = 区间数 + 1

    # 计算目标等级的好友上限
    # 1级有255个好友上限，每升一级增加5个
    friends_limit = 255 + (target - 1) * 5

    # 计算目标等级的展柜数
    # 每10级解锁一个展柜，最多19个
    showcase_count = min(target // 10, 19)

    return {
        "exp": total_exp,
        "sets": total_sets,
        "friends": friends_limit,
        "showcase": showcase_count,
    }
