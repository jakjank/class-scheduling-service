# Algorithms

The service offers 4 scheduling algorithms. Each is shortly described below.

## Probabilistic algorithm

`Set method field to 'probabilistic_alg' to use this algorithm`

The simples algorithm implemented in the service. It is the base of other ones.
The way it works is presented by below pseudocode:

**Input:**  
- An object of class **Problem** `P`

**Output:**  
- A list of assignments **result**

```
1. Initialize `rs` ← assignments defined by the user  
2. Initialize `gs` ← groups without assignments in `rs`

3. While `gs` is not empty:
   1. Select and remove a random group `g` from `gs`
   2. Let `xs` ← all assignments of `g` that satisfy the constraints of `P`
   3. If `xs` is empty:
      - Return **fail**
   4. Select a random element `x` from `xs`
   5. Update the constraints in `P` to account for `x`
   6. Add `x` to `rs`

4. Return `rs`
```

Let's imagine a situation where one group in **P** has only one possible assignment, while another has many. Both groups have the same lecturer. If the second group is chosen first to find its assignment, it is possible that it will be chosen with a term that conflicts with the first group's only assignment. In such a situation, we will not find a solution even though it exists. This problem is addressed by the next algorithm.

## Group Sorting Algorithm

`Set method field to 'ordered_groups_alg' to use this algorithm`

In this algorithm, instead of randomly selecting groups for which we're searching for assignments, we select them sequentially from a list sorted in descending order of difficulty. What does it mean that it's difficult to find a matching term for a group? The heuristic used here means that a difficult group has few possible assignments or that one of the groups it's clustered with has few assignments. The algorithm can be described as follows:

**Input:**  
- An object of class **Problem** `P`

**Output:**  
- A list of assignments **result**

```
1. Initialize `rs` ← assignments defined by the user  
2. Initialize `gs` ← groups without assignments in `rs`

3. Sort `gs` in descending order by group difficulty

4. While `gs` is not empty:
   1. Take and remove the first group `g` from `gs`
   2. Let `xs` ← all assignments of `g` that satisfy the constraints of `P`
   3. If `xs` is empty:
      - Return **fail**
   4. Select a random element `x` from `xs`
   5. Update the constraints in `P` to account for `x`
   6. Add `x` to `rs`

5. Return `rs`
```

Of course, assigning one group may, and almost certainly will, result in the lack of assignment to other groups. This leads to the next algorithm.

## Deep Group Sorting Algorithm

`Set method field to 'deep_ordered_groups_alg' to use this algorithm`

It differs from the above only in that the groups are sorted after each assignment.

Pseudocode:

**Input:**  
- An object of class **Problem** `P`

**Output:**  
- A list of assignments **result**
```
1. Initialize `rs` ← assignments defined by the user  
2. Initialize `gs` ← groups without assignments in `rs`

3. Sort `gs` in descending order by group difficulty

4. While `gs` is not empty:
   1. Take and remove the first group `g` from `gs`
   2. Let `xs` ← all assignments of `g` that satisfy the constraints of `P`
   3. If `xs` is empty:
      - Return **fail**
   4. Select a random element `x` from `xs`
   5. Update the constraints in `P` to account for `x`
   6. Add `x` to `rs`
   7. Sort `gs` in descending order by group difficulty

5. Return `rs`
```

## Algorithm with Rating Function

`Set method field to 'rating_function_alg' to use this algorithm`

When selecting assignments, the algorithm with a grading function takes into account the expected characteristics of the schedule being created. We favor, for example, even-numbered class starts, a small number of empty chairs in the classroom, and days without classes for lecturers. This algorithm is a modification of the arranged-group algorithm and is described in the following pseudocode:

**Input:**  
- An object of class **Problem** `P`  
- A timetable evaluation function `F`

**Output:**  
- A list of assignments `rs`

```
1. Initialize `rs` ← assignments defined by the user  
2. Initialize `gs` ← groups without assignments in `rs`

3. Sort `gs` in descending order by group difficulty

4. While `gs` is not empty:
   1. Take and remove the first group `g` from `gs`
   2. Let `xs` ← all assignments of `g` that satisfy the constraints of `P`
   3. If `xs` is empty:
      - Return **fail**
   4. Select the element `x` from `xs` that maximizes `F`
   5. Update the constraints in `P` to account for `x`
   6. Add `x` to `rs`

5. Return `rs`
```