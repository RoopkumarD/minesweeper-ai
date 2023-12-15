from typing import Dict, List, Tuple


class Knowledge:
    def __init__(self, dependency: set[tuple[int, int]], bombs: int) -> None:
        self.dependency = dependency
        self.bomb_count = bombs

    def __repr__(self) -> str:
        return f"{self.dependency} = {self.bomb_count}"

    def remove_bomb(self, bomb: tuple[int, int]):
        if bomb not in self.dependency:
            return

        self.dependency.remove(bomb)
        self.bomb_count -= 1

        if self.bomb_count < 0:
            raise Exception("Got a -ve bomb_count")

    def evaluate(self, model: Dict) -> bool:
        count = 0
        for c in self.dependency:
            count += model[c]

        return count == self.bomb_count

    def remove_safe(self, safe: tuple[int, int]):
        if safe not in self.dependency:
            return

        self.dependency.remove(safe)


def possible_combinations(knowledge: Knowledge) -> List[Dict[Tuple[int, int], int]]:
    possible_states = list()
    initial = dict()
    for m in knowledge.dependency:
        initial[m] = 0
    possible_states.append(initial)

    for m in knowledge.dependency:
        for p in range(len(possible_states)):
            t = dict(possible_states[p])
            possible_states[p][m] = 0
            t[m] = 1
            possible_states.append(t)

    final_evaluation = list()
    for model in possible_states:
        if knowledge.evaluate(model) == True:
            final_evaluation.append(model)

    return final_evaluation


def combine_possibilities(
    base_possibility: List[Dict[Tuple[int, int], int]],
    new_possibility: List[Dict[Tuple[int, int], int]],
):
    if len(base_possibility) == 0:
        return new_possibility

    combined_possibility = list()

    for new_possible in new_possibility:
        for base in base_possibility:
            # print("Checking for base", base, "and new", new_possible)
            if len(set(new_possible.keys()).intersection(set(base.keys()))) != 0:
                # print("There are common elements")
                contradiction = False
                for key in new_possible:
                    if key in base and new_possible[key] != base[key]:
                        contradiction = True
                        break

                # print("contradiction", contradiction)
                if contradiction == False:
                    temp = dict()
                    for key in new_possible:
                        temp[key] = new_possible[key]

                    for key in base:
                        temp[key] = base[key]

                    combined_possibility.append(temp)
                    # print(combined_possibility, "after adding the new possible_state")
            else:
                # print("There is no common elements")
                temp = dict()
                for key in new_possible:
                    temp[key] = new_possible[key]

                for key in base:
                    temp[key] = base[key]

                combined_possibility.append(temp)
                # print(combined_possibility, "after adding the new possible_state")

    return combined_possibility


def bucket_probability(
    bucket: List[Knowledge],
) -> Tuple[Dict[Tuple[int, int], int], int]:
    # print("Bucket", bucket)
    combinations = list()

    for knowledge in bucket:
        # print(
        #     "Checking for this knowledge",
        #     knowledge,
        #     "Against this combinations",
        #     combinations,
        # )
        new_combinations = possible_combinations(knowledge)
        combinations = combine_possibilities(combinations, new_combinations)

    total = len(combinations)
    # print("combinations", combinations)
    for i in range(1, len(combinations)):
        for key in combinations[0]:
            combinations[0][key] = combinations[0][key] + combinations[i][key]

    return (combinations[0], total)


def create_buckets(knowledge_base: List[Knowledge]) -> List[List[Knowledge]]:
    buckets = []
    bucket_coordinate = dict()

    for knowledge in knowledge_base:
        i = -1

        for coordinate in knowledge.dependency:
            if coordinate in bucket_coordinate:
                i = bucket_coordinate[coordinate]
                break

        if i != -1:
            buckets[i].append(knowledge)
        else:
            buckets.append([knowledge])
            i = len(buckets) - 1

        for coordinate in knowledge.dependency:
            if coordinate not in bucket_coordinate:
                bucket_coordinate[coordinate] = i

    return buckets
