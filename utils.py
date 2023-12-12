from copy import deepcopy
from typing import Dict, List, Set


class Knowledge:
    def __init__(self, dependency: set[tuple[int, int]], bombs: int) -> None:
        self.dependency = dependency
        self.bomb_count = bombs

    def remove_bomb(self, bomb: tuple[int, int]):
        if bomb not in self.dependency:
            return

        self.dependency.remove(bomb)
        self.bomb_count -= 1

    def evaluate(self, model: Dict) -> bool:
        count = 0
        for c in self.dependency:
            count += model[c]

        return count == self.bomb_count

    def remove_safe(self, safe: tuple[int, int]):
        if safe not in self.dependency:
            return

        self.dependency.remove(safe)

    def add_nodes(self, node: tuple[int, int]):
        # only used for bucket_coordinate
        self.dependency.add(node)


def factorial(n):
    total = 1
    for i in range(1, n + 1):
        total = total * i

    return total


def nCr(n, r):
    if r < 0 or r > n:
        raise Exception("r < 0 or r > n")

    num = factorial(n)
    deno = factorial(n - r) * factorial(r)

    return num / deno


def bucket_combinations(
    bucket: List[Knowledge],
    dependency: Set[tuple[int, int]],
    model: Dict[tuple[int, int], int],
    count: Dict[tuple[int, int], int],
    total: Dict[str, int],
):
    if len(dependency) == 0:
        model_consistent = True

        for k in bucket:
            if k.evaluate(model) == False:
                model_consistent = False
                break

        if model_consistent == True:
            total["total"] += 1
            for key in count:
                count[key] += model[key]

        return
    else:
        copied_dependency = deepcopy(dependency)
        elem = copied_dependency.pop()

        copied_model1 = deepcopy(model)
        copied_model1[elem] = 1
        bucket_combinations(bucket, copied_dependency, copied_model1, count, total)

        copied_model2 = deepcopy(model)
        copied_model2[elem] = 0
        bucket_combinations(bucket, copied_dependency, copied_model2, count, total)

        return


def new_bucket_coordinate(buckets: List[List[Knowledge]]):
    new_bucket_coordinate_list = list()

    for b in range(len(buckets)):
        temp = set([d for k in buckets[b] for d in k.dependency])
        new_bucket_coordinate_list.append(Knowledge(temp, b))

    return new_bucket_coordinate_list


def combine_buckets(buckets: List[List[Knowledge]]):
    new_buckets = []
    length = len(buckets)

    for i in range(length - 1):
        for j in range(i + 1, length):
            temp1 = set([d for k in buckets[i] for d in k.dependency])
            temp2 = set([d for k in buckets[j] for d in k.dependency])

            if len(temp1.intersection(temp2)) != 0:
                new_buckets.append(buckets[i] + buckets[j])

    if len(new_buckets) != 0:
        return combine_buckets(new_buckets)
    else:
        return buckets
