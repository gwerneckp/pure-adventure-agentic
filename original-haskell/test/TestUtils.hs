module TestUtils (testGame, testDialogue) where

import Dialogue
import GameWorld
import Types

testGame :: Node -> Game
testGame i = Game [(0, 1)] i ["Russell"] [[], ["Brouwer", "Heyting"]]

testDialogue :: Dialogue
testDialogue =
  Branch
    (isAtZero)
    (Choice "Russell: Let's get our team together and head to Error." [])
    ( Choice
        "Brouwer: How can I help you?"
        [ ("Could I get a haircut?", Choice "Brouwer: Of course." []),
          ( "Could I get a pint?",
            Choice
              "Brouwer: Of course. Which would you like?"
              [ ("The Segmalt.", Action "" id),
                ("The Null Pinter.", Action "" id)
              ]
          ),
          ("Will you join us on a dangerous adventure?", Action "Brouwer: Of course." (add ["Brouwer"] . removeHere ["Brouwer"]))
        ]
    )
  where
    isAtZero Over = False
    isAtZero (Game _ n _ _) = n == 0
