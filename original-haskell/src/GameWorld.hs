module GameWorld where

import Types
import Utils (msort)

connected :: Map -> Node -> [Node]
connected m n = reverse (go m n [])
  where
    go :: Map -> Node -> [Node] -> [Node]
    go [] _ acc = acc
    go ((n1, n2) : xs) node acc
      | n1 == node = go xs node (n2 : acc)
      | n2 == node = go xs node (n1 : acc)
      | otherwise = go xs node acc

connect :: Node -> Node -> Map -> Map
connect n1 n2 m
  | n1 == n2 = m
  | elem pair m = m
  | otherwise = msort (pair : m)
  where
    pair = (min n1 n2, max n1 n2)

disconnect :: Node -> Node -> Map -> Map
disconnect a b m = filter (\(c, d) -> (c, d) /= (min a b, max a b)) m

add :: Party -> Event
add _ Over = Over
add p (Game m loc party npcs) =
  Game m loc (msort (party ++ p)) npcs

addAt :: Node -> Party -> Event
addAt _ _ Over = Over
addAt n p (Game m loc party npcs) =
  Game m loc party (go n npcs)
  where
    go :: Node -> [Party] -> [Party]
    go _ [] = []
    go 0 (x : xs) = msort (x ++ p) : xs
    go i (x : xs) = (x : go (i - 1) xs)

addHere :: Party -> Event
addHere _ Over = Over
addHere p g@(Game _ loc _ _) = addAt loc p g

remove :: Party -> Event
remove _ Over = Over
remove p (Game m loc party npcs) =
  Game m loc (filter (`notElem` p) party) npcs

removeAt :: Node -> Party -> Event
removeAt _ _ Over = Over
removeAt n p (Game m loc party npcs) =
  Game m loc party (go n npcs)
  where
    go :: Node -> [Party] -> [Party]
    go _ [] = []
    go 0 (x : xs) = ((filter (`notElem` p) x) : xs)
    go i (x : xs) = (x : (go (i - 1) xs))

removeHere :: Party -> Event
removeHere _ Over = Over
removeHere p g@(Game _ loc _ _) = removeAt loc p g
