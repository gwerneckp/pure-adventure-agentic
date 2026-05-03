module GameLoopSpec (spec) where

import Dialogue (DialogueInput (..), DialogueStep (..), dialoguePure)
import GameData (theLocations)
import GameLoop (GameStep (..), StepInput (..), stepPure)
import GameWorld (connected)
import Test.Hspec
import TestUtils (testGame)
import Types

spec :: Spec
spec = do
  describe "stepPure game loop" $ do
    it "matches expected behaviour from coursework.pdf example" $ do
      let g = testGame 0

      let RunDialogue dialogue _ = stepPure g (StepValidInput [2])

      let NeedChoice _ dialogue'@(Choice msg _) = dialoguePure g dialogue DialogueNoInput
      msg `shouldBe` "Russell: Let's go on an adventure!"

      let DeadEnd msg' = dialoguePure g dialogue' (DialogueValidInput 1)
      msg' `shouldBe` "You pack your bags and go with Russell."

      let Transition g' = stepPure g (StepValidInput [1])
      g' `shouldBe` testGame 1

      let RunDialogue dialogue'' _ = stepPure g' (StepValidInput [4, 2])
      let DeadEnd msg'' = dialoguePure g' dialogue'' (DialogueNoInput)
      msg'' `shouldContain` "Heyting: Hi Russell, what are you drinking?"

    it "handles invalid and exit inputs as expected" $ do
      let g = testGame 1

      -- out of bounds inputs
      let Invalid g' = stepPure g (StepValidInput [5])
      g' `shouldBe` g

      -- 1 input in move range, 1 input in dialogue range
      let Invalid g'' = stepPure g (StepValidInput [1, 2])
      g'' `shouldBe` g

      -- 1 zero input, 2 inputs in dialogue range
      let Invalid g''' = stepPure g (StepValidInput [0, 3, 4])
      g''' `shouldBe` g

      -- empty input
      let Invalid g'''' = stepPure g (StepValidInput [])
      g'''' `shouldBe` g

      -- exit input
      let Transition Over = stepPure g (StepValidInput [0])
      Over `shouldBe` Over
