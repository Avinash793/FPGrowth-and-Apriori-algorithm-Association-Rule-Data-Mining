import itertools
import time

#take input of file name and minimum support count
print("Enter the filename:")
filename = input()
print("Enter the minimum support count:")
min_support = int(input())

#read data from txt file
with open(filename) as f:
    content = f.readlines()

content = [x.strip() for x in content]

Transaction = []                  #to store transaction
Frequent_items_value = {}         #to store all frequent item sets

#to fill values in transaction from txt file
for i in range(0,len(content)):
    Transaction.append(content[i].split())

#function to get frequent one itemset
def frequent_one_item(Transaction,min_support):
    candidate1 = {}

    for i in range(0,len(Transaction)):
        for j in range(0,len(Transaction[i])):
            if Transaction[i][j] not in candidate1:
                candidate1[Transaction[i][j]] = 1
            else:
                candidate1[Transaction[i][j]] += 1

    frequentitem1 = []                      #to get frequent 1 itemsets with minimum support count
    for value in candidate1:
        if candidate1[value] >= min_support:
            frequentitem1 = frequentitem1 + [[value]]
            Frequent_items_value[tuple(value)] = candidate1[value]

    return frequentitem1

values = frequent_one_item(Transaction,min_support)
print(values)
print(Frequent_items_value)


# to remove infrequent 1 itemsets from transaction
Transaction1 = []
for i in range(0,len(Transaction)):
    list_val = []
    for j in range(0,len(Transaction[i])):
        if [Transaction[i][j]] in values:
            list_val.append(Transaction[i][j])
    Transaction1.append(list_val)


#class of Hash node
class Hash_node:
    def __init__(self):
        self.children = {}           #pointer to its children
        self.Leaf_status = True      #to know the status whether current node is leaf or not
        self.bucket = {}             #contains itemsets in bucket

#class of constructing and getting hashtree
class HashTree:
    # class constructor
    def __init__(self, max_leaf_count, max_child_count):
        self.root = Hash_node()
        self.max_leaf_count = max_leaf_count
        self.max_child_count = max_child_count
        self.frequent_itemsets = []

    # function to recursive insertion to make hashtree
    def recursively_insert(self, node, itemset, index, count):
        if index == len(itemset):
            if itemset in node.bucket:
                node.bucket[itemset] += count
            else:
                node.bucket[itemset] = count
            return

        if node.Leaf_status:                             #if node is leaf
            if itemset in node.bucket:
                node.bucket[itemset] += count
            else:
                node.bucket[itemset] = count
            if len(node.bucket) == self.max_leaf_count:  #if bucket capacity increases
                for old_itemset, old_count in node.bucket.items():

                    hash_key = self.hash_function(old_itemset[index])  #do hashing on next index
                    if hash_key not in node.children:
                        node.children[hash_key] = Hash_node()
                    self.recursively_insert(node.children[hash_key], old_itemset, index + 1, old_count)
                #since no more requirement of this bucket
                del node.bucket
                node.Leaf_status = False
        else:                                            #if node is not leaf
            hash_key = self.hash_function(itemset[index])
            if hash_key not in node.children:
                node.children[hash_key] = Hash_node()
            self.recursively_insert(node.children[hash_key], itemset, index + 1, count)

    def insert(self, itemset):
        itemset = tuple(itemset)
        self.recursively_insert(self.root, itemset, 0, 0)

    # to add support to candidate itemsets. Transverse the Tree and find the bucket in which this itemset is present.
    def add_support(self, itemset):
        Transverse_HNode = self.root
        itemset = tuple(itemset)
        index = 0
        while True:
            if Transverse_HNode.Leaf_status:
                if itemset in Transverse_HNode.bucket:    #found the itemset in this bucket
                    Transverse_HNode.bucket[itemset] += 1 #increment the count of this itemset.
                break
            hash_key = self.hash_function(itemset[index])
            if hash_key in Transverse_HNode.children:
                Transverse_HNode = Transverse_HNode.children[hash_key]
            else:
                break
            index += 1

    # to transverse the hashtree to get frequent itemsets with minimum support count
    def get_frequent_itemsets(self, node, support_count,frequent_itemsets):
        if node.Leaf_status:
            for key, value in node.bucket.items():
                if value >= support_count:                       #if it satisfies the condition
                    frequent_itemsets.append(list(key))          #then add it to frequent itemsets.
                    Frequent_items_value[key] = value
            return

        for child in node.children.values():
            self.get_frequent_itemsets(child, support_count,frequent_itemsets)

    # hash function for making HashTree
    def hash_function(self, val):
        return int(val) % self.max_child_count

