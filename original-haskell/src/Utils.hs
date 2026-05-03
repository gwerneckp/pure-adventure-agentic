module Utils where

import Text.Read (readMaybe)

merge :: (Ord a) => [a] -> [a] -> [a]
merge xs [] = xs
merge [] ys = ys
merge (x : xs) (y : ys)
  | x < y = x : merge xs (y : ys)
  | x == y = x : merge xs ys
  | otherwise = y : merge (x : xs) ys

msort :: (Ord a) => [a] -> [a]
msort [] = []
msort [x] = [x]
msort xs = msort (take n xs) `merge` msort (drop n xs)
  where
    n = length xs `div` 2

line6 :: String
line6 = "[Unrecognized input]"

-- This helper function handles invalid input uniformly.
-- It takes as a parameter the IO action to continue the program:
--   - in the game loop, it will repeat the step function
--   - in dialogues, it repeats the current dialogue
invalidInput :: IO a -> IO a
invalidInput continue = do
  putStrLn line6
  continue

-- Parse a space-separated string of numbers safely (for game loop choices)
parseChoices :: String -> Maybe [Int]
parseChoices inp = mapM readMaybe (words inp)

-- Parse a single choice safely (dialogue choice)
parseChoice :: String -> Maybe Int
parseChoice inp = readMaybe inp