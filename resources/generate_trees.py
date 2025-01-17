import os
from typing import Set, Any, Tuple, NamedTuple, Literal, Union

from nbtlib import nbt
from nbtlib.tag import String as StringTag, Int as IntTag

Tree = NamedTuple('Tree', name=str, feature=Literal['random', 'overlay', 'stacked'], variant=str, count=Union[int, Tuple[int, ...]])
NORMAL_TREES = [
    Tree('acacia', 'random', 'acacia', 35),
    Tree('ash', 'overlay', 'normal', 0),
    Tree('aspen', 'random', 'aspen', 16),
    Tree('birch', 'random', 'aspen', 16),
    Tree('blackwood', 'random', 'blackwood', 10),
    Tree('chestnut', 'overlay', 'normal', 0),
    Tree('douglas_fir', 'random', 'fir', 9),
    Tree('hickory', 'random', 'fir', 9),
    Tree('kapok', 'random', 'jungle', 17),
    Tree('maple', 'overlay', 'normal', 0),
    Tree('oak', 'overlay', 'tall', 0),
    Tree('palm', 'random', 'tropical', 7),
    Tree('pine', 'random', 'fir', 9),
    Tree('rosewood', 'overlay', 'tall', 0),
    Tree('sequoia', 'random', 'conifer', 9),
    Tree('spruce', 'random', 'conifer', 9),
    Tree('sycamore', 'overlay', 'normal', 0),
    Tree('white_cedar', 'overlay', 'white_cedar', 0),
    Tree('willow', 'random', 'willow', 7),
]

LARGE_TREES = [
    Tree('acacia', 'random', 'kapok_large', 6),
    Tree('ash', 'random', 'normal_large', 5),
    Tree('blackwood', 'random', 'blackwood_large', 10),
    Tree('chestnut', 'random', 'normal_large', 5),
    Tree('douglas_fir', 'random', 'fir_large', 5),
    Tree('hickory', 'random', 'fir_large', 5),
    Tree('maple', 'random', 'normal_large', 5),
    Tree('pine', 'random', 'fir_large', 5),
    Tree('sequoia', 'stacked', 'conifer_large', (3, 3, 3)),
    Tree('spruce', 'stacked', 'conifer_large', (3, 3, 3)),
    Tree('sycamore', 'random', 'normal_large', 5),
    Tree('white_cedar', 'overlay', 'tall', 0),
    Tree('willow', 'random', 'willow_large', 14)
]


class Count:  # global mutable variables that doesn't require using the word "global" :)
    SKIPPED = 0
    NEW = 0
    MODIFIED = 0
    ERRORS = 0


def main():
    print('Tree sapling drop chances:')
    for tree in NORMAL_TREES:
        analyze_tree_leaves(tree)

    print('Making tree structures')
    for tree in NORMAL_TREES:
        make_tree_structures(tree, False)

    for tree in LARGE_TREES:
        make_tree_structures(tree, True)

    print('New = %d, Modified = %d, Unchanged = %d, Errors = %d' % (Count.NEW, Count.MODIFIED, Count.SKIPPED, Count.ERRORS))


def make_tree_structures(tree: Tree, large: bool):
    result = tree.name + '_large' if large else tree.name
    if tree.feature == 'random':
        for i in range(1, 1 + tree.count):
            make_tree_structure(tree.variant + str(i), tree.name, str(i), result)
    elif tree.feature == 'overlay':
        make_tree_structure(tree.variant, tree.name, 'base', result)
        make_tree_structure(tree.variant + '_overlay', tree.name, 'overlay', result)
    elif tree.feature == 'stacked':
        for j, c in zip(range(1, 1 + len(tree.count)), tree.count):
            for i in range(1, 1 + c):
                make_tree_structure('%s_layer%d_%d' % (tree.variant, j, i), tree.name, 'layer%d_%d' % (j, i), result)


def make_tree_structure(template: str, wood: str, dest: str, wood_dir: str):
    f = nbt.load('./structure_templates/%s.nbt' % template)
    for block in f['palette']:
        if block['Name'] == 'minecraft:oak_log':
            block['Name'] = StringTag('tfc:wood/log/%s' % wood)
            block['Properties']['natural'] = StringTag('true')
        elif block['Name'] == 'minecraft:oak_wood':
            block['Name'] = StringTag('tfc:wood/wood/%s' % wood)
            block['Properties']['natural'] = StringTag('true')
        elif block['Name'] == 'minecraft:oak_leaves':
            block['Name'] = StringTag('tfc:wood/leaves/%s' % wood)
            block['Properties']['persistent'] = StringTag('false')
        else:
            print('Structure: %s has an invalid block state \'%s\'' % (template, block['Name']))

    # Hack the data version, to avoid needing to run DFU on anything
    f['DataVersion'] = IntTag(2865)

    result_dir = '../src/main/resources/data/tfc/structures/%s/' % wood_dir
    os.makedirs(result_dir, exist_ok=True)

    file_name = result_dir + dest + '.nbt'
    try:
        if os.path.isfile(file_name):
            # Load and diff the original file - do not overwrite if source identical to avoid unnecessary git diffs due to gzip inconsistencies.
            original = nbt.load(file_name)
            if original == f:
                Count.SKIPPED += 1
                return
            else:
                Count.MODIFIED += 1
        else:
            Count.NEW += 1
        f.save(result_dir + dest + '.nbt')
    except:
        Count.ERRORS += 1


def analyze_tree_leaves(tree: Tree):
    if tree.feature == 'random':
        leaves = count_leaves_in_random_tree(tree.variant, tree.count)
    elif tree.feature == 'overlay':
        leaves = count_leaves_in_overlay_tree(tree.variant)
    else:
        raise NotImplementedError

    # Every tree results in 2.5 saplings, on average, if every leaf was broken
    print('%s: %.4f,' % (repr(tree.name), 2.5 / leaves))


def count_leaves_in_random_tree(base_name: str, count: int) -> float:
    counts = [count_leaves_in_structure(base_name + str(i)) for i in range(1, 1 + count)]
    return sum(counts) / len(counts)


def count_leaves_in_overlay_tree(base_name: str) -> float:
    base = nbt.load('./structure_templates/%s.nbt' % base_name)
    overlay = nbt.load('./structure_templates/%s_overlay.nbt' % base_name)

    base_leaves = leaf_ids(base)
    leaves = set(pos_key(block) for block in base['blocks'] if block['state'] in base_leaves)
    count = len(leaves)

    for block in overlay['blocks']:
        if block['state'] in base_leaves and pos_key(block) not in leaves:
            count += 0.5
        elif pos_key(block) in leaves:
            count -= 0.5

    return count


def count_leaves_in_structure(file_name: str):
    file = nbt.load('./structure_templates/%s.nbt' % file_name)
    leaves = leaf_ids(file)
    return sum(block['state'] in leaves for block in file['blocks'])


def leaf_ids(file: nbt.File) -> Set[int]:
    return {i for i, block in enumerate(file['palette']) if block['Name'] == 'minecraft:oak_leaves'}


def pos_key(tag: Any) -> Tuple[int, int, int]:
    pos = tag['pos']
    return int(pos[0]), int(pos[1]), int(pos[2])


if __name__ == '__main__':
    main()