#To generate hash tree from candidate itemsets
def generate_hash_tree(candidate_itemsets, max_leaf_count, max_child_count):
    htree = HashTree(max_child_count, max_leaf_count)             #create instance of HashTree
    for itemset in candidate_itemsets:
        htree.insert(itemset)                                     #to insert itemset into Hashtree
    return htree

#to generate subsets of itemsets of size k
def generate_k_subsets(dataset, length):
    subsets = []
    for itemset in dataset:
        subsets.extend(map(list, itertools.combinations(itemset, length)))
    return subsets

def subset_generation(ck_data,l):
    return map(list,set(itertools.combinations(ck_data,l)))

#apriori generate function to generate ck
def apriori_generate(dataset,k):
    ck = []
    #join step
    lenlk = len(dataset)
    for i in range(lenlk):
        for j in range(i+1,lenlk):
            L1 = list(dataset[i])[:k - 2]
            L2 = list(dataset[j])[:k - 2]
            if L1 == L2:
                ck.append(sorted(list(set(dataset[i]) | set(dataset[j]))))

    #prune step
    final_ck = []
    for candidate in ck:
        all_subsets = list(subset_generation(set(candidate), k - 1))
        found = True
        for i in range(len(all_subsets)):
            value = list(sorted(all_subsets[i]))
            if value not in dataset:
                found = False
        if found == True:
            final_ck.append(candidate)

    return ck,final_ck

def generateL(ck,min_support):
    support_ck = {}
    for val in Transaction1:
        for val1 in ck:
            value = set(val)
            value1 = set(val1)

            if value1.issubset(value):
                if tuple(val1) not in support_ck:
                    support_ck[tuple(val1)] = 1
                else:
                    support_ck[tuple(val1)] += 1
    frequent_item = []
    for item_set in support_ck:
        if support_ck[item_set] >= min_support:
            frequent_item.append(sorted(list(item_set)))
            Frequent_items_value[item_set] = support_ck[item_set]

    return frequent_item

# main apriori algorithm function
def apriori(L1,min_support):
    k = 2;
    L = []
    L.append(0)
    L.append(L1)
    print("enter max_leaf_count")              #maximum number of items in bucket i.e. bucket capacity of each node
    max_leaf_count = int(input())
    print("enter max_child_count")             #maximum number of child you want for a node
    max_child_count = int(input())

    start = time.time()
    while(len(L[k-1])>0):
        ck,final_ck = apriori_generate(L[k-1],k)                 #to generate candidate itemsets
        print("C%d" %(k))
        print(final_ck)
        h_tree = generate_hash_tree(ck,max_leaf_count,max_child_count)       #to generate hashtree
        if (k > 2):
            while(len(L[k-1])>0):
                l = generateL(final_ck, min_support)
                L.append(l)
                print("Frequent %d item" % (k))
                print(l)
                k = k + 1
                ck, final_ck = apriori_generate(L[k - 1], k)
                print("C%d" % (k))
                print(final_ck)
            break
        k_subsets = generate_k_subsets(Transaction1,k)                  #to generate subsets of each transaction
        for subset in k_subsets:
            h_tree.add_support(subset)                                  #to add support count to itemsets in hashtree
        lk = []
        h_tree.get_frequent_itemsets(h_tree.root,min_support,lk)                  #to get frequent itemsets
        print("Frequent %d item" %(k))
        print(lk)
        L.append(lk)
        k = k + 1
    end = time.time()
    return L,(end-start)


L_value,time_taken = apriori(values,min_support)
print("Time Taken is:")
print(time_taken)
#print("final L_value")
#print(L_value)
print("All frequent itemsets with their support count:")
print(Frequent_items_value)