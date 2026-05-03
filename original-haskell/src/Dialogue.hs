module Dialogue (dialoguePure, dialogue, findDialogue, prompt, line0, DialogueStep (..), DialogueInput (..)) where

import GameData (theDialogues)
import Types (Dialogue (..), Event, Game (..), Party)
import Utils (invalidInput, parseChoice)

prompt :: String
prompt = ">>"

line0 :: String
line0 = "There is nothing we can do."

data DialogueStep
  = DoAction String Event
  | Exit
  | DeadEnd String
  | -- Dialogue happens when first encountering a Choice node.
    -- Or when an invalid choice was made.
    -- The Bool indicates whether this is a result of an invalid input (True) or the first time presenting choices (False).
    NeedChoice Bool Dialogue

data DialogueInput
  = DialogueNoInput
  | DialogueInvalidInput
  | DialogueValidInput Int

dialoguePure :: Game -> Dialogue -> DialogueInput -> DialogueStep
-- We separate dialogue from dialoguePure to keep the pure logic isolated from IO
-- With this design, dialoguePure has no side effects and can be tested easily.
dialoguePure _ (Action msg ev) _ = DoAction msg ev
dialoguePure g (Branch cond t f) _ = if cond g then dialoguePure g t DialogueNoInput else dialoguePure g f DialogueNoInput
dialoguePure g (Choice msg opts) choiceStr
  | null opts = DeadEnd msg
  | otherwise = case choiceStr of
      DialogueNoInput ->
        NeedChoice False (Choice msg opts) -- first time presenting choices
      DialogueInvalidInput -> NeedChoice True (Choice msg opts) -- non-parsable input, we pass True
      DialogueValidInput n
        | n == 0 -> Exit -- choice 0 means exit dialogue
        | n >= 1 && n <= length opts ->
            let (_, dlg) = opts !! (n - 1) -- convert to 0-based index
             in dialoguePure g dlg DialogueNoInput -- recurse into selected dialogue
        | otherwise -> NeedChoice True (Choice msg opts) -- out-of-bounds choice, we pass True

dialogue :: Game -> Dialogue -> IO Game
dialogue game dlg = do
  case dialoguePure game dlg DialogueNoInput of
    DoAction msg ev -> do
      putStrLn msg
      return (ev game)
    NeedChoice isInvalid dlg'@(Choice msg opts)
      | isInvalid -> do
          invalid dlg'
      | otherwise -> do
          putStrLn msg
          printOptions opts
          putStrLn prompt
          inp <- getLine
          choice <- return (parseChoice inp)
          let choiceInput = case choice of
                Just n -> DialogueValidInput n
                Nothing -> DialogueInvalidInput
          case dialoguePure game dlg' choiceInput of
            DoAction msg' ev -> do
              putStrLn msg'
              return (ev game)
            NeedChoice True dlg'' -> do
              invalid dlg''
            NeedChoice False dlg'' -> do
              dialogue game dlg''
            DeadEnd msg' -> do
              putStrLn msg'
              return game
            Exit -> return game
    NeedChoice _ _ -> invalid dlg -- should not happen, included for totality
    DeadEnd msg -> do
      putStrLn msg
      return game
    Exit -> return game
  where
    invalid :: Dialogue -> IO Game
    invalid d = invalidInput (dialogue game d)

printOptions :: [(String, Dialogue)] -> IO ()
printOptions opts =
  mapM_ (\(i, (txt, _)) -> putStrLn (show i ++ ". " ++ txt)) (zip ([1 ..] :: [Int]) opts)

-- Lookup dialogue by party
findDialogue :: Party -> Dialogue
findDialogue party =
  case lookup party theDialogues of
    Just dlg -> dlg
    Nothing -> Action line0 id
