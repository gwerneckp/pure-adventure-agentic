module Solver where

import Data.List (find, findIndex, subsequences)
import Data.Maybe (maybeToList)
import Dialogue (DialogueInput (..), DialogueStep (..), dialoguePure, findDialogue)
import GameData
import GameLoop (GameStep (..), StepInput (..), stepPure)
import GameWorld (connected)
import Types
import Utils (merge, msort)

talk :: Game -> Dialogue -> [(Game, [Int])]
talk g dlg = case dialoguePure g dlg DialogueNoInput of
  DoAction _ ev
    | ev g == g -> [] -- No state change, no commands
    | otherwise -> [(ev g, [])]
  NeedChoice _ dialogue@(Choice _ opts) ->
    concat
      [ case dialoguePure g dialogue (DialogueValidInput i) of
          DoAction _ ev -> [(ev g, [i])]
          NeedChoice _ dlg' -> [(g', i : path) | (g', path) <- talk g dlg']
          Exit -> []
          DeadEnd _ -> []
      | i <- [1 .. length opts]
      ]
  NeedChoice _ _ -> [] -- unreachable
  Exit -> [] -- unreachable
  DeadEnd _ -> []

select :: Game -> [Party]
select Over = []
select (Game _ node party partylevel) = partition merged
  where
    partition :: Party -> [Party]
    partition [] = [[]]
    partition (x : xs) =
      let ps = partition xs
       in ps ++ map (x :) ps

    merged
      | node < 0 || node >= length partylevel = msort party
      | otherwise =
          let currentChars = msort (partylevel !! node)
           in merge (msort party) currentChars

travel :: Map -> Node -> [(Node, [Int])]
travel m srcNode = bfs [(srcNode, [])] [] []
  where
    bfs :: [(Node, [Int])] -> [Node] -> [(Node, [Int])] -> [(Node, [Int])]
    bfs [] _ acc = acc
    bfs ((curr, path) : xs) visited acc
      | curr `elem` visited = bfs xs visited acc
      | otherwise =
          let visited' = curr : visited
              nbrs = connected m curr
              acc' = acc ++ [(curr, path)]
              nexts = [(nb, path ++ [i]) | (i, nb) <- zip [1 ..] nbrs, nb `notElem` visited'] -- We zip with [1..] to get 1-based indices which correspond to player choices
           in bfs (xs ++ nexts) visited' acc'

allSteps :: Game -> [(Solution, Game)]
allSteps Over = []
allSteps game@(Game m node party partylevel) = do
  (newNode, travelCmd) <- travel m node
  let travelGame = if newNode == node then game else Game m newNode party partylevel

  selectedParty <- filter (not . null) (select travelGame)

  let dialogue = findDialogue selectedParty
  (talkGame, cmds) <- talk travelGame dialogue

  return ([Travel travelCmd, Select selectedParty, Talk cmds], talkGame)

solve :: Game -> Solution
solve Over = []
solve g = case find ((/= g) . snd) (allSteps g) of
  Just (sol, g') -> sol ++ solve g'
  Nothing -> []

walkthrough :: IO ()
walkthrough = (putStrLn . unlines . filter (not . null) . map format . solve) start
  where
    format (Travel []) = ""
    format (Travel xs) = "Travel: " ++ unwords (map show xs)
    format (Select xs) = "Select: " ++ foldr1 (\x y -> x ++ ", " ++ y) xs
    format (Talk []) = ""
    format (Talk xs) = "Talk:   " ++ unwords (map show xs)
