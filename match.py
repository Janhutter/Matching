from collections import defaultdict, deque
import pandas as pd 

def hopcroft_karp(graph, left_nodes):
    """
    Standard Hopcroft–Karp algorithm for maximum bipartite matching.
    `graph` should be a dict mapping each left node to a list of right nodes.
    `left_nodes` is the iterable of nodes on the left side.
    Returns a dictionary `match_left` mapping left node -> matched right node.
    """
    INF = float('inf')
    match_left = {}   # left_node -> right_node
    match_right = {}  # right_node -> left_node
    dist = {}

    def bfs():
        queue = deque()
        for u in left_nodes:
            if u not in match_left:
                dist[u] = 0
                queue.append(u)
            else:
                dist[u] = INF
        dist[None] = INF
        while queue:
            u = queue.popleft()
            if dist[u] < dist[None]:
                for v in graph[u]:
                    u_prime = match_right.get(v, None)
                    if dist.get(u_prime, INF) == INF:
                        dist[u_prime] = dist[u] + 1
                        queue.append(u_prime)
        return dist[None] != INF

    def dfs(u):
        if u is not None:
            for v in graph[u]:
                u_prime = match_right.get(v, None)
                if dist.get(u_prime, INF) == dist[u] + 1 and dfs(u_prime):
                    match_left[u] = v
                    match_right[v] = u
                    return True
            dist[u] = INF
            return False
        return True

    matching_size = 0
    while bfs():
        for u in left_nodes:
            if u not in match_left:
                if dfs(u):
                    matching_size += 1

    return match_left

def match_student_pairs(students_info):
    """
    Given a list of student records, each as a tuple:
      (student_id, current_group, desired_group, accept_teammate_swap, teammate_student_id)
    returns a list of matched pairs (as tuples (student1, student2)) that satisfy:
      - student1.current_group == desired_group of student2
      - student2.current_group == desired_group of student1
      - If a student is not flexible (accept_teammate_swap==False), then they only match with
        the specific student indicated in teammate_student_id.
      
    Students who already have current_group == desired_group are skipped.
    
    The matching is done separately for each pair of groups (A,B) where swaps are possible.
    """
    # Partition students by the (current_group, desired_group) pair.
    # Only consider students who actually need a swap.
    swaps = defaultdict(list)  # key: (current_group, desired_group) -> list of student records
    student_lookup = {}  # so that we can quickly look up a student by id
    for record in students_info:
        student_id, current_group, desired_group, accept_swap, teammate_id = record
        student_lookup[student_id] = record
        if current_group == desired_group:
            # Already in desired group, no swap needed.
            continue
        swaps[(current_group, desired_group)].append(record)

    # The valid pair swap can only happen between a student from group A wanting B and a student from B wanting A.
    paired_matches = []
    
    # Process each group pair (A,B) and its reverse (B,A).
    # To avoid double processing, we can iterate over keys and only handle when current_group < desired_group (lexicographically)
    processed_pairs = set()
    for (group_A, group_B) in list(swaps.keys()):
        if (group_A, group_B) in processed_pairs:
            continue  # already handled
        reverse_key = (group_B, group_A)
        # Only proceed if the reverse exists; otherwise, no valid swap partner exists.
        if reverse_key not in swaps:
            processed_pairs.add((group_A, group_B))
            continue
        # U: students from group_A wanting group_B.
        # V: students from group_B wanting group_A.
        U = swaps[(group_A, group_B)]
        V = swaps[reverse_key]
        # Build the bipartite graph from U (left) to V (right).
        graph = defaultdict(list)
        left_ids = []  # we'll store student_ids for the left side
        for record_i in U:
            student_i, cur_i, des_i, accept_i, teammate_i = record_i
            left_ids.append(student_i)
            # For each candidate in V, add an edge if the swap is allowed.
            for record_j in V:
                student_j, cur_j, des_j, accept_j, teammate_j = record_j
                # Check that the group conditions are automatically met by construction:
                #    des_i (B) == cur_j (B) and des_j (A) == cur_i (A).
                # Now check the teammate swap restrictions.
                valid = True
                # If student_i is not flexible, they require student_j to be their designated teammate.
                if not accept_i and teammate_i != student_j:
                    valid = False
                # Similarly, if student_j is not flexible, they require student_i.
                if not accept_j and teammate_j != student_i:
                    valid = False
                if valid:
                    graph[student_i].append(student_j)
        # Only attempt a matching if there is at least one left node.
        if not left_ids:
            processed_pairs.add((group_A, group_B))
            processed_pairs.add((group_B, group_A))
            continue

        # Run Hopcroft-Karp to find the maximum matching.
        match_left = hopcroft_karp(graph, left_ids)
        # Each edge in match_left is a pairing: student_i (from U) matched with student_j (from V).
        for student_i, student_j in match_left.items():
            # Record the pair (we can sort the tuple so that order is consistent)
            paired = tuple(sorted([student_i, student_j]))
            paired_matches.append(paired)
        # Mark these group pairs as processed.
        processed_pairs.add((group_A, group_B))
        processed_pairs.add((group_B, group_A))
    
    return paired_matches

# -------------------------
# Example usage:
if __name__ == '__main__':
    # Example 1: Both students are flexible (accept_teammate_swap == True).
    #   - Alice (G1->G2) and Bob (G2->G1) can swap.
    # Example 2: Students with restricted partner choices.
    #   - Charlie (G1->G2) requires specifically Dave.
    #   - Dave (G2->G1) requires specifically Charlie.
    swappers = pd.read_csv('swappers.csv')
    students_info = []

    for i in range(len(swappers)):
        # swappers has same order as students_info, so we can get all values at once
        student_id, current_group, desired_group, accept_teammate_swap, teammate_student_id = swappers.iloc[i].values
        students_info.append((student_id, current_group, desired_group, accept_teammate_swap, teammate_student_id))

    
    
    matches = match_student_pairs(students_info)
    
    print("Matched pairs:")
    for pair in matches:
        print(pair)
