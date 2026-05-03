module GameLoop (game, stepPure, GameStep (..), StepInput (..)) where

import Dialogue (dialogue, findDialogue, prompt)
import GameData (start, theDescriptions, theLocations)
import GameWorld (connected)
import Types
import Utils (invalidInput, msort, parseChoices)

line1 :: String
line1 = "You are in "

line2 :: String
line2 = "You can travel to:"

line3 :: String
line3 = "With you are:"

line4 :: String
line4 = "You can see:"

line5 :: String
line5 = "What will you do?"

data GameStep
  = Transition Game
  | Invalid Game
  | RunDialogue Dialogue Game

data StepInput
  = StepInvalidInput
  | StepValidInput [Int]

stepPure :: Game -> StepInput -> GameStep
-- Similarly to dialoguePure, we separate step from stepPure to keep the pure logic isolated from IO.
-- stepPure has no side effects and can be tested easily.
stepPure Over _ = Transition Over
stepPure g@(Game m loc party npcs) input = do
  case input of
    StepValidInput choices ->
      -- Input rules:
      -- - Non number input = invalid.
      -- - A single number in the move range = travel.
      -- - A single number in the dialogue range = dialogue with one character.
      -- - Multiple numbers all in the dialogue range = dialogue line with all of them.
      -- - Any number out of bounds = invalid.
      -- - Any mix of move and dialogue numbers = invalid.
      -- - Two or more move numbers = invalid.
      if choices == [0]
        then Transition Over
        else
          if any (\n -> n < 1 || n > total) choices
            then Invalid g
            else do
              let extractChoicesInRange :: Maybe Int -> Maybe Int -> [Int] -> [Int]
                  extractChoicesInRange Nothing _ _ = []
                  extractChoicesInRange _ Nothing _ = []
                  extractChoicesInRange (Just lo) (Just hi) xs =
                    filter (\n -> n >= lo && n <= hi) xs

                  toIndexes :: Maybe Int -> [Int] -> [Int]
                  -- Note on Nothing: this means there are no items in this section, therefore list would always be empty.
                  -- We keep this case for completeness.
                  toIndexes Nothing _ = []
                  toIndexes (Just startIndex) xs = map (\n -> n - startIndex) xs

                  moves = extractChoicesInRange locStart locEnd choices
                  partyDialogues = extractChoicesInRange partyStart partyEnd choices
                  npcDialogues = extractChoicesInRange npcsStart npcsEnd choices

                  -- The input uses k-based numbering relative to the start of each section,
                  -- so we subtract the section’s start value k to get the correct 0-based index.
                  movesIndexes = toIndexes locStart moves
                  partyIndexes = toIndexes partyStart partyDialogues
                  npcIndexes = toIndexes npcsStart npcDialogues

              case (length moves, length (partyDialogues ++ npcDialogues)) of
                (0, 0) -> Invalid g
                (1, 0) ->
                  case movesIndexes of
                    [moveChoice] ->
                      let moveTo = connectedLocs !! moveChoice
                       in Transition (Game m moveTo party npcs)
                    _ ->
                      -- This branch should not occur because (1,0) implies exactly one move,
                      -- but it is included to keep the pattern match total.
                      Invalid g
                (0, _) ->
                  let partyNames = map (\i -> party !! i) partyIndexes
                      npcNames = map (\i -> npcsHere !! i) npcIndexes
                      allNames = msort (partyNames ++ npcNames)
                   in RunDialogue (findDialogue allNames) g
                _ -> Invalid g
    StepInvalidInput -> Invalid g
  where
    ((locStart, locEnd), (partyStart, partyEnd), (npcsStart, npcsEnd)) =
      optionRanges g

    connectedLocs = connected m loc
    npcsHere = npcs !! loc

    total =
      length (connected m loc)
        + length party
        + length (npcs !! loc)

step :: Game -> IO Game
step Over = return Over
step g@(Game m loc party npcs) = do
  putStrLn (line1 ++ locationDescriptionAt loc)

  -- Print each section using the same range logic as stepPure
  printSection line2 connectedLocs locRange locationNameAt
  printSection line3 party partyRange id
  printSection line4 npcsHere npcsRange id

  putStrLn line5
  putStrLn prompt

  inp <- getLine
  choices <- return (parseChoices inp)
  choicesInput <-
    case choices of
      Just ns -> return (StepValidInput ns)
      Nothing -> return StepInvalidInput

  -- Handle the input using the pure step
  case stepPure g choicesInput of
    Transition g' -> return g'
    Invalid g' -> invalid g'
    RunDialogue dlg g' -> dialogue g' dlg
  where
    connectedLocs = connected m loc
    npcsHere = npcs !! loc

    ((locRangeStart, _), (partyRangeStart, _), (npcsRangeStart, _)) =
      optionRanges g

    locRange = locRangeStart
    partyRange = partyRangeStart
    npcsRange = npcsRangeStart

    printSection :: String -> [a] -> Maybe Int -> (a -> String) -> IO ()
    printSection _ [] _ _ = return ()
    printSection _ _ Nothing _ = return ()
    printSection line xs (Just startIndex) f = do
      putStrLn line
      mapM_ (\(i, x) -> putStrLn (" " ++ show i ++ " " ++ f x)) (zip [startIndex ..] xs)

    invalid g' = invalidInput (return g')

game :: IO ()
game = go start
  where
    -- IO monad is used to sequence game steps: step produces an IO Game,
    -- and >>= feeds the resulting state back into the loop.
    go Over = return ()
    go g = step g >>= go

-- Helpers
range :: Maybe Int -> Int -> (Maybe Int, Maybe Int)
range _ 0 = (Nothing, Nothing)
range Nothing n = (Just 1, Just n)
range (Just n) k = (Just (n + 1), Just (n + k))

optionRanges :: Game -> ((Maybe Int, Maybe Int), (Maybe Int, Maybe Int), (Maybe Int, Maybe Int))
optionRanges Over = ((Nothing, Nothing), (Nothing, Nothing), (Nothing, Nothing)) -- Unreachable, included for totality
optionRanges (Game m loc party npcs) =
  ( (locStart, locEnd),
    (partyStart, partyEnd),
    (npcsStart, npcsEnd)
  )
  where
    -- we pass Just 0 to indicate the first section starts from 1, think of first argument as where the previous section ended
    (locStart, locEnd) = range (Just 0) (length (connected m loc))
    (partyStart, partyEnd) = range locEnd (length party)
    -- The reason for max here is that if there are no party members, the npcs start index should follow the locEnd directly.
    -- Otherwise, we might end up with overlapping indices for party and npcs. Such as 1 - 3 for loc, 0 for party, and 1 - 2 for npcs, as partyEnd would be Nothing.
    (npcsStart, npcsEnd) =
      max
        (range partyEnd (length (npcs !! loc)))
        (range locEnd (length (npcs !! loc)))

locationNameAt :: Node -> String
locationNameAt n = theLocations !! n

locationDescriptionAt :: Node -> String
locationDescriptionAt n = theDescriptions !! n
